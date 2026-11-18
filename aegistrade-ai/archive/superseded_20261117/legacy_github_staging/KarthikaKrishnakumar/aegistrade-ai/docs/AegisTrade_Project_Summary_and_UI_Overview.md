# AegisTrade AI
Project summary and frontend overview

**Read this first • Source version 0.19.0 • 11 November 2026**

**Current rules — v0.19.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.
**Current memory update — v0.19:** Company materiality windows and bounded evidence packing are implemented. Completed portfolios can draft pending process lessons for human review, freeze and version-pinned retrieval into a NEW C2 run. See the final “Version 0.19” section for the exact UI sequence and development-replay/date rules. No improved profit result is claimed before testing.


**Demo history reset — 11 November 2026:** Existing portfolio/research/backtest history and simulated broker ledgers/approvals were cleared at the user's request. Earlier run IDs and numerical examples below describe archived rehearsals; they are not available in the active saved-run lists. Start a new run for your demo. Recoverable originals are under data/history_archives/20261111_105802/. Market data, company evidence, policy/model caches, reviewed lessons and private configuration were preserved.

This introduction explains the purpose of the project and its eight frontend workspaces. Read AegisTrade_Detailed_Design_and_Demo_Guide.docx afterwards for setup commands, architecture, detailed controls and demonstration instructions.

## 1. What does this project do?

AegisTrade studies how AI-assisted research and trading rules work together in a simulated stock portfolio. You choose a historical period and starting capital. The system screens a 20-stock research subset of the Nifty 50, researches eligible candidates using information available at the historical decision time, simulates trades and reports how the portfolio performed.

For example, you can ask: “Starting with ₹200,000, what would happen over this period if the project selected stocks, researched entries, reviewed holdings and applied its exit rules?” The result includes cash, trades, portfolio value, returns, drawdown and any holdings still open at the end.

**It uses simulated money and has no live exchange or broker connection.** Profitability is a research question to measure; adding AI does not by itself establish a trading advantage.

### The main C2 historical workflow

**Choose dates and capital → screen stocks → complete dated C2 research → validate and size an entry → simulate a later-open fill → review holdings and apply exits → report results.**

C2 has three AI specialists: the market specialist interprets technical and company evidence; the strategy specialist explains the permitted route and recommends ENTER, HOLD or EXIT for the appropriate purpose; the critic checks the reasoning and evidence. Code calculates indicators, quantities, costs and risk limits. The AI cannot change those rules.

The portfolio checks dated financial filings and issuer announcements/releases. Evidence published after the decision cutoff is excluded. Missing evidence can block an entry. This is bounded company research, not a complete independent-news or valuation service.

Protective stops and strategy exits operate in code. Scheduled C2 reviews can also recommend exiting a holding. **The end date does not force a sale:** remaining holdings stay open in the report and contribute their marked value and unrealized profit/loss.

### Understand the three operating paths

| Path | Purpose | Approval and model calls |
|---|---|---|
| C2 historical portfolio | Main end-to-end research and portfolio simulation | You approve historical rules and external-inference allowance upfront; simulated fills then proceed automatically. C2 researches entries and scheduled holding reviews. |
| Technical-only baseline | Compare trading rules without generative research | Zero generation calls. Useful as the reference against which C2 is evaluated. |
| Supervised single action | Demonstrate a person controlling an exact simulated order | Complete C2 first, then explicitly approve, edit or reject that individual proposal. |

These paths answer different questions. A technical-only return is not a C2 return; the supervised single-order demo is not a full portfolio performance history.

## 2. What is each frontend workspace used for?

Use the visible **Workspace** selector to move between the eight screens. You do not need to visit every screen to run a C2 portfolio: Strategy Backtests coordinates that complete historical loop internally.

### Market Data — “What data are we using?”

Start here to inspect the active source, stock universe, available dates, coverage and dataset limitations. It explains how the frozen 20-stock subset was selected and allows you to activate the downloaded NSE dataset or export its OHLCV data. OHLCV means each session's opening, highest, lowest and closing price, plus trading volume.

**Use it to:** confirm that the correct dataset is active before interpreting charts or running simulations. Downloaded data is not a live market feed. This screen makes no paid model calls.

### Overview — “What does one stock's market evidence look like?”

Choose an instrument and history window to view prices, indicator overlays and the current code-defined market regime/strategy candidate. A regime describes conditions such as trend, range or breakout.

**Use it to:** understand the technical evidence behind a possible candidate. A chart or strategy candidate is not completed C2 research and does not authorize an order.

### Strategy Backtests — “How did the complete portfolio perform?”

This is the main screen for your end-to-end historical simulation. Select **C2 historical portfolio**, enter capital, dates, risk and trading costs, then choose the total model-request allowance and holding-review interval. Approve the historical rules and paid requests before starting.

New runs enable a trailing stop at2×entry-signal ATR14. It follows the highest completed closing price since entry, never moves down and applies from the next session. Inspect Exit rules, profit target and stop adjustments and SELL_TRAILING_STOP events. Code strategy exits and scheduled C2 exits remain active. Old saved runs retain their original policy and need a new run to use trailing. This feature adds no model calls and does not guarantee profit.

The job runs in the background. Refresh its progress, inspect research decisions, pause/resume and reopen a saved run. Results include the equity curve, trade ledger, C2 research traces, realized/unrealized P&L, open holdings and pending intentions. After completion, compare with the technical ROUTER reference and passive benchmark. Select **Technical-only baseline** when you want the separate zero-generation comparison.

**Use it to:** evaluate the portfolio consequences of C2-assisted decisions. Historical fills appear in this screen's ledger. Model charges are reported separately in USD; INR trading returns include trading fees/slippage and exclude those model charges.

### AI Agent Experiments — “Why did the AI reach this decision?”

Inspect a small number of historical research cases in detail. C0 is a fixed code reference; C1 is one tool-using agent; C2 is the three-specialist team. C2 is the project's main agentic workflow; the other configurations support evaluation rather than requiring you to maintain several applications.

The company-research controls prepare or inspect dated filings and issuer releases. A research result shows specialist hand-offs, citations, company/event assessment, critic verdict, errors and model usage. An eligible ENTRY case can be handed to Supervised Trading.

**Use it to:** study the reasoning and source evidence for one case, prepare company evidence or demonstrate the agent workflow. The selected-date preview button checks stock selection without paid calls. This screen does not itself submit trading orders.

### Supervised Trading — “Should this exact proposed action be approved?”

A passing C2 ENTRY case is required first. Code creates a risk-sized BUY proposal. You inspect the exact symbol, quantity, prices, stop, explanation, company sources and approval hash, then approve, edit or reject. An edit requires fresh checks and another approval. A successful action is recorded only by the local simulated broker.

**Use it to:** demonstrate human control, stale-data rejection, emergency control and recovery. Reference capital sizes one proposal; this screen is separate from the historical portfolio ledger. Its individual approval requirement does not add a human pause to every historical replay fill.

### Policy Knowledge — “Which project rule supports the explanation?”

Search the project's policy/strategy knowledge and inspect retrieved passages, source IDs and dates. RAG means retrieving relevant source material before generating an evidence-grounded answer. Here you can inspect retrieval itself; C2 uses those passages when reasoning.

**Use it to:** understand risk/strategy rules and check cited policy evidence. The policy corpus is distinct from the dated company-filings packs. Searching this screen does not make a paid OpenRouter generation call.

### Learning & Lessons — “What lessons are allowed to influence research?”

Inspect candidate lessons, accept or reject them with reasons, and freeze the reviewed playbook before evaluation. Lesson memory stays off and unavailable until accepted lessons have been frozen; the first C2 run does not need any lessons. A lesson is guidance about an observed reasoning failure, not permission to change trading risk rules. Frozen relevant lessons can be enabled in AI Agent Experiments; they are not automatically added to every historical portfolio run.

**Use it to:** demonstrate controlled memory and human-reviewed improvement. Accepting a plausible lesson does not prove that it helps unseen cases; that benefit needs comparison tests.

### Broker Audit — “What happened to a human-reviewed simulated order?”

Inspect approval decisions, simulated broker outcomes and timeout/reconciliation records. Match an event to the exact proposal and request identity.

**Use it to:** verify the supervised single-action workflow. **C2 historical portfolio fills are recorded in Strategy Backtests, not this separate broker audit.**

## 3. A simple first-use route

1. **Market Data:** confirm the active dataset, dates and limitations.
2. **Overview:** inspect one stock to understand the charts and candidate route.
3. **Strategy Backtests:** choose C2 historical portfolio and a short date window. Set capital and request allowance; provide reviewer authentication and the two approvals. Start, refresh progress and inspect decisions/results.
4. **AI Agent Experiments + Policy Knowledge:** examine one case and its company/policy sources to understand how the agents reason.
5. **Supervised Trading → Broker Audit:** separately demonstrate exact human approval and confirm the simulated action's audit record.
6. **Learning & Lessons:** explore reviewed memory after understanding the main workflow.

The sidebar's **reviewer token** authenticates privileged actions. It is different from the OpenRouter API key, which stays in private server configuration. Do not paste the provider key into the reviewer-token box or display private configuration in a demo.

C2 makes paid OpenRouter calls. A research case normally uses six requests, with an eight-request ceiling. The historical job's allowance defaults to48 requests across its cases. It pauses before exceeding the allowance; an explicit resume can add more. Missing evidence blocks a case, and provider errors pause the job. A paused run is not a completed result for the entire chosen period.

## 4. How to read the results

| Term | Plain-language meaning |
|---|---|
| Ending equity | Cash plus the marked value of unsold shares. |
| Realized P&L | Profit/loss from positions actually sold, after their trading costs. |
| Unrealized P&L | Profit/loss in holdings still open at the end, based on the last available mark and entry cost. |
| Drawdown | How far portfolio value fell from an earlier peak. |
| Benchmark | A reference portfolio used for comparison; here a passive equal-weight buy-and-hold portfolio. |
| BLOCKED | A required evidence, critic or code check did not permit the action. It is not a fill. |
| COMPLETED_WITH_GAPS | The period finished, but some research/fill opportunities were blocked or unavailable. Inspect them before interpreting returns. |

A positive total return alone does not establish that C2 adds value. Compare risk, the technical baseline, source coverage and model costs. The current dataset uses today's constituents and unadjusted prices, so survivorship bias and unresolved corporate actions remain important limits on financial conclusions.

Next reading: **AegisTrade_Detailed_Design_and_Demo_Guide.docx**, especially the operating-path explanation, C2 portfolio lifecycle and UI walkthrough. Use the separate viva handbook later to practise explaining the design.

## 5. ChatGPT Plus demo route

The current local configuration uses codex_cli, so the three specialists make real model calls through your existing ChatGPT-authenticated Codex CLI. OpenRouter remains available by configuration and restart. Plus usage limits still apply; CLI invocation counts are not internal provider request counts or guaranteed dollar/token ceilings. The verified HINDUNILVR-2023-03-31 case is saved in UI research history. Use AegisTrade_ChatGPT_Plus_Full_UI_Demo_Runbook.docx for account setup, exact UI steps, a short historical portfolio, approval and switching providers. No Claude CLI adapter is implemented.

The C2 decision table now distinguishes formatting failures from missing evidence or provider access. Selecting a failed record shows the exact field-level reason. Missing or review-required entry evidence blocks early, saving additional specialist calls. Saved jobs keep their prompt version; start a new short run after a prompt change.


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
