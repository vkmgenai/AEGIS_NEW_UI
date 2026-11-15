# AegisTrade AI — simplified UI demonstration guide

Version 0.31 · 14 November 2026 · simulation only

## What to demonstrate

AegisTrade compares a zero-generation technical baseline (C0), a controlled single-agent baseline (C1), and the specialist/critic agent workflow (C2). It grounds research in evidence available by the historical decision date, validates typed outputs, keeps financial arithmetic in Python, and records decisions and failures. It never connects to a live broker.

The portfolio screen fixes risk settings so that C0 and C2 use the same reproducible policy rather than hand-tuned settings.

## Before the demo

1. From the repository root, run `bash scripts/start_unix.sh`.
2. Wait for FastAPI on `http://127.0.0.1:8000` and Streamlit on `http://127.0.0.1:8501`.
3. Open `http://127.0.0.1:8000/health` for the API check. The bare API root may return `Not Found`; that is not a failure.
4. Confirm `AEGIS_REVIEWER_TOKEN` exists in `.env`, then restart the app. It authenticates write actions internally and is not entered or displayed in the UI.
5. Confirm **Market Data** shows the intended frozen universe and completed date coverage.
6. Confirm at least one inference adapter is ready. All three remain available:
   - **ChatGPT (Codex CLI login)** uses the signed-in Codex CLI/ChatGPT allowance.
   - **OpenRouter (API key)** uses `OPENROUTER_API_KEY` and provider credits.
   - **Claude (Claude CLI login)** uses the signed-in Claude CLI allowance.
7. Use a short, already-covered period for a live C2 demo. Long runs can exhaust account or examination time.

## Recommended 12–15 minute walkthrough

### 1. Overview and provenance

Open **Overview**, select a stock, and show OHLCV, EMA/RSI indicators, regime and the code-approved candidate. Indicators create candidates; they do not authorize a trade.

Open **Policy Knowledge** and show the corpus fingerprint, dated passages and source IDs. Evidence after a historical cutoff is excluded and missing evidence is reported rather than invented.

### 2. C0 technical portfolio

Open **Strategy Backtests**, choose **C0 Technical baseline**, use capital `₹200,000`, and choose a covered three-month window with at least 45 market sessions. Check the rule approval, expand **Fixed, reproducible simulation policy**, and run.

Show the equity curve, return, drawdown, benchmark, selection audit, trading ledger, open holdings and zero model calls. This is C0: deterministic routing and portfolio mechanics without GenAI.

### 3. C2 agentic portfolio

Choose **C2 historical portfolio**. In **Run AI agents using**, select ChatGPT, OpenRouter or Claude and press **Use this provider**. All three use the same typed AegisTrade contract; there is no automatic provider fallback.

Use the same capital and dates as C0. Use inference allowance `48` for a small rehearsal, choose **No portfolio lessons** for a clean memory-off comparison, and check inference consent and replay-rule approval.

Start the run. Show live progress, current date/stage, saved run ID, and refresh/pause/resume controls. After completion, open one trace and show the shortlist, dated RAG/web evidence, market specialist, strategy specialist, independent critic, deterministic validation, later-open fill, and holding-review/exit reason.

Compare C2 with C0. Do not claim that a short-window return proves profitability; the capstone claim concerns grounding, auditability, policy compliance and safety versus inference cost.

### 4. Fair C0/C1/C2 experiment

Open **AI Agent Experiments**. Pick one stock and locked historical period. Use the same provider, case, tools and bounded budget for C1 and C2. Run **ALL** or open a retained experiment. Show C0 zero-call output, C1 single-agent trace, C2 specialist/critic trace, aligned ledgers/equity, latency, calls, failures and citations. C1 is an evaluation baseline, not another portfolio workflow.

The primary UI automatically selects eligible entry cases; there is no separate BUY/HOLD/SELL scenario control. C2 determines whether a grounded actionable recommendation exists, and only then displays the human review interrupt. Historical holding reviews and exits remain part of the C2 portfolio engine and saved trace rather than a duplicate experiment form.

**Reading the results.** The first table is the capability-oriented architecture comparison. C0 is the reference by construction, so its research columns read N/A. For C1 and C2, point out three things: how many cases have grounded company evidence, whether a block is a *safe evidence abstention* (the agents found a cited adverse item and stopped) or a *hard model/policy failure* (for example a route that conflicts with the code), and that Route validation counts only decided cases, with abstentions shown beside it. Open **Technical audit metrics** to show the raw task-success, error, call and latency figures. None of these columns is a profit result.

### 5. Human evidence override, memory and evaluation

For the optional intervention study, open **Strategy Backtests → Optional evaluation controls** and enable **HUMAN_EVIDENCE_OVERRIDE study** before starting a fresh C2 run. The run pauses only for an evidence-insufficient positive technical BUY or holding SELL with no hard adverse/safety failure. Record `KEEP_BLOCKED` or `APPROVE_OVERRIDE` with reviewer and rationale. Approved BUYs are linked through later reviews and exit; stop, trailing-stop and target exits remain automatic. Show the separate lifecycle ledger and explain that the original C2 block is preserved.

Strategy Backtests first shows two large tiles. Choose **C0/C2 Portfolio Backtests** for the active-universe simulation and human-override demonstration. Choose **Single-stock C0/C2 Comparison** for a focused same-stock ledger, equity curve and P&L comparison. Use **← Back to Strategy Backtests** to return to the tile page; this navigation does not delete or restart a run.

An approved BUY is not immediately a successful lesson. Its outcome remains `INCONCLUSIVE_OPEN` until the linked position exits. A later discretionary C2 SELL recommendation pauses for `KEEP_HOLDING` or `APPROVE_EXIT`; an evidence-blocked SELL can also pause for review. Deterministic stop, trailing-stop and take-profit exits do not wait for approval. After exit, the ledger reports `SUPPORTED` only when realized P&L is positive and `NOT_SUPPORTED` otherwise; either label is merely eligible for later human lesson review. It is never accepted into memory automatically. The reviewer token is local authorization for writing this audit decision; it is not sent to an LLM.

While the dashboard is open, the notification bell refreshes every 15 seconds. When a C2 checkpoint needs a decision, the bell shows a count and a one-time toast appears. Open the bell, identify the stock/action/date, and select **Open review**. The UI switches to Strategy Backtests and loads the exact saved run; inspect the evidence there before deciding. The notification disappears after the decision is durably recorded and the run leaves `PAUSED_HUMAN_OVERRIDE`. This is an in-app notification only, so it does not send email or operating-system alerts when the dashboard is closed.

Open **Learning & Lessons → Human decision outcomes** to show the separate decision ledger and fixed 10-session outcome. State that the outcome is review evidence, not causal proof; an eligible row can only inform a conditional lesson after human review and is never learned automatically. Then show that lessons remain drafts until review and freezing. Open **Capstone Evaluation** for retained E1–E4 runs, manifests and questionnaires.

## Fixed portfolio policy

| Setting | Fixed value |
|---|---:|
| Strategy mode | ROUTER |
| Normal / breakout risk | 1% / 0.5% |
| Normal initial/trailing stop | 2× ATR14 |
| Breakout initial/trailing stop | 2.5× ATR14 |
| Breakout trail activation | 1R |
| Net take-profit target | 8% |
| Slippage | 10 bps per transaction |
| C2 research pool | 3 candidates per session |
| Holding review | every 5 sessions |
| Recovery watch | 10 sessions, one confirmed retry |

The API and saved-run schema retain these values for reproducibility and backward-compatible viewing. They are not tuning controls in the final demo UI.

## Why the workspaces remain

| Workspace | Capstone evidence |
|---|---|
| Market Data | frozen universe, coverage and provenance |
| Overview | technical features and code-approved candidates |
| Strategy Backtests | C0/C2 replay, progress, ledger and P&L |
| AI Agent Experiments | fair C0/C1/C2 architecture comparison |
| Capstone Evaluation | retained E1–E4 evidence and human review status |
| Policy Knowledge | RAG sources, dates, IDs and fingerprints |
| Learning & Lessons | reviewed/frozen memory governance |

Each maps to a capstone minimum-bar requirement. Redundant C1 portfolio, newsletter-import and manual risk-tuning controls were removed from the primary demo flow.

## Safe fallback

If inference is unavailable, do not repeatedly retry. Open a retained completed run and demonstrate its manifest, traces, decisions and ledger. Run C0 live because it needs no model account. Clearly distinguish retained evidence from live execution.
