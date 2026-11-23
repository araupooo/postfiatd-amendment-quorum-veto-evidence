# Gap Register

Gaps are unknowns that the pinned source alone cannot answer. Each gap
names what is missing and what would close it. No live node was run and
no live-network data was observed.

| ID | Gap | What would close it |
| --- | --- | --- |
| G-01 | Live validator count and UNL composition on the postfiat network. | A live `server_info` / validator-list observation. |
| G-02 | Whether `AmendmentMajorityCalc` is enabled in the live postfiatd network rules (determines whether 67% or 204/256 applies live). | A live ledger-rules / feature-table read. |
| G-03 | Real flag-ledger spacing and close cadence on the live network (the two-week hold is 1,344 flag ledgers only if closes average 15 min). | Live ledger close-time series. |
| G-04 | Which pseudo-transaction wins when nodes propose conflicting amendment actions (GotMajority vs LostMajority vs Enable) in the same consensus round. | A live-network or testnet observation of a disputed amendment at its deadline. |
| G-05 | Real vote shares for any live amendment. | Live validation sampling over two weeks. |
| G-06 | Whether any amendment is currently inside its two-week hold on the live network. | A live `sfMajorities` read. |
| G-07 | Operator veto configuration on the live network (private node config). | Operator disclosure. |
| G-08 | Time for a vetoed amendment to be un-vetoed and re-gain majority (depends on operator action, not code). | Operator action log. |

## Counts

- Total: 8 gaps.
