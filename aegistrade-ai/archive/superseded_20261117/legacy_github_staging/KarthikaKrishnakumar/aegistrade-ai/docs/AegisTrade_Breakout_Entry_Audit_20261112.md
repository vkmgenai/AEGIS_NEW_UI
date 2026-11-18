# AegisTrade — Breakout entry audit and corrected evidence gate

Version 0.22.1 • 12 November 2026

## Findings from the supplied ledger

The ledger contains two completed breakout trades. Both had readable dated sources and accepted critics under v0.22.0. They were not evidence-free. The weakness was that any cited readable company document plus a nonempty breakout_support explanation could satisfy the corroboration check; a short-term breakout did not require a structured source quote demonstrating the claimed reported improvement or completed commercial event.

| Stock | Signal / fill | Recorded exit | Recorded realized P&L | Audit finding |
|---|---|---|---|---|
| ITC | 2 / 3 January 2025 | Trailing stop, 6 January | −₹5,554.59 | The hotels demerger was accepted as a catalyst on an unadjusted-price replay that does not account for the distributed shares. This is also a price-comparability/accounting problem. |
| ONGC | 8 / 9 January 2025 | Stop, 13 January | −₹4,111.71 | The selected technical-services provider supplied dated context, but selection and prospective recovery benefits do not establish achieved operating improvement. The old approval lacked structured quoted corroboration. |

The exported results are preserved. Loss after entry does not itself establish that an entry decision was invalid; equally, a readable filing and a successful schema check do not establish strong corroboration or predictive edge.

## ITC: distinguish a raw price move from complete economic P&L

NSE circular NSE/CMTR/65845, dated 27 December 2024, scheduled ITC's special pre-open price-discovery session for 6 January 2025. ITC's 30 December presentation identifies 6 January as the record date and a distribution of one ITC Hotels share for every ten ITC shares. These were published before the 2 January signal.

The simulator's raw ITC-share ledger does not credit that entitlement or reconstruct a full adjusted wealth series. Its recorded stop-loss P&L therefore cannot by itself represent the complete shareholder economic result across the demerger. The correction does not erase the loss, invent an entitlement valuation, retroactively change prices or classify a demerger as adverse news.

Primary sources:

- [NSE special-session circular](https://nsearchives.nseindia.com/content/circulars/CMTR65845.pdf)
- [ITC's 30 December 2024 presentation](https://nsearchives.nseindia.com/corporate/ITC_30122024153104_SELetter.pdf)
- The research also read ITC's 31 December issuer disclosure: https://nsearchives.nseindia.com/corporate/ITC_31122024181701_SELetter.pdf

## ONGC: dated context versus realized support

The 8 January disclosure names the selected Mumbai High technical-services provider and discusses prospective production improvement over a multi-year period. This can be relevant business information, but it is not proof that those gains had already occurred or that the next few sessions would rise. The old handoffs explicitly acknowledged that production gains were not established.

Source inspected in the cached research pack: https://nsearchives.nseindia.com/corporate/ONGC_08012025074955_Stockexchange08012025SD.pdf

Under the new gate, the original record fails because it has no structured source-linked quotation. A selection-only passage or a sole forecast cannot be promoted to reported improvement merely by choosing an optimistic evidence label. A different qualifying source, if actually available by the historical cutoff, would need to be retrieved, quoted and independently checked; it cannot be assumed to exist.

## Corrected breakout evidence contract

The technical breakout remains close above the prior 20-session high with ADX14 at least 18. The correction changes research approval, not that signal.

For an entry, the market specialist supplies breakout_support and breakout_evidence with:

- **document_id:** an exact observed readable company-source ID, included in company citations.
- **kind:** EARNINGS_IMPROVEMENT, OPERATING_IMPROVEMENT or COMPLETED_COMMERCIAL_EVENT.
- **quote:** a 40–600 character exact contiguous passage visible in the model's observed source excerpt or source window.
- **relevance:** a concise explanation connecting the cited fact to corroboration, without claiming a price guarantee.

Code checks source availability within the preceding 30 calendar days and before the signal cutoff, exact quote grounding, an explicit reported benefit metric and language consistent with the claimed reported improvement or completed commercial event. The 30-day window is a fixed conservative research setting, not an empirically established optimum. Stale sources, altered numbers, auditor boilerplate, vague goals, provider selection alone, sole forecasts and structural-action catalysts do not meet the contract.

The independent critic reads its own tool observations and supplies its own breakout_evidence for the same source. A bare accept=true is insufficient. The final completed-C2 gate and later-open fill revalidation enforce the contract again, even if a researcher incorrectly claims guard_pass=true. Failed code validation now produces a specific recorded reason rather than a generic completed-validation failure.

These are conservative eligibility and provenance checks. They do not fully automate semantic truth, establish material profitability, or prevent a genuine supported breakout from failing. The critic's interpretation remains a model limitation.

## Structural-action quarantine

A known, readable, non-financial disclosure explicitly titled as a demerger, split, bonus issue, rights issue or capital reduction, available within the preceding 30 days, quarantines **new entries** on this unadjusted simulator. The check uses full source metadata before display-title truncation. It applies to all entry routes as a data-quality check; it does not mark a corporate action as adverse news or force a holding sale by that label.

This is a bounded disclosure-based quarantine, not a complete corporate-action calendar. It does not repair existing holdings, dividends, entitlements or all historical indicators. A validated adjusted dataset and explicit entitlement accounting remain necessary for reliable financial conclusions across structural actions.

## Validation and reproduction

Controlled tests cover missing quotes despite readable filings, altered quote values, stale/future dates, forecasts, selection-only announcements, auditor context, a valid completed order, independent critic evidence, source disagreement, structural-action quarantine before title truncation, a false researcher pass blocked before BUY, and unchanged eligibility under later profit versus loss labels. No new model calls are needed to recheck the original records against the deterministic gate.

The original ITC approval fails the new UNADJUSTED_CORPORATE_ACTION check using its pre-signal disclosure. The original ONGC approval fails BREAKOUT_SOURCE_QUOTE_REQUIRED. This is a prospective policy comparison against stored observations, not a live-model rerun, proof that every losing trade should have been blocked or evidence of improved out-of-sample returns.

After updating the API and dashboard, confirm v0.22.1, refresh the UI and start a new run. Old runs retain their original outcomes and policy fingerprints. Inspect the market's structured quotation and load the full trace for the critic's independent quotation. Keep the same capital, period, costs, stops, profit target and lesson version for a process comparison; evaluate separately on an untouched period.
