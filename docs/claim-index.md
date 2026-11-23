# Claim-to-Evidence Index

Every claim carries one status: **VERIFIED** (line-verified in the pinned
source), **SPECIFIED** (documented rule, quoted from the docs, no code
source), **MODELLED** (deterministic simulator output on stated inputs),
**UNTESTABLE** (no live node, no live-network observation). Simulated
results are never presented as source-derived facts.

Source: postfiatd commit `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10). Excerpt ids refer to `fixtures/source-excerpts/`.

| ID | Status | Claim | Evidence |
| --- | --- | --- | --- |
| C-01 | VERIFIED | A flag ledger occurs every 256 ledgers (sequence % 256 == 0). | R-01; E27 (`Ledger.cpp:970-985`); `Ledger.h:426` |
| C-02 | VERIFIED | Amendment voting happens only at flag ledgers and only when the validated-ledger quorum is met; otherwise the whole round is skipped. | R-02, R-03; E28, E29 (`RCLConsensus.cpp:364-376`); E13 (`LedgerMaster.cpp:309-330`); S-13 |
| C-03 | VERIFIED | Pre-fix majority threshold is floor(204/256 * N), and a vote count >= the threshold passes. 27 of 35 passes (79.6875%). | R-04; E01 (`SystemParameters.h:83`); E09 (`AmendmentTable.cpp:359-378`); S-01 |
| C-04 | VERIFIED | Post-fix majority threshold is floor(67/100 * N), and a vote count strictly greater than the threshold passes. 23 of 35 fails; 24 passes. | R-05; E01 (`SystemParameters.h:85`); E09; S-02 |
| C-05 | VERIFIED | A majority must be held for two weeks (1,209,600 s) before activation is proposed; the default majority time is two weeks. | R-28, R-29; E01 (`SystemParameters.h:88`); E39 (`Config.h:248`); S-04 |
| C-06 | VERIFIED | Only votes from validators in the local trusted set count; trusted votes expire 24 hours after their close time. | R-10, R-12; E03, E04 (`AmendmentTable.cpp:24-55, 139-188`); S-10 |
| C-07 | VERIFIED | A node's own vote is announced in its validation (`sfAmendments`) and only on voting ledgers (flag ledgers). | R-11, R-15; E29 (`RCLConsensus.cpp:898-915`); E31 (`Change.cpp:352-372`) |
| C-08 | VERIFIED | In doValidation, only amendments that are supported, not enabled, and locally voted up are announced as up; everything else is announced as down. | R-16; E18 (`AmendmentTable.cpp:813-839`) |
| C-09 | VERIFIED | A veto is a local vote change only: `veto()` changes up to down and `unVeto()` changes down to up; the veto itself is never announced to the network. | R-18, R-19; E15 (`AmendmentTable.cpp:736-760`); S-12 |
| C-10 | VERIFIED | Losing a majority clears the majority record and the two-week clock; a later majority starts a new hold. | R-22; E20 (`AmendmentTable.cpp:847-935`); S-04, S-05 |
| C-11 | VERIFIED | Enablement is a no-flag pseudo-transaction that enables the amendment once it passes; there is no path to un-enable an enabled amendment. | R-36, R-40; E31 (`Change.cpp:352-372`); E21 (`AmendmentTable.cpp:762-800`) |
| C-12 | VERIFIED | Enabling an amendment the node does not support sets the amendment-blocked state; in CONNECTED mode the server blocks. | R-41, R-42; E32 (`Change.cpp:286-380`); E41 (`NetworkOPs.cpp:1840-1844`); E40 (`LedgerMaster.cpp:309-330`) |
| C-13 | VERIFIED | An EnableAmendment transaction carrying both tfGotMajority and tfLostMajority is invalid (temINVALID_FLAG); duplicate or already-decided amendments are rejected (tefALREADY). | R-37, R-38, R-39; E32 (`Change.cpp:286-380`) |
| C-14 | VERIFIED | When a majority is recorded, its timestamp is the parent ledger's close time; majorities are read back from `sfMajorities` in ledger entries. | R-30; E32 (`Change.cpp:344-350`); E33 (`View.cpp:1016-1036`) |
| C-15 | VERIFIED | With a single trusted validator, one vote passes even post-fix (the >= exception for N == 1). | R-17; E09 (`AmendmentTable.cpp:359-378`); S-08 |
| C-16 | VERIFIED | `AmendmentMajorityCalc` is itself an amendment (DefaultYes); whether the 67% or the 204/256 regime applies depends on whether it is enabled in the ledger rules. | R-08; E37 (`features.macro:104`); E43 (`Feature.cpp:253-257`) |
| C-17 | SPECIFIED | Docs: an amendment needs ">80% of validators for two weeks" before activation. Quoted in `docs/citations.md`. | R-07; xrpl.org amendments page (fetched 2026-11-24) |
| C-18 | SPECIFIED | Docs: if support drops to 80% or less after a majority is recorded, "an EnableAmendment pseudo-transactions is added" and the amendment is ultimately enabled. Quoted verbatim in `docs/citations.md`. | R-45; xrpl.org amendments page (fetched 2026-11-24) |
| C-19 | MODELLED | S-04: one round below threshold after a majority restarts the two-week clock, delaying enablement by 961 rounds (864,900 s). | `outputs/derived/amendment-results.json` S-04; R-22 |
| C-20 | MODELLED | S-11: support lost at the deadline round emits LostMajority only — the amendment is NOT enabled in the model, contradicting the docs' "ultimately enabled". | `outputs/derived/amendment-results.json` S-11; R-45; DVG-3 |
| C-21 | MODELLED | Minority-coalition sizes: 12 of 35 blocks post-fix (S-03); 3 of 5 passes pre-fix but fails post-fix (S-09); churn 35→29 kills a majority (S-07), 35→30 survives it (S-06). | `outputs/derived/amendment-results.json` S-03, S-06, S-07, S-09; blocking_table |
| C-22 | MODELLED | S-12: a local veto does not block network enablement — if the other 24 of 25 validators keep voting up, the amendment enables. | `outputs/derived/amendment-results.json` S-12; R-18, R-23 |
| C-23 | UNTESTABLE | The wall-clock duration of a two-week hold on the live postfiat network (depends on the network's actual close cadence; no live node observed). | R-35; `docs/gap-register.md` G-03 |
| C-24 | UNTESTABLE | Which pseudo-transaction wins when nodes propose conflicting amendment actions (GotMajority vs LostMajority vs Enable) in the same consensus round. | R-33; `docs/gap-register.md` G-04 |

## Counts

- Total: 24 claims — VERIFIED 16, SPECIFIED 2, MODELLED 4, UNTESTABLE 2.
- Rule coverage: every VERIFIED claim cites at least one VERIFIED rule;
  every SPECIFIED claim cites a documented rule with a verbatim quote;
  every MODELLED claim cites a scenario run and its inputs in
  `configs/scenarios.json`.
