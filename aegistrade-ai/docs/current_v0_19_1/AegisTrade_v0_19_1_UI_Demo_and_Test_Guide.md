# AegisTrade AI — UI Demo and Test Guide

Version 0.19.1 • Prepared 11 November 2026 • Beginner-friendly rehearsal and exam guide

## 1. Goal and suggested order

Demonstrate that the project screens stocks, completes dated C2 research, validates it, simulates entries and exits, preserves unsold holdings, and explains every result. Also show reviewed memory and the separate exact-order human approval path. A valid demo is an auditable workflow; it does not require a positive return.

Read the Project Design and Orchestration document before the viva bank. For the UI, follow: prerequisites → policy/market screens → short C2 smoke test → three-month rehearsal → trace/exit/accounting review → supervised approval → evidence capture. Complete long simulations before the exam and show genuine saved results during the short presentation.

There is one recommended settings profile below. The smoke test and three-month rehearsal use the same rules and different date windows. The later comparison without lessons is an evaluation exercise, not a new strategy variant.

## 2. Prerequisites: check before consuming inference allowance

### A. Preserve running work

Inspect Strategy Backtests → C2 portfolio progress, resume and saved jobs. If another job is active, let it finish or request Pause C2 portfolio, then refresh until the worker is no longer active. A single-worker queue means a new job may wait behind existing work. Do not delete ledgers, restart a running job or begin several overlapping demos to solve a delay.

Documentation creation did not start, pause or resume any portfolio. Preparation-time job statuses may differ by the time you read this guide.

### B. Start or inspect the local application

| Address | What to check |
|---|---|
| http://127.0.0.1:8501 | Streamlit dashboard |
| http://127.0.0.1:8000/health | Version 0.19.1; compatible interface; backend and capabilities |
| http://127.0.0.1:8000/ | Local API landing page |
| http://127.0.0.1:8000/docs | Interactive endpoint documentation |

If the application is already healthy, use it. If stopped, open Terminal in the project folder and run:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
.venv/bin/python scripts/launch_local.py
```

This starts the existing installed environment without a new dependency installation. On a fresh machine that has not been bootstrapped, use `bash scripts/start_unix.sh` and complete its dependency/setup steps first. Keep the launcher terminal open. Stop it with Ctrl+C when idle; do not start duplicate copies on ports 8000/8501.

### C. Check the selected inference transport

Open AI Agent Experiments or inspect /health. Expect codex_cli, codex-default and ready status for the currently configured ChatGPT account. Version 0.19.1 should report structured specialist content support in inference metadata.

If authentication is unavailable, use the configured Codex executable in Terminal with `login status` and, when needed, `login`; complete supported ChatGPT browser sign-in. Do not change to an API-key login accidentally. This guide uses your existing ChatGPT-authenticated transport, not an OpenRouter paid key. Plan limits and service availability still apply.

No external inference occurs simply because you open a page, inspect a saved trace, review/freeze a portfolio lesson or search local policy RAG. Running a C2 case or resuming a job does consume inference allowance. Public-company evidence preparation may download archive data even though it makes no generation call.

### D. Enter the correct reviewer token

Open .env privately and find AEGIS_REVIEWER_TOKEN. Paste only its value in Reviewer token in the left sidebar and press Enter. This is not an OpenRouter API key, ChatGPT password or Codex login token. Do not display .env during the exam or put its contents in a screenshot.

If Save portfolio lesson review is disabled, the sidebar token must be entered and the review rationale needs at least five non-whitespace characters. Press Enter or click outside the text field to commit the edit. A nonempty but incorrect token can enable a button and still be rejected by the API; enter the configured value.

### E. Confirm real data is active

Select Market Data. Check NSEPYTHON, the 20-symbol universe and date coverage. The retained manifest requests November 2021–November 2026, with indicator warm-up. Actual bars determine available sessions. The persisted data/market_config.json activation overrides the fallback AEGIS_DATA_SOURCE environment value.

Use the existing dataset. Do not redownload five years immediately before the exam. If synthetic is actually active, use the UI's downloaded-data activation control after inspecting its provenance and accepting the displayed limitations. This is an explicit activation, not an automatic fallback.

### F. Confirm the frozen portfolio lessons

In Learning & Lessons, inspect the portfolio-memory section above the separate legacy experiment lessons. At preparation time all three process lessons were accepted, and a frozen three-lesson version existed with trained_through 29 December 2023. There is also a one-lesson version, so identify the intended version by count/date/hash.

Do not draft duplicates or freeze again merely to start a run. Existing frozen versions are reusable. If starting from an empty installation, draft from a completed source portfolio, review the dated source cases, save ACCEPT/REJECT with rationale, select accepted lessons and freeze once.

A rationale should explain your real reason. For the citation lesson: “I accept this because claims should match their exact source and reporting period, improving research accuracy without changing risk rules.” Do not claim to have verified every financial filing unless you actually did.

### G. Understand evidence preparation

The portfolio worker prepares the exact dated company pack before researching a selected candidate. To rehearse evidence manually, use AI Agent Experiments → Historical company research. Choose a known symbol and the actual decision date, inspect the cached pack, and deliberately prepare if missing. Check cutoff, source links, reporting period/units and bounded adverse-scan coverage.

Prepare/refresh before the target run where possible. Refreshing a pack can invalidate linked prior research and approvals. A missing pack or incomplete scan is not fixed by increasing model allowance. The system cannot invent absent historical news or assert a clear assessment from unreadable required evidence.

## 3. One settings profile for the demo

| UI field | Recommended demonstration value |
|---|---|
| Workspace | Strategy Backtests |
| Simulation engine | C2 historical portfolio |
| Initial capital | ₹300,000 of simulated money |
| Maximum risk per trade | 1.0% |
| Automatically screen and rank stocks | Enabled |
| Strategies to run | ROUTER |
| Fees | 10 basis points per transaction |
| Slippage | 10 basis points per transaction |
| Take-profit target | 8.0% net modeled holding return |
| Enable trailing stop | Checked |
| Trailing distance | 2.0 × entry-signal ATR14 |
| Review each holding every N market sessions | 5 |
| Frozen portfolio lesson version | The reviewed three-lesson version trained through 2023-12-29 |
| Mark as development replay if training overlaps dates | Unchecked for the March–May 2024 examples |
| Total inference allowance | 48 initial units |
| External-inference authorization | Check after reviewing allowance |
| Historical replay-rule approval | Check after reviewing settings |

Ten basis points means 0.10% on each modeled transaction. These are demo assumptions rather than a quote of your actual brokerage/tax schedule. Risk 1% is a planned stop-distance budget; it is not a guaranteed maximum realized loss. At most four holdings and a 20% per-name equity cap further constrain investment, so the full capital need not be deployed.

The 8% target is a reproducible current default, not a claimed optimum. It applies to a holding, not the total portfolio. Change one parameter at a time only in a separate labelled experiment after the workflow works.

Forty-eight inference units are an initial checkpoint budget, not an estimate that an entire quarter will finish. Normal complete C2 uses six units per researched case and reserves eight. Blocks may use fewer, corrections more. Scheduled holding reviews also consume units. Prior runs have needed more than 48 even for one month.

## 4. Short smoke test: prove the pipeline first

Use the profile above with Simulation start = 2024-03-11 and Simulation end = 2024-03-15. These dates are after the lesson cutoff and within the active cache. This five-session window is a practical diagnostic choice, not a profitable-period recommendation.

1. Select the frozen three-lesson version before submitting the form.
2. Set capital/risk/costs/exits, the smoke-test dates, allowance and five-session review frequency.
3. Read and tick both inference authorization and historical replay-rule approval.
4. Click Run historical portfolio simulation once. Record the run ID.
5. Progress and recorded usage now update automatically every five seconds while the job is active (dashboard update, 12 November 2026). Keep Refresh C2 progress for an immediate full-result refresh. The job is asynchronous; never start another run merely to refresh its display.
6. Inspect the status, completed/total sessions, current date/phase and inference usage. If QUEUED, check for an earlier active worker.
7. When complete, open C2 entry / holding-review decisions and traces. Inspect one ENTRY attempt, its company assessment and exact failure or ENTER reason.
8. Select a research record and click Load C2 portfolio research trace. Show the market/strategy/critic hand-offs, actual tool calls, citations, guard result and portfolio_memory manifest/lesson_ids.
9. Inspect the C2 ledger and open holdings. If a BUY exists, its fill date must be later than the researched close; verify its quantity and costs. It is acceptable for a new call to block a candidate or leave this short run without a fill.

The saved month-long example contains a MARUTI decision on 11 March and a buy on 12 March, plus an AXISBANK decision on 14 March and a buy on 15 March. This helps choose a useful inspection window, but the shorter run has different portfolio history and your selected settings/memory differ. It is not a promise of the same decisions, quantities or returns.

Pass criterion: a saved result or a correctly explained pause/block with retrievable evidence, valid budgets and no unsupported fill. A completely blocked smoke test warrants diagnosis before a long replay; it does not warrant switching off material-risk checks.

## 5. Three-month portfolio rehearsal

After the smoke test works, keep the same profile and create a separate run for 2024-03-01 through 2024-05-31. This is a three-calendar-month historical window containing 61 sessions in the currently cached dataset, verified during document preparation. The engine uses actual cached market sessions and marks holdings at the final available session. Starting on a Friday demonstrates post-gap entry review; the first fill need not happen on the first or second date.

Record the new run ID and selected memory version. Do not assume the new run continues the smoke test's holdings; each new run starts from its own initial capital. Keep the initial 48-unit checkpoint allowance, inspect results at pauses and deliberately extend it when needed. A full quarter may take substantial wall time and account allowance; complete it before the examination slot.

A budget pause occurs before another case would exceed the available reservation. A provider pause is different. Refresh before resuming, confirm the job is inactive/paused, and follow the appropriate procedure below. Repeatedly clicking Run creates independent portfolios rather than advancing the existing one.

The ending result should show:

- Actual covered sessions, terminal status and any evidence gaps.
- C2, same-settings technical reference and passive benchmark with their differing purposes.
- Cash, equity, realized and unrealized P&L and surviving holdings.
- Selection audit, research actions, ledger, exit policy and trailing-stop changes.
- Known inference units, remaining/charged allowance and unknown provider cost where applicable.

There is no requirement to sell every holding by 31 May. Read final holdings and marked P&L alongside realized results. A positive final equity change does not necessarily mean every closed trade won or all profit was realized.

## 6. How to diagnose and resume safely

| Status or message | Meaning | Next step |
|---|---|---|
| RUNNING | Worker is processing a session or research case | Refresh progress; avoid starting another job |
| QUEUED | Job awaits the single worker | Check the earlier active job |
| PAUSED_BUDGET | Insufficient allowance to reserve another case | Add a deliberate allowance, authorize resume and resume the same ID |
| PAUSED_PROVIDER / CODEX_OUTPUT_INVALID | Transport could not parse/validate a response | Inspect validation_stage/json_error in usage; version 0.19.1 uses typed specialist objects; do not assume a credit failure |
| CODEX_TIMEOUT | Invocation exceeded local wall-clock limit | Inspect timeout and connection/model behavior; resume deliberately after addressing it |
| CODEX_AUTH_REQUIRED | Supported ChatGPT CLI sign-in is not ready | Check the configured executable/login privately |
| CODEX_QUOTA | Account reports a usage/rate limit | Wait for or resolve the account allowance; adding local units cannot bypass it |
| BLOCKED / EVIDENCE | Research cannot support the action | Inspect dated scan, coverage and assessment; do not force ENTER |
| CRITIC_REJECTED | Evidence/policy support failed independent critique | Read the reason and cited sources; this is not a transport pause |
| Version/data/corpus mismatch on resume | Job would mix research conditions | Preserve the old result and create a compatible new run |
| COMPLETED_WITH_GAPS | Requested replay finished but some cases had gaps/blocks | Discuss coverage and decisions; do not label every case a clean success |

To resume: open the existing saved portfolio, enter the reviewer token, set Additional inference units on resume, tick the displayed resume authorization and click Resume C2 portfolio. If remaining allowance already covers another reservation, set added units to 0. Otherwise add a chosen increment, for example 48. A local allowance increase does not buy API credits or expand ChatGPT plan limits.

The earlier response-format-paused run used two of 48 units and could resume with zero added units after the correction. That is an example, not a command to resume every old job. Inspect the selected run's own current usage. Failed calls remain counted; a retry is a fresh attempt of the failed research case, not continuation inside a broken response.

## 7. Read the output in a useful order

1. Status and date coverage: is the result terminal or partial? A partial result is not a complete-quarter comparison.
2. Accounting: equity, cash, realized/unrealized P&L and open positions. Verify the identity rather than judging only the headline return.
3. Selection audit: was the stock eligible, selected, deferred or excluded by code?
4. Research table: distinguish ENTER, HOLD, EXIT, BLOCKED, DEFERRED_REVIEW, ENTRY_CANCELLED and PROVIDER_FAILURE.
5. Individual trace: check the actual dated company evidence, policy citations, specialist responses, critic and final guard.
6. Ledger and stop adjustments: identify fill date, fee, realized exit reason and trailing stop's effective next session.
7. Memory: inspect the pinned hash, trained_through, evaluation scope and actual selected IDs. Optional retrieval may return fewer than three lessons to preserve context space.
8. Comparisons: examine exposure, cash and drawdown alongside return. C2 may miss winners or avoid losses; either is possible.

HOLD means keeping existing shares after a review; it is neither a new BUY nor an error by itself. A BLOCKED entry creates no position. A final holding is not necessarily an overdue exit: the exit rules may not have fired before the window ended.

## 8. Genuine saved example for demonstration continuity

Open saved C2 portfolio da8d6838ad194143bd374086a890b364. Its requested period is 1–31 March 2024, actual final bar 28 March, starting capital ₹300,000 and no portfolio memory. It used risk 1%, fee 5 bps, slippage 10 bps, a 6% target, ATR trail 2× and reviews every five sessions. Therefore it is not an exact replay of this guide's 10-bps-fee, 8%-target profile.

| Saved evidence | Recorded value |
|---|---|
| Status | COMPLETED_WITH_GAPS |
| Inference usage | 101 typed-specialist CLI invocations; final local allowance 144 |
| Ending equity | ₹301,578.23, approximately +0.526% |
| Technical reference ending equity | ₹299,480.43, approximately −0.173% |
| Entries | Four BUY events |
| Profit exit | MARUTI, 22 March 2024, SELL_TAKE_PROFIT |
| Stop exit | INFY, 26 March 2024, SELL_STOP |
| Holdings left at end | Two |
| Evidence gaps | 32 BLOCKED decisions; inspect reasons |

Show a dated ENTRY trace, the take-profit exit, the losing stop exit and the final holdings. This demonstrates actual successful typed CLI responses and complete accounting after the format correction. It does not establish a general strategy edge, and because memory was off it cannot establish lesson benefit.

Do not overwrite or clear this saved result to make the presentation look cleaner. Explain unfavorable outcomes and missing coverage honestly.

## 9. Demonstrate the separate per-order human approval

This is a separate demonstration after the portfolio walkthrough. A portfolio research record is not automatically a linked AI Agent Experiments run in the supervised UI.

1. Open AI Agent Experiments. Select C2 and one case, automatic ranking, output cap 4800, and a narrow dated window with eligible candidates. A useful rehearsal starting point is 11 March 2024, where a prior monthly portfolio researched MARUTI; an automatically selected experiment can differ. Confirm the shortlisted date/symbol before authorizing inference.
2. Keep the legacy experiment lesson option off unless that separate playbook has been reviewed and frozen. The portfolio playbook selector is not the legacy experiment memory switch.
3. Enter the reviewer token and authorize the inference request. Click Run AI experiment once and inspect real model/tool traces. If it blocks, explain the reason and use a separately prepared passing current case; do not bypass the gate.
4. For a passing C2 ENTRY case, select Use this C2 case in Supervised Trading. In Supervised Trading, inspect the linked research and reference capital.
5. Click Prepare researched order for human review. Show that the research explanation and citations are already present before approval.
6. Inspect the exact order and payload hash. First demonstrate reject if time permits. For edit, change an allowed quantity, submit the edit and show that another approval is required after revalidation.
7. Approve only the exact displayed simulated payload. Final freshness, quote deviation, expiry, risk and research checks can still reject it. A historical signal does not provide a current live quote; use the application's explicit simulated snapshot flow.
8. Open Broker Audit to inspect simulated approval/submission/reconciliation evidence. The portfolio's historical ledger and this broker audit are distinct stores.

Complete a passing current supervised case during rehearsal if you need it for the exam. Do not promise that a new generation call will pass simply because an earlier case did.

## 10. Fair test of memory after the demonstration

Create two separate current-version C2 runs with identical data, dates, capital, risk, costs, exits, backend/model and budgets: one with No portfolio lessons and one with the same frozen three-lesson version. Choose later dates than 29 December 2023 and prefer dates not used to tune the rules. Keep all other settings fixed and retain both results, including unfavorable ones.

Report decision quality, block categories, source/citation correctness, drawdown, invested exposure, turnover, fees, inference units and latency as well as return. The code's LATER_PERIOD_EVALUATION label is a temporal safeguard, not proof of statistical independence or superiority.

Do not compare an old-code run against a new-code memory run and attribute every difference to lessons. Likewise, the March saved example's different fee and target settings prevent it being an exact control for this guide's standard profile.

## 11. Fifteen-minute examination script

| Time | Action and explanation |
|---|---|
| 0–2 minutes | Explain purpose, two signature challenges, simulation scope and architecture diagram |
| 2–4 minutes | Show active data, date cutoff, one regime/route and a local policy query |
| 4–8 minutes | Open a genuine completed C2 portfolio; show research hand-offs, ledger, target/stop exits and unsold holdings |
| 8–10 minutes | Show accepted lesson version, source cutoff, selection and actual trace IDs; distinguish retrieval from fine-tuning |
| 10–13 minutes | Show a prepared passing supervised proposal, exact approval/edit boundary and simulated audit |
| 13–15 minutes | Explain tests, actual example versus general claims, limitations and team contributions |

An optional short live C2 request demonstrates connectivity if time/allowance permits. Clearly label it live and show saved evidence separately. Do not start a full three-month inference job expecting it to finish inside 15 minutes.

## 12. Evidence checklist to save after rehearsal

Save the application version/backend, dataset manifest/hash, selected settings, run IDs and memory version/hash. Capture the architecture diagram; one genuine tool-request/observation/final-response sequence; a cited assessment; a correctly explained block; one BUY; one exit; one remaining holding; the equity/P&L table; and the exact human approval/audit screen.

Record failed requests and pauses as part of the evidence. Keep model cost marked unknown where the provider does not report it. Review screenshots for secrets before sharing. Use the fresh Viva Questions and Answers document to practise explaining the evidence rather than memorizing unsupported success claims.
