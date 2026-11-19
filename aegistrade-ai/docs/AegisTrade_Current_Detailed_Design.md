# AegisTrade AI — current detailed design and code guide

Version 0.35 · 17 November 2026 · Simulation-only capstone prototype

## 1. Purpose of this document

This is the current learning document for the implemented project. It explains what AegisTrade does, how information moves through the system, where C0/C1/C2 differ, how human intervention works, and which source file owns each responsibility. It describes the design independently from experiment results because additional inference runs are still being collected. Result tables can be updated later without changing the architecture described here.

The most important boundary is simple:

> Python code owns signals, money, permissions, validation and simulated fills. LLM agents research dated evidence, explain a permitted action and critique claims. A human may govern narrowly defined evidence-uncertainty cases. No live broker exists.

## 2. Project in one page

AegisTrade studies historical NSE equity decisions. It downloads or loads daily OHLCV bars, calculates technical indicators, selects eligible stocks, and compares three research architectures:

- **C0 — deterministic technical reference:** no LLM. Code routes among EMA Trend, EMA Pullback, RSI Reversion, Breakout and the configured technical catalogue.
- **C1 — evaluation-only single-agent baseline:** one tool-using LLM agent is run on the same research case and budget. C1 remains in AI Agent Experiments; it is not a new portfolio workflow.
- **C2 — agentic research system:** a market specialist, strategy specialist and independent critic use dated company evidence, policy RAG and typed hand-offs. Code validates the result before a simulated action is possible.

The project has two different kinds of comparison:

| Comparison | Question answered | Where to run it |
|---|---|---|
| AI Agent Experiment | Does the C2 specialist team improve grounded research over the same-budget C1 single agent, and at what cost? C0 is a deterministic reference. | AI Agent Experiments |
| Historical strategy backtest | What simulated P&L, exposure and drawdown result from the shared execution policy? | Strategy Backtests |

These must not be mixed. A grounded answer is not automatically profitable, and a profitable historical outcome is not automatically well-grounded research.

## 3. Current system architecture

[[FIGURE:current_architecture]]

*Figure 1: Current AegisTrade architecture. The numbered stages are explained below.*

1. The user chooses a dataset, workflow, historical window and capital in Streamlit. The UI exposes ChatGPT/Codex CLI, OpenRouter and Claude CLI adapters.
2. FastAPI validates typed inputs, reviewer authorization, explicit inference consent and call allowance.
3. Market-data code loads the active frozen universe, calculates indicators and ranks eligible technical candidates without an LLM.
4. C0 finishes in deterministic code. C1 calls one evaluation agent. C2 runs market, strategy and critic specialists with a shared bounded allowance.
5. MCP tools expose market snapshots, dated company evidence, policy RAG, the permitted strategy route and reviewed lesson memory. These are read tools; no LLM receives a live broker-write tool.
6. Deterministic gates validate schemas, cutoff dates, citations, route consistency, adverse-risk policy and the critic result.
7. The historical engine calculates whole-share quantity, costs, slippage, stops, targets, capacity and cash. Fills occur only at eligible historical bars.
8. If the optional `HUMAN_EVIDENCE_OVERRIDE` study encounters an eligible uncertainty block, the run checkpoints and pauses. The human decision is written separately; the original C2 block is never rewritten.
9. JSON/SQLite ledgers retain inputs, outputs, calls, decisions, positions and P&L. Reviewed lessons require an additional accept-and-freeze process before later retrieval.

## 4. User-interface design

The main application is `app/ui.py`. The retained blue-theme preview is `app/ui_blue_preview.py`. The new faculty-demo redesign proposal is `app/ui_redesign_preview.py` on port 8504. All call the same FastAPI backend; the redesign preview does not introduce another research or portfolio engine.

### 4.0 Proposed simplified demo shell

The separate redesign follows the supplied UI proposal while removing controls that are not required for the final demonstration. Its home page presents four primary questions rather than a long workspace dropdown:

1. **Data & Stock** — confirm universe, coverage, limitations and one price history.
2. **C2 Portfolio** — configure and inspect the end-to-end governed historical workflow.
3. **Agent Comparison** — compare C1 single-agent and C2 multi-agent results; C0 remains the deterministic reference.
4. **Evaluation Evidence** — inspect repeat status, retained runs and the independent-review boundary.

Policy retrieval and reviewed lessons share one secondary **Knowledge & Lessons** view. Persistent left navigation and a Home control replace repeated dropdown selection. Attention cards surface paused C2 jobs, pending human interventions and current AI evidence. The preview deliberately disables creation of a new C2 job until the design is approved; it reads the real retained API records. The existing UI on port 8501 remains unchanged.

The preview stylesheet isolates sidebar buttons from workspace tiles: the permanently expanded sidebar uses a navy gradient with white controls, while the four home workspace tiles use solid blue gradients. This prevents the earlier white-on-white sidebar collision caused by a global Streamlit button rule.

### 4.1 Home-level workspaces

| Workspace | Purpose |
|---|---|
| Market Data | Select/prepare a frozen universe and inspect coverage, provenance and limitations. |
| Overview | Inspect OHLCV, indicators, regime and current code-selected candidate strategy. |
| Strategy Backtests | Run the end-to-end C2 portfolio replay and optional human evidence override. |
| AI Agent Experiments | Run the same locked research cases through C0, C1 and C2. |
| Capstone Evaluation | Inspect retained E1–E4 evidence and evaluation artifacts. |
| Policy Knowledge | Inspect RAG passages, sources, dates and the active corpus fingerprint. |
| Learning & Lessons | Review, reject, accept and freeze conditional lessons. |

### 4.2 Strategy Backtests

Strategy Backtests displays one focused workflow: the C2 historical portfolio, including automatic technical screening, dated multi-agent research, cash/positions, ledgers, checkpoints and optional human override. The old C0/single-stock comparison services and artifacts remain readable for reproducibility, but duplicate controls are not exposed in the final demonstration UI.

### 4.3 Notification bell

The top-right bell polls `GET /simulation/c2/notifications` every 15 seconds while the dashboard is open. It reports only runs in `PAUSED_HUMAN_OVERRIDE`. A new checkpoint produces a one-time toast. Clicking **Open review** loads the exact run in Strategy Backtests. The bell is read-only: it cannot approve a decision and creates no LLM call. It is not an email or operating-system notification when the dashboard is closed.

## 5. End-to-end C0/C1/C2 research flow

[[FIGURE:research_flow]]

*Figure 2: Same-case AI Agent Experiment and the separate financial-outcome path.*

### 5.1 Locked case creation

The system selects a completed historical session and builds a snapshot containing symbol, signal date, regime, indicators and code-permitted strategy. The evidence cutoff is locked to the decision date. Future publications must not enter the case.

### 5.2 C0

C0 reads the code snapshot and route. It performs no evidence interpretation and makes zero generation calls. It is the deterministic route reference, so agreement with itself is labelled **reference by construction**, not universal quality.

### 5.3 C1

C1 uses one tool-using agent with the same model family, available read tools and bounded allowance used for the fair experiment. It tests whether a single general agent can retrieve evidence, follow the permitted route and produce a valid typed result.

### 5.4 C2

C2 separates responsibilities:

1. **Market specialist:** assesses the technical snapshot and dated company evidence; reports cited adverse risks and evidence limitations.
2. **Strategy specialist:** reads the code route and policy RAG; proposes only an allowed `ENTER`, `HOLD` or `EXIT` interpretation.
3. **Independent critic:** checks claims, citations, contradictions and policy compliance. It cannot authorize a fill.
4. **Code gate:** validates the typed result and rejects unsupported, future-dated or route-conflicting output.

The normal flow uses bounded correction rather than unlimited retries. Provider, timeout, schema, policy and evidence failures remain distinguishable in the trace.

### 5.5 Capability-oriented experiment metrics

The prominent AI Experiment table deliberately avoids a misleading single “quality” score:

| Metric | Interpretation |
|---|---|
| Route validation | Agreement with deterministic routing and code guards. C0 is the reference by construction. |
| Grounded company evidence | Cases with dated cited company evidence. C0 is N/A. |
| Adverse-risk flags | Cited material-risk observations detected by the research architecture. |
| Decision coverage | Cases reaching `ENTER`, `HOLD` or `EXIT`. |
| Safe evidence abstentions | Evidence-related blocks; lower coverage but not automatically a model failure. |
| Hard model/policy failures | Provider/schema/policy/route failures that are not safe evidence abstentions. |

The original task-success, error, call and latency fields remain under **Technical audit metrics**. Nothing unfavorable is deleted; it is presented with the correct meaning.

## 6. Historical portfolio flow

### 6.1 Common financial rules

C0 and C2 share capital, dates, data, cost model and core risk rules. Python calculates quantities and maintains the cash identity. The visible demonstration uses fixed defaults to reduce post-hoc tuning. Important rules include whole-share sizing, strategy-specific risk, NSE delivery costs, slippage, protective stops, trailing stops, take-profit and position capacity.

### 6.2 Session sequence

For every historical session:

1. Process queued exits before entries at the eligible open.
2. Apply opening-gap-aware stop and target rules.
3. Mark current holdings.
4. At the completed close, update trailing stops for the next session.
5. Review held positions when due or when a dated adverse disclosure candidate appears.
6. Rank new technical candidates and, for C2, research the bounded shortlist.
7. Queue valid actions for a later eligible open.
8. Save the checkpoint before moving to the next session.

The engine does not force every holding to be sold on the final date. Remaining positions are marked to the last available close, and the result separates realized and unrealized P&L.

### 6.3 Single-stock comparison

Legacy single-stock comparison artifacts remain available through the retained service contract for reproducibility; they are not part of the simplified final UI or the primary architecture evaluation.

## 7. Human evidence override

`HUMAN_EVIDENCE_OVERRIDE` is an optional research study, not permission to bypass every C2 block.

### 7.1 Eligible case

The system may pause when there is a technically valid BUY or holding SELL but C2 cannot obtain sufficient dated evidence and no concrete adverse event or hard provider/schema/policy/risk failure exists.

The reviewer chooses:

- `KEEP_BLOCKED`, or
- `APPROVE_OVERRIDE`.

The original C2 decision stays `BLOCKED`; the human event is a separate immutable ledger record.

### 7.2 Linked position and exit

If a blocked BUY is overridden, the resulting simulated position stores the override/position ID. A later discretionary C2 exit pauses for `KEEP_HOLDING` or `APPROVE_EXIT`. A later evidence-blocked SELL may also be reviewed. Protective stop, trailing-stop and take-profit exits remain automatic because delaying a risk control for human availability would make the replay unsafe and unrealistic.

### 7.3 Outcome and learning

An open override position is `INCONCLUSIVE_OPEN`. After exit, positive realized P&L is labelled `SUPPORTED` and non-positive P&L `NOT_SUPPORTED`. These are evaluation labels, not automatic lessons or profitability claims. A closed lifecycle becomes eligible for later human lesson review; memory still requires explicit acceptance and freezing.

## 8. RAG and dated evidence

The policy knowledge base stores stable passage IDs, source/authority metadata and dates. Retrieval combines lexical and vector search, reciprocal-rank fusion and reranking. The case cutoff is applied before results are sent to an agent.

Company research prepares bounded official filings and issuer releases. When the historical pack is genuinely incomplete, a bounded dated-web fallback may search for information available by the case date. Evidence remains untrusted data: tool hooks scan it, agents must cite observed IDs, and code verifies the citations.

Known limitations remain important:

- Current or curated membership applied backward creates survivorship/selection bias.
- Raw prices may not be fully adjusted for splits, bonuses and demergers.
- Historical archives and extracted PDFs may be incomplete.
- “No adverse item found” is not proof that none existed.

## 9. Memory and lessons

The project does not train model weights. Its governed memory is a reviewed playbook:

1. Development failures or completed override outcomes produce conditional draft lessons.
2. A human checks the original sources and accepts, edits or rejects each draft.
3. Accepted lessons are frozen into an immutable version with reviewer, dates and hash.
4. A later run explicitly selects a version and retrieves only bounded applicable lessons.
5. Held-out evaluation compares memory off/on; a lesson is never accepted merely because later P&L was positive.

## 10. State, audit and reproducibility

Saved C2 portfolios pin the data fingerprint, prompt version, corpus hash, inference adapter/model and engine version. A changed identity requires restoring the original configuration or starting a fresh run. Checkpoints prevent already completed sessions and research calls from being silently repeated.

The project retains:

- research hand-offs, citations, observed evidence and usage;
- selection audits and reasons for exclusion;
- cash, positions, queued orders and simulated fills;
- stop changes, fees, realized and unrealized P&L;
- provider/schema/policy/evidence failure categories;
- human override requests, decisions and linked outcomes;
- reviewed lesson candidates and frozen versions.

## 11. Inference adapters and efficiency

The three retained adapters are:

- `codex_cli`: uses the signed-in ChatGPT/Codex CLI account;
- `openrouter`: uses the configured OpenRouter API key;
- `claude_cli`: uses the signed-in Claude CLI account.

Saved runs remain tied to the adapter/model identity with which they started. Routine typed extraction and policy checking do not automatically require the most powerful model. A smaller model is appropriate only after it passes held-out schema, citation, adverse-event and route tests. The project controls cost with candidate screening, early evidence blocks, specialist output limits, a shared call allowance, cached evidence and resumable checkpoints.

## 12. Source-code map: which file implements what

The color code distinguishes the code used in the current port-8501 demonstration from files retained for evaluation or backward compatibility:

- **🟩 Green — current demo/runtime:** directly used by the approved UI demonstration or its required backend path.
- **🟦 Blue — capstone support:** required for evaluation, tests, monitoring or reproducibility, but not normally opened during the short UI demo.
- **🟨 Yellow — retained compatibility/alternative:** still readable or callable for old runs, tests or comparison history, but not part of the current UI demo flow.
- **⬜ Grey — generated artifact:** run state or evidence produced by the application; it is not source code.

Yellow does not mean defective. It means “do not present this as the current demo path.” Removing a yellow module requires a separate migration because old saved runs or API compatibility tests may still depend on it.

### 12.1 Application and API

| Status | File | Current responsibility |
|---|---|---|
| 🟩 Current demo/runtime | `app/ui.py` | Official Streamlit UI on port 8501: market data, overview, focused C2 Strategy Backtest, C1/C2 AI experiment, evidence/lesson views, notification bell and result interpretation. Dead duplicate single-stock comparison rendering has been removed. |
| 🟩 Current demo/runtime | `app/api.py` | FastAPI contracts for market data, C2 portfolio work, C1/C2 experiments, notifications, lessons, retained evidence and provider selection. |
| 🟩 Current demo/runtime | `app/live_progress.py` | Converts the selected C2 checkpoint into the live progress panel and refreshes it through read-only status calls. |
| 🟩 Current demo/runtime | `app/portfolio_view.py` | Remembers and safely restores the selected C2 run, verifies run/flow identity and prevents a legacy C0/C1 result from being displayed as C2. The current UI does **not** show C0 beside C2 on this page. |
| 🟩 Current demo/runtime | `app/dataset_progress.py` | Displays market-data preparation progress used by the Market Data workspace. |
| 🟩 Current demo/runtime | `app/capstone_ledger.py` | Supplies the read-only retained-run evidence shown in Capstone Evaluation. |
| 🟩 Current demo/runtime | `app/backend_compat.py` | Enforces the UI/API capability contract and displays a restart warning for an older backend. |
| 🟩 Current demo/runtime | `app/client_errors.py` | Converts structured API failures into specific UI messages and corrective actions. |
| 🟨 Retained alternative | `app/ui_blue_preview.py` | Earlier blue-theme UI alternative. It is not launched by the approved port-8501 demo. |
| 🟨 Retained alternative | `app/ui_redesign_preview.py` | Rejected port-8504 redesign proposal retained only for design history. It is not part of the submitted demo. |

### 12.2 Market data, signals and execution

| Status | File | Current responsibility |
|---|---|---|
| 🟩 Current demo/runtime | `aegistrade/market.py` | Prepares OHLCV and indicator-ready market frames. This replaces the erroneous old map entry `aegistrade/data.py`, which does not exist. |
| 🟩 Current demo/runtime | `aegistrade/nse_data.py` | NSEPython download/cache, coverage and dataset provenance. |
| 🟩 Current demo/runtime | `aegistrade/universes.py` | Configured Nifty20, Nifty100 and research30 universes and metadata. |
| 🟩 Current demo/runtime | `aegistrade/strategies.py` | EMA trend, EMA pullback, RSI reversion and breakout routing plus deterministic exit signals. |
| 🟩 Current demo/runtime | `aegistrade/smc.py` | SMC feature calculation and the permitted C2 SMC route. |
| 🟩 Current demo/runtime | `aegistrade/selection.py` | Candidate eligibility, ranking and the selection audit displayed in C2 results. |
| 🟩 Current demo/runtime | `aegistrade/engine.py` | Deterministic replay, quantity sizing, cash accounting, fees, equity curve and performance calculations. |
| 🟩 Current demo/runtime | `aegistrade/simulation_service.py` | Shared settings, normalization, execution-policy construction and deterministic reference calculation used by C2. Its standalone C0 endpoints are retained compatibility. |
| 🟩 Current demo/runtime | `aegistrade/fees.py` | Fixed modeled NSE equity-delivery charges applied to simulated fills. |
| 🟩 Current demo/runtime | `aegistrade/execution_policy.py` | Fixed strategy-specific stops, targets, exposure and protective-exit rules. |
| 🟩 Current demo/runtime | `aegistrade/trailing_stop.py` | Close-updated trailing-stop state and auditable exit reason. |
| 🟩 Current demo/runtime | `aegistrade/breakout_reentry.py` | Controlled breakout recovery watch after a stopped setup. |
| 🟩 Current demo/runtime | `aegistrade/smc_reentry.py` | Controlled SMC recovery watch after a stopped setup. |
| 🟨 Retained compatibility | `aegistrade/portfolio_comparison.py` | Old single-stock C0/C2 comparison service. Its widgets are no longer in the approved UI; routes remain readable/callable for saved comparison history and regression tests. |
| 🟨 Retained compatibility | `aegistrade/experiments.py` | Earlier deterministic strategy-comparison helper retained for API/notebook compatibility; it is not the current C1-versus-C2 AI experiment. |

### 12.3 Agents, tools, RAG and evidence

| Status | File | Current responsibility |
|---|---|---|
| 🟩 Current demo/runtime | `aegistrade/agentic.py` | C1 single-agent baseline and C2 supervisor/market/strategy/critic execution, typed hand-offs, bounded correction and tool-use audit. |
| 🟩 Current demo/runtime | `aegistrade/research_service.py` | Same-case C0 reference plus fair C1/C2 experiment execution, budgets, summaries, standardized secondary outcomes and saved results. |
| 🟩 Current demo/runtime | `aegistrade/research_gate.py` | Authoritative completed-C2 validation, evidence/action checks and final guard. |
| 🟩 Current demo/runtime | `aegistrade/llm_backend.py`, `aegistrade/llm_research.py` | ChatGPT/Codex CLI, OpenRouter and Claude CLI adapters, provider identity, JSON transport and typed response models. |
| 🟩 Current demo/runtime | `aegistrade/agent_tools.py`, `aegistrade/mcp_runtime.py`, `mcp_servers/` | Real typed read-tool boundary for market, company, policy, strategy and records observations. The old map entry `aegistrade/mcp_servers.py` was incorrect. |
| 🟩 Current demo/runtime | `aegistrade/corpus.py`, `aegistrade/knowledge.py`, `aegistrade/vector_store.py` | Active corpus loading, hybrid retrieval, fusion/reranking and immutable fingerprint. The old map entry `aegistrade/rag.py` was incorrect. |
| 🟩 Current demo/runtime | `aegistrade/company_research.py`, `aegistrade/evidence_library.py` | Historical company evidence packs, official attachments, cached coverage and adverse scans. |
| 🟩 Current demo/runtime | `aegistrade/company_excerpts.py` | Bounded relevant excerpts that retain document IDs and source provenance. |
| 🟩 Current demo/runtime | `aegistrade/dated_web.py` | Bounded historical web fallback constrained by the decision-date cutoff. |
| 🟩 Current demo/runtime | `aegistrade/evidence_context.py` | Lossless evidence projection and explicit context-budget controls. |
| 🟩 Current demo/runtime | `aegistrade/research_diagnostics.py` | Provider, schema, policy and evidence failure classification shown in results. |
| 🟦 Capstone support | `scripts/run_report_ai_repeats.py` | Resumable three-repeat E1 runner used to produce report evidence; not a normal UI-demo action. |
| 🟨 Retained compatibility | `aegistrade/c1_gate.py` | Old C1 portfolio/SMC order validation needed to read or test legacy C1 portfolio records. The current C1 baseline is evaluated in AI Agent Experiments, not Strategy Backtests. |

### 12.4 Portfolio, human control and learning

| Status | File | Current responsibility |
|---|---|---|
| 🟩 Current demo/runtime | `aegistrade/c2_portfolio.py` | Checkpointed C2 historical loop, research allowance, positions, evidence override, notifications and linked human entry/exit outcomes. Legacy C1 branches remain readable but are not exposed for new UI runs. |
| 🟩 Current demo/runtime | `aegistrade/portfolio_memory.py`, `aegistrade/lessons.py`, `aegistrade/memory.py`, `aegistrade/reflection.py` | Draft, human review, freeze and bounded retrieval of governed lessons. No outcome becomes memory automatically. |
| 🟩 Current demo/runtime | `aegistrade/safety.py` | Deterministic order/risk validation, simulated broker safety and audit helpers. |
| 🟩 Current demo/runtime | `knowledge/corpus.jsonl` | Versioned policy/reference passages observed through RAG. |
| ⬜ Generated artifact | `data/c2_portfolio_runs/<id>/state.json` | Durable per-run C2 checkpoint and ledger. It is generated evidence, not executable source. |
| ⬜ Generated artifact | `data/research_runs/<id>.json` | Saved C0/C1/C2 AI Agent Experiment result and traces. It is generated evidence, not executable source. |

### 12.5 Evaluation, deployment and tests

| Status | File/folder | Current responsibility |
|---|---|---|
| 🟩 Current demo/runtime | `scripts/start_unix.sh`, `scripts/launch_local.py` | Approved macOS/Unix startup path for FastAPI on 8000 and the original Streamlit UI on 8501. |
| 🟦 Capstone support | `evaluation/` | E1–E4 harnesses, fresh development/held-out cases, attacks, clean controls, judge calibration, Recall@5 and the experiment ledger. |
| 🟦 Capstone support | `monitoring/` | Prometheus/Grafana definitions and alerts used as operational evidence, not a required UI-demo screen. |
| 🟦 Capstone support | `.github/workflows/` | Hosted CI regression and evaluation gates. |
| 🟦 Capstone support | `tests/` | 377 deterministic regression, UI-contract, evidence, safety and orchestration tests. |
| 🟦 Capstone support | `docker-compose.yml`, `docker-compose.neural.yml` | Reproducible container and optional neural-retrieval stacks; the local viva demo uses `start_unix.sh`. |
| 🟦 Capstone support | `scripts/render_c1_c2_flow_graphs.py` | Regenerates the code-accurate C1 and C2 flow diagrams used for explanation. |
| 🟨 Retained compatibility | `scripts/start_redesign_preview.sh` | Starts the rejected UI redesign preview. It is retained for design history and must not be used in the approved demo. |

## 13. Key API routes

| Status | Route | Current purpose |
|---|---|---|
| 🟩 Current demo/runtime | `GET /health` | UI/API capability, feature contract and inference identity. |
| 🟩 Current demo/runtime | `GET /market/universe` | Active dataset symbols, coverage and provenance. |
| 🟩 Current demo/runtime | `POST /simulation/c2/run` | Start the checkpointed C2 portfolio replay shown in Strategy Backtests. |
| 🟩 Current demo/runtime | `GET /simulation/c2/status/{run_id}` | Read live or saved C2 progress and results. |
| 🟩 Current demo/runtime | `POST /simulation/c2/resume/{run_id}` | Add explicit inference allowance and resume a compatible safe checkpoint. |
| 🟩 Current demo/runtime | `GET /simulation/c2/notifications` | Read pending human evidence-override checkpoints for the notification bell. |
| 🟩 Current demo/runtime | `POST /simulation/c2/human-override/{run_id}` | Record an authenticated keep/override/exit decision and rationale. |
| 🟩 Current demo/runtime | `POST /research/experiments/run` | Run the fair C1 single-agent versus C2 multi-agent comparison; ALL also includes C0 as a secondary reference. |
| 🟩 Current demo/runtime | `GET /research/experiments/result/{run_id}` | Load a retained AI experiment and its traces. |
| 🟩 Current demo/runtime | `GET /portfolio-lessons` | List reviewed and frozen lesson versions. |
| 🟨 Retained compatibility | `POST /simulation/run` and related `/simulation/recent`, `/simulation/result/{id}` | Standalone deterministic C0 history retained for old saved runs and internal reference calculations. It is no longer a selectable Strategy Backtests workflow. |
| 🟨 Retained compatibility | `/research/portfolio-comparison/*` | Old single-stock C0/C2 financial comparison API. The current UI widgets were removed; the routes remain for saved history and regression tests. |
| 🟨 Retained compatibility | `/simulation/c1/*` | Legacy C1 portfolio records remain readable, but new C1 portfolio submission returns a retirement response. C1 now belongs only to AI Agent Experiments. |

## 14. How to read a result

For an AI Agent Experiment, first inspect the C1/C2 capability table, then case-level traces, and only then open the collapsed technical audit. A safe C2 abstention is different from a route/schema/provider failure. A separate standardized outcome evaluates each entry decision from the next session's open to the twentieth later-session close on a fixed ₹100,000 notional, including modeled fees and slippage. It is calculated only after research, never exposed to the agents, and is secondary to grounding/safety/cost.

For a Strategy Backtest, inspect status and completeness first. Partial-run metrics do not represent the full requested window. Then inspect capital/equity identity, open holdings, ledger, selection audit, evidence decisions, model usage and benchmark limitations. This C2 portfolio result demonstrates the end-to-end governed system; it is not the single-versus-multi-agent ablation.

## 15. Updating results after current inference runs

The design does not need to change when new runs finish. Update only the evidence snapshot:

1. Record run ID, date, dataset/case split, model/adapter and prompt/corpus versions.
2. Confirm the run is complete and preserve timeouts/failures.
3. Export the capability table and technical audit.
4. For financial comparisons, confirm the same data, capital, costs and execution assumptions.
5. Add independent reviewer labels and three held-out repetitions before claiming architecture improvement.
6. Do not replace an unfavorable result; explain whether it was a safe abstention, hard failure or financial outcome.

The final project report intentionally treats current inference numbers as a replaceable dated snapshot. The run ledger remains the source of truth.

### 15.1 Current three-repeat development snapshot

The report runner fixed the model, three cases, evidence capabilities, token budget and per-case call ceiling across three repetitions. C1 produced guard-pass counts `0, 1, 1`; C2 produced `1, 1, 1`. C2 consistently entered LT and stayed out of IDEA/HINDALCO, while C1 entered LT in two repetitions. C2 used 12 model requests per run and C1 used 11. The result is useful repeatability evidence, but it is still a development experiment. The 40 held-out cases and E2/E3 evaluation remain blocked until the independently reviewed JSONL templates are returned and frozen.

The 102 templates from 17 November remain untouched in their canonical folder and are not archived. Because the current UI/code is still awaiting approval, they are treated as historical pre-freeze candidates. After approval, the project generates a new versioned set and repeats independent review before final held-out E1–E4. See `POST_UI_FREEZE_EVALUATION_PLAN.md`.

## 16. Limitations and viva summary

AegisTrade does not prove future profitability. Its defensible contribution is the engineering separation of deterministic finance controls, dated evidence research, multi-agent critique, human governance and reproducible evaluation.

For a viva, remember five sentences:

1. C0 is the deterministic route reference and makes no LLM calls.
2. C1 tests one general tool-using agent; C2 tests specialist separation plus an independent critic.
3. RAG supplies dated evidence, but code validates citations, dates and permitted actions.
4. Python owns quantities, cash, fees, stops and simulated fills; no live broker exists.
5. Human overrides are separately audited, linked through exit and reviewed as lessons only after outcomes are known.
