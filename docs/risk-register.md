# Risk Register

Severity: HIGH (activation outcome can diverge from operator expectation),
MEDIUM (delay or loss of majority), LOW (edge-case or operator-config
consequence). Every risk cites a rule or finding; risks are ranked by
severity, then by id.

| ID | Severity | Risk | Evidence |
| --- | --- | --- | --- |
| K-01 | HIGH | Activation at 68–80% support: the post-fix 67% threshold activates an amendment while the public docs promise >80%, so operators watching the docs are surprised by an early activation. | F-01; R-05; DVG-1 |
| K-02 | HIGH | Lose-at-deadline ambiguity: docs say the amendment is "ultimately enabled"; code emits LostMajority only when support is lost at the deadline, so the amendment is silently cancelled instead. | F-03; R-45; DVG-3 |
| K-03 | HIGH | Validator quorum 67% (fork) lowers the voting gate: fewer validators need to be online for a voting round to run, so a minority of validators can drive amendment voting. | F-02; R-03; DVG-2 |
| K-04 | MEDIUM | Minority delay: 34% no-voters block a post-fix majority, and a one-round dip below threshold restarts the full two-week clock (S-04: +961 rounds). | F-05; R-22; S-04 |
| K-05 | MEDIUM | Churn kills majority: validator departures mid-hold can drop support below the threshold and reset the clock (S-07: 35→29 kills it). | F-06; R-25; S-07 |
| K-06 | MEDIUM | 24h vote cache: a dead validator's yes vote is counted for up to 24 hours, inflating apparent support after a validator stops voting. | F-07; R-12; S-10 |
| K-07 | MEDIUM | Small-UNL regime flip: at N=5, 3 votes pass pre-fix (60%) but fail post-fix, so the same vote shares change outcome when `AmendmentMajorityCalc` activates. | F-09; R-04, R-05; S-09 |
| K-08 | MEDIUM | Single-validator network: one vote activates any amendment on its own, so a lone-validator testnet activates amendments without any quorum debate. | F-10; R-17; S-08 |
| K-09 | MEDIUM | Unsupported-amendment enablement blocks the server: a node that lacks the amendment code stops when the network enables it. | F-12; R-41, R-42; S-12 |
| K-10 | MEDIUM | Veto is local-only: an operator who vetoes cannot stop network enablement; the veto only removes their own vote from the count. | F-08; R-18, R-23; S-12 |
| K-11 | MEDIUM | Regime switch: enabling `AmendmentMajorityCalc` itself changes every threshold mid-network (204/256 >= → 67/100 >), so pending majorities can flip outcome overnight. | F-01; R-08; S-09 |
| K-12 | LOW | Config conflict: `[amendments]` and `[veto_amendments]` listing the same amendment silently drops the veto (config error). | R-44; E39 |
| K-13 | LOW | Quorum disabled: when publishers are unavailable, amendment voting stalls entirely — no votes are counted at all. | F-11; R-03; S-13 |
| K-14 | LOW | Obsolete/unknown amendments are frozen as vetoed; there is no path to un-veto them without a code change. | R-24; E20 |

## Counts

- Total: 14 risks — HIGH 3, MEDIUM 8, LOW 3.
