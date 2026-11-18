# AegisTrade AI — Signal-specific research and adverse-news exits

Version 0.22.1 • 12 November 2026

## The requested change

Historical C2 continues to complete research before a simulated entry. Its evidence policy now differs by strategy. Strong trend and RSI-reversion signals are not rejected solely because financial or independent-news evidence is missing. Breakouts require readable dated corroboration. A supported adverse finding prevents entry and requires EXIT for an existing holding after independent critic validation.

These are experimental rules chosen for this project. They do not establish that the next run will be profitable. Permitting incomplete coverage adds research risk; selling on small adverse events can increase turnover, fees and slippage. Evaluate the actual outcomes rather than treating fewer blocks as proof of improvement.

[[FIGURE:signal_policy]]

## Entry rules

| Strategy | Technical requirement for the coverage-gap path | Research requirement |
|---|---|---|
| EMA trend | Existing code-qualified entry; ADX14 at least 22 and Close above EMA20 above EMA50 | Read dated company evidence and attempt bounded web retrieval if needed. Incomplete coverage alone may permit LIMITED / COVERAGE_LIMITED, with observed check citations and explicit limitations. |
| RSI reversion | Existing code-qualified entry; RSI14 below 42 and Close above 0.88 × EMA50 | The same coverage-gap permission applies. A low RSI alone does not bypass screening, sizing or risk checks. |
| Breakout | Existing breakout signal: Close above prior 20-session high and ADX14 at least 18 | Requires a verbatim structured source quote, available within 30 days before the cutoff, supporting reported improvement or a completed commercial event with a reported benefit metric. Market and critic must separately corroborate the same source. Prose alone, sole forecasts and COVERAGE_LIMITED cannot justify entry. |

The existing liquidity, history, volatility, raw-price discontinuity, ranking, capital, position and daily-loss constraints remain. Eligible candidates still pass market, strategy, independent critic and deterministic checks. Friday/pre-gap refresh and later-open fill rules remain in force. A holding's code stops, trailing stops, take-profit and strategy exits remain active.

## Understand the assessment labels

**NO_MATERIAL_ADVERSE_FOUND** means no material adverse finding within a supported bounded scan. It is not exhaustive news coverage or a statement of safety.

**COVERAGE_LIMITED** means the required research check was observed, but coverage is incomplete and no concrete adverse event has been identified as unresolved. For a qualified trend/reversion case, code permits following the technical signal with that residual evidence risk. The company status must be LIMITED, limitations must be disclosed, and event_risks must be empty. This label cannot support a breakout, conceal a known event, or claim clean fundamentals. A recorded failed search is evidence of an attempted check, not evidence that the company is safe.

**UNKNOWN** means a concrete potentially adverse exposure lacks essential context. It continues to block entry. Missing source context on a known fraud investigation, default or operating restriction is not a coverage-only exception.

**ADVERSE_EVENT_FOUND** records an actual supported adverse event, including a small disclosed penalty under the selected exit policy. **MATERIAL_ADVERSE** records material severity. Both need readable source citations and nonempty event details. Both block entries. In a holding review, both require an EXIT rather than HOLD; an incorrect HOLD is rejected for correction within the existing research budget. The independent critic must still accept the factual finding and action.

Routine administrative information is not automatically adverse. In particular, a trading-window closure for insiders is not an operating closure or proof of insider wrongdoing. A routine title that also states an actual investigation or other adverse event remains eligible for review. Disclosure classification does not authorize a transaction by itself.

## Evidence-processing corrections

The previous amount matcher could match the end of “Towers,” in an exchange address. The new matcher requires a separate currency marker followed by an actual digit. Addresses and scrip codes are not monetary exposures.

The extractive view now starts at the substantive subject/body where available and keeps disclosure_context alongside materiality windows. This prevents an address-only numeric window from displacing the announcement body. Amount, impact, event and resolution windows remain verbatim; missing impact stays unknown rather than becoming Nil. Complete source text, metadata, hashes and prior snapshots remain stored.

Routine trading-window closure notices are excluded from the adverse-candidate scan unless the title also identifies an actual adverse event. Recent Regulation 30/board-outcome disclosures can still be examined because their substantive contents may matter. Financial and other selected documents remain available independently of their adverse-candidate classification.

The evidence-view version is company-view-v5-substantive-body. The adverse-scan version is adverse-scan-v2-routine-notices. Preparing a dated pack under the new rules can rescan the archive and reuse validated cached PDFs. It does not delete old research results or rewrite old trading outcomes.

## Holding surveillance and exits

1. The normal stop, profit and strategy-exit code runs as before.
2. For NSE historical portfolios, each eligible close also checks bounded official issuer-announcement metadata since the previous checked cutoff. These are HTTP/source checks, not generation calls. Empty checks add no LLM usage.
3. An after-close release is not visible at that day's earlier close. The next eligible session's check includes releases after the previous cutoff. Future releases are excluded. Exact date checks are cached and recorded.
4. A new disclosure candidate triggers C2 holding research between scheduled reviews. A candidate is a request to investigate, not a sell signal. The specialist reads the dated company pack and optional web evidence, then the independent critic verifies the conclusion.
5. A supported ADVERSE_EVENT_FOUND or MATERIAL_ADVERSE holding assessment requires EXIT. A routine or benign disclosure can justify HOLD. A metadata/network failure is recorded as unavailable; it does not become a clean scan or an adverse event.
6. A validated EXIT queues a simulated sale at the next eligible open. Existing protective stop/profit gap rules take precedence where applicable. The exact research is revalidated before a C2 sale fills. Missing bars defer execution under the existing rules.
7. Holdings are not forcibly liquidated at the period end. The simulator avoids a paid last-day research review that cannot execute within the requested period. Remaining positions are marked to the last available close.

This watch covers bounded official issuer metadata. It is not a complete real-time news service, and independent press information may only reach the scheduled or triggered research path when a usable dated source is retrieved.

## Orchestration and usage

The supervisor coordinates market → strategy → independent critic → code validation. The market specialist classifies evidence and limitations. The strategy specialist follows the permitted route and action. The critic reads its own company/policy observations. Code checks the strong-signal exception, breakout requirements, source identity, dates, citations, adverse EXIT requirement and sizing/execution constraints.

A normal C2 assessment still uses approximately six generation calls, with a shared maximum of eight. An extra correction or reassessment can use seven or eight. The output-token ceiling and 36,000-character conversation guard remain. Lossless company-evidence references avoid resending duplicate source text. Daily empty metadata checks use zero generation calls. New disclosure candidates can increase the total number of research assessments across a run, so total inference usage may increase even though the per-assessment ceiling is unchanged.

Historical fills follow the user's upfront-approved rules. The separate supervised workflow retains per-order human approval and final checks. No live exchange orders are enabled.

## How to test in the UI

1. Refresh the dashboard after restarting the API and UI. The health endpoint should report 0.22.1, signal_specific_evidence_supported and adverse_news_exit_supported.
2. Confirm the intended active universe in Market. Your frozen 30-stock dataset is retained; the existing top-20 and Nifty 100 alternatives remain available.
3. Start a **new** C2 historical portfolio simulation. Use the same period, capital, costs, stops, profit target and lesson version as the previous run for a direct process comparison. The old run cannot be resumed under the changed prompt, policy-corpus and simulator fingerprints.
4. Review the new entry-policy explanation and choose the usual inference allowance and scheduled-review interval. Upfront rule and inference authorization remain required. The source monitor does not initiate a portfolio by itself.
5. In decisions/traces, inspect evidence_policy as well as action. A trend/reversion ENTER with COVERAGE_LIMITED should visibly disclose the missing coverage. A breakout ENTER must have readable cited corroboration and breakout_support. UNKNOWN event risk must not be hidden under COVERAGE_LIMITED.
6. Inspect the dated issuer-disclosure checks. CHECKED with no candidates requires no extra generation. A new candidate should lead to a holding review. If its adverse finding is accepted, verify EXIT and the later-open SELL_C2 ledger entry. Protective stops/profit exits may supply the actual sale reason if they trigger first.
7. Compare fees, realized/unrealized return, drawdown, exposure, blocked reasons, exits and model usage against the unchanged technical reference. Fewer blocks do not necessarily mean better returns. Use a separate untouched period for evaluation after development decisions are frozen.

## Viva questions

**Why allow missing evidence for trend and RSI?** This experimental policy treats them as technical strategies. It still researches downside, but missing fundamental coverage alone does not veto a qualifying signal. The residual uncertainty is explicit rather than presented as positive evidence.

**Why is breakout different?** The selected project rule requires additional dated corroboration for breakout entries. A technical break above a prior high alone is insufficient under this policy. This is a hypothesis to evaluate, not a proven universally optimal distinction.

**What prevents COVERAGE_LIMITED from bypassing genuine risk?** Code requires the appropriate qualified strategy, a hashed observed research check, LIMITED status, citations and no unresolved event listed. The independent critic reads the same dated source pack. A concrete uncertain adverse event remains UNKNOWN and blocks entry; semantic interpretation is still an LLM limitation.

**Does an empty news search prove no adverse news exists?** No. It records limited coverage or a failed search. It cannot prove safety, exhaustive coverage or historical profitability.

**Why sell on a small adverse event?** It is the user's chosen experimental exit rule. A factual cited adverse event requires EXIT even if financially small. The cost is possible churn and unnecessary exits, which must be measured in evaluation.

**Why not sell immediately at the same close?** The research uses completed-close evidence. A later eligible open avoids assuming execution before the information and decision existed. Protective intraday exits remain separate code rules.

**Does every daily check call the model?** No. Empty issuer-metadata checks use no generation. New candidates can trigger research before the next scheduled holding review, with the same bounded C2 call ceiling.

**What was verified?** Synthetic-price and mocked-generation tests cover qualified coverage-only entries, breakout support requirements, source identity/critic gates, adverse EXIT correction, announcement extraction, routine notices, after-close news timing, causal later-open exits and zero extra generation on empty checks. Cached NTPC source extraction was inspected locally without fetching or generating new company conclusions. No profitability improvement or full live-model portfolio success is claimed.

## Breakout correction and raw-price comparability — v0.22.1

The stronger breakout_evidence contract requires document_id, kind, an exact visible source quote and relevance in both the market assessment and an accepting independent critic. Code checks source recency, grounding and reported improvement/completed-event criteria. An auditor review, ordinary filing, provider selection or prospective target alone is insufficient. For example, a possible production increase over a multi-year plan is not already achieved output. Valid corroboration remains compatible with a later trading loss.

A known recent explicit structural-action disclosure quarantines new entries across all routes on the unadjusted simulator. This data-quality rule is separate from missing fundamental coverage and from adverse news. It neither forces a holding sale nor reconstructs distributed-share entitlements. See AegisTrade_Breakout_Entry_Audit_20261112.docx for the supplied ITC/ONGC ledger audit, source references and limitations. Existing technical entry/exit thresholds, stops, costs and position sizing are unchanged. Start a new run after updating.


## Version 0.23.0 update: breakout recovery and pullback

EMA_PULLBACK is now available for confirmed trend pullbacks. BREAKOUT retains its strict evidence/critic gate, including the new BREAKOUT_BOUNCE stop-recovery entry. Breakout has separate 0.5% risk, 2.5 ATR initial/trailing stops and 1R trailing activation defaults. A stop closes the position first; at most one re-entry follows a later confirmed close within ten sessions, fresh C2 and a later-open fill. See AegisTrade_Breakout_Reentry_and_Pullback_Guide for exact rules and UI steps. Existing saved runs are retained; start a new run for this version.
