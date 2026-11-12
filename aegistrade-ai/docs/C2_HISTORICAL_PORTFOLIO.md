# End-to-end C2 historical portfolio — source 0.18.0

Implemented 9 November 2026. This is a chronological portfolio simulation with actual C2 research in the entry/holding decision path, not a renamed technical backtest. Historical trading uses upfront approval of rules; the separate Supervised Trading workspace retains exact per-order human approval. No workflow connects to a live broker.

## Daily lifecycle

1. Initialize cash, the frozen universe, risk/cost settings and historical warm-up indicators. Lock data fingerprint, prompt/model configuration and policy-corpus hash.
2. At each session open, process previously queued exits before entries. Every C2 entry and model-recommended exit is revalidated against its saved research before filling. Recalculate affordable whole shares at the actual open; gaps, fees, cash, capacity and daily loss can block an entry.
3. Apply the previously active protective stop using daily OHLC. An opening gap below the stop fills at the open with adverse slippage, not an impossible guaranteed stop price. Protective exits do not wait for an LLM.
4. At the completed close, ratchet enabled trailing stops on all surviving holdings before any research pause: stop=max(previous stop, highest completed close since fill −2×entry-signal ATR14), using the selected multiplier. The increase takes effect next session; today's low is never retested against a new stop. Then check the held strategy's code exit: EMA trend exits when EMA20<EMA50; RSI reversion when RSI>58; breakout when Close<EMA20. Queue a valid code exit for the next eligible open. C2 cannot veto these upfront-approved risk/strategy rules.
5. For a holding not already exiting, run a C2 holding review every N market sessions (default 5). The existing three specialists inspect current technical evidence, current position context, policy and company evidence available by15:30 IST. Return a typed HOLD or EXIT. Accepted EXIT queues a sale at the next eligible open. HOLD never removes the protective stop. No extra fourth agent is added.
6. Rank new candidates under the actual portfolio's cash, holdings and capacity. For each selected prospect, prepare/check its dated company pack and run the complete market→strategy→critic C2 flow. Only validated ENTER with sufficient cited financial/company evidence can queue a new entry. The shortlist is not a fill.
7. Save research traces, decisions, orders, cash, holdings, last marks and the close checkpoint. Advance one session; never use later bars or later publications in a decision.
8. At the end date stop advancing time. **Do not liquidate remaining holdings.** Mark them at their last available close, disclose mark date/staleness and report unrealized P&L. An exit signalled only at the final close remains a pending intention, not a fill beyond the period. No paid final-day review/entry research is performed when it cannot result in a fill inside the window.

A new independent simulation starts with its specified initial cash; open holdings are reported rather than automatically rolled into another newly created run. Resume continues the same interrupted period/state. Extending the end date or changing data/settings requires a new run.

## Trailing-stop policy

New UI/API runs default to trailing_stop_enabled:true and trailing_atr_multiple:2.0 (validated0.5–10). Initial protection remains signal-close minus2ATR, fixed before entry. Entry-signal ATR stays constant for trailing distance; intraday highs and fill-day/future ATR are not used. Disabled trailing retains the initial fixed stop. Stop updates are saved in stop_updates; holdings expose initial_stop, stop, highest_close and entry_signal_atr. Raised-stop sales are SELL_TRAILING_STOP; unchanged initial stops are SELL_STOP. New runs also default to an8% net take-profit target; the final date never forces a sale.

The same trailing setting applies to the active technical reference. Passive buy-and-hold has no stops. Per-position close markers prevent duplicate stop updates on resume; missing bars do not advance them. Engine c2-portfolio-v2-trailing and POL-43 bind this policy to new runs. Older saved results retain their fixed stops and cannot resume across the changed engine/corpus. No additional LLM calls are introduced. See [Trailing-stop policy](TRAILING_STOP_POLICY.md) and the updated portfolio demo guide for examples and UI steps.

## Model decision and safety contracts

The research snapshot includes purpose ENTRY or HOLDING_REVIEW. Holding context includes current quantity, entry price/strategy, protective stop and holding-session count. The strategy hand-off adds portfolio_action ENTER/HOLD/EXIT. Its strategy field still reports the current code-permitted route; a held position can be reviewed when that current route is NONE. Models interpret evidence, not money arithmetic.

ENTRY and HOLD allow SUFFICIENT financial research or explicitly LIMITED financial coverage with a completed cited adverse-disclosure scan and NO_MATERIAL_ADVERSE_FOUND. Material/unknown risk prevents new entries or HOLD. A cited REVIEW_REQUIRED assessment can support a critic-accepted, risk-reducing EXIT of an existing holding, never ENTER/HOLD. Required company provenance, correct dated adverse scan, readable claim citations and critic checks still apply; numerical financial claims still require appropriate financial sources. Insufficient/missing evidence cannot authorize a model action. A blocked holding review leaves the holding under existing protective/code exits, records the gap and makes no new assumption that fundamentals are clean.

Every new C2 entry requires three typed specialist hand-offs, accepted critic, code agreement, observed project-policy and qualifying financial citations, and matching company/corpus provenance. Evidence changes before a queued fill block that fill. Saved past research remains in the run audit; changing source data or prompt/corpus configuration prevents resuming a mixed-version run. Stops and code exits operate under the rules approved before replay, independently of research availability.

## Budgets, background execution and restart

Normal C2 uses six generation requests per research case and seven tool invocations; the per-case ceiling remains eight model requests/16 tools. A candidate entry and a scheduled holding review are separate research cases. No model call is made merely to simulate a fill, calculate a stop, value holdings or reach the end date.

The UI's total request allowance defaults to48 and can be set up to2400 per authorization. Before each case, the run durably reserves eight requests. On completion it releases the unused reservation and records actual attempts, tokens and available provider cost. If less than eight remain before a needed case, status becomes PAUSED_BUDGET. Explicit resume consent can add allowance. This is a request ceiling, not a guaranteed dollar cap.

Jobs run outside the HTTP request in one local background worker. The UI refreshes status and can pause/resume or open a saved run ID. Checkpoints separate the OPEN and CLOSE phases, so resuming a paused close does not repeat that day's opening fills/stops. Completed research files are reused for the same decision; a restart does not silently rerun a successful paid case. Provider requests themselves cannot be resumed mid-call. A crash with no durable response leaves the full reservation charged as uncertain; it is not reported as zero cost or silently refunded.

Provider failures pause immediately as PAUSED_PROVIDER instead of consuming the entire allowance on repeated failures. The failed attempt remains in the trace; retry requires a consented resume. Missing company coverage records BLOCKED and continues other candidates, without paid generation for that missing-evidence case. Completed runs with such gaps are labelled COMPLETED_WITH_GAPS. Pause requests are honored at safe boundaries; an active provider/archive request may finish first.

Data is under data/c2_portfolio_runs/RUN_ID/: state.json and research/DECISION_ID.json. Atomic phase writes preserve the portfolio. Do not edit active state/decision files. Current code/model/prompt/corpus/data fingerprints must match on resume. The historical simulator is independent of the supervised mock-broker ledger; it does not create externally approved broker orders.

## Results and fair interpretation

The report includes C2 equity/cash curve, fills with linked entry/exit research IDs, ENTER/HOLD/EXIT/BLOCKED/provider-failure decisions, source/usage traces, open holdings, pending orders and separate realized/unrealized P&L. Accounting must satisfy:

Ending equity = cash + marked open holdings = initial capital + realized P&L + unrealized P&L.

Entry fees are included in cost basis and assigned once to realized or unrealized P&L. Exit fees/slippage are charged only when a sale actually fills. Unsold positions do not incur fictitious terminal exit costs. Model charges are reported separately in USD; INR trading-return metrics exclude them rather than silently assuming a foreign-exchange conversion. Missing provider cost is unknown, not zero.

A technical-only ROUTER reference and passive equal-weight benchmark use the same date window, capital and market costs. C2 differs through entry screening and holding-review exits; compare both returns and drawdown, turnover, gaps and research costs. While a C2 job is partial, full-period baseline metrics are withheld and reference curves stop at the visible C2 date. A completed-with-gaps return includes abstention due to missing data, not necessarily beneficial LLM reasoning. No profitability or superiority claim is established by implementation or mocked tests.

The current NSE cache still uses current constituents and unadjusted prices. Corporate actions, dividends, historical membership and source completeness remain financial-validity limitations. The model never receives reference-curve future returns or hidden expected outcomes.

## UI steps

1. Restart API/dashboard on 0.15.0. Open Strategy Backtests; choose **C2 historical portfolio** as Simulation engine.
2. Enter capital, historical start/end, risk, fees and slippage. C2 uses automatic ROUTER screening. Start with a short period; five years is supported but may need many consented budget extensions and historical source preparation.
3. Set Total OpenRouter request allowance (default 48) and Review each holding every N market sessions (default 5).
4. Enter the private reviewer token. Select paid-call consent and the historical rule-approval checkbox. This authorizes automatic simulated entries, protective/code exits and validated C2 EXIT actions under those rules, with no per-fill human pause.
5. Click Run historical portfolio simulation. The API returns a job/run ID while the background worker proceeds. Open **C2 portfolio progress, resume and saved jobs** and click Refresh C2 progress.
6. Inspect status, date/phase, call usage, decisions and research traces. PAUSED_BUDGET needs new allowance/consent; PAUSED_PROVIDER needs provider/configuration resolution followed by consented resume. Do not describe a paused run as a complete five-year result.
7. Inspect the C2 ledger, equity/drawdown, realized/unrealized P&L, open holdings and pending intentions. Open holdings at the end are expected when no valid exit filled.
8. After a complete run compare C2 against ROUTER and passive results, including gaps and model cost. Download complete JSON/ledger. Choose **Technical-only baseline** for the separate zero-generation strategy experiment.

The ordinary AI Agent Experiments page remains useful for a single-case trace and manual supervised-order demo; it is no longer the only place C2 can participate in historical evaluation.

## Verification boundaries

Tests use explicitly mocked model responses to verify actual control flow/accounting. They cover next-open entries and C2 exits, independent stop/strategy exits, surviving final holdings, unfilled final-close exit intentions, missing marks/evidence, budget/provider pauses, conservative unknown-call accounting, phase resume without duplicates, API auth/consent and UI request wiring. Real-provider output quality and financial effectiveness still require a funded explicitly consented run and independent evaluation. No multi-year paid model run is automatically executed while developing this feature.

## Selectable inference transport (0.16)

AEGIS_LLM_BACKEND selects openrouter (default) or codex_cli. Each job records backend/model/adapter/budget unit and rejects a changed identity on execute/resume. Codex requires supported ChatGPT login; no OpenRouter key is needed for that backend. Reservations count CLI invocations rather than internal provider requests; response-token budgets are guidance/local checks, not a guaranteed provider token cap. Actual reported tokens are retained, per-run USD cost is unknown and plan limits may pause as PAUSED_PROVIDER. No fallback occurs. Use the Plus UI runbook for the full demo route.


## v0.18 entry timing, adverse-risk review and profit exits

**Current rules — v0.18.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.

The matched active technical reference uses the same Friday/gap timing and selected profit target. The passive benchmark has neither active-entry timing nor active stop/profit limits. The engine is c2-portfolio-v3-fresh-adverse-profit; all original completed results remain unchanged.


## Version 0.19: materiality and reviewed portfolio memory

The current company view preserves issuer impact sections that can occur after long cover letters. Each matched adverse disclosure has extractive windows for action, amount, impact, status and event context. Windows from overlapping positions in the same source are merged. Identical windows share a text reference; each document retains its own citation ID, date and field mapping. Full source text, metadata and pack snapshots remain local. A missing field is unknown, never an invented Nil. An issuer statement of Nil impact is attributed, not independently verified.

C2 assesses severity, operating restrictions, unresolved consequences, recency and resolution rather than treating every negative keyword as material downside. Missing unrelated coverage alone is not a finding of adverse risk. Genuinely incomplete scans, unreadable required attachments and unresolved material exposure still block ENTER/HOLD. The independent critic and code gates remain authoritative. This is an evidence-quality improvement, not an instruction to buy every strong signal.

### Portfolio lessons through the UI

1. Open **Learning & Lessons → Portfolio lesson memory**. Select a completed C2 portfolio and click **Draft portfolio lesson candidates**. The reviewer token is required. Drafting is deterministic and makes zero generation calls; it does not judge a blocked trade from its later return.
2. Select a candidate. Inspect **Dated source cases and original assessment**, including source links and available materiality windows from the original immutable pack. Check the facts before generalizing. Missing financial coverage, context overflow and citation errors have different remedies. A draft is a hypothesis; not every blocked case was wrong.
3. Edit the conditional lesson and **Applies when** as needed. Choose ACCEPT or REJECT, write a rationale and click **Save portfolio lesson review**. Pending and rejected candidates cannot enter C2 context.
4. Select accepted candidates and click **Freeze portfolio lesson version**. Each immutable version records ID, hash, source period, accepted text and review provenance. Further accepted lessons require a new version; old runs remain pinned.
5. Open **Strategy Backtests → C2 historical portfolio**. Choose **Frozen portfolio lesson version** before creating a run. Default is **No portfolio lessons**. Up to three relevant reminders and at most 2400 characters enter market/strategy/critic context, with fewer or none when source evidence needs the context space. Inspect each saved research trace's `portfolio_memory` manifest and `lesson_ids`.
6. For evaluation, choose dates strictly after the latest source run end (`trained_through`). To debug an overlapping period, explicitly tick **Mark as development replay if lesson training overlaps these dates**. It is labelled DEVELOPMENT_REPLAY and is not unseen-period evidence. LATER_PERIOD_EVALUATION denotes date separation, not a statistical proof of benefit.
7. Create a new run. Start with one short window and 48 inference units; normal C2 uses six units per researched case and reserves eight. Resume only after inspecting any pause. Draft/review/freeze/retrieval adds no model requests; ordinary C2 research still uses the selected inference backend and allowance.

Friday/pre-gap fresh review, the default 8% net take-profit, fixed-entry-ATR 2× trailing stop, code sizing/cost rules and no forced end-date sale remain unchanged. Memory cannot change those rules or force a trade. There is no weight fine-tuning, self-training or automatic profit optimization.

### Fair test after this update

Preserve earlier results. Use identical dates, data, capital, risk, fees/slippage, entry/exit rules and inference configuration for technical reference, current C2 without portfolio lessons and current C2 with one frozen version. Start later than all lesson source runs for the memory comparison. Prefer a short diagnostic run before a three-month run; ₹200,000, risk 1%, fees/slippage 10 bps each, target 8%, ATR trail 2× and holding review every five sessions are reproducible starting settings, not optimized profit settings. Confirm the chosen dates exist in the active dataset and dated company packs can be prepared. At run start, plan for enough inference allowance; 48 units are a checkpoint budget, not a promise that three months will finish.

Report realized/unrealized return, drawdown, time in cash, fees, blocked reasons and inference use. Higher returns alone do not establish better research; lower exposure can reduce both return and drawdown. A rising stock after a block does not prove that the original block was wrong. No new profitable result is claimed before actual testing.

### Storage, versions and startup

Portfolio candidates/versions use `data/portfolio_lessons.sqlite`, separate from the legacy AI Agent Experiments playbook in `data/reviewed_lessons.sqlite`. The existing research-failure reflection workflow is retained. New endpoints: GET `/portfolio-lessons`; authenticated POST `/portfolio-lessons/draft`, `/review`, `/freeze`. Source checksums protect draft/review/freeze; version hash and temporal binding are rechecked on portfolio execution/resume and completed-C2 validation. Existing saved runs and ledgers remain unchanged. Earlier prompt/corpus/engine versions cannot resume under the new configuration; read them as historical results and create a fresh run.

Run from the project root: `bash scripts/start_unix.sh`. Open `http://127.0.0.1:8501`; API health is `http://127.0.0.1:8000/health`. Restart the API and dashboard together after an update, stopping the previous launcher first if its ports are occupied. This update preserves the configured inference backend and private credentials. It starts no portfolio or external inference request automatically.
