# Amendment Voting Quorum and Veto in postfiatd

How amendment voting reaches quorum and how minority coalitions can
delay or veto activation in postfiatd at commit
`0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).

## Headline findings

- **Post-fix majority is 67%, not the documented 80%.** The code
  threshold is `67/100` with strict `>` (`SystemParameters.h:85`);
  the docs say ">80% support for two weeks".
- **Validator quorum is 67% in this fork**, not 80%
  (`ValidatorList.cpp:1897-1900, 1934`).
- **Lose-at-deadline:** the docs say an amendment that loses support
  at the deadline is "ultimately enabled"; the code emits
  LostMajority only.
- **A veto is local.** It changes the operator's own vote from up to
  down; it cannot block network enablement (S-12).
- **One round below threshold restarts the two-week clock**
  (S-04: +961 rounds, 864,900 s).

## Contents

- 45 rules (VERIFIED 38, SPECIFIED 4, MODELLED 2, UNTESTABLE 1) —
  `configs/amendment-rules.json`, with grep-verified file:line ranges
  and verbatim excerpts in `fixtures/source-excerpts/` (44 excerpts,
  16 source files).
- Deterministic simulator (`src/amendment_model.py`) + scenario matrix
  — 13 scenarios, 18 runs: enabled 10, majority_lost 3,
  never_majority 5, quorum_gate_skip_runs 1.
- Claim-to-evidence index: 24 claims (VERIFIED 16, SPECIFIED 2,
  MODELLED 4, UNTESTABLE 2) — `docs/claim-index.md`.
- Findings: 12 (HIGH 3, MEDIUM 5, LOW 4) — `findings.json`.
- Risk register: 14 risks (HIGH 3, MEDIUM 8, LOW 3) —
  `docs/risk-register.md`. Gap register: 8 gaps —
  `docs/gap-register.md`.
- Contested-amendment operator memo + parameter sensitivity —
  `docs/decision-memo.md`. Methodology — `docs/methodology.md`.
  Evidence index — `docs/evidence-index.md`.

## Reproduction

```bash
bash scripts/run_all.sh        # exit 0 only if every check passes
bash scripts/clean_reproduce.sh  # fresh-copy reproduction (run twice)
```

- Full suite: `run_all.sh` exits 0; probe 12/12 checks pass.
- `outputs/run.log` (unedited full-run log, 10 lines) SHA-256:
  `863921c48fa10da406502828129e32d08222d24df32374218fe7d4e38904a4a3`
- Fresh-copy reproduction was run twice; both passed with
  byte-identical deterministic outputs (compare 53/53 checks pass).
  Fresh-clone run log: `outputs/fresh-clone-run.log` SHA-256:
  `863921c48fa10da406502828129e32d08222d24df32374218fe7d4e38904a4a3`
  (identical to the shipped `run.log` digest — the fresh copy
  reproduces the shipped log byte-for-byte).
- Digests: `amendment-results.json`
  `cb72896d37c1143cb648e6a538bed42f5f00a5e294b8a1a1b1d2e5816e01805a`;
  `scenario-matrix.json`
  `96684aa1a65fa5a0e1492382bf366b8c1c7deb57f3192af0f4c528b301d82262`.
- Verify all digests: `bash scripts/verify_digests.sh`.

## CI

Continuous integration runs the same suite on every push; see the
workflow runs page:

https://github.com/araupooo/postfiatd-amendment-quorum-veto-evidence/actions/workflows/verify.yml

## What is simulated vs source-derived

- **Source-derived:** all 38 VERIFIED rules, the 44 excerpts, the
  threshold/quorum formulas, the 67%-vs-80% divergences.
- **Simulated:** the 13 scenarios / 18 runs and the blocking table —
  deterministic outputs of `src/amendment_model.py` on the stated
  inputs in `configs/scenarios.json`. Simulated results are labelled
  MODELLED in the claim index and are never presented as code facts.
- **Unknown:** live-network state (live UNL, whether
  `AmendmentMajorityCalc` is enabled live, real close cadence) —
  see `docs/gap-register.md`. No live node was run.
