# AegisTrade AI — Dated web evidence fallback

Version 0.21.1 • 12 November 2026

## What changed

C2 can research a code-qualified stock even when its local historical company evidence is incomplete. Before an evidence-based abstention, it can call the new MCP tool `search_dated_web`. The tool searches the public web for historically dated financial and adverse-event information, fetches selected source pages, validates them and enriches the dated company pack. The market specialist reassesses that evidence. The independent critic and code checks still decide whether the proposed action is permitted.

A strong technical signal earns additional research. It does not establish that a stock is safe or profitable. Missing financial statements need not automatically block a candidate when a LIMITED assessment has a validated bounded adverse-evidence scan, supported citations and disclosed gaps. Unresolved material downside risk or UNKNOWN risk still prevents entry or HOLD.

## Orchestration

[[FIGURE:dated_web]]

1. Code screens the selected universe using the historical bars and existing strategy rules. Ordinary risk, portfolio and data-quality constraints remain in force.
2. The existing historical archive preparation attempts to assemble company evidence for the simulated signal date. Policy RAG remains a separate source of project rules; it is not a company-news archive.
3. The C2 market specialist reads the technical snapshot and the dated company pack. A missing or inadequate pack no longer ends an otherwise eligible case before the new retrieval opportunity.
4. For a qualifying entry or an existing holding, missing evidence or an UNKNOWN assessment can trigger `search_dated_web`. The model may request the optional tool. The application also requests it before an evidence abstention if the model has not done so and the bounded turn budget allows reassessment. The trace identifies `model` or `controller_fallback` as initiator.
5. The tool issues two fixed queries: financial results and adverse/regulatory/default news. The query includes a 180-day lookback and historical upper bound. Search results only identify possible sources; they are not evidence.
6. Up to four selected trusted pages are fetched, with up to two accepted documents. A bounded scan is ready only when both queries complete, at least one accepted primary source exists, and required source checks leave no unresolved source gap. Known incomplete official risk disclosures cannot be silently cleared by a web result.
7. The market specialist receives the actual validated source text, dates, source IDs and scope. It reassesses the company as SUFFICIENT, LIMITED, REVIEW_REQUIRED or INSUFFICIENT_EVIDENCE, with adverse-risk classification and citations.
8. The strategy specialist checks the permitted route. The independent critic reads the enriched company pack and policy evidence. Code validates typed outputs, evidence identity, citations, risk and the final action.
9. For supervised proposals, sizing precedes human review and final submission checks. For historical C2 portfolios, the existing upfront-approved replay rules govern later-session simulated fills. Existing stops, trailing stops, take-profit and holding reviews remain in force. No live exchange order is placed.

## When the fallback is eligible

The existing code must already have produced a candidate. Additional retrieval eligibility requires positive ATR and the existing strong-signal conditions: TREND uses ADX at least 22 and Close above EMA20 above EMA50; RANGE uses RSI below 42 and Close above 88% of EMA50; BREAKOUT uses ADX at least 18. Existing holding reviews are eligible. These checks do not replace the strategy's own entry or order constraints.

A ready official pack normally avoids the extra search. An UNKNOWN market assessment can still cause a search before abstention. The tool does not run unrestricted research for arbitrary tickers supplied inside model text: the MCP server binds it to the current case.

## Dates, source validation and limitations

The historical cutoff is 15:30 Asia/Kolkata on the signal date. Accepted publication and availability must fall on or before that cutoff and inside the 180-day lookback. Datetime metadata must have a timezone. Date-only metadata gets a conservative 48-hour availability delay. A known modification after the historical cutoff rejects the HTML page.

Sources come from allowlisted exchange/regulator, issuer and established news domains. Issuer-specific primary domains are configured for the frozen 30-stock universe; wider-universe cases can use the shared exchange/regulator and secondary domains. Source text must match the company and be readable. Injected instructions are rejected. Primary financial documents must contain financial content. A PDF requires an already verified exchange publication timestamp for its exact URL; PDF creation dates, filenames and search snippets do not establish publication.

Search runs now against pages labelled with historical dates. This is not a certified archive of the precise page version available in the past. Missing or inaccurate publisher metadata and the LLM's pretrained knowledge remain limitations. Current or later material cannot be used merely because a search engine returned it. Free public search can be challenged, rate limited, or return unhelpful results; publishers may block automated access.

The live public-search smoke test completed both queries for a historical TCS case. It found no usable accepted evidence: an issuer page was inaccessible and a returned PDF lacked a verified publication timestamp. The case correctly remained insufficient. Controlled end-to-end tests separately establish that valid dated evidence can support a permitted entry; this does not establish successful live retrieval for every stock/date or a trading edge.

## Configuration, calls and audit

The default is `AEGIS_DATED_WEB_SEARCH=true`. Set it to `false` in `.env` to disable this fallback, then restart the services. No additional search API key or package is required. The provider is public DuckDuckGo HTML search. The tool itself makes HTTP requests and zero generation calls; the market reassessment uses the selected existing LLM backend. It does not switch OpenRouter/Codex providers.

Normal C2 uses six generation calls. Retrieval can fit into those six when missing evidence is detected during the first tool round. A further market reassessment after an UNKNOWN answer can use seven. The existing shared eight-call ceiling, three turns per specialist, 16-tool-call ceiling and output-token budget still apply. A budget or provider failure does not authorize bypassing evidence checks.

Each exact symbol/date has one saved web attempt, including failed attempts. Repeated tool reads use that saved result; refresh of the progress panel does not repeat paid research or web searches. The audit records queries, selected URLs, rejection reasons, accepted IDs, publication/availability/retrieval dates and content hashes. Fetched content is cached, and earlier company-pack snapshots are retained. `web_scan` stays separate from the official `adverse_scan` so a web search cannot falsely establish exchange archive completeness.

## UI demonstration

1. Let active jobs finish or pause them using the normal UI before restarting. From the project directory run `bash scripts/start_unix.sh`. Confirm the API health endpoint reports version 0.21.1 and `dated_web_search_supported: true`.
2. Open the Streamlit dashboard at `http://127.0.0.1:8501`. Keep the currently prepared universe or select another prepared dataset through the existing universe selector. Switching the universe does not create a complete news archive.
3. Start a **new C2 historical portfolio simulation** with your chosen historical dates, capital and existing stop/profit/risk assumptions. Explicitly authorize the displayed inference allowance and replay rules. Start with a short period and modest allowance to inspect behavior before a long run. This feature does not establish an optimal capital, date range or guaranteed profitable demonstration.
4. Watch the live progress panel or use Refresh. In **C2 entry / holding-review decisions and traces**, inspect the `web_search` column. Open a decision's research trace to inspect `search_dated_web`, its initiator and returned sources. `SUPPORTED_BOUNDED_SCAN` means the bounded source checks passed; `SEARCHED_BUT_INSUFFICIENT` means they did not. Neither status alone is a BUY decision.
5. In the company-evidence inspection panel, select the same symbol/date and inspect the cached pack. Compare official adverse-scan readiness, the separate web scan, source IDs, dates and links. Preparing an archive pack manually is distinct from a C2 model-tool round.
6. Explain the result: ENTER requires the strategy, market assessment, independent critic and code gates; BLOCK may remain correct if sources cannot be verified or risk remains unresolved. Provider errors pause the job under the existing handling. Retain source limitations in the demo discussion.

Previously saved results remain available. Research prompt and policy-corpus fingerprints changed, so old interrupted/paused jobs require a new run to use this flow; do not mix the old and new research configurations in one replay. The policy RAG index was rebuilt locally for the revised evidence policy, with no generation calls.

## Context-budget troubleshooting — v0.21.1

`CONTEXT_BUDGET_EXCEEDED` is the application's research-input guard. It is separate from the account quota, number of inference calls and output-token allowance. One recorded TATASTEEL case on 5 January 2026 accumulated 44,092 characters against the older 26,000-character limit because the company tool and web tool supplied the same 13-document projection twice. Other cases exceeded the limit on a later market turn or the independent critic's first complete evidence read.

The corrected flow sends each specialist a complete first company projection. Later identical observations use an explicit reference. Changed observations use exact JSON Pointer operations against an identified earlier projection when that is smaller than sending the new projection in full. Source IDs, financial text, changed amounts, unknown values, adverse risks and new documents remain recoverable exactly. The application reconstructs each update and verifies equality before sending it. Full tool observations remain in the audit. The critic receives its own complete first projection; it never depends on a market-only message.

The per-request conversation guard is now 36,000 characters to accommodate a complete independent critic read plus policies and handoffs. This is a character bound, not exact provider token accounting. Oversized requests still stop before the next inference call; the failure records actual size and limit. No material risk is removed to force a fit. The generation-call ceiling and output-token budget are unchanged. A larger input guard permits larger requests and can increase API input-token cost when used; eliminating duplicate evidence reduces unnecessary input.

Refresh the UI after the services restart and start a **new C2 portfolio simulation** using the same universe and parameters for comparison. Resuming an old run would not re-evaluate its already blocked historical candidates, and the changed prompt fingerprint deliberately prevents mixing configurations. Adding inference allowance or refreshing progress alone does not resolve an input-size failure. Old results and the selected frozen 30-stock dataset remain available; this fix does not certify the research conclusions or profitability of the blocked candidates.

## Viva questions and answers

**Why is this agentic?** The specialist can select a bounded evidence tool and reassess the returned observations. The supervisor also guarantees the retrieval opportunity before an eligible evidence abstention. Tool initiators are separately audited; controller-requested calls are not presented as autonomous model choices.

**Is web search the same as RAG?** No. Policy RAG retrieves existing indexed project rules; the company pack supplies dated company documents. Web search discovers additional sources. Validated fetched text becomes retrieved context for generation, with citations and scope.

**Why not buy whenever the technical signal is strong?** The signal supports a strategy candidate. It does not resolve a dated fraud, default, operating restriction or other material downside exposure. More research is appropriate; an unconditional buy is not.

**Does a negative news keyword block an order?** No. Materiality must be supported by source context, severity, impact and resolution. The market and critic assess it; missing essential impact on a serious unresolved event remains UNKNOWN.

**Can LIMITED evidence support an entry?** Yes, when the permitted bounded scan is ready, no material adverse event is found in that observed scope, citations support the assessment and missing coverage is disclosed. It is not an assertion that no adverse information exists anywhere.

**How is look-ahead controlled?** Source availability is compared to the simulated cutoff. Known later updates, future documents and unsupported dates are rejected. Live retrieval metadata cannot prove a historically unchanged page, so that residual limitation is disclosed.

**Why can the order still be blocked after search?** Search may fail, dated sources may be inaccessible or unverifiable, the scan may be incomplete, risk may remain UNKNOWN, the critic may reject, or code risk/strategy checks may fail.

**Does it improve profit?** It can reduce avoidable evidence-only abstentions. Profit improvement must be tested on untouched periods with identical capital, costs, exits and universe assumptions. Valid research and profitable prediction are separate measurements.

**What was verified?** Controlled tests cover source date/identity checks, future updates, missing metadata, injection rejection, unavailable search, cache reuse, optional model calls, controller fallback, critic source identity and a portfolio entry following valid enrichment. Public-network testing verifies query access and honest abstention when fetched sources are unusable; it does not establish live inference success.
