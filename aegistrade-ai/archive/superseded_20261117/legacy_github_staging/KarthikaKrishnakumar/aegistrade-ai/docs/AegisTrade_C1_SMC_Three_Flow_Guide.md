# AegisTrade AI: C1 SMC and the three portfolio flows

Version 0.25.0 · 13 November 2026

## Choose the workflow

| Strategy Backtests option | Research order | Agent design | Entry | Exit |
| --- | --- | --- | --- | --- |
| C2 historical portfolio | Technical shortlist → dated research | Market, strategy and independent critic specialists | Existing approved router: trend, confirmed pullback, RSI reversion or breakout, including bounded stopped-breakout rebound | Existing code stop/trail/target/strategy exits and supported C2 EXIT |
| C1 SMC portfolio | Liquidity/history screen → dated company research → SMC eligibility | One tool-using agent plus deterministic validation; no independent LLM critic | Regular daily-bar SMC pattern or confirmed stopped-position recovery, after a fresh company screen | Configured profit percentage, protective stop, optional trailing and supported adverse C1 EXIT |
| Technical-only baseline | Code screening → signal | No generation calls | Existing technical modes; explicit SMC mode also available | Code exits and costs; no company/news model assessment |

C1 is the requested evidence-before-signal case. It is an additional workflow; it does not replace C2 or remove breakout. Existing data, lessons and saved runs remain. New engine/prompt/corpus fingerprints require a fresh run for this version; old results remain readable.

## What SMC means here

SMC means Smart Money Concepts. Its broader vocabulary includes market structure, sweeps and order blocks; see the educational [Dukascopy SMC overview](https://www.dukascopy.com/swiss/english/marketwatch/articles/smart-money-concept/). The implementation below is this project's own fixed daily-bar approximation. It does not observe institutional orders, infer who traded, or implement every SMC variant. The educational source does not validate these parameters or their profitability.

1. **Liquidity sweep:** the current low is below the lowest low of the previous 20 completed sessions, but its close returns above that previous-low level. Record the sweep and the highest high of the five bars preceding it.
2. **Bullish structure break:** within ten later sessions, a bullish candle closes above that recorded five-bar high. Its body must be at least 0.5×ATR14. This must occur after the sweep bar.
3. **Order-block zone:** use the last bearish candle between three bars before the sweep and the bar immediately before the structure break. Its low and open define the lower and upper zone bounds. If there is no such bearish candle, do not create a zone.
4. **Retest confirmation:** within ten sessions after the break, a later candle overlaps the zone and closes bullish above its upper bound. A close below the lower bound invalidates the zone. The structure-break candle cannot count as its own retest. A confirmed zone is consumed once; there is no repeated signal on every following bar.
5. **Entry:** after dated company screening passes and code finds this SMC signal, queue a later eligible open. Revalidate the original company pack, date, signal proof, stop calculation, cash, position cap and risk before filling. Friday/pre-gap signals still require fresh next-trading-close review; a one-bar setup may cease qualifying during that delay. No stale Friday entry is forced.

No fair-value gap is required in this version. There are no future-confirmed swing pivots, intraday order-book feeds or short trades. History warmup, high-volatility exclusions, liquidity checks and raw-price discontinuity guards still apply. Patterns may be sparse on daily bars. No signal is an expected outcome, not proof of a software failure.

## Exact C1 orchestration

[[FIGURE:c1_smc]]

The engine computes causal historical features from available bars, but does not use SMC eligibility to select the companies to research. On each close it first applies data/history, turnover, volatility, held/pending-position and discontinuity constraints. It sorts eligible companies by turnover and rotates a bounded batch, default three per session (UI permits one to ten). This is a cost limit, not research of every stock every day. A signal on an unselected stock can be missed.

The C1 agent receives a COMPANY_SCREEN case with regime UNCERTAIN and approved strategy NONE. Its tools do not expose an SMC context or approved SMC signal at this stage. It must gather company_evidence, market_snapshot, search_policy and check_strategy. Policy search uses the existing RAG retriever. Company retrieval uses the bounded, dated evidence pack with official filings, issuer disclosures and any eligible imported news/newsletters. When company evidence is missing or unknown, the bounded dated web-search tool can seek original sources subject to existing source, date and identity validation.

The model returns a typed company assessment, observed citations, strategy NONE and action SCREEN. That result is not a buy decision. Code checks current corpus and company-pack hashes, observed source/tool provenance, publication cutoff, company identity, assessment status and adverse-risk coverage. Missing/unknown evidence and cited adverse findings do not permit entry. The strong-trend incomplete-coverage exception does not apply to C1 SMC/company screening. A failed bounded web search is not proof that a company has no adverse news.

Only after the screen passes does the portfolio inspect SMCSignal. The saved decision is NO_SMC_SIGNAL if no pattern qualifies. ENTER means the evidence passed and the code pattern qualified; the record stores the SMC proof, research ID and evidence-before-signal ordering. The saved model response still says SCREEN, accurately separating the single agent's research from code's entry decision.

At a later open, both the dated screen and code SMC proof are checked again. Sizing remains arithmetic. During holdings, scheduled single-agent reviews and dated issuer-disclosure triggers can produce HOLD or a supported adverse EXIT. No independent LLM critic is claimed for C1. C2 retains its separate critic and stricter breakout quotation gates.

## Profit target, stop and costs

C1 defaults to a **4% net trading return target**, editable in the UI and required to be above zero. This is a prototype parameter for testing, not an optimized target or expected return. The target accounts for modeled entry/exit fees and slippage; provider/ChatGPT charges are excluded from trading return and reported separately when available.

The common initial-stop controls apply to SMC: default signal close minus 2×ATR14, with a percentage alternative. Default risk is 1% of current equity, subject to cash and the existing position/exposure caps. Trailing is off by default in C1; it can be enabled explicitly. Breakout-specific controls and breakout rebound watches do not apply to C1.

SMC has no EMA/RSI strategy exit. Profit target, protective stop, optional trailing and evidence-backed adverse EXIT govern its holdings. Stops remain active while model research is paused. Adverse exits fill at a later eligible open after source validation. A gap through a stop fills at the available open with modeled costs. If a daily bar touches both stop and target after opening, the conservative stop-first rule applies. The simulator does not know the real intraday sequence. Unsold holdings remain marked to market at the end; the requested period never forces every holding to sell.

## News and newsletter preparation in the UI

Historical newsletter availability is not assumed. No paid subscription or complete five-year newsletter archive is bundled. Automatic public web search may find company filings or original news, but cannot promise coverage of newsletters or reconstruct every page's historical version.

1. Choose **Strategy Backtests → C1 SMC portfolio**.
2. Expand **Optional: add reviewed historical news or newsletters before research**.
3. Choose the company and the exact decision date for the case. Click **Prepare dated company pack for newsletter**. This downloads/prepares bounded official sources without a generation request. A reviewer token is required.
4. Provide one or two licensed excerpts in a JSONL file. Each record needs symbol, kind (`news` or `newsletter`), title, publisher, original source_url, published_at, original_publication_verified=true, and 100–4000 characters of source text. Enter the name of the person who actually verified the original publication. Do not invent a source or attest verification that was not performed. The UI example is a format template, not usable evidence.
5. Click **Import reviewed historical excerpts**. Pause active portfolio workers before importing. Future or unverified records are rejected. Date-only publications become available the following local midnight; explicit availability cannot precede original publication. Imports are limited to the 180-day evidence window.
6. Start a fresh simulation including that decision date. The excerpt supplements that exact company's dated pack; it is not automatically copied to every later decision date. Import another eligible dated pack if needed for a later case. Refreshing an official pack can replace imports; inspect the cached pack afterwards.
7. Open the saved AI research trace and inspect company_research.documents for kind newsletter/news, original URL, publication/availability, text hash and citation IDs. Check the single hand-off, tool observations and later code SMC decision.

A newsletter cannot fabricate an official financial filing, replace a failed official scan, guarantee an adverse-free company, override structural-action guards, or cause a trade without an SMC signal. Text is treated as untrusted data, not instructions to the agent. A contract test proves this path with a clearly synthetic newsletter; no real newsletter was fabricated or downloaded as financial evidence during implementation.

## UI demo run

1. Start services together with `bash scripts/start_unix.sh`. Open http://127.0.0.1:8501. Health should report 0.25.0 and c1_smc_portfolio_supported=true. Confirm the intended existing universe and downloaded period in Market Data. Nothing switches your universe automatically.
2. Enter your private reviewer token. Keep the configured OpenRouter or signed-in Codex backend. C1 uses the same configured inference backend; it does not require a second API account or key.
3. In Strategy Backtests choose **C1 SMC portfolio**. Start with a short available window (for example two trading weeks) and ₹200,000, risk 1%, ATR stop 2, target 4%, trailing off, three company screens/session, five-session holding review, and normal modeled fees/slippage. A short window tests the workflow; it need not contain an SMC trade. Choose dates supported by your downloaded data, not a guaranteed winning period.
4. Begin with 48 inference units to inspect a few cases. A simple C1 case often uses two invocations (tool selection and typed response), but web retrieval/corrections can require more. The engine conservatively reserves eight per case before starting. Evidence-first research can consume allowance even when no trade signal exists. Increase allowance only with consent after inspecting the run; the total allowance does not increase the per-case cap.
5. For a three-month experiment, use the same capital/risk/fees/target across comparisons. With about 63 sessions and three screens/session, roughly 378 invocations would be needed if every screen took two calls, before holding reviews. A 512-unit starting allowance is an illustration, not a guarantee that the run or your account quota will cover all work. The hard eight-per-case bound is much larger; provider/model failures can pause sooner. Use one screen/session to reduce cost while accepting reduced stock coverage.
6. Authorize external inference and historical replay rules. Click **Run historical portfolio simulation**. Follow live progress; **Refresh AI progress** remains available. The same saved-job controls pause, open and resume C1/C2; the stored flow cannot change on resume. A single shared worker queues concurrent AI jobs.
7. Inspect research_summary and decisions: company_screens → evidence_passed → NO_SMC_SIGNAL / ENTER. A passed screen without an SMC signal is not a blocked trade. BLOCKED means source/policy/schema/provider validation prevented progress; inspect the saved reason.
8. For ENTER, inspect the later BUY, stored SMC dates/zone, dated company pack and subsequent SELL_TAKE_PROFIT / SELL_STOP / SELL_C1 or remaining holding. Compare C1 to SMC_REFERENCE, which uses the same causal SMC, rotating screen limit and execution settings but no evidence gate or model reviews. Returns differ because evidence decisions and holding reviews change the portfolio; they do not isolate a universally profitable LLM effect.
9. Compare C2 separately with its existing strategies. Technical-only SMC is selectable for a no-generation mechanics comparison; technical ALL retains the existing router-plus-four-strategy set, so SMC is explicit rather than silently changing historical ALL comparisons.
10. Inspect disjoint periods before changing parameters. Keep an untouched held-out period for capstone evaluation. Do not call a window chosen for pattern visibility or a tuned profitable run an independent test.

## Synthetic worked case

This is a contract-test illustration, not an NSE trade recommendation or stored real company evidence. Prior 20-session lows are ₹99; a later candle dips to ₹97 and closes ₹100. A subsequent bullish candle closes ₹104 above the recorded ₹102 structure level. The preceding bearish candle defines zone ₹97–₹101. A later candle trades into that zone and closes bullish at ₹103. A source-grounded COMPANY_SCREEN passes before code checks this retest. The next eligible open is ₹103 before slippage; the engine sizes the buy, freezes the initial stop and computes the gross price needed to obtain 4% net of modeled fees/slippage. A later bar reaching that target exits. Tests also cover missing evidence, no signal, a stop, an adverse exit, remaining holdings and pause/resume. No actual generation request was made for this illustration.

## Viva questions

**Why three flows?** C2 demonstrates specialist orchestration and independent critique. C1 demonstrates one tool-using agent researching before a fixed SMC strategy. Technical-only gives a code-only comparator. They are different experimental configurations, not three claims of profitability.

**Is C1 autonomous trading?** It autonomously gathers bounded evidence under consent and can influence simulated eligibility. Code controls pattern detection, sizing, exits and submission. Historical replay has upfront rule approval; live brokerage is disabled.

**What makes this evidence-first?** Research candidate selection does not use SMC eligibility. The agent sees NONE/UNCERTAIN with COMPANY_SCREEN and no SMC proof. Only a validated dated screen allows the subsequent code SMC check. Causal features may be precomputed offline, but are not used to decide which companies to research or exposed as a signal to the screen agent.

**Does a good newsletter mean buy?** No. Verified dated excerpts supplement the company assessment. Price structure and all code/risk checks must still qualify.

**Does C1 have a critic?** No independent LLM critic. It has source provenance, typed schemas, code gates and pre-fill validation. C2 alone keeps the independent critic stage.

**Why can C1 consume calls without trading?** Evidence research occurs before SMC eligibility. This ordering tests the requested research-first approach and costs more than researching only confirmed signals. A rotating capped batch bounds cost and can miss stocks.

**Why a 4% target?** It is an editable prototype default, not a promised profit. Risk, transaction costs, gaps and market regime affect the outcome. A target never guarantees that price will reach it.

**Why keep a stop if exits are profit based?** The target defines normal profit-taking; the stop bounds intended downside. Removing all loss/adverse exits would leave risk uncontrolled while waiting indefinitely for a target.

**How is lookahead avoided?** Rolling windows exclude current/future comparison bars. Sweep, break and retest occur on different completed bars; fills occur later. Company/news availability cannot exceed the case cutoff. Date-only news is delayed, and incomplete historical version verification remains a stated limit.

**Does this prove that institutions entered?** No. SMC is a named, reproducible price-pattern approximation. It does not identify traders or infer institutional intent from daily OHLCV.

**Can saved C1 research be used to approve a supervised C2 order?** No. The supervised C2 gate requires C2 provenance and critic hand-offs; C1 results cannot satisfy it.


## Progress and signal diagnostics (0.24.1 correction)

The C1/C2 live progress panel now appears directly below the simulation-engine selector, above configuration controls. Selecting C1 automatically opens the latest saved C1 run if no C1 run is already selected. C1, C2 and Technical-only retain separate displayed results and run IDs. Switching tabs/flows or opening a run only performs read-only status requests; it never starts research or adds allowance. A saved paused job is refreshed from the backend on page rerun, so a resume from another browser is visible.

The market-session bar shows completed sessions out of the selected period. Within a session, live activity shows source preparation, company archive retrieval, the current LLM specialist/turn/tool, research validation and SMC checking. This activity is persisted separately from the financial checkpoint and contains no prompts, source text or credentials. No artificial percentage increase occurs while a single source download or model call is pending.

C1 live counters distinguish company screens, evidence-passed cases, actual SMC checks, confirmed SMC signals, queued buys and BUY fills. Latest decisions update in the five-second live panel. Research-blocked cases do not count as negative SMC signals: price eligibility has not been checked. A bounded rotating batch can miss stocks on their signal dates; the panel reports shortlisted versus eligible company-sessions.

A passed case now records its exact SMC stage: waiting for sweep, sweep found, waiting for structure break, structure break confirmed, waiting for retest, expired/invalidated setup, or confirmed entry. Its explanatory text states why no entry exists. The SMC thresholds, profit/stop rules, evidence policy, existing model allowance and historical trades are unchanged by this correction. Earlier decisions without detailed stage telemetry retain their original data; they are not retroactively relabelled as fresh research.

Use **Refresh AI progress** to reload all detailed tables. Expand **C1 saved runs, refresh, pause and resume** for C1 controls (or the corresponding C2 controls). A progress bar remains visible for queued, paused, completed and interrupted runs. A zero-entry result does not prove the process is idle: inspect evidence blockers, SMC stages and batch coverage. Existing 0.24.0 jobs remain compatible with this display/telemetry patch; no new simulation or additional allowance is required merely to see the corrected progress.


## SMC re-entry after a stop (0.25.0)

The C1 UI now offers **Allow one SMC recovery entry after a stop**, enabled by default for new runs, and **SMC recovery watch (trading sessions)**, default ten (range one to thirty). The same switch applies to an explicit technical-only SMC simulation; other technical/C2 strategies retain their own rules. The C1 technical reference uses identical SMC recovery settings.

1. Execute the protective or trailing stop sale first, including gap handling, fees and slippage. Persist the real stop-ledger ID, symbol, date/index, stop level, original entry date, original order-block context and recovery count. Profit-target, strategy or adverse-research exits do not open a recovery watch.
2. Within the watch window, prioritise stopped positions within the existing bounded research batch based only on the known stop history. Selection does not use the current recovery signal. High-volatility, history, liquidity, discontinuity, position/cash and daily-loss limits remain. With multiple watches and a small batch, not every stock is necessarily screened every session.
3. C1 performs a fresh dated COMPANY_SCREEN using RAG/filings/news and bounded web fallback under the existing evidence policy. The model still returns NONE/SCREEN before code sees recovery eligibility. A prior favourable company screen is not reused as approval. Missing/unknown evidence blocks; a cited adverse finding cancels the watch.
4. Only after the screen passes, require a **later** bullish candle (close above open) whose completed close exceeds the previous-session high, the stopped price and the original order-block upper level. The stop session is ineligible even if it rebounds strongly. This is SMC_RECOVERY_CONFIRMED, a recovery variant of the stopped setup; another full sweep/BOS sequence is not required.
5. Queue a later-open BUY with entry_setup SMC_RECOVERY. Freeze a new stop from the recovery signal and recalculate quantity from current equity/cash and normal SMC risk/exposure limits. Do not increase risk to recover the prior loss. The existing profit target, protective stop and optional trailing apply. Friday/pre-gap freshness rules still apply.
6. Before filling, validate fresh research plus the original recorded stop, immutable zone, watch ID/window/count, actual recovery candle and calculated stop. A forged/missing proof or an ordinary-SMC order attempting to bypass an active watch is blocked. Unfilled orders do not consume the retry. The window governs confirmation; later execution still follows existing later-open/missing-bar rules.
7. One recovery fill consumes the retry. If it stops again, mark the setup EXHAUSTED; no third buy is allowed for that watched setup. An adverse cancellation also prevents a recovery. Once the window expires, a future independent full SMC setup can qualify under fresh evidence; the stock is not permanently excluded.

Inspect **SMC stopped-position recovery watches** in results for WATCHING, EXHAUSTED, CANCELLED_ADVERSE or EXPIRED. Live decisions distinguish WAITING_SMC_RECOVERY, SMC_REENTRY_SAME_SESSION, SMC_RECOVERY_CONFIRMED and SMC_REENTRY_UNAVAILABLE. BUY/SELL records retain their stop/zone/research provenance. A recovery is a new risk decision and can lose again; no improved profit is established by these mechanical tests.

This release changes execution policy and the policy corpus. **Start a fresh simulation to use SMC re-entry.** Earlier runs remain saved under their original rules; an active earlier run is checkpoint-paused before loading this version. Do not mix the new recovery policy into an already partially evaluated historical portfolio.

### Additional viva questions

**Why exit and re-enter instead of holding through the stop?** The stop ends the original risk contract. The recovery is a separate, later decision with fresh evidence, stop, size, costs and audit IDs.

**Does the LLM decide that the candle has turned bullish?** No. The single agent screens dated company evidence first. Code checks explicit recovery conditions afterwards.

**How do you prevent repeated recovery losses?** One recovery fill per stopped chain; the next stop exhausts it until expiry. The system never increases risk to make back a loss.

**Can a saved order invent a favourable old stop level?** Pre-fill code binds it to the actual stop ledger, original order-block context, dates, count and frozen window. Matching a forged queue and watch is insufficient if the stop ledger differs.
