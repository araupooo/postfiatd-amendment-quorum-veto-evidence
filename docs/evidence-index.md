# Evidence Index

## What this pack is

An evidence pack for amendment voting quorum and veto behaviour in
postfiatd at commit `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10). It separates code facts (VERIFIED), documented rules
(SPECIFIED), modelled outcomes (MODELLED), and live-network unknowns
(UNTESTABLE).

## Files

| Path | What it is |
| --- | --- |
| `README.md` | This overview; how to reproduce |
| `configs/amendment-rules.json` | 45 rules (VERIFIED 38, SPECIFIED 4, MODELLED 2, UNTESTABLE 1) with file:line ranges, anchors, and divergence notes |
| `configs/scenarios.json` | 13 scenarios, 18 runs, full inputs |
| `src/amendment_model.py` | Deterministic simulator |
| `scripts/run_all.sh` | Entry point — runs the full suite, exit 0 only if every check passes |
| `scripts/probe.py` | 12 re-verification checks (A-00, A-01, B-01, C-01, D-01, E-01, F-01, G-01, H-01, I-01, J-01, T-01) |
| `scripts/extract_excerpts.py` | Extracts verbatim excerpts from the pinned checkout |
| `scripts/verify_digests.sh` | Verifies SHA256SUMS |
| `scripts/make_sha256sums.sh` | Regenerates SHA256SUMS |
| `scripts/clean_reproduce.sh` | Fresh-copy reproduction (run twice) |
| `fixtures/excerpts-manifest.json` | 44 excerpts, 16 source files, blob SHAs/sizes |
| `fixtures/source-hashes.json` | SHA-256 of every excerpt and source file |
| `fixtures/source-excerpts/E01.txt` … `E44.txt` | Verbatim source ranges |
| `outputs/derived/amendment-results.json` | Full simulator output (per-round transitions, blocking table) |
| `outputs/derived/scenario-matrix.json` | Per-run outcome table |
| `outputs/derived/probe-results.json` | Probe check results |
| `outputs/derived/run-summary.json` | Step statuses and counts |
| `outputs/run.log` | Unedited log of a full `run_all.sh` run (full SHA-256 digests) |
| `outputs/probe-run.log` | Unedited log of a standalone probe run |
| `outputs/fresh-clone-run.log` | Unedited log of a fresh-copy reproduction (`bash scripts/clean_reproduce.sh`, run twice; both passed, outputs byte-identical) |
| `docs/claim-index.md` | 24 claims (VERIFIED 16, SPECIFIED 2, MODELLED 4, UNTESTABLE 2) |
| `docs/methodology.md` | Method, classification, divergences, limits |
| `docs/decision-memo.md` | Contested-amendment operator memo + parameter sensitivity |
| `docs/excerpts.md` | Excerpt table (44 excerpts, 16 files) |
| `docs/scenario-matrix.md` | Scenario matrix + blocking table |
| `docs/risk-register.md` | 14 risks (HIGH 3, MEDIUM 8, LOW 3) |
| `docs/gap-register.md` | 8 gaps (live-network unknowns) |
| `docs/citations.md` | Verbatim docs quotes for the SPECIFIED rules |
| `docs/evidence-index.md` | This file |
| `findings.json` | 12 findings (HIGH 3, MEDIUM 5, LOW 4) |
| `run-manifest.json` | Counts, digests, probe pass count |
| `SHA256SUMS` | SHA-256 of every shipped file except itself |
| `.github/workflows/verify.yml` | CI: checkout pinned postfiatd → verify shipped digests → run full suite → verify regenerated digests |

## Headline numbers

- 45 rules: VERIFIED 38, SPECIFIED 4, MODELLED 2, UNTESTABLE 1.
- 13 scenarios, 18 runs: enabled 10, majority_lost 3, never_majority 5,
  quorum_gate_skip_runs 1.
- 12 findings, 24 claims, 14 risks, 8 gaps.
- 44 excerpts across 16 source files; 12/12 probe checks pass.
- Key divergence: post-fix majority is 67% (code) vs >80% (docs);
  validator quorum is 67% in this fork vs 80% in the docs.
