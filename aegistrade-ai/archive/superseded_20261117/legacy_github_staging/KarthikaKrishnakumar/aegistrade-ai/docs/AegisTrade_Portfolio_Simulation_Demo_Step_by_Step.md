# AegisTrade AI
Portfolio simulation demo: exact settings and UI steps

**Source 0.19.0 • Prepared 11 November 2026 • ChatGPT Plus / Codex CLI**

**Current rules — v0.19.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.
**Current memory update — v0.19:** Company materiality windows and bounded evidence packing are implemented. Completed portfolios can draft pending process lessons for human review, freeze and version-pinned retrieval into a NEW C2 run. See the final “Version 0.19” section for the exact UI sequence and development-replay/date rules. No improved profit result is claimed before testing.


**Demo history reset — 11 November 2026:** Existing portfolio/research/backtest history and simulated broker ledgers/approvals were cleared at the user's request. Earlier run IDs and numerical examples below describe archived rehearsals; they are not available in the active saved-run lists. Start a new run for your demo. Recoverable originals are under data/history_archives/20261111_105802/. Market data, company evidence, policy/model caches, reviewed lessons and private configuration were preserved.

Use this guide for your first portfolio demonstration. It gives one recommended starting run, the prerequisites and the results to inspect. Use the same C2 historical portfolio engine throughout. A “proper result” means an auditable completed simulation with researched decisions, accounting and any surviving holdings; it does not mean a guaranteed positive return.

## 1. Recommended first-run values

Start with three actual market sessions: Friday candidate, Monday close review and Tuesday open fill. This proves the entry-to-valuation flow with a small model allowance before attempting an eight-month period.

| UI control | Enter/select |
|---|---|
| Workspace | Strategy Backtests |
| Simulation engine | C2 historical portfolio |
| Initial capital | ₹200,000 |
| Simulation start | 2023-12-01 — Friday |
| Simulation end | 2023-12-05 — Tuesday |
| Maximum risk per trade | 1.0% |
| Automatically screen and rank stocks | Enabled; C2 uses automatic selection |
| Strategies to run | ROUTER |
| Fees | 5 basis points per transaction |
| Slippage | 5 basis points per transaction |
| Enable trailing stop | Checked |
| Trailing distance (× ATR14 at entry signal) | 2.0 |
| Take-profit target (% net return) | 8.0 |
| Total inference allowance | 32 |
| Review each holding every N market sessions | 5 |
| External-inference consent | Check after reading the displayed allowance |
| Historical replay-rule approval | Check after reviewing these settings |

One basis point is0.01%;5 bps means0.05%. These are chosen simulation assumptions, not a statement of your actual brokerage costs. A1% risk setting limits planned risk under the stop-distance calculation; gaps and execution assumptions can produce different realized losses. Position-exposure and cash limits also constrain quantities.

Why these settings: ₹200,000 provides enough reference capital for whole-share entries under the existing exposure/risk rules. Friday-to-Tuesday allows Friday screening, fresh Monday-close C2 review and an earliest Tuesday-opening fill. The former Friday-to-Monday two-session example cannot produce a BUY under the new review rule. It avoids interpreting a weekend as a missing trading day.32 units reserve up to8 for each of four shortlisted research cases; ordinary complete C2 usually needs6 per case. The end date does not cause a sale.

The selected historical candidates include TMPV, BHARTIARTL, AXISBANK and HINDALCO with the current cached dataset/settings. Selection is calculated by code. It is a research shortlist, not an investment recommendation, and it is not a promise that every candidate will pass C2 or fill.

## 2. Prerequisites to check once

### A. Start the correct local services

Source version0.17.0 adds trailing stops. Use the existing services if health confirms trailing_stop_supported:true; otherwise restart your launcher once. Do not launch another copy on occupied ports.

| Page | Address | Expected result |
|---|---|---|
| Main dashboard | http://127.0.0.1:8501 | Workspace selector and project screens |
| Backend landing | http://127.0.0.1:8000/ | Links to dashboard, documentation and health |
| Backend health | http://127.0.0.1:8000/health | ok:true; source0.19.0 or later; ui_api_contract:1; trailing_stop_supported:true |
| API documentation | http://127.0.0.1:8000/docs | Interactive endpoint documentation |

If services are stopped, open Terminal:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
bash scripts/start_unix.sh
```

Keep that Terminal running. To stop your launcher, use Ctrl+C in its Terminal. Do not start a second launcher on the same ports or terminate an unrelated process. API and UI compatibility now use an explicit interface contract, so ordinary compatible patch-version differences do not block the dashboard.

### B. Confirm the model backend

Open AI Agent Experiments briefly to inspect status; you do not need to run a separate experiment before the portfolio. Expect Inference backend = codex_cli and Inference enabled and ready = Yes. The portfolio runs its own C2 research internally.

The local .env already selects your ChatGPT-authenticated Codex CLI. No OpenRouter payment is needed for that selected transport. Your Plus usage allowance still applies. Each displayed unit is one CLI invocation; internal provider requests and per-run USD cost are not known. The response-token setting is not a hard cap on all provider reasoning/input/output tokens.

If sign-in is unavailable, privately inspect AEGIS_CODEX_BIN in .env and run that executable with login status, then login if needed. Complete the supported browser sign-in with your account. Do not paste ChatGPT credentials or an OpenRouter key into the reviewer-token field.

### C. Enter the reviewer token

Privately copy AEGIS_REVIEWER_TOKEN from .env and paste only that value into Reviewer token in the sidebar. It authorizes protected local actions and model-run consent. It is different from your ChatGPT login. Keep .env off the presentation screen.

### D. Confirm the downloaded NSE data

Select Market Data. Confirm NSEPYTHON is active and the frozen20-stock cache includes December2023. Use the existing dataset; do not redownload five years for this demo. Indicator warm-up history is already included before the selected evaluation period.

The universe is a current-membership research snapshot applied backwards, and prices are unadjusted for unresolved corporate actions. Disclose these limitations when discussing returns. This guide demonstrates workflow and accounting rather than independently established profitability.

### E. Check the dated company evidence

The older December1 demo packs remain available as historical financial evidence. The new entry review requires fresh December4 adverse-disclosure coverage; the worker prepares or upgrades exact-date packs before research. In AI Agent Experiments, expand Historical company research and inspect the cached evidence for each shortlisted symbol at2023-12-01. Inspecting cache makes no generation call.

Confirm that the pack has sufficient bounded coverage and readable financial evidence. Review the financial reporting period, consolidated/standalone basis, units, publication/availability timestamp and source link. The cutoff is15:30 IST on the selected decision date; quarter-end alone is not the publication date.

Two quarterly attachments previously failed the8 MB download bound. The downloader now allows up to32 MB, retains the page/text bounds and caches extracted attachments. The repaired source text is real public exchange material. The new extractive view preserves financial headings, results narratives and announcement bodies, prioritizes usable evidence, and lists omitted unreadable/non-financial attachments separately. Complete source text and metadata remain in hashed local packs and archived versions.

For a missing pack, choose the exact symbol/date, then Prepare historical company evidence. For a genuinely failed older cached attachment, select Refresh existing company archive pack and prepare deliberately. This performs public downloads, not generation. Refresh changes evidence provenance and can invalidate older research/approval; finish preparation before starting the model run.

Optional preparation command for the specifically configured demo repair is:

```bash
.venv/bin/python -m scripts.prepare_portfolio_demo_evidence
```

It expects the four dated packs to exist, repairs recorded financial attachments using their original approved URLs and preserves publication timestamps. It makes zero model calls. Its report is reports/portfolio_demo_evidence.json. A full public archive refresh is unnecessary when those packs are already prepared.

SUFFICIENT pack coverage means readable material is available. The model may still judge the substantive assessment insufficient or review-required. Never change that status or disable a check to obtain a trade.

## 3. Run the first portfolio through the UI

1. Open Strategy Backtests. Select C2 historical portfolio.
2. Enter every setting from Section1. Check both dates before submitting; the form changes take effect when Run is pressed.
3. Verify capital₹200,000, risk1%, costs5/5 bps, ROUTER, trailing enabled at2.0×ATR14, allowance32 and review interval5.
4. Read the upfront replay-rule approval. It authorizes automatic historical entries/exits within the stated assumptions. This path does not pause for individual fill approval. Exact per-order approval is demonstrated separately in Supervised Trading after completed research.
5. Check external-inference consent and historical-rule approval. Ensure the reviewer token is present.
6. Click Run historical portfolio simulation once. Note the returned run ID.
7. Expand C2 portfolio progress, resume and saved jobs. Click Refresh C2 progress to see updates. Do not start another run because this one is taking time.
8. Wait for COMPLETED or COMPLETED_WITH_GAPS, or inspect a pause reason. The first case can load local neural models and launch MCP processes, so preparation/inference can take several minutes.
9. Open the decision table, ledger, open holdings, equity curve and accounting fields described below.
10. Save the result JSON/ledger through the available download controls. Retain the run ID with your rehearsal notes.

You do not manually choose a stock in this form. Code screens/ranks the universe; prospective entries complete market→strategy→critic C2, followed by code validation. Accepted entries are queued for the next eligible open, where research, cash and risk are checked again and whole-share size is calculated.

[[FIGURE:portfolio]]

The same engine applies code stops/strategy exits and scheduled C2 holding reviews when the period is long enough.

## 4. Read the output correctly

HOLD is a successful scheduled review of an existing holding. It keeps the shares without creating a new fill; stops and strategy exits remain active. Repeated HOLD rows can refer to different stocks or later reviews of the same stock. The saved run settings determine review spacing. The reason column now shows successful explanations as well as errors; select the matching date/symbol/HOLDING_REVIEW under C2 portfolio research record to read the full Decision explanation below. A blank failure_category means no recorded failure, not missing reasoning. Each researched HOLD can consume inference allowance even though it creates no trading fee.

| Output | What to inspect and explain |
|---|---|
| Status/progress | All three rehearsal market sessions completed; a pause is not a final full-window result |
| Stock-selection audit | Why each stock was eligible, ranked, selected or excluded |
| C2 decisions | ENTER/BLOCKED; purpose ENTRY; calls, category, reason and research ID |
| Selected research trace | Actual specialist outputs, MCP tools, citations, critic and context usage |
| Trading ledger | A passing entry signals on December1 and can BUY on December4; a shortlist alone is not a fill |
| Open holdings | Remaining shares, mark date/value and unrealized P&L |
| Ending portfolio | Cash plus marked holdings |
| Realized P&L | Outcomes of shares actually sold inside the window |
| Unrealized P&L | Marked gains/losses on holdings still owned, with the engine's entry-fee allocation |
| Costs | Chosen fees and adverse slippage affect simulated fills/returns |
| Usage | Known CLI invocations, budget reservations, reported tokens and unknown per-run USD charge |
| Accounting | equity_identity_error should be near zero within floating-point precision |

The key identity is:

**Ending equity = cash + marked holdings = initial capital + realized P&L + unrealized P&L.**

A result with open holdings and zero realized P&L is expected in a two-session entry demonstration. It does not mean the exit code is missing. The final date is an observation boundary, not a reason to sell.

A negative return can also be a valid result, especially over two sessions after fees/slippage. Do not select dates solely to manufacture a positive number. Explain decisions, costs, drawdown, evidence and limits alongside returns.

## 5. Verified rehearsal result on this machine

This genuine Codex rehearsal completed both sessions with job **64263380f155412ea95a4deca6355a1f**. It used real NSE bars, actual MCP/neural policy retrieval and real dated company filings; inference/fills were not mocked. Evidence preparation used the existing cache.

| Recorded item | Actual result |
|---|---|
| Status | COMPLETED_WITH_GAPS |
| CLI invocations | 23 out of32 authorized |
| Simulated fill | BUY38 BHARTIARTL on2023-12-04, following its2023-12-01 signal |
| Entry price / fee | ₹1,036.518 per share / ₹19.693842 |
| Ending cash | ₹160,592.62 |
| Marked holding value | ₹39,250.20 |
| Ending equity | ₹199,842.82 |
| Total return | Approximately−0.08% |
| Realized / unrealized P&L | ₹0 / approximately−₹157.18 |
| End-date holdings |38 BHARTIARTL shares; no forced sale |
| Accounting identity error | Approximately2.2×10^-11 INR |
| Provider cost | Unknown per-run USD cost; not reported as zero |

This is a completed workflow example with disclosed gaps, not a clean research result for all four candidates. TMPV and AXISBANK reached the critic but additional policy retrieval exceeded the rehearsal's earlier22,000-character cap; their measured contexts were22,884 and22,669 characters. Current prompts clarify policy versus company citations and the bounded ceiling is26,000 characters. These changes cover the measured context sizes, but do not retrospectively approve those blocked entries. HINDALCO's model assessment was insufficient and correctly blocked early.

The archived result remains unchanged and predates trailing stops: it used the original fixed-stop policy. It is not evidence of trailing-stop performance. A fresh run with the current prompt/engine version can differ, and its outcome has not been presented as a guaranteed all-pass result. Do not repeatedly fund a long replay simply to chase trades. Annualized CAGR and Sharpe over two sessions are not meaningful investment evidence; focus on fills, costs, marking and reconciliation.

Historical summary: reports/portfolio_demo_verified.json. Original research files are archived under data/history_archives/20261111_105802/data/c2_portfolio_runs/64263380f155412ea95a4deca6355a1f/research/.

This earlier job was archived during the requested history reset. It no longer appears under Saved C2 portfolio and cannot be opened or resumed through the active UI. The historical summary remains an example; create and retain a new rehearsal result for the current demonstration.

A saved result is useful for explaining the full record if account/network access fails during the presentation. Label it as a saved rehearsal result. Re-running the same settings can produce different model judgements or usage; deterministic accounting does not make model responses identical.

## 6. Three-month C2 portfolio demonstration

For the main rehearsal, use the following single configuration. These values are for simulated money. Complete the short C2 rehearsal first to check actual account access and model output before authorizing a larger run.

| UI control | Three-month demonstration value |
|---|---|
| Workspace / engine | Strategy Backtests / C2 historical portfolio |
| Stock universe | Current cached20-stock subset; automatic selection enabled |
| Initial capital | ₹500,000 (₹5 lakh simulated cash) |
| Start | 2023-12-01 |
| End | 2024-02-29 |
| Risk per trade | 1.0% |
| Strategy | ROUTER |
| Fees / slippage | 10 /10 basis points per transaction |
| Enable trailing stop / ATR distance | Checked /2.0 |
| Take-profit target (% net return) | 8.0 |
| Holding-review interval | 10 market sessions |
| Total inference allowance | 480, only after reviewing the short-run outcome and remaining account allowance |
| External-inference consent / historical-rule approval | Both checked after reviewing the settings |

The current cache contains63 sessions and1,260 bars across20 symbols for this window. The date range was chosen because December1 already has prepared company evidence, not by searching for a profitable quarter. The four initial code-shortlisted candidates are TMPV, BHARTIARTL, AXISBANK and HINDALCO; their local December1 packs have SUFFICIENT bounded readable coverage. This does not mean the LLM must approve the substantive assessment. Later dates require separate dated packs.

₹5 lakh gives practical whole-share quantities. Code still caps four simultaneous positions and20% of equity per position, initially about₹100,000. Planned initial risk is at most1% of current equity, initially₹5,000, before gap/slippage effects. Increasing capital scales rupee exposure and does not fix a negative-return strategy. Maximum positions and exposure cap are current engine defaults, not additional UI inputs.

Ten-session C2 reviews reduce repeated generation while daily code checks, trailing stops and strategy exits continue on every available bar. With four holdings maintained through most of the window, a rough planning example is24 holding reviews plus4 entry cases: around168 inference units in total at six per ordinary case (28×6). This is an illustration, not a forecast. Replacements, rejected candidates, revisions and failures can use much more. The480-unit ceiling allows about80 ordinary six-unit cases, with eight units reserved before each case and unused units released when actual usage is known. It does not guarantee completion or reserve ChatGPT account allowance. Units are CLI invocations for the configured codex_cli transport, or requests for OpenRouter.

If PAUSED_BUDGET appears, inspect progress and explicitly approve additional allowance only when wanted. PAUSED_PROVIDER needs the displayed account/model/connection issue resolved before consented resume; extra portfolio budget alone is not a remedy. Do not bypass insufficient evidence. Reopen the same run ID to continue; do not create duplicate jobs. Research and downloads can take substantial time, so finish the quarter ahead of the exam and retain its saved result for presenting the complete ledger. An inference cap is not a runtime cap.

A no-generation technical-only prerequisite check completed this window with32 ledger events and78 stop increases using these capital/risk/cost/trailing settings. These counts belong to the deterministic baseline, not C2. At the time of that prerequisite check, the complete C2 quarter had not been run. The user subsequently completed run95ef3724c1a94eb6bf69286a4c60272a for this window with ₹500,000, risk1%, costs10/10 bps, trailing2ATR and a FIVE-session review interval. Its initial allowance48 was explicitly increased to528, with313 invocations actually recorded. Status was COMPLETED_WITH_GAPS; ending equity₹521,314.06, return4.26%, realized profit₹5,310.26 and unrealized profit₹16,003.80 across four surviving holdings. Technical ROUTER returned4.41%; passive equal-weight20-stock returned8.68% with different exposure/risk rules. The actual review interval and allowance differed from the recommended ten-session/480 setup above, so this is not a measured outcome for every recommended parameter. The supplied24-event ledger and all ten stop/fill calculations were verified without new model calls. See AegisTrade_Three_Month_Portfolio_Performance_Review.docx and reports/portfolio_performance_review_20261111.json. This is development evidence, not independent proof of profitability or AI superiority. The earlier prerequisite record remains reports/three_month_demo_preflight.json.

### Should the universe include all50?

My design recommendation is to screen all50 and research only a small eligible shortlist, while retaining the four-position portfolio cap. It broadens the available companies but does not establish that selected trades, sector balance or returns improve. Screening more stocks does not require an LLM call for every stock. The current20 were selected by pre-period liquidity, not by knowing later winners.

The current downloader explicitly allows1–20 and the active cache contains20. Expanding requires code/UI/manifest changes and additional downloads, dated company coverage and correct eligibility for companies without the full earlier listing history. A naive --top50 currently fails; the pre-period-ranking and five-year-coverage assumptions also need adaptation. Current membership applied backwards still has survivorship bias, and expanding alone does not correct raw corporate-action prices. The settings in this section work with the existing20; they do not silently switch the project to50.

Prepare exact-date company evidence for entry and review dates as needed; the UI worker can prepare it automatically. Reused attachment text avoids downloading an unchanged PDF repeatedly, but a new decision date still needs its own valid historical availability/coverage pack.

C2 holding reviews can return HOLD or EXIT. Code also applies initial2ATR stops, enabled trailing stops and strategy exits independently. Accepted model EXIT normally fills at a later eligible open. A stop can fill earlier under the approved risk rules. Neither the model nor the human should invent an exit simply to make the demonstration more dramatic.

### Inspect the trailing stop

For a NEW run, leave Enable trailing stop checked and Trailing distance at2.0. The stop follows the highest completed close since the fill, minus2×ATR14 from the entry signal. It never falls. Each increase is active from the next session, after that day's low has already been tested against the previous stop. This adds no model calls.

Example: initial stop₹480 and entry-signal ATR₹10. If the highest completed close becomes₹530, the next-session stop is₹510. If the next close is₹525, the stop stays₹510. A later close₹545 raises it to₹525. A gap opening below₹525 sells at the opening price with adverse slippage and fees;₹525 is not a guaranteed fill.

Expand Exit rules, profit target and stop adjustments to inspect old_stop, new_stop, highest_close, entry_signal_atr and effective_after_close. Open holdings shows the current stop and initial_stop. A triggered raised stop appears as SELL_TRAILING_STOP in the ledger; an unchanged initial stop appears as SELL_STOP. A two-session run may show only a stop adjustment and an open holding. It does not have to produce an exit, and no sale is forced on the end date.

Old runs retain their original policy and results. Start a new run for trailing stops; earlier engine/corpus versions cannot be resumed under this changed exit policy. The technical ROUTER reference uses the same trailing setting; the passive benchmark has no stops. The separate Supervised Trading screen remains an individual approved action and does not continuously monitor positions. Trailing can protect some accumulated gains but cannot guarantee a profitable run.

An end-date holding can remain open. An exit intention at the final close cannot fill outside the requested period. Changing end date or capital requires a new run; resume does not extend an earlier simulation or automatically roll its holdings into a separate run.

## 7. Handle pauses and blocks

| Status/category | Action |
|---|---|
| PAUSED_BUDGET | Inspect consumption and remaining account allowance. Add a deliberate additional allowance and consent to Resume only if you choose to continue |
| PAUSED_PROVIDER | Check Codex login, quota/model access and connectivity; resolve the issue before an explicitly consented retry |
| PAUSED_USER | Continue only if the job's configuration still matches and you intend to consume its remaining allowance |
| INTERRUPTED | Inspect its state and possible uncertain reservation; resume only with matching data/model/prompts and explicit consent |
| COMPLETED_WITH_GAPS | The window finished but some decisions/fills were blocked. Explain them; this is not the same as a complete set of researched trades |
| EVIDENCE | Open the company assessment and exact-date sources. Insufficient coverage/interpretation blocks an entry; more model allowance does not fix missing facts |
| SCHEMA | Read the named field/limit. Current prompts provide600-character summary limits and specific correction feedback within existing bounds |
| CODEX_TIMEOUT | One CLI invocation exceeded the application's local time limit. Refresh progress first; do not resume an already RUNNING job. A timeout alone does not prove a login/quota issue |
| CONTEXT_BUDGET_EXCEEDED | Inspect trace context_usage. Do not repeatedly fund the same failed case; use the current compact evidence view and preserve the failed record |
| Research configuration changed | Load the old audit, then start a new run. Prompts/model/evidence changes cannot silently mix inside a resumed job |

Prior August/December runs used earlier prompts or evidence views. Their records and consumption are preserved. Use a new short run for this guide rather than repeatedly resuming an old long run.

Refresh C2 progress before deciding that nothing happened. A browser timeout is not proof that a job stopped. Pause is honored at safe boundaries; an active model/download request may finish first. Never increase allowance automatically just because the result is blocked.

### Recover from an isolated Codex timeout

The November11 three-month run95ef3724c1a94eb6bf69286a4c60272a paused on the first market invocation for SBIN-2023-12-29 after120.029 seconds. Its previous ledger and completed sessions remained saved. A later user-authorized resume advanced past that case to January2024. At the diagnostic check,108 other saved invocations had succeeded, with a median8.83 seconds and maximum17.163 seconds. This supports an isolated long invocation; the saved timeout does not establish why it was slow or prove an authentication/quota failure. Transport recovery does not mean that the company's research assessment must pass.

First press Refresh C2 progress. If RUNNING, let the worker continue. If still PAUSED_PROVIDER with CODEX_TIMEOUT, inspect the failed trace and account/connectivity status. If you choose to retry and at least eight units remain unreserved, set Additional inference units on resume to0, check the resume-consent box and click Resume C2 portfolio once. The failed attempt remains counted and a retry uses more of the existing allowance. Completed opening fills and successful close decisions are not replayed. If fewer than eight units remain, deliberate additional allowance is required before the next case.

For repeated timeouts, the application supports AEGIS_CODEX_TIMEOUT_SECONDS in private.env, currently120 seconds and validated15–600. A300-second setting is an operational option, not a proven cure or a provider guarantee. Apply it by restarting only after the job is safely paused; then reopen the same job and explicitly resume. Increasing this timeout does not itself change the model, prompt, data or call allowance. Do not change model/reasoning settings within a frozen experiment to disguise a timeout. No timeout/configuration change, restart or model retry was performed by the diagnostic check while the user's recovered run was active. Official CLI automation background: https://learn.chatgpt.com/docs/non-interactive-mode.

## 8. Repeated “restart API and dashboard” warning

The earlier UI compared exact patch versions while Streamlit hot-reloaded source edits and FastAPI retained its earlier code. It could therefore block a compatible dashboard during an update.0.16.2 introduces explicit interface compatibility and restarts both services together.

Refresh the browser first. If health is reachable and ui_api_contract is1, compatible patches should work. If an incompatible-interface warning remains, stop your own launcher and start the project once using the command in Section2. Do not repeatedly start duplicate launchers or assume the warning indicates a model-key failure.

## 9. Suggested presentation narration

“I enter capital, dates, risk and costs. Code screens the historical stock universe. Each prospective entry receives dated financial/news research through MCP, three LLM specialist hand-offs, critic review and code validation. Code sizes accepted entries and fills them at a later historical open. The report accounts for cash, fees and marked holdings; it does not force liquidation at the end. A longer run adds holding reviews and code/model exits. Missing evidence blocks a decision rather than being treated as a clean company. We demonstrate controlled research and simulation, while profitability remains an independent evaluation question.”

For the professor-approved three-person team, one member can enter settings and explain data/ranking, one can explain C2/MCP/RAG and evidence, and one can explain accounting, approval scope, exits and failure recovery. These are suggested demo responsibilities, not a claim about completed contributions.

Before the viva keep: this guide, the exact saved run ID/result, data/corpus/prompt versions, one selected research trace, the ledger and known limitations. Do not present a mocked context test as genuine model performance. The separate Supervised Trading screen demonstrates exact human approve/edit/reject after completed C2; it is a different approval scope from this historical replay.

## 10. Specific timeout/output errors and independent citation verification — 11 November

The November11 TMPV screenshot belongs to run327fd2f2b0d2453fb58b2decec69d259. Its first attempt completed seven invocations, then the extra eighth strategy-revision invocation exceeded the local120-second timeout (CODEX_TIMEOUT). A consented retry recorded CODEX_OUTPUT_INVALID on the same unproductive revision path. The saved run consumed16 invocations and remains paused; neither trace establishes that ChatGPT credits or login failed. Increasing the total job allowance does not change the eight-unit case ceiling or120-second local timeout.

The earlier critic could not find a policy ID in its semantic top-five results even though the strategy had retrieved that ID. Version0.16.3 makes the critic's existing MCP search independently fetch the exact cited policy IDs along with semantic matches, with the same corpus/date checks. A real critic rejection still blocks, and now ends the case immediately instead of making an extra strategy call that could not produce an approved result.

The UI now shows specific transport codes, failure category and elapsed time for saved provider failures. Old responses and call counts are preserved; a clearer label does not refund usage or approve a trade. Keep the pause while inspecting the cause. Changed research prompts require a new short run, not resuming the older frozen job. No new model generation was performed to diagnose or validate this update; tests use mocked replies and actual in-process MCP retrieval.


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


## Codex response-format correction — version 0.19.1

A saved RELIANCE entry case dated 1 February 2024 paused with CODEX_OUTPUT_INVALID after two CLI invocations. The usage record identifies JSONDecodeError, not an established quota/authentication failure. The original trace did not retain the parsing stage, so the precise malformed text cannot be reconstructed. The CLI envelope previously required the specialist JSON to be encoded again as a string; the adapter now supplies the exact specialist object schema directly, removing that extra encoding layer. Legacy valid JSON strings remain readable. Malformed JSON is not repaired or accepted; stage and line/column diagnostics are recorded without retaining arbitrary raw private output. Native tools and all C2 evidence/risk gates remain restricted.

This transport correction preserves the portfolio engine, policy corpus, prompts, memory version and backend identity. The current paused run can be resumed after restarting the API and dashboard together. In Strategy Backtests, open the paused saved C2 portfolio, set Additional inference units on resume to 0 (the observed run used 2 of its existing 48 units), tick the resume authorization and click Resume C2 portfolio. Failed calls remain counted. Resume starts a fresh research attempt for the failed case; it does not continue inside the broken CLI response. Later budget exhaustion can still require a deliberate allowance increase. No automatic retry, backend fallback or simulation is started by the patch.

If the error recurs, inspect the new validation_stage and json_error fields in the saved research usage; do not assume that buying API credits addresses a response-format error. Mocked schema/transport and regression tests validate the correction; actual account-backed success remains to be tested by an explicitly resumed run.
