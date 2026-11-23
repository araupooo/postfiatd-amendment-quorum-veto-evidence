# Citations

External documentation cited by the SPECIFIED rules. These are the docs'
claims, quoted verbatim — they are not code facts. Where the code
disagrees, the divergence is recorded in the rule's `divergence`
field and in `docs/methodology.md`.

Source page: <https://xrpl.org/docs/concepts/networks-and-servers/amendments>
(fetched 2026-11-24).

## R-07 — Docs: more than 80% support for two weeks

> "If an amendment receives more than 80% support for two weeks, the
> amendment passes and the change applies permanently to all subsequent
> ledger versions."

Code says otherwise: the post-fix threshold is 67/100 with strict `>`
(`include/xrpl/protocol/SystemParameters.h:85`), the pre-fix threshold
is 204/256 with `>=` (`:83`). Divergence DVG-1.

## R-27 — Docs: amendments with removed source are vetoed by the network

> "Amendments that have had their source code removed without being
> enabled are considered Vetoed by the network."

Code: obsolete and unknown amendments are vetoed locally
(`AmendmentTable.cpp:847-935`, doVoting). No network-level "vetoed"
state exists in the code; the veto is a per-node vote of down.

## R-33 — Docs: flag ledgers about 15 minutes apart; enabled amendments apply from flag + 2

> "The process to enable it happens within the XRP Ledger network,
> which checks the status of amendments every flag ledger (typically
> about 15 minutes apart)."

Code: flag ledgers occur every 256 ledgers
(`src/xrpld/app/ledger/Ledger.cpp:970-985`, `Ledger.h:426`). The
"about 15 minutes" figure is a wall-clock approximation that depends
on the network's actual close cadence; the ledger-count rule is exact.
The "apply from flag + 2" half of this rule is a documented rule with
no single code line to cite — see R-33 in `configs/amendment-rules.json`.

## R-45 — Docs: amendment ultimately enabled when support is lost at the deadline

> "It's possible for an amendment to lose 80% support on the same
> ledger it reaches the required two-week period to be enabled. In
> these cases, an EnableAmendment pseudo-transactions is added for both
> scenarios, but the amendment is ultimately enabled."

Code says otherwise: in `doVoting` (`AmendmentTable.cpp:847-935`),
LostMajority is checked before Enable, and a node emits one action
per amendment per round — a node seeing the drop emits LostMajority
only. Divergence DVG-3; modelled in S-11.

## Other sources

- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA) are
  cited only in the post-quantum RPC/API readiness pack, not here.
- All other claims in this pack cite the pinned postfiatd source
  directly; see `docs/excerpts.md` for the verbatim ranges.
