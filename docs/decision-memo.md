# Operator Decision Memo: Contested Amendments

## The question

An amendment is contested: some validators vote up, some vote down,
support hovers near the threshold, or a minority coalition is
deliberately delaying it. What should an operator do, and what can the
operator actually change?

## What the code says (verified)

1. **The threshold is 67%, not 80%.** Post-fix, an amendment activates
   when strictly more than 67% of trusted validations vote up, held for
   two weeks. The docs' ">80% for two weeks" is pre-fix language.
   (F-01, R-05)
2. **Your veto is local.** `veto()` changes your own vote from up to
   down. It does not announce anything, and it does not block the
   network: if the other validators still hold a majority, the
   amendment enables without you (S-12). (F-08, R-18, R-23)
3. **A one-round dip restarts the clock.** If support drops below the
   threshold for even one flag ledger after a majority was recorded,
   the majority record is cleared and the two-week hold starts over
   (S-04: +961 rounds). (F-05, R-22)
4. **Churn can kill a majority.** Validators leaving the UNL mid-hold
   change both the threshold and the vote count; 35→29 kills a
   25-vote majority, 35→30 survives it (S-06, S-07). (F-06)
5. **Dead validators' votes linger 24 hours.** Trusted votes expire
   24 hours after their close time, so a silent validator's yes vote
   still counts for up to a day (S-10). (F-07)
6. **Enabling an amendment you do not support blocks your server.**
   If the network enables an amendment your build lacks, your server
   sets amendment-blocked and stops in CONNECTED mode. Upgrade before
   the hold expires. (F-12, R-41, R-42)
7. **Voting can stall entirely.** If publishers are unavailable, the
   validator quorum is disabled and no amendment voting happens at all
   (S-13). (F-11, R-03)

## Parameter sensitivity

- **Threshold regime matters most at small UNL sizes.** At N=5, 3
  votes pass pre-fix (60%) but fail post-fix; at N=35, the post-fix
  minimum passing vote is 24 vs 27 pre-fix. The blocking minority
  grows from 9 to 12 at N=35 when the fix activates.
- **The two-week hold is 1,344 flag ledgers at the modelled 900 s
  spacing.** If the network's real close cadence is slower, the
  wall-clock hold is longer; the ledger-count hold is exact.
- **The majority time is configurable** (`AMENDMENT_MAJORITY_TIME`,
  default 2 weeks). A network operator can shorten it, but that
  changes every pending majority at once.
- **The regime switch itself is the largest single parameter change:**
  enabling `AmendmentMajorityCalc` moves every threshold from
  204/256 (>=) to 67/100 (>). Pending majorities recorded under the
  old regime keep their recorded timestamps; their outcome under the
  new threshold is decided at the next flag ledger.

## Recommendations

1. **Watch the threshold you actually run, not the docs.** Read the
   enabled-features table on your own node; if
   `AmendmentMajorityCalc` is enabled, 68% support activates.
2. **Do not rely on a veto to stop an amendment.** A veto only
   removes your vote. To delay activation you need a coalition of at
   least 12 of 35 (post-fix) voting down, sustained for two weeks.
3. **Upgrade before a contested amendment's hold expires.** If the
   amendment enables and your build lacks it, your server blocks.
4. **Treat the deadline round as a cliff.** Support lost at the
   deadline round cancels the majority (docs say otherwise — the
   code wins). If you support the amendment, keep your validator
   voting up through the final flag ledger.
5. **Monitor validator churn during a hold.** A departure that drops
   support below threshold restarts the two-week clock from zero.

## What this memo does not claim

- No live-network data: whether `AmendmentMajorityCalc` is enabled
  live, what the live UNL is, and whether any amendment is currently
  in hold are all gaps (G-01–G-08).
- The disputed-amendment deadline outcome (S-11) is a single-node
  model; which pseudo-transaction wins in a multi-node consensus
  round is untestable from source alone.
