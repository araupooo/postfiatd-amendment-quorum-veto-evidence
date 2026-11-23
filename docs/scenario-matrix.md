# Scenario Matrix

Deterministic simulator output on the inputs in `configs/scenarios.json` (flag interval 900 s, majority time 1,209,600 s = two weeks). `delay_rounds` counts flag ledgers between the ideal enablement round (majority held from its first gain) and the actual enablement round. The Votes column is the run's initial vote count; runs with dips, churn, or expiry change votes over time — see the full per-round transitions in `outputs/derived/amendment-results.json`.

| Scenario | Run | UNL | Votes (initial) | Regime | Outcome | Majority round | Enabled round | Delay rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S-01 | A | 35 | 27 | pre | enabled | 0 | 1344 | 0 |
| S-01 | B | 35 | 26 | pre | never_majority | None | None | None |
| S-02 | A | 35 | 24 | post | enabled | 0 | 1344 | 0 |
| S-02 | B | 35 | 23 | post | never_majority | None | None | None |
| S-03 | A | 35 | 24 | post | enabled | 0 | 1344 | 0 |
| S-03 | B | 35 | 23 | post | never_majority | None | None | None |
| S-04 | A | 35 | 30 | post | enabled | 0 | 2305 | 961 |
| S-05 | A | 35 | 30 | post | majority_lost | 0 | None | None |
| S-06 | A | 35 | 30 | post | enabled | 0 | 1344 | 0 |
| S-07 | A | 35 | 24 | post | majority_lost | 0 | None | None |
| S-08 | A | 1 | 1 | post | enabled | 0 | 1344 | 0 |
| S-09 | A | 5 | 3 | pre | enabled | 0 | 1344 | 0 |
| S-09 | B | 5 | 3 | post | never_majority | None | None | None |
| S-10 | A | 35 | 28 | pre | enabled | 0 | 1544 | 200 |
| S-11 | A | 35 | 30 | post | majority_lost | 0 | None | None |
| S-12 | A | 35 | 30 | post | enabled | 0 | 1344 | 0 |
| S-13 | A | 35 | 30 | post | never_majority | None | None | None |
| S-13 | B | 35 | 24 | post | enabled | 0 | 1344 | 0 |

Totals: 13 scenarios, 18 runs — enabled 10, majority_lost 3, never_majority 5, quorum_gate_skip_runs 1.

## Blocking table

| UNL | Pre-fix threshold | Pre-fix min passing | Pre-fix min blocking | Post-fix threshold | Post-fix min passing | Post-fix min blocking | Validator quorum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 3 | 3 | 3 | 3 | 4 | 2 | 4 |
| 10 | 7 | 7 | 4 | 6 | 7 | 4 | 7 |
| 21 | 16 | 16 | 6 | 14 | 15 | 7 | 15 |
| 35 | 27 | 27 | 9 | 23 | 24 | 12 | 24 |
| 100 | 79 | 79 | 22 | 67 | 68 | 33 | 67 |
