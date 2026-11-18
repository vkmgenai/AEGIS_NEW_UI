# AegisTrade AI
Full UI demonstration using ChatGPT Plus and Codex CLI

**Source 0.19.0 • Checked 11 November 2026 • Local Mac demonstration**

**Current rules — v0.19.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.
**Current memory update — v0.19:** Company materiality windows and bounded evidence packing are implemented. Completed portfolios can draft pending process lessons for human review, freeze and version-pinned retrieval into a NEW C2 run. See the final “Version 0.19” section for the exact UI sequence and development-replay/date rules. No improved profit result is claimed before testing.


**Demo history reset — 11 November 2026:** Existing portfolio/research/backtest history and simulated broker ledgers/approvals were cleared at the user's request. Earlier run IDs and numerical examples below describe archived rehearsals; they are not available in the active saved-run lists. Start a new run for your demo. Recoverable originals are under data/history_archives/20261111_105802/. Market data, company evidence, policy/model caches, reviewed lessons and private configuration were preserved.

Read this document before the Detailed Design and Demo Guide. It gives one practical demonstration route using your existing ChatGPT sign-in, with OpenRouter available later through configuration. The three-person team remains professor-approved.

## 1. What changed and which account is used?

AegisTrade now supports two inference transports: **codex_cli** and **openrouter**. Your private local .env currently selects codex_cli. OpenRouter remains the default when no backend is configured. Claude CLI is not implemented in this release.

The Codex backend invokes the official Codex CLI non-interactively using your existing ChatGPT login. Plus includes Codex access, subject to your account's current usage allowance. It does not provide OpenRouter credits. Check remaining usage before rehearsal; having Plus does not guarantee an uninterrupted large simulation. See [OpenAI's plan guidance](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan).

This is a local CLI integration. The browser talks to FastAPI; FastAPI starts the installed CLI on this Mac. You are not pasting ChatGPT browser cookies, extracting OAuth tokens, or calling an undocumented ChatGPT API. Keep authentication in Codex's supported credential store.

The same C2 supervisor, three specialists, MCP tools, historical cutoff, financial citations, critic, typed validation, sizing and approvals apply to both transports. Switching transport does not remove agentic behavior. Codex itself has native tools disabled; it returns structured requests for AegisTrade's declared virtual tools. AegisTrade validates those requests and executes the real MCP calls.

[[FIGURE:backend]]

Figure 1. AegisTrade owns the evidence and decision loop. Codex receives only the current specialist conversation and returned observations; it does not browse the repo or execute its own MCP tools. Local retrieval and execution remain separate from inference.

## 2. What has actually been verified?

A genuine C2 run completed on this machine using ChatGPT-authenticated Codex, actual NSE bars, actual stdio MCP and neural RAG:

| Item | Recorded result |
|---|---|
| Historical case | HINDUNILVR — 31 March 2023 |
| Saved research run ID | 290874d24eeb498b868949c2796b3424 |
| Configuration | C2; three specialists; no frozen memory |
| CLI invocations | 7, including a correction; normal target is 6 |
| MCP tool calls | 7 |
| Code guard and completed-research gate | Both passed |
| Recorded latency | Approximately 66 seconds for this run; future timing varies |
| Tokens reported by CLI | 59,069 input plus output tokens in total; this is not a billing estimate |
| Per-run USD cost | Unavailable; reported as unknown |
| Evidence file | reports/codex_c2_demo.json |

The result is saved in data/research_runs and can be loaded in the UI. It is real inference, unlike earlier reports explicitly labelled MOCKED. It verifies one research case, not investment profitability, all historical dates, or the final capstone experiment suite. Automated tests also exercise portfolio entries/exits, accounting, pauses, approval binding and provider switching with mocked inference.

A second genuine verification completed the two-session portfolio 2023-03-31 to 2023-04-03, job **714a9bdfbde04ad1a464424d4de5bd72**. It used existing real company archives only, 7 CLI invocations, and created a next-open BUY of 15 HINDUNILVR shares. One holding remained open; MARUTI was blocked for absent cached evidence, so status is COMPLETED_WITH_GAPS. The accounting identity error was below 0.000001 INR; no forced sale occurred. See reports/codex_c2_portfolio_demo.json. The UI can load this saved job; unlike this cache-only verification, the normal UI run can prepare additional missing public archives. This short window did not exercise a live model holding review or exit; automated contract tests cover those paths.

The configured model label is codex-default: the CLI chooses its available default. The current CLI JSON did not disclose a resolved model ID. Do not describe this as a pinned model experiment. For formal C0/C1/C2 comparisons, select one supported model explicitly in AEGIS_LLM_MODEL and keep it fixed; the capstone runner rejects the moving default for CLI comparisons.

## 3. Budget terms you will see

| Setting or result | OpenRouter | Codex CLI |
|---|---|---|
| One inference unit | One application HTTP generation request | One codex exec invocation |
| Normal C2 case | Usually 6 units | Usually 6 units |
| Per-case maximum | 8 units | 8 units |
| Response-token budget | Provider max_tokens sent per request; aggregate allocated output capped | Conciseness guidance and local response-size checks; no guaranteed provider output/reasoning cap |
| Actual usage | Provider-returned usage/cost if supplied | CLI-reported tokens; internal provider request count unknown; per-run USD charge unknown |
| Account limit | OpenRouter account access/credits | ChatGPT plan allowance |

The 4,800 response-token setting is not a total input-token cap. CLI reasoning and context can consume more allowance than the small final JSON suggests. Eight CLI invocations do not mean eight known internal provider requests. There is no automatic billing switch or silent fallback. If CLI access fails, research blocks and a historical job pauses as PAUSED_PROVIDER.

The existing API field consent_to_paid_calls is retained for compatibility; for Codex it means explicit permission to consume plan allowance. The UI uses provider-neutral wording.

## 4. Prepare before opening the UI

1. Open Terminal and change to the project directory:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
```

2. The CLI installed with your VS Code extension was detected and already reports ChatGPT sign-in. To check it privately:

```bash
CODEX_BIN='/Users/karthikakrishnakumar/.vscode/extensions/openai.chatgpt-26.1021.22027-darwin-arm64/bin/macos-aarch64/codex'
"$CODEX_BIN" --version
"$CODEX_BIN" login status
```

If login is required, run the following in your own Terminal and complete the browser flow with the Plus account:

```bash
"$CODEX_BIN" login
```

Do not put a ChatGPT password or token into .env. This backend deliberately requires ChatGPT login rather than API-key login. The extension path may change after an update; then update AEGIS_CODEX_BIN. A standard CLI installation on PATH can instead use that executable. See [official authentication instructions](https://learn.chatgpt.com/docs/auth).

3. In your editor, privately verify these non-secret settings in .env:

```text
AEGIS_LLM_BACKEND=codex_cli
AEGIS_LLM_MODEL=codex-default
AEGIS_CODEX_BIN=/Users/karthikakrishnakumar/.vscode/extensions/openai.chatgpt-26.1021.22027-darwin-arm64/bin/macos-aarch64/codex
AEGIS_CODEX_TIMEOUT_SECONDS=120
AEGIS_ENABLE_LLM_EXPERIMENTS=true
AEGIS_RETRIEVAL_MODE=neural
```

Keep the existing reviewer token and cached-data settings. Existing OpenRouter credentials are preserved but unused by codex_cli. Never show .env in the demo.

4. Stop the old launcher using Ctrl+C in its own Terminal if one is running. Start the current local services once:

```bash
bash scripts/start_unix.sh
```

Open http://127.0.0.1:8501. FastAPI documentation is at http://127.0.0.1:8000/docs. Source0.18.0 adds fresh entry review, adverse research and profit exits; health should show trailing_stop_supported:true. Compatible patch versions use interface contract1; a missing required feature needs one coordinated restart. Do not start multiple launchers on the same ports. This guide uses the local Mac launcher; a Docker container does not inherit host Codex authentication/executable automatically.

5. Enter only AEGIS_REVIEWER_TOKEN in the sidebar. The reviewer token authorizes local protected actions; it is different from the model account login.

6. Use a wide browser window and 100% zoom. Screens are selected using Workspace in the main content area, not only the sidebar.

## 5. Demo sequence and expected evidence

Rehearse once before presenting. Allow extra preparation time for public archive downloads and initial neural-model loading. During the presentation use already prepared data/evidence and the saved genuine example if a new run is unavailable; label saved results as saved.

| Order | Workspace | What you demonstrate |
|---|---|---|
| 1 | Market Data | Frozen NSE20 cache, available dates and provenance |
| 2 | Overview | Indicators, regime and code-permitted strategy |
| 3 | Policy Knowledge | Local neural retrieval and source authority |
| 4 | AI Agent Experiments | Real C2 inference, company filings, MCP and critic |
| 5 | Supervised Trading | Completed research before exact human approval |
| 6 | Broker Audit | Simulated submission, events and recovery evidence |
| 7 | Strategy Backtests | Full chronological C2 portfolio, exits and final holdings |
| 8 | Learning & Lessons | Human-reviewed memory process and current availability |

### Step A — Market Data

Select Market Data. Confirm the source is NSEPYTHON and 20 instruments are active. Inspect coverage/provenance and the downloadable OHLCV table. The local evaluation window is 8 November 2021 through 8 November 2026; the last trading session is 6 November 2026. Warm-up data begins earlier.

Explain that today's frozen constituents applied backwards create survivorship bias. The raw prices are not fully adjusted for corporate actions/dividends. These limitations restrict performance conclusions even when code and model calls work. Use the existing cache; downloading five years again is unnecessary for a rehearsal. Synthetic data is useful for tests but does not become real market evidence merely because C2 is enabled.

### Step B — Overview

Select Overview and HINDUNILVR. Show close prices, EMA20/EMA50, RSI14, ADX14 and ATR14. Explain that code computes the regime and permitted strategy. The Overview's latest label may differ from the historical March 2023 case; the saved case snapshot is the authoritative evidence for that date.

Say: “The LLM interprets evidence and checks the constrained explanation. It cannot change the strategy catalogue, size the order or authorize a broker action.”

### Step C — Policy Knowledge

Select Policy Knowledge. Search for “human approval and risk limits” or “holding review exit evidence”. Inspect passage IDs, project-policy versus external-background authority, corpus hash and the neural retrieval configuration. Retrieval uses local embeddings/reranking; this screen does not launch Codex generation. Retrieved policy IDs ground C2's explanation later.

### Step D — Prepare the dated company evidence

Select AI Agent Experiments. Verify Inference backend = codex_cli and Inference enabled and ready = Yes. Read the ChatGPT sign-in and allowance notice.

Expand Historical company research. Choose HINDUNILVR and 2023-03-31, then Inspect cached company evidence. The prepared pack should show SUFFICIENT coverage, dated filings/releases, CMP IDs, source links and limitations. The historical cutoff is 15:30 IST on the case date. Company coverage sufficiency is not a recommendation to buy.

Use Prepare historical company evidence only if the cache is missing. This may download public exchange PDFs, but makes no generation call. Avoid refreshing an existing pack after C2 succeeds: a changed source hash invalidates research and outstanding approval. Prepare all required evidence before a planned live model run.

### Step E — Preview and run one real C2 case

Use these settings in the experiment form:

| Control | Value |
|---|---|
| Experiment configuration | C2 |
| Research cases to test | 1 |
| Earliest case date | 2023-03-31 |
| Latest case date | 2023-03-31 |
| Response-token budget per case | 4800 |
| Research automatically ranked eligible stocks | Checked |
| Use frozen human-reviewed lessons | Off; currently unavailable until a nonempty reviewed playbook is frozen |
| Reference screening capital | ₹200,000 |

Click Preview selected-date stock shortlist (no model calls). This submits the form dates. Verify HINDUNILVR is the top eligible stock. Preview does not download company evidence or use plan allowance.

Read Plan and permissions. It should identify codex_cli, codex-default, read-only tools and an eight-unit ceiling. Select the consent checkbox only when ready, then click Run AI experiment once. Leave the page open. It can take several minutes; do not click again because a slow request may still be active.

Inspect results: guard_pass, critic acceptance, citations, company assessment, all three hand-offs and the trajectory. A normal flow is market tool request → observations → market JSON → strategy tool request → observations → strategy JSON → critic tool request → observations → critic JSON → code validation. A bounded correction may add another invocation. The LangGraph supervisor adds no model call of its own.

If you want to avoid another inference run, expand Load a previously saved agent experiment. Select the saved C2 run beginning 290874d2 and load it. It contains the genuine case in Section 2. Loading it consumes no plan allowance. Never relabel a saved or mocked result as a fresh live call.

### Step F — Demonstrate human approval after research

For a passing C2 case, select HINDUNILVR-2023-03-31 and click Use this C2 case in Supervised Trading. The workspace opens with the research linkage. Set reference capital to ₹200,000. Keep stale-quote and timeout injections off initially.

Click Prepare researched order for human review. The server reloads the saved case, current matching source hashes, technical snapshot and entry eligibility. It then sizes a whole-share order in code. Expect WAITING_HUMAN if every check passes; an earlier passing explanation alone cannot bypass this revalidation.

Inspect the company assessment, citations, exact payload, price, quantity, stop, expiry and approval hash. The person sees completed research before deciding. Pick approve and Submit reviewer decision to demonstrate one simulated submission. Approve promptly within the displayed expiry; expired approval requires a fresh proposal. No extra LLM call is needed to approve or submit.

For a separate review demonstration, prepare another proposal and choose edit. Change quantity; submitting the edit creates a revised payload/hash and requires a second explicit approval. Reject can be demonstrated on another proposal. These are separate example orders, not additional positions in the historical portfolio.

For a failure demonstration, prepare a new proposal with Inject stale quote checked. Explain the block. For reconciliation, prepare a new proposal with Inject timeout after simulated commit checked and approve: inspect that recovery reconciles rather than creating duplicate simulated orders. Never assume an errored browser request means no action occurred; inspect state and audit first.

### Step G — Broker Audit

Open Broker Audit. Inspect order events, payload hashes, simulated submissions and audit trail. Match a thread/order from Step F. Explain research validation, approval binding, final freshness/risk checks and idempotent recovery. This ledger is separate from the historical simulator's fills.

### Step H — Run the end-to-end C2 historical portfolio

Open Strategy Backtests. Select C2 historical portfolio. This is the main portfolio simulation: it starts from cash and advances through historical sessions. It conducts C2 research before entries, reviews existing holdings and records its own fills, equity and P&L.

For the smallest entry-to-valuation rehearsal choose 2023-03-31 through 2023-04-04, ₹200,000 capital, 1% risk, ROUTER, 10 bps fees, 10 bps slippage, total inference allowance 16 and review interval 5. Approve the historical rules and consent to external inference. Run once; record the job ID. Refresh C2 progress. The final session does not start research that cannot fill in the window, so this tiny run mainly demonstrates entry and open-holding valuation.

For an extended holding/exit demonstration create a NEW run for 2023-03-31 through 2023-04-12, review interval 2 and initial allowance 24. Prepare dated company packs for eligible candidates and holding-review dates where practical. The system normally reserves eight units before each research case. Other eligible stocks can consume allowance; the demo is not hard-coded to HINDUNILVR. A short interval can still pause, and public source availability can produce coverage gaps. Budget additional consent only if you choose to continue after inspecting progress.

For the verified saved tiny portfolio, open Saved C2 portfolio with ID beginning 714a9bdf; loading it consumes no plan allowance. For your own job use its saved selector or job ID, then Refresh C2 progress. Inspect:

1. Stock-selection audit: eligible/blocked candidates and code-ranked scores.
2. Research decisions: ENTER, HOLD, EXIT, BLOCKED or provider failures and linked case IDs.
3. Ledger: next-eligible-open entries; protective stops; strategy exits; accepted C2 EXIT fills; fees and prices.
4. Equity/metrics: cash plus marked holdings, return, drawdown, realized and unrealized P&L.
5. Open holdings: quantity, last mark/date and unrealized P&L. The end date does not force sale.
6. Usage: cli_invocations, known attempts, conservative reservations, tokens and unknown USD cost.

Exit behavior depends on the actual data and evidence; a chosen window may correctly contain only HOLD or open holdings. Do not force an EXIT or alter evidence to make the demo dramatic. Code initial2ATR stops, enabled trailing stops and strategy exits do not wait for C2; model-proposed exits require critic/code validation. An exit decided at the final close remains pending if no eligible open exists inside the period.

For new runs, keep Enable trailing stop checked and Trailing distance (× ATR14 at entry signal) at2.0. The stop follows the highest completed close since fill minus the fixed entry-signal ATR distance, only rises and is effective next session. Inspect Exit rules, profit target and stop adjustments, current/initial stops under open holdings and SELL_TRAILING_STOP in the ledger. Gaps may fill below the stop. No extra model calls are added. Old saved runs retain their original fixed-stop results and need a new run to use the changed policy; no end-date sale is forced. See the updated Portfolio Simulation Demo Step-by-Step guide for examples.

The historical-rules checkbox authorizes automatic historical fills, including exits, within those assumptions. This path has no per-fill human pause. The separate Supervised Trading example demonstrates exact per-order approval. Both require research before a new model-governed entry. Neither path places live orders.

If status is PAUSED_BUDGET, inspect the remaining units, choose an additional allowance and explicitly consent to Resume C2 portfolio. Zero additional allowance can resume a manually paused job if it already has enough. If PAUSED_PROVIDER, fix account/network/model access before consenting to resume. Do not change backend or model halfway through a job: resume rejects a changed identity. Data, prompt, corpus and simulator changes also require a new run.

A missing company pack or invalid assessment blocks that candidate/review, possibly ending COMPLETED_WITH_GAPS. A paused/incomplete job is not a full-window performance comparison. Technical ROUTER and passive reference results are presented for comparison when the C2 period completes. Actual model usage is separate from INR trading returns.

### Step I — Learning & Lessons

Open Learning & Lessons and show reviewed status and freeze information. Current lesson memory is disabled until a nonempty accepted playbook is frozen. That is expected. Explain development-only failure reflection → pending lesson → human accept/reject → frozen version → later retrieval. Do not create or freeze fabricated lessons for a demo or tune on held-out answers. A separately consented reflection can consume one inference unit; quota/login failures need an operational fix, not a paid lesson.

## 6. Recovery table

| Observation | Next action |
|---|---|
| CLI not found | Correct AEGIS_CODEX_BIN after installation/extension update; restart API |
| ChatGPT sign-in unavailable | Run codex login status/login in Terminal using the account; never paste auth into UI |
| CODEX_QUOTA | Check usage/reset status; wait or use account-supported additional allowance; preserve saved output |
| CODEX_TIMEOUT | Application time limit exceeded; refresh job status first. If RUNNING, continue waiting. If still paused, inspect the failure and explicitly resume once with0 additional units when sufficient existing allowance remains. The failed attempt stays counted. Repeated timeouts can justify a longer configured timeout and a safe-boundary restart; see the portfolio guide |
| CODEX_EXEC_FAILED | Inspect saved execution/connectivity diagnostics; this is distinct from a local timeout or a confirmed quota/login error |
| Model unavailable | Use a model offered to your CLI account, or codex-default for rehearsal; start a new job after switching |
| Guard/model validation fails | Inspect hand-offs/citations/company status; no order is eligible; do not bypass the research gate |
| No frozen playbook | Leave memory off; basic C2 does not require memory |
| Archive unavailable/insufficient | Prepare/inspect the exact symbol/date; use genuine available evidence or a previously verified case |
| UI request times out | Check saved experiments/job status before launching another run; a browser failure is not a cancellation |
| Backend/model changed on resume | Restore the job's exact configuration or start a new job |
| HTTP 402 on OpenRouter | Resolve OpenRouter credits/access; Plus does not fund that provider |

C2 research has no durable mid-invocation continuation. Historical portfolio checkpoints preserve completed cases and OPEN/CLOSE phases. A crash with no durable response conservatively charges the reservation as uncertain. Pause is honored at a safe boundary; an active request may finish first.

## 7. Switch back to OpenRouter later

Stop the local launcher. In private .env change:

```text
AEGIS_LLM_BACKEND=openrouter
AEGIS_LLM_MODEL=
OPENROUTER_MODEL=openai/gpt-4.1-mini
AEGIS_ENABLE_LLM_EXPERIMENTS=true
```

Retain or update your private OPENROUTER_API_KEY; obtain provider access/credits for a model supporting tools. The empty generic model override is intentional: it lets OPENROUTER_MODEL apply. Restart and verify the UI backend/model before consenting to a new run. Set a provider-side spending limit where available.

To return to Plus, select codex_cli and codex-default (or a supported pinned CLI model), restart and verify login. Existing completed results keep their provenance. Historical jobs are bound to their original transport/model/adapter and cannot mix transports during resume. There is no source-code edit or automatic fallback involved in switching.

## 8. Presentation checklist and viva explanation

Before the exam, retain a genuine research JSON, a completed short C2 portfolio report, screenshots or a labelled recording, the exact source version, corpus hash and data provenance. Record current CLI version and selected model; keep account secrets off the screen. Rehearse login/network/expiry and leave enough account allowance for the live case. A paid OpenRouter account can be prepared as a separately configured alternative, but is not required for the verified Plus research route.

Suggested explanation: “AegisTrade uses code for market indicators, candidate ranking, quantities and risk. Three LLM specialists request historical evidence through MCP, interpret it, cite sources and independently critique a constrained strategy. Research must complete before an individual human sees an order for approval. Historical simulation instead uses upfront-approved rules, recurring C2 research, code/model exits and marked open holdings. We measure the resulting ledger and research quality without claiming guaranteed profit.”

A working UI demo does not complete the capstone's held-out evaluation requirements. Keep independently reviewed cases, repeats, calibrated different-family judging, attack/defence evidence and required experiment artifacts separate. Codex/OpenRouter switching does not add that missing evidence automatically. The professor-approved team size remains three.

Implementation references: aegistrade/llm_backend.py, agentic.py, research_gate.py, c2_portfolio.py; app/api.py and app/ui.py. The CLI protocol uses documented [non-interactive structured output](https://learn.chatgpt.com/docs/non-interactive-mode) and [configuration controls](https://learn.chatgpt.com/docs/config-file/config-reference). Authentication, plan limits and model availability should be rechecked before the exam because they can change.

## 9. Field-validation fix and the August 2023 replay

Version 0.16.2 fixes a repeated formatting failure seen in replay 5b766b7259a44113913eb31a207c1d2d. TMPV, ICICIBANK and BHARTIARTL on 2023-08-01 each completed three Codex invocations but returned company.summary longer than the schema's600-character limit. The old umbrella error incorrectly suggested evidence/budget/provider failure as alternatives. Revalidation of the saved responses identified the exact field; the calls had succeeded.

Prompts now include field limits generated from the actual typed schemas. Correction feedback names the field, limit and received length. Bounds are unchanged; summaries are not silently truncated and evidence/risk checks are preserved. New failures carry separate SCHEMA, EVIDENCE, PROVIDER, BUDGET or POLICY categories. The UI reconstructs specific diagnostics for older schema-failed records without modifying their original responses, trading decisions or usage. Expand/select a research record to read the complete reason below the table.

TATASTEEL's zero-call missing-financial-filing block is a separate evidence gap; changing output formatting does not resolve it. A typed market assessment of INSUFFICIENT_EVIDENCE, or REVIEW_REQUIRED for an entry, now blocks before strategy/critic calls. An adequately cited REVIEW_REQUIRED can still proceed through a holding EXIT review.

The affected replay was paused safely after21 consumed invocations, with its state, remaining allowance and audit preserved. Its old prompt version remains frozen: do not resume it under new prompts. Load it to inspect the original evidence and diagnoses; start a new short run (for example two trading sessions) to use the correction. No new four-month replay or extra run allowance was authorized automatically. A fresh run has its own explicitly approved allowance and does not refund prior usage.

Post-fix genuine check: BHARTIARTL-2023-08-01, saved run a63dfb2759a0468396b133fc2d811e63, returned a valid364-character company summary in two invocations with zero schema errors. The market specialist assessed INSUFFICIENT_EVIDENCE, so the new early-stop policy correctly prevented an entry and avoided further specialist calls. This proves formatting/early-stop behavior, not a successful investment assessment. See reports/field_validation_fix.json. All125 automated tests pass; their model responses are mocked.

## 10. Portfolio-focused rehearsal and repeated restart warning (0.16.2)

Use AegisTrade_Portfolio_Simulation_Demo_Step_by_Step.docx for the current small portfolio settings, evidence prerequisites and measured December2023 result. The genuine completed-with-gaps job64263380f155412ea95a4deca6355a1f bought38 BHARTIARTL shares and retained them, with reconciled accounting. The guide distinguishes the original context failures from later prompt/cap improvements; it does not claim every stock passed or a positive return.

API/UI interface1 compatibility replaces the earlier exact patch-version block. Evidence now preserves results narratives and event bodies; repaired quarterly PDFs use a bounded32 MB limit and validated attachment cache. New company views and prompt changes require fresh research rather than silently changing historical trades.


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
