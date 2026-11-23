# Methodology

## Source

postfiatd at commit `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10). Every rule in `configs/amendment-rules.json` cites a
file:line range in that checkout, verified with `grep -n` on the local
checkout; every excerpt in `fixtures/source-excerpts/` is a verbatim
copy of the cited range, and `fixtures/source-hashes.json` records the
SHA-256 of each excerpt and the git blob SHA + size of each source
file. Line numbers are never taken from a browser fetch of a raw file
(those can serve different content than the pinned commit).

## Rule classification

- **VERIFIED** — the rule is in the pinned source; the cited range
  contains the anchor token (re-checked by `scripts/probe.py` A-01).
- **SPECIFIED** — the rule is a documented rule with no code source in
  the pinned tree; it carries a verbatim quote and a URL
  (`docs/citations.md`). SPECIFIED rules are the docs' claims, not
  code facts.
- **MODELLED** — a parameter or outcome derived from the simulator on
  stated inputs (flag interval 900 s, majority time 1,209,600 s).
- **UNTESTABLE** — a question the pinned source cannot answer and no
  live node was available to test.

## Simulator

`src/amendment_model.py` is a deterministic model of the amendment
voting logic, not a port of the C++ code. It implements, on the stated
inputs:

- threshold: pre-fix `max(1, floor(204/256 * N))` with `>=` (plus the
  single-validator `>=` exception); post-fix `max(1, floor(67/100 * N))`
  with strict `>`.
- validator quorum gate: voting runs only when validations >=
  `max(ceil(0.67 * UNL), ceil(0.6 * UNL))`.
- majority hold: 1,344 rounds of 900 s; losing the majority clears the
  record and restarts the clock.
- 24-hour trusted-vote expiry, modelled as scheduled vote drops.
- local veto: the vetoing node votes down; the network count is
  unchanged otherwise.

Inputs are in `configs/scenarios.json` (13 scenarios, 18 runs).
Outputs are `outputs/derived/amendment-results.json` and
`outputs/derived/scenario-matrix.json`. Re-running the simulator is
byte-identical (probe G-01).

## Divergences

Five code-vs-docs divergences are recorded in
`research/amendment-rules.md` (internal working notes, not shipped):

- **DVG-1** — post-fix majority is 67%, docs say >80%.
- **DVG-2** — validator quorum is 67% in this fork, docs assume 80%.
- **DVG-3** — lose-at-deadline: docs say "ultimately enabled", code
  emits LostMajority only.
- **DVG-4** — docs "more than 80%" for tfGotMajority is pre-fix
  language (pre-fix 79.6875% can record a majority).
- **DVG-5** — docs "80% or less" for tfLostMajority is pre-fix
  language.

## What was not done

- No live node was run; no RPC call was made; no live-network data
  was observed. All live-network unknowns are in
  `docs/gap-register.md`.
- No amendment was enabled, vetoed, or voted on in any live network.
- The simulator models the documented voting rules; it does not model
  consensus-set selection of pseudo-transactions, so a disputed
  amendment at its deadline (S-11) is modelled as the single-node
  doVoting outcome, not as a multi-node consensus outcome.

## Reproduction

```bash
bash scripts/run_all.sh   # exit 0 only if every check passes
bash scripts/clean_reproduce.sh   # fresh-copy reproduction, twice
```

`run_all.sh` prints full 64-char SHA-256 digests of every
deterministic output. `outputs/run.log` is the unedited log of a full
run.
