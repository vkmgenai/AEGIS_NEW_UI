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

### 5. Human control, memory and evaluation

In **AI Agent Experiments**, select a completed grounded C2 recommendation. Show that its status is `WAITING_HUMAN`, inspect its RAG citations and company evidence, enter reviewer name/initials and record APPROVE or REJECT with a rationale. Explain that this uses the already-completed C2 result and makes no extra research calls. HOLD, blocked and failed cases correctly show no approval control.

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
