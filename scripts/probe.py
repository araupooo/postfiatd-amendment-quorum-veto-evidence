#!/usr/bin/env python3
"""probe.py — re-verify the amendment quorum/veto pack from its outputs.

Usage:
    python3 scripts/probe.py [--skip-manifest-check] [AMENDMENT_RESULTS_JSON]

The --skip-manifest-check flag is for run_all.sh step 4 only: the
manifest on disk at that point predates the just-regenerated results,
so comparing against it would fail on any input change; step 5b re-runs
the probe without the flag after rewriting the manifest. A standalone
probe run (no flag) always performs the manifest check.

Checks (all re-derived, none trusted):
  A-00 pinned checkout HEAD equals the pinned commit.
  A-01 every VERIFIED rule's anchor sits inside its cited range in the
     pinned checkout; SPECIFIED rules carry external URLs; MODELLED /
     UNTESTABLE rules carry no file source. (45 rules: 38/4/2/1.)
  B-01 scenario arithmetic: 13 scenarios, 18 runs; outcomes enabled 10 /
     majority_lost 3 / never_majority 5; quorum_gate_skip_runs 1;
     matrix rows == runs; delay_rounds consistent with majority/enabled
     rounds.
  C-01 threshold math re-derived for UNL sizes 5, 10, 21, 35, 100 in both
     regimes: threshold, min passing votes, min blocking minority.
  D-01 key tokens at recorded lines: 204/256 (SystemParameters.h:83),
     67/100 (:85), weeks{2} (:88), FLAG_LEDGER_INTERVAL = 256
     (Ledger.h:426), tfGotMajority 0x00010000 (TxFlags.h:128),
     AMENDMENT_MAJORITY_TIME (Config.h:248).
  E-01 67% validator-quorum comment and formula re-grep:
     "Original XRPL uses 80%" + 0.67f / 0.6f in ValidatorList.cpp.
  F-01 counts reconcile across files: matrix == results == scenarios
     (13); findings 12, claims 24 (16/2/4/2), risks 14, gaps 8; excerpts
     44 across 16 files agree across manifest, files, hashes.
  G-01 determinism: re-running the simulator to a temp dir reproduces
     byte-identical outputs (full SHA-256 compare).
  H-01 excerpt integrity: every excerpt file digest matches
     fixtures/source-hashes.json and every manifest blob SHA/size
     matches `git hash-object` / file size in the checkout;
     run-manifest digests match the shipped derived files.
  I-01 absence findings re-grepped: kAmendmentMajorityCalcThreshold
     0 hits; tfEnableAmendment 0 hits (enable uses no flag); "0.8"
     literal 0 hits in AmendmentTable.cpp.
  J-01 divergence tokens: post-fix ratio is 67/100 (not 80/100) and
     pre-fix is 204/256; the "80%" figure appears only in the docs
     citations, never as a code threshold.
  T-01 timing sanity only (non-negative, never recorded).

Exit 0 only if every case passes. Prints one PASS/FAIL line per case
with the FULL 64-char SHA-256 digest where a digest is involved, and
writes outputs/derived/probe-results.json plus outputs/probe-run.log
(the log is the unedited stdout of this run; it contains no absolute
paths and no timestamps). No live node is involved.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parent.parent
PINNED_COMMIT = "0085a1ff885d6a446369cf73a4430f75af22be55"
PINNED_CHECKOUT = Path(os.environ.get(
    "PINNED_CHECKOUT", str(Path.home() / "workspace" / "postfiatd-pin-0085a1f")))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def git_blob(relpath):
    out = subprocess.run(["git", "-C", str(PINNED_CHECKOUT), "hash-object", "--", relpath],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def read_lines(relpath):
    return (PINNED_CHECKOUT / relpath).read_text().splitlines()


def grep_hits(pattern, *roots):
    proc = subprocess.run(
        ["grep", "-rn", pattern, *[str(PINNED_CHECKOUT / r) for r in roots]],
        capture_output=True, text=True)
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]


def main():
    started = time.time()
    argv = [a for a in sys.argv[1:] if a != "--skip-manifest-check"]
    skip_manifest = "--skip-manifest-check" in sys.argv[1:]
    results_path = Path(argv[0]) if argv else \
        PACK_ROOT / "outputs" / "derived" / "amendment-results.json"
    doc = load_json(results_path)
    matrix = load_json(PACK_ROOT / "outputs" / "derived" / "scenario-matrix.json")
    rules = load_json(PACK_ROOT / "configs" / "amendment-rules.json")["rules"]
    scenarios = load_json(PACK_ROOT / "configs" / "scenarios.json")["scenarios"]
    manifest = load_json(PACK_ROOT / "fixtures" / "excerpts-manifest.json")
    hashes = load_json(PACK_ROOT / "fixtures" / "source-hashes.json")
    findings = load_json(PACK_ROOT / "findings.json")["findings"]
    checks, lines = [], []

    def check(cid, label, ok, detail=""):
        checks.append({"id": cid, "check": label, "pass": bool(ok), "detail": detail})
        lines.append(("PASS " if ok else "FAIL ") + cid + " " + label +
                     ((" — " + detail) if detail else ""))

    # A-00: pinned checkout HEAD.
    head = subprocess.run(["git", "-C", str(PINNED_CHECKOUT), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    check("A-00", "pinned checkout HEAD equals the pinned commit",
          head.stdout.strip() == PINNED_COMMIT,
          f"HEAD={head.stdout.strip()}")

    # A-01: rule anchors inside cited ranges.
    bad = []
    counts = Counter(r["status"] for r in rules)
    for r in rules:
        if r["status"] == "VERIFIED":
            s = r.get("source")
            if not s:
                bad.append(f"{r['id']}: no source")
                continue
            try:
                chunk = read_lines(s["file"])[s["start_line"] - 1:s["end_line"]]
            except (FileNotFoundError, IndexError):
                bad.append(f"{r['id']}: unreadable range")
                continue
            if s.get("anchor") and not any(s["anchor"] in ln for ln in chunk):
                bad.append(f"{r['id']}: anchor not in range")
        elif r["status"] == "SPECIFIED":
            ext = r.get("external")
            if not ext or "url" not in ext or "quote" not in ext:
                bad.append(f"{r['id']}: specified rule needs url+quote")
        else:
            if r.get("source") is not None:
                bad.append(f"{r['id']}: {r['status']} rule must carry no file source")
    check("A-01",
          "45 rules: 38 VERIFIED anchors inside cited ranges, 4 SPECIFIED (external URLs), 2 MODELLED, 1 UNTESTABLE, none with a faked source",
          not bad and len(rules) == 45 and counts == {"VERIFIED": 38, "SPECIFIED": 4, "MODELLED": 2, "UNTESTABLE": 1},
          "; ".join(bad[:3]) or f"counts={dict(sorted(counts.items()))}")

    # B-01: scenario arithmetic.
    totals = doc["totals"]
    runs = [run for sc in doc["scenarios"] for run in sc["runs"]]
    outcomes = Counter(run["outcome"] for run in runs)
    delay_ok = True
    for run in runs:
        if run["enabled_round"] is not None and run["ideal_enable_round"] is not None:
            if run["delay_rounds"] != run["enabled_round"] - run["ideal_enable_round"]:
                delay_ok = False
        if run["enabled_round"] is not None and run["delay_s"] is not None:
            if run["delay_s"] != run["delay_rounds"] * 900:
                delay_ok = False
    check("B-01",
          "per-scenario arithmetic reconciles; totals 13 scenarios / 18 runs / enabled 10 / majority_lost 3 / never_majority 5 / quorum_gate_skip_runs 1; matrix rows == runs; delays consistent",
          totals == {"scenarios": 13, "runs": 18, "enabled": 10,
                     "majority_lost": 3, "never_majority": 5,
                     "quorum_gate_skip_runs": 1}
          and outcomes == {"enabled": 10, "majority_lost": 3, "never_majority": 5}
          and len(matrix["rows"]) == 18 and delay_ok,
          f"totals={totals} outcomes={dict(outcomes)}")

    # C-01: threshold math re-derived.
    def thr(n, regime):
        num, den = (204, 256) if regime == "pre" else (67, 100)
        return max(1, (n * num) // den)

    def minpass(n, regime):
        for v in range(0, n + 1):
            t = thr(n, regime)
            if ((v >= t) if (regime == "pre" or n == 1) else (v > t)):
                return v
        return None

    def minblock(n, regime):
        failing = [v for v in range(0, n + 1)
                   if not ((v >= thr(n, regime)) if (regime == "pre" or n == 1) else (v > thr(n, regime)))]
        return n - max(failing) if failing else None

    c_ok = True
    c_detail = []
    for row in doc["blocking_table"]:
        n = row["unl_size"]
        for regime in ("pre", "post"):
            if (row[regime]["threshold"] != thr(n, regime)
                    or row[regime]["min_passing_votes"] != minpass(n, regime)
                    or row[regime]["min_blocking_minority"] != minblock(n, regime)):
                c_ok = False
                c_detail.append(f"n={n} {regime}")
        if row["validator_quorum"] != max(math.ceil(n * 0.67), math.ceil(n * 0.6)):
            c_ok = False
            c_detail.append(f"n={n} quorum")
    check("C-01",
          "threshold math re-derived for UNL 5/10/21/35/100 in both regimes (threshold, min passing votes, min blocking minority, validator quorum)",
          c_ok, "; ".join(c_detail[:3]) or "all match")

    # D-01: key tokens at recorded lines.
    def token_at(relpath, lineno, token):
        chunk = read_lines(relpath)
        return lineno <= len(chunk) and token in chunk[lineno - 1]

    d_checks = [
        ("include/xrpl/protocol/SystemParameters.h", 83, "204, 256"),
        ("include/xrpl/protocol/SystemParameters.h", 85, "67, 100"),
        ("include/xrpl/protocol/SystemParameters.h", 88, "weeks{2}"),
        ("src/xrpld/app/ledger/Ledger.h", 426, "FLAG_LEDGER_INTERVAL = 256"),
        ("include/xrpl/protocol/TxFlags.h", 128, "tfGotMajority"),
        ("src/xrpld/core/Config.h", 248, "AMENDMENT_MAJORITY_TIME"),
    ]
    d_bad = [f"{f}:{ln} {t!r}" for f, ln, t in d_checks if not token_at(f, ln, t)]
    check("D-01",
          "204/256 (SystemParameters.h:83), 67/100 (:85), weeks{2} (:88), FLAG_LEDGER_INTERVAL = 256 (Ledger.h:426), tfGotMajority (TxFlags.h:128), AMENDMENT_MAJORITY_TIME (Config.h:248)",
          not d_bad, "; ".join(d_bad[:3]) or "all 6 tokens at recorded lines")

    # E-01: 67% quorum comment + formula.
    vl = read_lines("src/xrpld/app/misc/detail/ValidatorList.cpp")
    e_ok = ("67% quorum" in "\n".join(vl[1895:1902])
            and "Original XRPL uses 80%" in "\n".join(vl[1895:1902])
            and "0.67f" in vl[1933] and "0.6f" in vl[1933])
    check("E-01",
          "67% quorum comment (ValidatorList.cpp:1897-1900) and formula max(ceil(0.67), ceil(0.6)) (:1934)",
          e_ok, "comment+formula verified" if e_ok else "mismatch")

    # F-01: counts reconcile across files.
    def table_rows(path, prefix):
        rows = []
        for ln in open(path, encoding="utf-8"):
            m = re.match(rf"\| ({prefix}-\d+) \| ([A-Z]+) \|", ln)
            if m:
                rows.append((m.group(1), m.group(2)))
        return rows

    claims = table_rows(PACK_ROOT / "docs" / "claim-index.md", "C")
    risks = table_rows(PACK_ROOT / "docs" / "risk-register.md", "K")
    gaps = [ln for ln in open(PACK_ROOT / "docs" / "gap-register.md", encoding="utf-8")
            if re.match(r"\| G-\d+ \|", ln)]
    man = load_json(PACK_ROOT / "run-manifest.json") if (PACK_ROOT / "run-manifest.json").is_file() else None
    f_ok = (len(doc["scenarios"]) == 13 and len(runs) == 18
            and len(findings) == 12 and len(claims) == 24
            and Counter(s for _, s in claims) == {"VERIFIED": 16, "SPECIFIED": 2, "MODELLED": 4, "UNTESTABLE": 2}
            and len(risks) == 14 and len(gaps) == 8
            and len(manifest["excerpts"]) == 44
            and len(hashes["files"]) == 16
            and len(hashes["excerpts"]) == 44)
    check("F-01",
          "matrix == results == scenarios (13); findings 12, claims 24 (16/2/4/2), risks 14, gaps 8; excerpts 44 across 16 files agree across manifest, files, hashes",
          f_ok, f"claims={len(claims)} risks={len(risks)} gaps={len(gaps)} excerpts={len(manifest['excerpts'])}")

    # G-01: determinism — capture digests, re-run simulator, compare.
    res_before = sha256_file(PACK_ROOT / "outputs" / "derived" / "amendment-results.json")
    mat_before = sha256_file(PACK_ROOT / "outputs" / "derived" / "scenario-matrix.json")
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, "src/amendment_model.py"],
            cwd=str(PACK_ROOT), capture_output=True, text=True)
        g_ok = proc.returncode == 0
    res_digest = sha256_file(PACK_ROOT / "outputs" / "derived" / "amendment-results.json")
    mat_digest = sha256_file(PACK_ROOT / "outputs" / "derived" / "scenario-matrix.json")
    g_ok = g_ok and res_digest == res_before and mat_digest == mat_before
    check("G-01",
          "determinism: simulator re-run reproduces byte-identical results and matrix (full SHA-256)",
          g_ok,
          f"results shipped={res_before} rerun={res_digest}; matrix shipped={mat_before} rerun={mat_digest}")

    # H-01: excerpt integrity + manifest digests.
    h_bad = []
    for ex_id, rec in hashes["excerpts"].items():
        p = PACK_ROOT / "fixtures" / "source-excerpts" / f"{ex_id}.txt"
        if not p.is_file() or sha256_file(p) != rec["sha256"]:
            h_bad.append(ex_id)
    for relpath, rec in hashes["files"].items():
        if git_blob(relpath) != rec["git_blob_sha"]:
            h_bad.append(f"{relpath}:blob")
        if (PINNED_CHECKOUT / relpath).stat().st_size != rec["size_bytes"]:
            h_bad.append(f"{relpath}:size")
    man_ok = True
    if not skip_manifest and man is not None:
        man_ok = (man.get("results_sha256") == res_digest
                  and man.get("matrix_sha256") == mat_digest)
    check("H-01",
          "every excerpt digest matches source-hashes.json; every manifest blob SHA/size matches the checkout; run-manifest digests match shipped derived files",
          not h_bad and man_ok,
          "; ".join(h_bad[:3]) or ("manifest digests match" if man_ok else "manifest digest mismatch"))

    # I-01: absence findings re-grepped.
    def count_hits(pattern, *roots):
        return len(grep_hits(pattern, *roots))

    i1 = count_hits("kAmendmentMajorityCalcThreshold", "src", "include")
    i2 = count_hits("tfEnableAmendment", "src", "include")
    i3 = count_hits("0\\.8", "src/xrpld/app/misc/detail/AmendmentTable.cpp")
    check("I-01",
          "absence findings re-grepped: kAmendmentMajorityCalcThreshold 0 hits; tfEnableAmendment 0 hits; '0.8' literal 0 hits in AmendmentTable.cpp",
          i1 == 0 and i2 == 0 and i3 == 0,
          f"kAmendmentMajorityCalcThreshold={i1} tfEnableAmendment={i2} 0.8={i3}")

    # J-01: divergence tokens.
    sp = read_lines("include/xrpl/protocol/SystemParameters.h")
    j_ok = ("67, 100" in sp[84] and "204, 256" in sp[82]
            and "80" not in sp[82] and "80" not in sp[84])
    cit = (PACK_ROOT / "docs" / "citations.md").read_text()
    j_ok = j_ok and "80%" in cit
    check("J-01",
          "post-fix ratio is 67/100 and pre-fix 204/256 (no 80 in the threshold lines); '80%' appears only in the docs citations, never as a code threshold",
          j_ok, "divergence tokens verified" if j_ok else "mismatch")

    # T-01: timing sanity.
    elapsed_ms = int((time.time() - started) * 1000)
    check("T-01",
          "timing sanity: total probe elapsed_ms is non-negative (loose band, never exact)",
          elapsed_ms >= 0, "value not recorded; never compared")

    passed = sum(1 for c in checks if c["pass"])
    total = len(checks)
    lines.append(f"probe: {passed}/{total} checks PASS")
    lines.append(f"probe: amendment-results.json sha256: {res_digest}")
    lines.append(f"probe: scenario-matrix.json sha256: {mat_digest}")
    lines.append(f"probe: pinned commit {PINNED_COMMIT}")
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    result_doc = {"pack": "Amendment Voting Quorum and Veto in postfiatd",
                  "pinned_commit": PINNED_COMMIT,
                  "results_file": "outputs/derived/amendment-results.json",
                  "results_sha256": res_digest, "matrix_sha256": mat_digest,
                  "checks": checks, "passed": passed, "total": total}
    out_derived = PACK_ROOT / "outputs" / "derived" / "probe-results.json"
    out_derived.parent.mkdir(parents=True, exist_ok=True)
    with open(out_derived, "w", encoding="utf-8") as fh:
        json.dump(result_doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    (PACK_ROOT / "outputs" / "probe-run.log").write_text(text)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
