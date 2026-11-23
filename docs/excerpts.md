# Source Excerpts

Verbatim excerpts from postfiatd commit `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10). Each excerpt file is the exact cited range; digests are in `fixtures/source-hashes.json` and re-verified by `scripts/probe.py` (H-01).

| ID | File | Lines | Anchor |
| --- | --- | --- | --- |
| E01 | `include/xrpl/protocol/SystemParameters.h` | 79-88 | `preFixAmendmentMajorityCalcThreshold` |
| E02 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 92-120 | `class TrustedVotes` |
| E03 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 120-152 | `trustChanged` |
| E04 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 153-180 | `recordVotes` |
| E05 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 186-220 | `sfAmendments` |
| E06 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 232-266 | `Timeout: Clearing votes` |
| E07 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 267-286 | `getVotes` |
| E08 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 289-311 | `one-way switch` |
| E09 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 313-342 | `computeThreshold` |
| E10 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 359-378 | `it->second > threshold_` |
| E11 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 380-401 | `trustedValidations` |
| E12 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 600-630 | `veto_amendments` |
| E13 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 633-660 | `Invalid FeatureVotes row` |
| E14 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 660-686 | `never be changed` |
| E15 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 736-760 | `AmendmentTableImpl::veto` |
| E16 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 762-812 | `AmendmentTableImpl::enable` |
| E17 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 813-839 | `Voting for amendment` |
| E18 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 840-846 | `getDesired` |
| E19 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 847-880 | `Counted votes from` |
| E20 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 881-935 | `tfGotMajority` |
| E21 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 943-990 | `needValidatedLedger` |
| E22 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 997-1033 | `injectJson` |
| E23 | `src/xrpld/app/misc/AmendmentTable.h` | 40-70 | `veto` |
| E24 | `src/xrpld/app/misc/AmendmentTable.h` | 100-145 | `doValidatedLedger` |
| E25 | `src/xrpld/app/misc/AmendmentTable.h` | 146-185 | `ttAMENDMENT` |
| E26 | `src/xrpld/app/ledger/Ledger.h` | 420-432 | `FLAG_LEDGER_INTERVAL` |
| E27 | `src/xrpld/app/ledger/Ledger.cpp` | 968-986 | `isFlagLedger` |
| E28 | `src/xrpld/app/consensus/RCLConsensus.cpp` | 355-390 | `isFlagLedger` |
| E29 | `src/xrpld/app/consensus/RCLConsensus.cpp` | 895-920 | `isVotingLedger` |
| E30 | `src/xrpld/app/tx/detail/Change.cpp` | 286-312 | `applyAmendment` |
| E31 | `src/xrpld/app/tx/detail/Change.cpp` | 313-345 | `tefALREADY` |
| E32 | `src/xrpld/app/tx/detail/Change.cpp` | 346-380 | `No flags, enable amendment` |
| E33 | `src/libxrpl/ledger/View.cpp` | 1000-1040 | `getMajorityAmendments` |
| E34 | `src/xrpld/app/misc/detail/ValidatorList.cpp` | 1845-1875 | `calculateQuorum` |
| E35 | `src/xrpld/app/misc/detail/ValidatorList.cpp` | 1895-1935 | `67% quorum` |
| E36 | `src/xrpld/app/misc/ValidatorList.h` | 490-510 | `quorum()` |
| E37 | `include/xrpl/protocol/detail/features.macro` | 100-108 | `AmendmentMajorityCalc` |
| E38 | `include/xrpl/protocol/TxFlags.h` | 125-132 | `tfGotMajority` |
| E39 | `src/xrpld/core/Config.h` | 245-250 | `AMENDMENT_MAJORITY_TIME` |
| E40 | `src/xrpld/app/ledger/detail/LedgerMaster.cpp` | 305-345 | `hasUnsupportedEnabled` |
| E41 | `src/xrpld/app/misc/NetworkOPs.cpp` | 1835-1850 | `setAmendmentBlocked` |
| E42 | `src/libxrpl/protocol/Feature.cpp` | 76-82 | `DefaultYes` |
| E43 | `src/libxrpl/protocol/Feature.cpp` | 250-290 | `Must be supported to be up-voted` |
| E44 | `src/xrpld/app/misc/detail/AmendmentTable.cpp` | 536-560 | `majorityTime_` |

Total: 44 excerpts across 16 source files.
