# AegisTrade AI — simplified UI demonstration guide

Version 0.35 · 17 November 2026 · simulation only

## What to demonstrate

AegisTrade compares a zero-generation technical baseline (C0), a controlled single-agent baseline (C1), and the specialist/critic agent workflow (C2). It grounds research in evidence available by the historical decision date, validates typed outputs, keeps financial arithmetic in Python, and records decisions and failures. It never connects to a live broker.

The portfolio screen fixes risk settings so that C0 and C2 use the same reproducible policy rather than hand-tuned settings.

## Which interface to open

- **Current full UI:** `http://127.0.0.1:8501`
- **Redesign proposal for review:** `http://127.0.0.1:8504`
- **Preview API:** `http://127.0.0.1:8002`

Start the redesign later with `bash scripts/start_redesign_preview.sh`. It is a separate question-led demo shell and does not replace the current UI until explicitly approved.

The redesign uses a permanently expanded navy sidebar with high-contrast white navigation and solid blue workspace tiles. If a browser retains an older Streamlit stylesheet, hard-refresh the page once after restarting the preview.

In the redesign, demonstrate only four primary tiles in this order: **Data & Stock → C2 Portfolio → Agent Comparison → Evaluation Evidence**. Use **Knowledge & Lessons** only when asked about RAG or memory. The home attention cards show pending human intervention, paused portfolios and current architecture evidence.

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

### 2. C2 agentic portfolio

Open **Strategy Backtests**. In **Run AI agents using**, select ChatGPT, OpenRouter or Claude and press **Use this provider**. All three use the same typed AegisTrade contract; there is no automatic provider fallback.

Use capital `₹300,000` and a covered three-month window with at least 45 market sessions. Use inference allowance `48` for a small rehearsal, choose **No portfolio lessons** for a clean memory-off run, and check inference consent and replay-rule approval.

Start the run. Show live progress, current date/stage, saved run ID, and refresh/pause/resume controls. After completion, open one trace and show the shortlist, dated RAG/web evidence, market specialist, strategy specialist, independent critic, deterministic validation, later-open fill, and holding-review/exit reason.

Inspect C2 return, drawdown, research ledger and human checkpoints. Do not claim that a short-window return proves profitability; the capstone claim concerns grounding, auditability, policy compliance and safety versus inference cost.

### 3. Fair C1/C2 agent experiment

Open **AI Agent Experiments**. Pick a locked historical period with at least 20 later sessions. Use the same provider, cases, evidence, available tool capabilities and bounded budget for C1 and C2. Run **ALL** or open a retained experiment. Show the C1 single-agent trace, C2 specialist/critic trace, latency, calls, failures and citations. Expand C0 only to explain the deterministic reference.

For the prepared demonstration, open any repeat ID: `1eac0a24d4e04453ab9bbab9e7c935da`, `e26275b0e9f34b22b7a7315cbbea0475`, or `51ab85a7df0b4abf94fed845595adc4f`. Explain that all three used identical IDEA/LT/HINDALCO cases. C2 selected LT consistently; C1 selected it in two of three repeats. These are development results, not held-out proof.

Do not start a new final held-out experiment merely because the preview changed. First approve and freeze the UI/code, generate the new versioned review set, complete its independent review, and then run the resumable E1–E4 plan. The old 102 templates remain retained but are not the new final review set.

The experiment automatically selects eligible entry cases; there is no separate BUY/HOLD/SELL scenario control. It runs to completion without approval pauses. Human evidence override belongs only to the checkpointed C2 portfolio, so research calls are not duplicated.

**Reading the results.** The first table compares C1 and C2. Point out grounded company evidence, safe evidence abstentions, hard model/policy failures and decision coverage. Open **Technical audit metrics** for raw calls, latency and errors. Then show **Secondary standardized forward outcome**: fixed ₹100,000 notional, next-session open to the 20th later-session close, modeled fees/slippage, and cash for non-entry. Explain that it is a financial interpretation of each decision, not the primary architecture score or a portfolio backtest.

### 4. Human evidence override, memory and evaluation

For the optional intervention study, open **Strategy Backtests → Optional evaluation controls** and enable **HUMAN_EVIDENCE_OVERRIDE study** before starting a fresh C2 run. The run pauses only for an evidence-insufficient positive technical BUY or holding SELL with no hard adverse/safety failure. Record `KEEP_BLOCKED` or `APPROVE_OVERRIDE` with reviewer and rationale. Approved BUYs are linked through later reviews and exit; stop, trailing-stop and target exits remain automatic. Show the separate lifecycle ledger and explain that the original C2 block is preserved.

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
| Strategy Backtests | end-to-end C2 portfolio, progress, human override, ledger and P&L |
| AI Agent Experiments | fair C1 single-agent versus C2 multi-agent comparison; C0 reference |
| Capstone Evaluation | retained E1–E4 evidence and human review status |
| Policy Knowledge | RAG sources, dates, IDs and fingerprints |
| Learning & Lessons | reviewed/frozen memory governance |

Each maps to a capstone minimum-bar requirement. Redundant C1 portfolio, newsletter-import and manual risk-tuning controls were removed from the primary demo flow.

## Safe fallback

If inference is unavailable, do not repeatedly retry. Open a retained completed run and demonstrate its manifest, traces, decisions and ledger. Run C0 live because it needs no model account. Clearly distinguish retained evidence from live execution.
