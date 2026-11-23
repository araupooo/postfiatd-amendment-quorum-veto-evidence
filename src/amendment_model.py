#!/usr/bin/env python3
"""amendment_model.py — deterministic amendment quorum/veto simulator.

Models the pinned postfiatd amendment voting rules at flag-ledger
granularity, following src/xrpld/app/misc/detail/AmendmentTable.cpp,
src/xrpld/app/consensus/RCLConsensus.cpp, src/xrpld/app/tx/detail/Change.cpp
and src/xrpld/app/misc/detail/ValidatorList.cpp at commit
0085a1ff885d6a446369cf73a4430f75af22be55.

One round is one flag ledger (256 ledgers apart). Close time advances
flag_interval_s per round (default 900, per xrpl.org "typically about
15 minutes"). Majority must be held for majority_time_s (two weeks,
1,209,600 s) from the round the majority is first recorded.

Threshold math (AmendmentSet::computeThreshold + passes):
  pre-fix:  threshold = max(1, (trusted * 204) // 256); passes iff votes >= threshold
  post-fix: threshold = max(1, (trusted * 67) // 100);  passes iff votes > threshold,
            except a single trusted validator, which still uses >=.
Validator quorum gate (RCLConsensus + ValidatorList::calculateQuorum):
  quorum = max(ceil(effective_unl * 0.67), ceil(unl * 0.6)); if the number of
  trusted validations present is below quorum, no amendment voting happens
  that round.
doVoting branch order (one action per amendment per round per node):
  has_val and not has_ledger and local vote up -> GotMajority (record majority)
  not has_val and has_ledger                    -> LostMajority (clear majority)
  has_ledger and majority held and local up     -> Enable (no-flag pseudo-tx)
  has_val and has_ledger                        -> Hold (waiting)
  otherwise                                     -> None
A local veto (local_vote_up false) suppresses the local node's GotMajority
and Enable actions; network_up says whether non-vetoing nodes still propose
them, so the ledger-level majority/enablement can still happen.

Deterministic: no timestamps, no absolute paths, no randomness. Re-runs
produce byte-identical outputs. Writes outputs/derived/amendment-results.json
and outputs/derived/scenario-matrix.json, and prints full SHA-256 digests.

Usage: python3 src/amendment_model.py [--help]
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parent.parent
PINNED_COMMIT = "0085a1ff885d6a446369cf73a4430f75af22be55"
MAJORITY_TIME_S = 1209600  # two weeks
FLAG_INTERVAL_S = 900  # docs: flag ledgers typically ~15 minutes apart

PRE_NUM, PRE_DEN = 204, 256
POST_NUM, POST_DEN = 67, 100


def threshold(trusted, regime):
    """AmendmentSet::computeThreshold: max(1, (trusted * num) // den)."""
    if regime == "pre":
        num, den = PRE_NUM, PRE_DEN
    elif regime == "post":
        num, den = POST_NUM, POST_DEN
    else:
        raise ValueError(f"unknown regime {regime!r}")
    return max(1, (trusted * num) // den)


def passes(votes, trusted, regime):
    """AmendmentSet::passes with the single-validator >= exception."""
    t = threshold(trusted, regime)
    if regime == "pre" or trusted == 1:
        return votes >= t
    return votes > t


def validator_quorum(unl_size, effective_unl_size=None):
    """ValidatorList::calculateQuorum (no publisher lists, no CLI override):
    max(ceil(effective * 0.67), ceil(unl * 0.6))."""
    if effective_unl_size is None:
        effective_unl_size = unl_size
    return max(
        math.ceil(effective_unl_size * 0.67),
        math.ceil(unl_size * 0.6),
    )


def min_passing_votes(trusted, regime):
    """Smallest vote count that passes for this trusted count and regime."""
    for v in range(0, trusted + 1):
        if passes(v, trusted, regime):
            return v
    return None


def min_blocking_minority(trusted, regime):
    """Smallest number of no-voters that blocks a majority (trusted - max
    failing votes). Returns None when even zero yes-votes pass (never)."""
    failing = [v for v in range(0, trusted + 1) if not passes(v, trusted, regime)]
    if not failing:
        return None
    return trusted - max(failing)


def simulate_run(scenario, run, flag_interval_s, majority_time_s):
    """Run one flag-round simulation. Returns a result dict."""
    regime = run.get("regime", scenario["regime"])
    unl = scenario["unl_size"]
    local_up = scenario["local_vote_up"]
    network_up = scenario["network_up"]
    events = sorted(run["events"], key=lambda e: e["round"])
    max_round = 0
    # Upper bound: enough rounds for a full hold plus the last event + margin.
    last_event_round = max(e["round"] for e in events)
    max_round = last_event_round + (majority_time_s // flag_interval_s) + 400

    votes = None
    trusted = unl
    validations = None
    events_by_round = {}
    for e in events:
        events_by_round.setdefault(e["round"], e)

    majority_since = None  # close time (s) when majority was first recorded
    enabled_round = None
    enabled_close_time = None
    majority_round = None
    lost_rounds = []
    got_rounds = []
    transitions = []
    hold_rounds = 0

    r = 0
    while r <= max_round:
        if r in events_by_round:
            e = events_by_round[r]
            if "votes" in e:
                votes = e["votes"]
            if "unl_size" in e:
                trusted = e["unl_size"]
            if "validations" in e:
                validations = e["validations"]
        if votes is None:
            r += 1
            continue
        if validations is None:
            validations = trusted
        close_time = r * flag_interval_s
        quorum = validator_quorum(trusted)
        t = threshold(trusted, regime)
        has_val = passes(votes, trusted, regime)
        has_ledger = majority_since is not None
        action = None
        if validations < quorum:
            # RCLConsensus skips amendment voting entirely this round.
            action = "quorum_gate_skip"
        elif has_val and not has_ledger and (local_up or network_up):
            action = "got_majority"
            majority_since = close_time
            if majority_round is None:
                # Ideal enablement is measured from the FIRST time the
                # amendment gained majority; a later re-gain after a loss
                # is a delay, not a new ideal.
                majority_round = r
            got_rounds.append(r)
        elif not has_val and has_ledger:
            action = "lost_majority"
            majority_since = None
            lost_rounds.append(r)
        elif (
            has_ledger
            and (majority_since + majority_time_s) <= close_time
            and (local_up or network_up)
        ):
            action = "enable"
            enabled_round = r
            enabled_close_time = close_time
        elif has_val and has_ledger:
            action = "hold"
            hold_rounds += 1
        else:
            action = "none"
        transitions.append(
            {
                "round": r,
                "close_time_s": close_time,
                "votes": votes,
                "trusted": trusted,
                "validations": validations,
                "quorum": quorum,
                "threshold": t,
                "has_majority": has_val,
                "ledger_majority": has_ledger,
                "action": action,
            }
        )
        if enabled_round is not None:
            break
        r += 1

    # Compress transitions: keep first round, every action change, and the
    # final round. Full per-round detail is recoverable from the event list.
    compressed = []
    prev_action = None
    for tr in transitions:
        if tr["action"] != prev_action or tr is transitions[0]:
            compressed.append(tr)
            prev_action = tr["action"]
    if transitions and compressed[-1] is not transitions[-1]:
        compressed.append(transitions[-1])

    ideal_enable_round = None
    if majority_round is not None:
        ideal_enable_round = majority_round + (majority_time_s // flag_interval_s)
    delay_rounds = None
    if enabled_round is not None and ideal_enable_round is not None:
        delay_rounds = enabled_round - ideal_enable_round

    if enabled_round is not None:
        outcome = "enabled"
    elif got_rounds:
        outcome = "majority_lost"
    else:
        outcome = "never_majority"

    return {
        "label": run["label"],
        "regime": regime,
        "threshold": threshold(trusted, regime),
        "min_passing_votes": min_passing_votes(trusted, regime),
        "min_blocking_minority": min_blocking_minority(trusted, regime),
        "validator_quorum": validator_quorum(trusted),
        "outcome": outcome,
        "majority_round": majority_round,
        "enabled_round": enabled_round,
        "enabled_close_time_s": enabled_close_time,
        "ideal_enable_round": ideal_enable_round,
        "delay_rounds": delay_rounds,
        "delay_s": (delay_rounds * flag_interval_s) if delay_rounds is not None else None,
        "got_majority_rounds": got_rounds,
        "lost_majority_rounds": lost_rounds,
        "hold_rounds": hold_rounds,
        "rounds_simulated": len(transitions),
        "transitions": compressed,
    }


def blocking_table():
    """Minimum blocking minority per UNL size and regime (R-09 / R-26)."""
    table = []
    for n in (5, 10, 21, 35, 100):
        row = {"unl_size": n}
        for regime in ("pre", "post"):
            row[regime] = {
                "threshold": threshold(n, regime),
                "min_passing_votes": min_passing_votes(n, regime),
                "min_blocking_minority": min_blocking_minority(n, regime),
            }
        row["validator_quorum"] = validator_quorum(n)
        table.append(row)
    return table


def main():
    ap = argparse.ArgumentParser(description="Deterministic amendment quorum/veto simulator.")
    ap.parse_args()
    rules = json.load(open(PACK_ROOT / "configs" / "amendment-rules.json"))
    scenarios_doc = json.load(open(PACK_ROOT / "configs" / "scenarios.json"))
    flag_interval_s = scenarios_doc.get("flag_interval_s_default", FLAG_INTERVAL_S)
    majority_time_s = scenarios_doc.get("majority_time_s", MAJORITY_TIME_S)

    results = {"pack": "Amendment Voting Quorum and Veto in postfiatd",
               "pinned_commit": PINNED_COMMIT,
               "model": {"flag_interval_s": flag_interval_s,
                         "majority_time_s": majority_time_s,
                         "pre_threshold": "204/256, passes on >=",
                         "post_threshold": "67/100, passes on strict >, single-validator >= exception"},
               "scenarios": [],
               "blocking_table": blocking_table()}
    totals = {"scenarios": 0, "runs": 0, "enabled": 0, "majority_lost": 0,
              "never_majority": 0, "quorum_gate_skip_runs": 0}
    for sc in scenarios_doc["scenarios"]:
        entry = {"id": sc["id"], "title": sc["title"], "regime": sc["regime"],
                 "unl_size": sc["unl_size"], "local_vote_up": sc["local_vote_up"],
                 "network_up": sc["network_up"], "runs": []}
        for run in sc["runs"]:
            res = simulate_run(sc, run, flag_interval_s, majority_time_s)
            entry["runs"].append(res)
            totals["runs"] += 1
            totals[res["outcome"]] += 1
            if any(t["action"] == "quorum_gate_skip" for t in res["transitions"]):
                totals["quorum_gate_skip_runs"] += 1
        results["scenarios"].append(entry)
        totals["scenarios"] += 1
    results["totals"] = totals

    matrix = []
    for sc in results["scenarios"]:
        for run in sc["runs"]:
            matrix.append({
                "scenario": sc["id"],
                "run": run["label"],
                "regime": run["regime"],
                "outcome": run["outcome"],
                "majority_round": run["majority_round"],
                "enabled_round": run["enabled_round"],
                "delay_rounds": run["delay_rounds"],
                "min_passing_votes": run["min_passing_votes"],
                "min_blocking_minority": run["min_blocking_minority"],
            })
    matrix_doc = {"pack": results["pack"], "pinned_commit": PINNED_COMMIT,
                  "flag_interval_s": flag_interval_s,
                  "majority_time_s": majority_time_s,
                  "rows": matrix}

    outdir = PACK_ROOT / "outputs" / "derived"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "amendment-results.json", "w") as fh:
        json.dump(results, fh, indent=1)
        fh.write("\n")
    with open(outdir / "scenario-matrix.json", "w") as fh:
        json.dump(matrix_doc, fh, indent=1)
        fh.write("\n")

    def sha256_file(path):
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    print(f"amendment model: {totals['scenarios']} scenarios, {totals['runs']} runs: "
          f"enabled {totals['enabled']}, majority_lost {totals['majority_lost']}, "
          f"never_majority {totals['never_majority']}")
    print("amendment-results.json sha256: " + sha256_file(outdir / "amendment-results.json"))
    print("scenario-matrix.json sha256: " + sha256_file(outdir / "scenario-matrix.json"))
    print(f"pinned commit {PINNED_COMMIT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
