# AegisTrade AI
## Capstone review, complete project guide and viva handbook

Prepared for Veneet, Karthika and Mathangi • 9 November 2026

Repository: `/Users/karthikakrishnakumar/aegistrade-ai`

**Team status:** The professor has approved the three-person team. No fourth-member approval is outstanding. The technical requirements still apply.

**Project status:** An implemented simulation-only research prototype with deterministic trading/risk code, tool-using GenAI agents, human-controlled simulated orders and local verification. This guide distinguishes code that exists, locally measured behaviour, external integrations not yet verified and evidence the team must create.

**Account separation:** Project model requests use the private OpenRouter key. Development is performed in the existing ChatGPT/Codex session. The application does not consume a ChatGPT session token or use a ChatGPT subscription as OpenRouter credit.

## 1. How to use this handbook

Read chapters 2–5 first to understand the project story and architecture. Use chapters 6–11 when running or explaining the implementation. Chapters 12–16 cover evaluation, deployment, the source-document gaps and the exam. Appendix A contains the file map; Appendix B is the remaining-evidence checklist.

The reviewed sources were the 17-page capstone guideline, the design proposal dated 26 October 2026, the four-slide initial proposal, and the actual repository. Course obligations come from the guideline, especially pages 2–6. The proposal is a design commitment, not evidence of implementation. The initial PPT is a concept deck, not a results presentation. Requirements inside these documents were reviewed as source material; embedded shell commands were not automatically treated as execution instructions.

The detailed traceability register is `docs/CAPSTONE_GAP_REVIEW.md`. This handbook is the updated account of the project. Older manuals describing a fixed three-specialist C2 pipeline or the later single-agent C2 experiment are superseded by the supervisor-plus-three-specialists implementation described here.

## 2. The project in one minute

AegisTrade helps a research user understand a rule-permitted trading scenario and review a simulated order safely. It calculates market indicators with code, routes among three predefined strategy families, retrieves authored policies, and asks LLM agents to gather evidence and explain the applicable choice. Completed C2 research and critic/code acceptance are mandatory before a separate deterministic risk engine constructs the order. A human must review the exact payload before the local broker simulator can accept it.

A useful viva opening is:

> AegisTrade is a human-governed trading research platform. We use LLMs for tool selection, evidence interpretation and policy-grounded explanations, while tested code calculates indicators, position sizes and risk. We compare a deterministic reference, one tool-using agent and a supervised team of three specialists. All execution is simulated. Historical replay fills automatically under approved rules, while every external-style supervised submission requires completed C2 research and approval of the exact payload.

The two signature challenges remain the same as the proposal: explainable market-regime-aware routing and safe, auditable execution. The current routing constraint is defined by code; the LLM explains and checks that constraint. It does not discover a profitable strategy or override the permitted catalogue.

A good engineering outcome can be a reliable abstention, a blocked stale order, a correct explanation, or evidence that the agent team costs more without improving quality. A positive synthetic return is not the definition of success.

## 3. What is GenAI, what is agentic, and what is deterministic?

| Component | Who decides or calculates? | Why it belongs there |
|---|---|---|
| OHLCV generation, indicators and regime thresholds | Python/Pandas/NumPy | Numerical calculations need repeatability and exact checking. |
| Entry/exit rules and permitted strategy catalogue | Deterministic strategy code | The experiment needs a frozen policy reference. |
| Which evidence tool/query to use | LLM specialist or single agent | This is model-directed action selection inside a restricted tool space. |
| Interpreting observations and writing rationale | LLM | This is the generative, language-based contribution. |
| Specialist hand-off validation and routing | Pydantic and LangGraph supervisor | Invalid evidence must not silently propagate. |
| Position size, exposure, stop and cash limits | Deterministic risk code | Money and permissions must not be guessed by a model. |
| Whether to approve/edit/reject the exact order | Human reviewer | An explanation cannot authorize a write. |
| Quote freshness, hash check, idempotency and simulated submission | Broker simulator code | Execution controls remain enforceable even after bad model output. |

GenAI means a real model produces an answer. Agentic behaviour adds tool choice, observations and subsequent decisions. A file named “agent” alone is not evidence of either. C2's tool-call trace and typed hand-offs show the model interaction. The LangGraph order workflow is an orchestrated control workflow; by itself, its deterministic nodes do not become LLM agents.

A cloud-hosted model can reason over synthetic data. Live brokerage access and real prices are not prerequisites for demonstrating GenAI. However, C0 and the default historical backtester do not call a model. Say this explicitly in the viva.

## 4. Architecture: research followed by supervised action

The application has two sequential stages of one mandatory research-before-approval workflow. They have separate UI screens, but the supervised order stage cannot run without completed, validated C2 research.

**Research workflow:** Streamlit → FastAPI paid-run gates → selected historical case → C0/C1/C2 → MCP evidence → typed validation → saved research result and explanation.

**Supervised action workflow:** a completed C2 result with accepted critic and passing code checks → market/provenance recheck → deterministic order/risk/critic → LangGraph interrupt → human approve/edit/reject → fresh simulated-quote checks → AuditBroker → audit record.

Historical portfolio simulation is a separate calculation path: the user approves its selection/risk/cost assumptions before an automatic replay. It evaluates deterministic strategy rules across days and produces curves and a ledger. It does not spend on daily LLM calls.

C2 uses a deterministic LangGraph supervisor and three LLM specialists:

1. **Market specialist:** owns `market_snapshot`; interprets the case's historical indicators and code-defined regime.
2. **Strategy specialist:** owns `search_policy` and `check_strategy`; uses the market hand-off and observed constraints to propose a cited strategy label.
3. **Compliance critic:** owns `search_policy` and `check_strategy`; checks the typed hand-offs against tool evidence and accepts/rejects the research result.

The supervisor coordinates these roles, checks contracts and enforces the shared budget. It does not make another model call to repeat a fixed scheduling decision. Each role has its own prompt, allowed tools and Pydantic response schema. The combined team has the same available tool set as C1.

The order graph adds proposal, deterministic risk, deterministic critic, approval and execution nodes. Pending or rejected research never reaches the human approval gate. These are control responsibilities, not extra paid “AI variants.” There is no C3.

## 5. Configuration, accounts and starting the project

Use the existing private `.env`. It contains the OpenRouter key, model ID, paid-experiment enable flag, reviewer token, data directory and dashboard configuration. Never paste those values into slides or exported evidence. `.env` and `.env.*` backups are excluded from Git/Docker packaging; `.env.example` remains an unsecret template.

The project currently reads `OPENROUTER_MODEL` with `openai/gpt-4.1-mini` as the default. Six-slot role prompts, temperature and shared agent limits live in `config/agents.json`; the prompt version is saved with research results. A private environment model override is recorded in the output so comparisons can identify it.

The Gmail address used to register an account does not determine API access. OpenRouter billing is separate from ChatGPT billing. The last provider check in this conversation accepted the key but returned HTTP 402 for an account that had not purchased credits. A USD 5 key limit is a ceiling, not proof of a funded balance. No new paid calls were made during this review.

From the repository run:

```bash
bash scripts/start_unix.sh
```

Then open Streamlit at `http://127.0.0.1:8501`, FastAPI documentation at `http://127.0.0.1:8000/docs` and health at `http://127.0.0.1:8000/health`. Keep the terminal open. Stop with Control+C. The existing service on port 8000 was left running during source correction; restart your launcher to load the updated source. Restart the API after changing `.env`; the running process will not automatically load a new key or flag.

Health distinguishes simulation-only mode, key presence, paid enablement, the selected model and C2 architecture. It does not certify credits or a successful inference. A reviewer token authenticates local review/paid actions; it is not the OpenRouter API key and is not production multiuser authentication.

If starting services separately, load the environment deliberately:

```bash
.venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --env-file .env
.venv/bin/python -m streamlit run app/ui.py --server.address 127.0.0.1 --server.port 8501
```

## 6. Market data and the actual trading specification

The active local research source is now a validated NSEPython cache for a 20-stock Nifty 50 subset, covering 8 November 2021–8 November 2026 plus warm-up. It contains 26,580 rows. Universe membership is the current snapshot, and prices are unadjusted; both limitations are displayed in the UI. See the NSE data/UI appendix for the selected stocks and selection criteria.

Synthetic OHLCV remains an explicit test mode for RELIANCE, INFY, HDFCBANK, ICICIBANK and NIFTYBEES. The synthetic test generator uses 620 business-day rows per symbol from 3 January 2022 and seed 42, with controlled drift/volatility phases. These are simulated series bearing stock labels, not downloaded NSE prices or an actual NSE holiday calendar.

The validator requires Date, Symbol, Open, High, Low, Close and Volume; normalizes dates, rejects duplicate symbol/date rows, non-finite or nonpositive values and inconsistent OHLC ranges. A ready row requires warmed-up EMA20, EMA50, ATR14, ADX14, prior 20-session high and realized volatility. RSI14 is also calculated.

Regime classification uses this precedence:

1. WARMUP if required indicators are unavailable.
2. HIGH_VOL if annualized realized volatility exceeds 0.48 or ATR14/Close exceeds 0.065.
3. BREAKOUT if Close exceeds the prior 20-session high and ADX14 is at least 18.
4. TREND if ADX14 is at least 22 and EMA20 exceeds EMA50.
5. RANGE if ADX14 is below 22.
6. UNCERTAIN otherwise.

| Strategy | Actual entry rule | Actual signal exit |
|---|---|---|
| EMA_TREND | Ready, EMA20 > EMA50 and Close > EMA20 | EMA20 < EMA50 |
| RSI_REVERSION | Ready, RSI14 < 42 and Close > 0.88 × EMA50 | RSI14 > 58 |
| BREAKOUT | Ready, Close > prior 20-session high and ADX14 ≥ 18 | Close < EMA20 |

Code-defined ROUTER maps TREND→EMA_TREND, RANGE→RSI_REVERSION and BREAKOUT→BREAKOUT; all other regimes map to NONE. A permitted route does not guarantee an entry signal. For example, a RANGE row can permit RSI_REVERSION while its RSI is too high for entry.

The proposal's RSI<30 with upward confirmation, 0.5% risk, five positions and 2% daily-loss example were proposed settings. Current defaults are RSI<42 with the price condition, 1% per-trade planned risk, four positions, 20% maximum position value and a 3% daily-loss limit. The UI permits experiment-specific backtest risk settings; record them. The supervised proposal uses its own fixed RiskParameters defaults. Do not say those settings automatically synchronize.

## 7. C0/C1/C2: complete LLM-call workflow

### 7.1 Before any paid request

The user selects configuration, case count, dates, output budget and memory setting in AI Agent Experiments. A plan and permissions are displayed before the run. The API requires a valid reviewer token, explicit paid consent, a configured key and `AEGIS_ENABLE_LLM_EXPERIMENTS=true`.

Ready historical rows are selected deterministically from the chosen period. ALL uses identical selected cases for all three configurations. Research inputs contain the symbol/date and approved numerical indicators. The agent-facing typed whitelist excludes expected outcome fields and future returns. The code-permitted route is available through a tool as a policy constraint; it is not an independent gold answer supplied secretly to the model.

### 7.2 C0: reference

C0 retrieves policy IDs and returns the deterministic route, making zero LLM requests. Its guard is true by construction. It is useful for contracts and cost comparison, not evidence that the model is better or worse at forecasting.

### 7.3 C1: one agent with all tools

C1 receives the union of market, policy-search and strategy-check tools. It can choose queries, gather observations and then return `StrategyJudgement`. It has the same model, eight-request ceiling, 16-tool-call ceiling and default 4,800-token total output allowance as C2. It often needs two requests, but actual provider behaviour determines the measured count.

### 7.4 C2: three specialists

A normal C2 run uses this sequence:

| Model request | Agent | Work performed |
|---|---|---|
| 1 | Market specialist | Selects its market tool; returns a structured tool call. |
| Local MCP call | Market server | Validates and returns the selected historical evidence. No LLM is used here. |
| 2 | Market specialist | Reads the observation and returns a typed regime explanation. |
| 3 | Strategy specialist | Reads the market hand-off and requests policy search plus code route. |
| Local MCP calls | Knowledge and strategy servers | Return dated passages and the code-permitted route. |
| 4 | Strategy specialist | Generates a cited typed strategy explanation. |
| 5 | Compliance critic | Reads both hand-offs and requests its own policy/strategy checks. |
| Local MCP calls | Knowledge and strategy servers | Return evidence for the critic to inspect. |
| 6 | Compliance critic | Generates typed accept/reject and reason. |
| Final code guard | No model | Verifies route agreement, retrieved citation IDs and critic acceptance. |

The normal six requests are justified by the course's requirement for three specialists that observe their own tools. The supervisor, arithmetic, deterministic risk and final guard add no LLM requests. Two additional requests can be used for correction within a shared maximum of eight; a role is limited to three turns. Tool requests can be grouped in a single turn.

### 7.5 Provider request and tool feedback

The client sends HTTPS POST requests to `https://openrouter.ai/api/v1/chat/completions` with the authorization header, configured model, system/user messages, selected tool schemas, temperature zero and a bounded output-token allowance. `usage.include` requests provider token/cost reporting.

The provider returns assistant text or `tool_calls`. Tool calls contain an ID, function name and JSON arguments. The local runtime validates the arguments and role permission. It invokes FastMCP through persistent stdio sessions on the Mac or configured HTTP URLs in Docker. Tool results are returned as `role: tool` messages with matching `tool_call_id`, then included in the specialist's next request.

The market and strategy tools receive a locked, typed case from the application. The model cannot substitute a different symbol or mutate indicator values because those tools accept no model-controlled case fields. `search_policy` permits a bounded model-selected query. No broker, shell, arbitrary file or general network tool is offered to the research agents.

### 7.6 Validation, correction and failure

MarketJudgement, StrategyJudgement and CriticJudgement enforce strict typed schemas. A strategy must use an allowed label and cite existing retrieved passages. Every specialist must actually obtain its own required tools. A contradictory regime, missing evidence or invalid response can trigger a correction turn; the trace records a `replan` event.

A rejected critic triggers the supervisor's revision branch if budget allows. A revision alone does not cancel the critic's rejection: without a fresh accepted review, the case remains blocked. This is a deliberately conservative boundary. A provider/account failure ends the case without automatic retry or fabricated fallback success.

The final guard checks agreement with the deterministic route and citation-ID provenance. It does not prove every sentence is supported. A different-family judge calibrated with human labels is needed for semantic explanation quality. No guard result authorizes an order.

### 7.7 Cost and context efficiency

Each request reserves at most 600 output tokens from a shared allowance. C1 and C2 default to 4,800 total output tokens per case. Message context has a 22,000-character per-request bound; oversized context blocks instead of silently dropping evidence. Character length is a practical bound, not exact tokenizer accounting. Provider input tokens also cost money.

C2: maximum eight model requests per case; with three UI cases, maximum 24. ALL: maximum 16 per case, or 48 for three cases. These are attempt limits, not promised usage. They reset for a new run. Maintain an account-level monetary cap and inspect actual billing. Missing cost stays unknown, and an incomplete cost report must not be treated as free.

## 8. Retrieval, corpus ingestion and memory

The active knowledge base contains 81 passages: 72 project policies/code-derived specifications and nine source-linked background references. Stable IDs, source/code locators, authority, indexed date and verified publication/retrieval metadata are retained. This is a policy/strategy/data-quality RAG corpus, not a financial-news or company-filings service.

The active local pipeline combines BM25 and 384-dimensional MiniLM embeddings with Reciprocal Rank Fusion, followed by a cross-encoder reranker and controlled query expansion. Chroma persists the vectors and source metadata; model weights are cached locally. The offline BM25/TF-IDF surrogate remains a separately labelled baseline.

The pretrained embedding/reranking weights, persistent Chroma round trip, neural API/UI and actual MCP neural retrieval were executed successfully. The Qdrant adapter and Docker override remain available, but that remote/full-stack deployment is not yet verified. The corpus fingerprint binds C2 to its retrieved knowledge version; changed or missing corpus provenance requires fresh C2 research.

To ingest reviewed authored passages, create JSONL rows with `id`, `date`, `source`, `title` and `text`, then run:

```bash
.venv/bin/python -m scripts.ingest_policies --input path/to/reviewed_passages.jsonl
```

Set `AEGIS_POLICY_CORPUS_PATH` to the resulting JSON and restart the API/MCP sessions. Unique IDs and provenance are validated. Ingestion does not certify the truth of a policy or execute its text.

True passage Recall@5 is the fraction of labelled relevant passages retrieved among the first five results, averaged across queries. Hit@5 asks only whether at least one relevant passage was found. If two passages are relevant and one is retrieved, Recall@5 is 0.5 while Hit@5 is 1.0. The code now reports both separately.

Short-term memory consists of bounded specialist conversations and checkpointed order state. Long-term memory stores proposed, accepted and rejected lessons in SQLite. Research memory-on retrieves applicable regime/grounding lessons only from a frozen human-reviewed playbook; pending/rejected lessons are excluded. Lexical applicability matching is a simple mechanism, not a learned relevance guarantee.

Freeze records the reviewer, time, accepted-lesson count and SHA-256 manifest. Frozen versions cannot be changed through normal lesson review. Do not delete or change a frozen experiment playbook to improve held-out results. Archive the version and start a new development version if policy changes.

## 9. Reflexion and human review of lessons

Canned lessons remain available for demonstration, but the project now has a real model-backed reflection path. After a failed C2 development run, select the failed case in the research results and authorize one paid reflection request. The API supplies only the scored failure's hand-offs and observations, asks for a short conditional lesson, validates its schema and stores it as PENDING_HUMAN.

A reviewer must accept or reject it with a reason in Learning & Lessons. Only accepted relevant lessons may enter later reasoning. A proposed lesson never changes code-enforced risk limits. Provider failures without a model response are excluded from paid reflection: adding account credit or fixing connectivity is an operational task, not something another model request can solve.

Lessons cannot be generated through this path from runs marked heldout. The E3 comparison requires a frozen playbook, runs the same reviewed cases with memory off/on and records the manifest. A helpful lesson should generalize a check, such as verifying citation IDs, rather than memorize a case's answer.

One rejected lesson to explain is “increase trade size after losses to recover.” It is unsafe because it conflicts with fixed risk limits and generalizes without evidence. Show the actual rejected record and reviewer reason; do not claim a team review that has not happened.

Current deletion policy is manual, local administration while services are stopped; there is no privacy-deletion UI or automatic retention scheduler. Preserve frozen research versions and audit the administrative change. Production deployment needs defined retention, encryption and user-specific authorization.

## 10. From a C2 explanation to a supervised simulated order

Complete C2 research first. In research results choose a case with all three specialist hand-offs, accepted critic, passing code checks and retrieved citation evidence, then click “Use this C2 case in Supervised Trading.” The saved run/case IDs are transferred to that screen. Starting the workflow loads the server-side result, checks the specialist hand-offs, critic verdict, citations and snapshot, and compares the saved numerical evidence with current data for the exact symbol/date. There is no direct deterministic order-proposal route. Without a linked passing C2 result, the proposal button is disabled and both normal and streaming API start routes reject the request. C0/C1 are research baselines and cannot satisfy this prerequisite.

Code then rechecks the permitted route and actual entry signal. A correct C2 explanation may still produce no order: NONE, a non-entry RSI, changed evidence or a missing bar results in rejection/abstention. This is expected. Research route agreement is not an instruction to buy.

For an eligible case, the deterministic proposal node computes the order from reference equity, cash, entry and ATR. The saved AI explanation/citations are displayed with the human review. No extra model request is needed to repeat that explanation.

Position sizing is:

- Risk quantity = floor(equity × risk fraction / (entry − stop)).
- Exposure quantity = floor(equity × position fraction / entry).
- Cash quantity = floor(available cash / (entry × (1 + fee fraction))).
- Proposed quantity = minimum of these quantities, subject to positive valid values and remaining controls.

For equity ₹100,000, entry ₹100, stop ₹96, 1% risk, 20% exposure, cash ₹100,000 and 10 bps fees: risk permits 250 shares, exposure permits 200, and cash permits 999. The proposed quantity is 200; planned stop-distance loss is ₹800, position value ₹20,000 and entry fee ₹20. A stop is an intended exit rule, not a guarantee against gaps.

The order contains request ID, symbol, side, quantity, market-order type, reference price, protective stop, strategy, DEMO_ONLY account, signal date and expiry. The canonical full payload is hashed with SHA-256.

Before every status reconstruction or approval resume, the backend reloads the saved C2 result and rechecks the market evidence. A SHA-256 digest binds the workflow to that exact research result. Changed research, changed indicators, missing provenance or an older workflow without C2 is blocked; create a new proposal after current C2 research. A lower-level graph call without validated C2 context also blocks before creating a proposal.

The graph calls `interrupt()` before issuing an approval token. Reject ends the workflow. Edit creates a changed payload/new request ID, invalidates the old hash, reruns risk/critic checks and asks again. Approve must include the current hash. The broker receives only the validated exact order and human-issued token.

The supervised demo sizes one proposal; it does not debit a persistent forward paper portfolio. The historical simulator has its own cash/positions ledger. Do not imply the two account stores are one live account.

## 11. Safety, fault recovery and kill switch

Before a new simulated submission, AuditBroker verifies exact approval, deterministic risk, timestamps, expiry and price deviation. Non-finite prices are rejected. The standard quote-age limit is 90 seconds; the UI order graph uses a 600-second demo policy. The quote is a deliberately timestamped simulated replay quote, not proof of live market freshness.

If the request ID already exists with the same payload hash, the broker returns the recorded result as an idempotent replay. The same ID with a different hash is rejected. An injected timeout after commit is reconciled by request ID rather than blindly resubmitting.

The human emergency control is in Supervised Trading. Enabling the kill switch blocks new proposals and new submissions and invalidates outstanding approval tokens. Disabling it does not restore those old tokens; a new approval is required. It does not liquidate positions or cancel real exchange orders. The action is recorded in the simulator's audit log.

Persisted LangGraph checkpoints allow a paused order workflow to be rebuilt after the checkpointer is closed. A local test verifies restore, edit, new hash and rejection of the earlier hash. Research outputs are saved as JSON; research specialist conversations are not currently resumed mid-provider-request after a process crash.

Security is layered: read-only role scopes, typed tool inputs, restricted query size, injection scanning, output checks, secret scrubbing, call/context budgets and a separate approval-controlled simulator. A regex injection scanner is imperfect. It cannot establish that all prompt injections are prevented. The strongest execution boundary is that research agents lack any broker tool.

## 12. Historical portfolio simulation and benchmarks

Run Strategy Backtests with starting capital, date interval, per-trade risk, fees and slippage. ALL evaluates ROUTER, EMA_TREND, RSI_REVERSION and BREAKOUT under matching assumptions. Indicators are computed on full source history before slicing the evaluation dates, preserving earlier warm-up information.

A signal from completed day T is queued for an eligible later bar and filled at its open with adverse slippage. Stops are fixed at signal creation using two ATR. A gap making the entry/stop relationship invalid blocks entry. A stop hit fills conservatively at the lower of open or stop, then applies sell slippage. Daily OHLC cannot reveal every intraday sequence or guarantee actual liquidity.

The revised engine carries the last known value of a held symbol across a missing bar instead of making its asset value disappear. Such a mark is stale and should be disclosed; it does not make missing data reliable. Pending orders remain queued until an eligible bar is available. A daily-loss gate blocks new entries after the configured loss threshold while allowing risk exits.

The separate passive benchmark buys equal cash allocations at the first selected session open, pays the same fee/slippage assumptions and holds to the last close. It has no active-strategy stops or position-exposure cap. State that difference when interpreting it. The benchmark is not an LLM configuration and does not create another AI variant.

Ending equity includes remaining cash and marked open positions. Total return is ending equity / starting capital − 1. Maximum drawdown is the worst fall from an observed equity peak. Sharpe uses daily return mean/volatility with square-root-of-252 scaling; short samples and synthetic data limit interpretation. Completed-trade win rate excludes open positions.

No actual NSE profitability, corporate-action correctness, point-in-time universe handling or walk-forward robustness is proven. A real-data study needs a licensed/provenance-tracked source, symbol/corporate-action handling, chronological splits, realistic costs, sensitivity tests and documented survivorship limitations.

## 13. Evaluation: what to run and what results mean

The course requires at least 60 independently prepared cases, about 20 development and at least 40 held-out, with related variants kept together. The repository contains candidate fixtures, not certified independent gold. The person tuning agents must not author final hidden labels, and the defence implementer must not author the final attack texts. Held-out candidate labels were not used to tune these corrections.

The original deterministic runner remains useful:

```bash
.venv/bin/python -m evaluation.run_eval --split dev --output reports/capstone_review_dev.json
```

It checks rules, broker controls, retrieval and a scanner. It does not run live model comparisons. The initial 16-passage offline run matched 20/20 generated development references and measured 0.9444 Recall@5 before and after rewriting on 36 candidate-labelled queries, with no rewrite improvement. The later expanded neural-corpus results and legacy-query regression are separately recorded in Appendix E. The scanner detected 30/32 attacks and falsely blocked 0/10 clean samples. These are small authored fixtures and scanner statistics, not general model safety rates.

`evaluation/run_capstone.py` provides the common experiment runner. For E1/E2/E3 supply a reviewed JSONL case file containing ID, scenario family, split, reviewer, `independently_reviewed: true`, typed input and a separately stored expected result. It rejects family leakage across splits. Expected labels are used by the checker, not placed into model prompts/tools. The reviewed flag is an attestation, not proof that review actually occurred.

| Experiment | Comparison | Claims it can support after real runs |
|---|---|---|
| E1 | C0 reference, C1 one agent, C2 team; same model/tools/budget ceiling | Route-task success, explanation quality with a calibrated judge, cost, latency and overhead. |
| E2 | Scanner off/on on isolated poisoned-tool and clean research cases | Authored forbidden-tool attempts/final-text violations and false blocks. Hard execution controls remain enabled. |
| E3 | Same cases with frozen reviewed lessons off/on | Task success/regressions and memory effect; retain reflection-generation usage as learning cost. |
| E4 | Deterministic regime router versus fixed strategies, plus passive benchmark | Routing ablation under specified synthetic trading assumptions; not AI investment performance. |

Example development command for a separately reviewed case file:

```bash
.venv/bin/python -m evaluation.run_capstone --experiment E1 --cases-file path/to/reviewed_cases.jsonl --split development --consent-paid --max-paid-calls 24 --output reports/e1_development.json
```

Use `--repeats 3` for final model comparisons and deliberately set a sufficient maximum paid-call allowance before running. The runner rejects an undersized allowance before spending. Sixty cases and repeats can be costly; first verify one case and account credits. Never mark generated labels as independent just to pass a validation flag.

E4 can run without any model spend:

```bash
.venv/bin/python -m evaluation.run_capstone --experiment E4 --output reports/capstone_e4_synthetic.json
```

Reports include outcomes, trajectories, tools, attempted model calls, median/p95 latency and provider cost if completely reported. Do not hide model errors by averaging only successful outputs. Accuracy against code routing measures compliance, not future returns. Explanation faithfulness requires a semantic judge or human assessment.

Judge calibration now requires at least 20 human labels and actual judge labels, a human-reviewer identity, solver model ID and a different-family judge model ID. The old suggested-machine labels are deliberately ignored. Run `python -m evaluation.judge_agreement --labels path/to/actual_calibration.json`. It refuses missing labels or same-family model IDs. The team must obtain real judge predictions; this script does not create them or train a judge. Cohen's kappa can be undefined when labels have no variation.

## 14. Verification, CI, monitoring and deployment

Run `.venv/bin/python -m pytest -q` for automated verification. After the mandatory-research correction on 9 November, all 72 tests passed. The tests exercise numerical safety, temporal fills, missing bars, exact approvals, stale quotes, idempotency, all 13 MCP tools, scoped research tools, three specialist hand-offs, correction, memory filtering, reflection boundaries and checkpoint restore. Model responses are mocked in unit tests; these do not prove a funded provider run or useful LLM explanations.

Actual local stdio MCP discovery and calls to market, strategy and knowledge tools also passed. Six smoke checks passed against the updated v0.11.0 API on temporary port 8011 with isolated test data; no paid model requests were made. The exported tool schemas are in `docs/MCP_TOOL_INVENTORY.json`. Write MCP tools are not connected to an LLM. Read-only Docker MCP services are internally exposed; the approval-controlled API owns the action workflow.

The Compose configuration includes API, dashboard, five read/compute MCP services, Qdrant, Prometheus and Grafana. Run `docker compose up --build` only after Docker Desktop is running. The Docker CLI was available, and base/neural Compose files validated in this review, but the daemon was not running. No full deployment, container health result or clean-machine proof is claimed.

For the alternative Docker/Qdrant retrieval deployment:

```bash
docker compose -f docker-compose.yml -f docker-compose.neural.yml up --build
```

The full runtime includes local neural dependencies; Linux/Docker install CPU-only Torch. Populate new Docker model/index volumes before paid experiments. The local cache is already built and verified, but is separate from Docker named volumes. Offline mode remains available as a baseline; independent held-out retrieval labels and semantic faithfulness evaluation remain outstanding.

Prometheus scrapes API metrics. Grafana shows system activity, not portfolio profit. The existing rules define API-down and risk-block-spike alerts. A rule file is not proof of a delivered/firing alert. Start the stack and capture a real alert state. Research JSON retains prompts' version, model, hand-offs, tool observations, usage and errors; it is local tracing, not an already-connected Langfuse/LangSmith deployment.

GitHub Actions runs tests, a 90% development evaluation gate and a source credential-pattern check. A workflow-dispatch option deliberately corrupts three copied development expectations in memory to demonstrate the gate; it does not modify files. Locally this produced 17/20 = 85% and exit code 1. That proves the local failure gate, not an actual failed GitHub run. The workspace has no `.git` repository, so publishing history and hosted CI evidence still require team setup.

## 15. Review of the proposal and initial PPT

The proposal correctly separates model reasoning from monetary controls and identifies the two signature challenges. Its promises about MCP, reviewed lessons and fair baselines were ahead of the implementation. Those paths have now been materially connected. The remaining promises must be backed by measured evidence rather than by renaming deterministic nodes as agents.

| Earlier statement | What to say now |
|---|---|
| Team size needs an exception or fourth member | Professor has approved Veneet, Karthika and Mathangi. |
| C2 is a fixed market → strategy → critic sequence of single prompts | C2 has three scoped tool-using specialists coordinated by a deterministic LangGraph supervisor. |
| C1 is one LLM prompt | C1 is a single tool-using agent with the same union of tools and shared budget ceiling. |
| Strategy examples use RSI<30 / 0.5% risk / 5 positions / 2% loss | Report the current frozen rules/defaults from chapter 6; examples were proposals. |
| Agents improve trading outcomes | Treat this as an unproven hypothesis; current portfolio results are deterministic. |
| Hybrid RAG is complete | Neural MiniLM/RRF/cross-encoder with persistent Chroma is measured; independent relevance review and generated-answer faithfulness remain outstanding. |
| Reflexion learns from failures | Development-only model-backed lesson drafting and reviewed retrieval exist; held-out benefit is unmeasured. |
| Deployment/CI/alerts are complete | Configurations exist; Docker daemon, real alert and hosted failed-CI evidence remain outstanding. |

The four-slide deck should evolve into a final 10–12-slide presentation: problem and users; scope and two challenges; actual architecture; actual rules/risk; C2 tool-call sequence; exact approval flow; RAG/memory; E1–E4 design; measured results with limitations; security/failure traces; deployment evidence; team contribution and next steps.

Do not erase the original concept slides. Keep them as the initial plan, and make a dated final deck reflecting the actual implementation. The comprehensive source-to-code gap table is in the companion gap review.

## 16. Three-person ownership and viva demonstration

Veneet leads domain/data, strategy specification, backtesting and independent evaluation/attack cases. Karthika leads RAG, MCP, C1/C2 orchestration, prompts and the improvement loop. Mathangi leads deterministic risk, approvals, simulated execution, security, UI/API and deployment. All three review integration and must explain the whole architecture.

Veneet should own final hidden labels and attacks rather than Karthika tuning agents or Mathangi building defences. Mathangi checks held-out policy correctness; Veneet independently reviews risk arithmetic. Keep dated contributions and reviewer decisions. These are responsibilities, not claims that every listed activity has already been completed by that person.

A practical 12-minute demonstration:

1. Minute 0–1, Veneet: problem, users, simulation boundary and NSE dataset provenance, including raw-price/current-membership limits.
2. Minute 1–3, Veneet: capital/date simulation, fixed strategies, benchmark, ledger and a limitation.
3. Minute 3–6, Karthika: C2 pre-run plan, real model call evidence if funded, tool observations, three typed hand-offs and cost. Use a clearly labelled saved result if connectivity fails; never present mocked output as a paid run.
4. Minute 6–8, Mathangi: link a completed, accepted C2 case, inspect code-sized order, edit quantity, show changed hash, and reject/approve the new payload.
5. Minute 8–10, Mathangi: stale-data rejection, timeout reconciliation and kill switch. Inspect audit history.
6. Minute 10–11, Karthika: accepted/rejected lessons, frozen manifest, E3 methodology and any measured regressions.
7. Minute 11–12, all: actual E1–E4 evidence, operations status, remaining limitations and individual contributions.

Choose a C2 case with a real entry signal for the order story. A passing route explanation may correctly abstain from an order. Prepare failure traces, saved JSON, screenshots and a backup video; label every artifact with provenance, date and whether it was mocked or real.

## 17. Viva questions with defensible answers

### 1. Why is this a GenAI project?

C1/C2 make actual OpenRouter model requests for tool selection and generated explanations. C2 specialists read their tool observations before producing typed answers. Deterministic backtests alone are not the GenAI demonstration.

### 2. What makes C2 multi-agent rather than three functions?

Three distinct model roles have separate prompts, tool permissions, conversations and typed hand-offs, coordinated by LangGraph. Each requests tools and interprets results. Pure code nodes are separately identified as controls, not described as LLM agents.

### 3. Why is the supervisor deterministic?

The current plan has a small known sequence. Code scheduling saves cost and makes permissions/budgets reliable. Replanning occurs when evidence/schema checks fail or the critic rejects. An additional planner model has no demonstrated benefit here.

### 4. What is the minimum normal C2 model cost?

Usually six requests: tool request plus observation interpretation for each of three specialists. Shared maximum is eight. C1 often needs two. Report actual tokens, cost and latency; do not say “same budget” means equal spend.

### 5. If code already knows the strategy, what is the LLM's value?

The experiment evaluates evidence gathering, policy-grounded explanation and review under constraints. It does not ask the model to override the route. Its value must be measured against C0/C1 using labelled tasks and explanation quality. If the team adds cost without benefit, report that result.

### 6. What is RAG here?

The policy tool retrieves source-labelled passages and C2 reads them before generating its explanation. The active pipeline is BM25 plus MiniLM vectors, RRF, query expansion and cross-encoder reranking, with persistent Chroma storage. It has been exercised through actual MCP and the UI; the offline surrogate remains a separate baseline.

### 7. How do you prevent hallucinated numbers?

Indicators and money are computed by code, locked into typed case evidence and checked in the order path. The model may still write an unsupported sentence. Citation existence and route agreement are necessary checks, while semantic faithfulness requires human/calibrated-judge evaluation.

### 8. What is MCP and where is it actually used?

MCP is the structured protocol between the agent runtime and the market, strategy and knowledge services. It carries tool schemas, arguments and results. Local development uses stdio and Docker uses HTTP. An OpenRouter tool call is translated into a real MCP invocation by the local runtime; it is not itself an MCP server request.

### 9. What happens when a tool fails?

The specialist receives a structured error observation and can correct its permitted request within finite budgets. Missing required evidence prevents final success. Unknown/write tools are denied by role scope. There is no bypass that converts an error into approval.

### 10. Show an actual replan.

The contract test plants a contradictory market answer after a tool observation. Code rejects the hand-off, records `replan`, and the specialist corrects it within seven total calls. That test uses mocked model responses; show a real recorded provider trace as separate evidence when available.

### 11. Why isn't a model-generated approval enough?

The model has no approval capability. LangGraph pauses for the human, and the token is issued only after approve with the current exact payload hash. Hash mismatch, expiry, stale quotes or risk failure blocks submission.

### 12. How do you avoid duplicate simulated orders?

The request ID and payload hash identify the action. A repeated identical request returns the stored result; a changed payload under the same ID is rejected. After timeout the workflow reconciles by ID rather than blindly retrying.

### 13. Can the graph survive a restart?

The order graph uses a SQLite checkpointer and a persisted context store. A test closes/reopens the checkpointer and resumes approval with edit validation. Mid-LLM-call research resume is not currently implemented.

### 14. What does memory retain?

Order checkpoints retain typed workflow state. The reviewed playbook retains proposed/accepted/rejected conditional lessons and reviewer reasons. Research uses only relevant accepted lessons from a frozen version. It does not automatically learn from every trade or retrain a model.

### 15. What is Reflexion versus fine-tuning?

Reflexion drafts a written lesson from a scored development failure, gets human review, and retrieves that lesson later. Model weights do not change. A helpful effect still needs a held-out memory-off/on comparison.

### 16. How do you prevent evaluation leakage?

Keep expected labels out of model inputs/tools, hold scenario families in one split, keep independent owners for hidden cases, freeze lessons before held-out evaluation and do not tune on final results. A folder name alone does not prove independence.

### 17. What does Recall@5 measure?

The fraction of all labelled relevant passages returned in the top five, averaged across queries. Hit@5 only asks whether at least one relevant passage appears. Candidate labels must be checked for completeness.

### 18. What did the measured retrieval change improve?

The initial offline run showed no rewrite improvement. After the corpus/neural upgrade, on 101 authored development queries Recall@5 was 0.9505 without rewriting and 0.9703 with rewriting. The old 36-query labels also show a regression versus the small original corpus. Report both findings and obtain independent relevance review before claiming generalization.

### 19. Are your 32 attack results proof of LLM security?

No. The local result is regex scanner detection on seeded attack text. Model-level E2 runs poisoned observations and checks authored unsafe behaviours/false blocks with scanner off/on, while hard execution controls stay enabled.

### 20. Why use a different-family judge?

To reduce correlated errors between solver and judge. We still compare the judge with at least 20 independent human labels and report kappa. A different family alone does not make a judge correct.

### 21. How do you prevent look-ahead in the backtest?

Compute a signal from completed day T and enter no earlier than a later eligible bar's open. The prior-high window is shifted, indicators use past history, and evaluation slicing retains earlier warm-up. Corporate actions/universe effects still require real-data review.

### 22. What is a stop-loss guarantee?

There is none. It is a predefined exit level. Opening gaps, slippage and liquidity can produce a larger realized loss; the simulator models adverse gap filling.

### 23. Why is the passive benchmark different from the router?

It invests equal allocations at the first selected open and holds, with the same costs but no active stops/exposure caps. It provides context, not a risk-identical strategy comparison.

### 24. What changed after reviewing the sources?

We replaced the single-agent C2 with a scoped three-specialist team, made C1 a fair tool-using baseline, connected real MCP, made passing C2 research mandatory before supervised proposals, connected frozen lessons, added real dev reflection, corrected recall/attack metrics and fixed numerical/trading safety defects. External evidence remains separately tracked.

### 25. What is unfinished before final submission?

Successful funded C1/C2 traces, independent gold/attack/retrieval labels, actual different-family judge predictions/calibration, model-level E2 and held-out E3, clean-machine deployment, a real alert and hosted failed CI, a final report/deck/video and licensed historical-data validation.

### 26. What would be needed for real users or live trading?

A separate production design: robust identity/roles, persistent portfolio accounting, secrets management, concurrency/security testing, licensed point-in-time data, operational monitoring and domain/legal review. Live trading is outside this capstone. The current project does not certify regulatory compliance.

### 27. Which parts did AI coding tools help with?

Be transparent about assisted implementation. The guideline permits coding assistance, but the team must understand and defend problem framing, design, labels, evaluation and interpretation themselves. Demonstrate ownership by reproducing checks and explaining failures.

## Appendix A. Code map for individual study

| File | What to understand for viva |
|---|---|
| `app/ui.py` | User journey, consent, pre-run plan, hand-offs, C2-to-order link, approvals and emergency control. |
| `app/api.py` | Reviewer auth, configuration gates, saved-run provenance, workflow start/resume, reflection and metrics. |
| `aegistrade/agentic.py` | C1/C2 shared budgets, specialist loops, LangGraph supervisor, role scope, correction, trace and final guard. |
| `config/agents.json` | Six-slot prompt inputs, role tools, version, temperature and budgets. |
| `aegistrade/llm_research.py` | OpenRouter HTTP client, usage/error sanitization, typed schemas and C0 dispatch. |
| `aegistrade/mcp_runtime.py` | Persistent stdio/HTTP sessions, credential-limited child environments and tool mapping. |
| `aegistrade/agent_tools.py` | Whitelisted case evidence, model-controlled query schema and deterministic route lookup. |
| `mcp_servers/*_server.py` | Six server definitions, 13 typed tools; only three read research tools reach LLMs. |
| `aegistrade/knowledge.py`, `corpus.py`, `vector_store.py` | Neural hybrid ranking, true recall, source/date validation, persistent Chroma and optional Qdrant path. |
| `aegistrade/market.py`, `strategies.py` | Synthetic provenance, OHLCV checks, indicator warm-up and exact strategy rules. |
| `aegistrade/engine.py`, `simulation_service.py` | Next-bar fills, cash/positions, stops, daily-loss gate, stale marks, benchmark and JSON. |
| `aegistrade/safety.py`, `workflow.py` | Exact hash, risk calculations, approval interrupt, edit loop, quote checks and reconciliation. |
| `aegistrade/lessons.py`, `memory.py`, `reflection.py` | Human review, applicability, freeze, development-only lesson generation and limitations. |
| `evaluation/run_capstone.py` | E1–E4, independent labels, shared budget, repeat protocol, trajectories and metrics. |
| `evaluation/run_eval.py`, `judge_agreement.py` | Offline reference/proxy limits, intentional CI failure, actual-label calibration. |
| `tests/` | Executable evidence and the distinction between real protocol tests and mocked model responses. |

## Appendix B. Submission checklist and honest status

Before final grading, retain: README and reproducible setup; actual architecture and numbered walkthrough; MCP schemas/tests; memory policy and threat model; versioned prompts/model IDs; independently reviewed golden/retrieval/attack datasets; E1–E4 experiment logs; calibrated-judge evidence; a 4–6-page evaluation report; contributions log; final slides; backup demo video; clean-machine installation, alert and failed-CI records.

The required order is: market analysis → completed C2 research → critic and code checks → code-sized order → human approval → final freshness/risk checks → simulated submission. If C2 cannot finish because of provider errors or credits, order preparation is unavailable. Historical backtests remain usable without model calls.

The three-person exception is settled. Do not spend time requesting it again. Spend that effort on evaluation ownership and evidence.

A valid final claim is “we implemented and tested a bounded agentic research platform with exact-payload control.” An unsupported claim is “our AI is profitable, fully secure, compliant or better than baselines” without the corresponding measurements.

## Source references

1. `capstone_fullstack_projects.pdf`, supplied by the user: pp. 2–3 architecture/minimum bar; pp. 4–6 roles, stack and experiments; p. 17 viva questions. Its finance Analyst Desk example is a reference architecture, not a requirement to replace this approved trading topic with SEC filing analysis.
2. `AegisTrade_AI_Capstone_Project_Proposal_and_Design.docx`, supplied design version, 26 October 2026: strategy/risk examples, architecture, experiments and initial team assumption.
3. `AegisTrade_AI_Initial_Proposal.pptx`, supplied four-slide concept deck: proposed pipeline, five phases, team split and intended evidence.
4. Repository source, `docs/CAPSTONE_GAP_REVIEW.md`, `docs/MCP_TOOL_INVENTORY.json`, `docs/BUILD_AND_VERIFICATION_STATUS.json` and locally produced development reports.
5. Provider protocol reference: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request . Provider billing/availability must be verified in the owning account before paid experiments.



## Appendix D. NSEPython data, automatic selection and updated UI

### NSEPython data and stock selection

Updated 9 November 2026. This is a 20-stock research subset of the Nifty 50, not an official “Nifty 20” index.

### Recommended capstone design

Use automatic historical replay for repeatable portfolio experiments after the user approves the selection/risk/cost assumptions. Demonstrate GenAI separately through the supervised path: deterministic shortlist → completed C2 market/strategy/critic research → code checks and sizing → exact human approval → final freshness/risk checks → simulated submission. The backtest does not ask an LLM to approve every historical fill and does not claim LLM-generated returns. C2 remains mandatory before every supervised proposal.

The ideal scientific universe is a genuine dated Nifty 50 membership snapshot from before the evaluation starts, or point-in-time membership if reconstituting throughout the study. Historical membership is different from historical prices. NSE Indices offers constituent-data products; do not pretend a current CSV is a historical constituent archive.

The implemented initial dataset uses the current official constituent CSV, explicitly marked `survivorship_bias: true`. The top 20 are then frozen using pre-period liquidity only. This avoids choosing five-year winners, but does not remove membership survivorship bias. For a rigorous rerun, supply a reviewed official constituent snapshot and its date using the downloader's `--constituents` and `--membership-asof` options.

### Downloaded dataset and provenance

- Library: nsepython 2.101, using its date-ranged equity-history interface, EQ series.
- Official universe CSV: https://archives.nseindia.com/content/indices/ind_nifty50list.csv . The other official host timed out; the NSE archive host succeeded.
- Evaluation window: 8 November 2021 through 8 November 2026, inclusive.
- Extra history for warm-up and pre-period ranking starts 1 July 2021.
- Downloaded rows: 26,580 across 20 stocks. Each stock has 1,242 rows inside the evaluation window and 1,329 rows including warm-up.
- Local OHLCV CSV: `data/nse_nifty20/ohlcv.csv`.
- Provenance, selected universe, ranking and checksums: `data/nse_nifty20/manifest.json`.
- Resumable request chunks: `data/nse_nifty20/chunks/`.
- Active source configuration: `data/market_config.json`, set to nsepython. This does not contain any API key.

The selected stocks, in frozen liquidity-rank order, are TMPV, RELIANCE, TATASTEEL, BHARTIARTL, INFY, TCS, SBIN, HDFCBANK, BAJFINANCE, ICICIBANK, KOTAKBANK, AXISBANK, HCLTECH, ITC, BAJAJFINSV, MARUTI, TECHM, HINDALCO, ADANIENT and HINDUNILVR.

A short warm-up sample was downloaded for the candidate list to screen it; full five-year histories were downloaded only for the selected 20. Full-history downloads for all 50 were not needed. The candidate list contains current members; the historical ranking is not proof that all those members belonged to the index in 2021.

Verified NSE symbol-name circulars support ZOMATO→ETERNAL, SRTRANSFIN→SHRIRAMFIN and TATAMOTORS→TMPV identifier normalization. Their official sources are recorded in `config/nse_symbol_aliases.json` and the manifest. This mapping does not adjust merger/demerger, split, bonus or distributed-share economics. Unexpected aliases stop the downloader instead of silently joining unrelated securities.

### Reproducible stock-picking criteria

There are two selection stages.

**Stage 1, freeze a 20-stock research universe:** before the evaluation start date, take up to 60 sessions per candidate and rank average daily Close × Volume, with at least 20 prior sessions. Pick the top 20. Only dates earlier than the evaluation start are allowed into this calculation. The ranking is not market capitalization, index weight, or return over the evaluation period.

**Stage 2, select trade candidates at each completed close:** screen the fixed universe using the following frozen research rules.

| Criterion | Rule |
|---|---|
| Data readiness | At least 60 historical sessions and ready indicators |
| Liquidity | At least ₹1 crore mean daily traded value over 20 sessions |
| Market risk | Abstain for HIGH_VOL, UNCERTAIN or WARMUP |
| ATR | Positive ATR; ATR/Close no greater than 6.5% |
| Price discontinuity | Exclude new candidates for 20 sessions after a raw close-to-close jump over 30%; this is a quarantine, not an adjustment |
| Entry | A valid existing EMA, RSI or breakout entry signal |
| Affordability | At least one whole share fits cash, planned-risk and position-value caps |
| Capacity | Exclude already-held symbols; at most four concurrent positions |
| Circuit breaker | No new entries when the daily-loss gate is active |

Eligible stocks receive a deterministic score: 70% strategy-specific signal strength, 20% same-session liquidity percentile and 10% lower ATR-fraction preference. Trend strength uses ADX plus 20-session momentum; RSI strength measures depth below the entry threshold; breakout strength uses breakout distance and relative volume. Exact formulas live in `aegistrade/selection.py` and are identified by `nifty20-selection-v1`.

Scores sort descending, with symbol as a stable tie-breaker. Selection uses only information available at that completed session. It does not read the remainder of the backtest period. Actual fill price and quantity are recomputed at a later eligible open, including fees/slippage. A ranked candidate can still be unfilled because of the next opening gap, cash constraints or risk checks.

Twenty stocks is the research universe, not the number of simultaneous positions. With limited money, fewer than four stocks may be affordable and cash may remain uninvested. The system should not force a trade simply to deploy all the capital.

These are explicit research hypotheses/settings, not promised profitable stock recommendations. Freeze them before held-out testing and report negative findings.

### Updated UI journey

### Market Data

This new workspace shows the download status, selected-stock count, cached chunk count, requested period, membership date/mode, top-20 ranking and per-stock coverage. It shows survivorship and unadjusted-price limitations. When the dataset is complete and not active, the authenticated reviewer can acknowledge its provisional nature and activate it. Activation persists the data-source setting and resets the API's data cache.

The downloaded NSE dataset is already configured as active in this workspace. Restart the running API/dashboard so the older process loads the new code and configuration. Use “Prepare OHLCV CSV download” and then “Download active OHLCV CSV” to export the active series.

### Overview

Charts now support five-year-sized history windows. The page displays the actual source and universe size. NSE raw-data and membership limitations appear at the top. The displayed workflow includes automatic selection, completed C2 research and mandatory approval.

### Strategy Backtests

Choose the date interval, starting money, risk, fees and slippage. Automatic screening/ranking is enabled by default. Approve the displayed assumptions before starting automatic historical replay. ROUTER and the three fixed strategies remain comparable configurations.

Results include the portfolio curve, cash/positions, passive benchmark and simulated ledger. Expand “Automatic stock-selection audit,” choose a date, and inspect ranked stocks, estimated shares and human-readable rejection reasons. “Research automatically selected stocks with C2” transfers the server-saved ROUTER run ID, date and capital into the research workspace; it makes no paid call by itself. It is disabled for fixed-strategy baselines or dates with no selected candidates. The research service reads the saved audit and restricts the hand-off to stocks that run actually selected.

### AI Agent Experiments

The no-spend shortlist preview shows code-generated candidates and rejection reasons. “Research automatically ranked eligible stocks” is enabled by default. The final selected date is used for the shortlist; early data outside the evaluation interval can supply indicator warm-up. Up to three of the highest-ranked eligible candidates are passed into the existing C0/C1/C2 comparison interface. If fewer qualify, fewer are run. If none qualify, no model call is made.

C2 is the main supervised research configuration. Its market evidence includes the code-produced selection score, rank and traded-value metric. Model tools do not get hidden future returns. C2 may fail or abstain; only completed, critic-accepted, code-validated C2 results unlock the next step. Reviewer authentication and explicit paid consent are still required.

The standalone research screen uses reference capital and the default supervised risk policy. A historical portfolio may have different cash/positions or a user-selected backtest risk percentage. The preview is therefore not an instruction to submit a trade from the historical portfolio ledger.

### Supervised Trading

A linked passing C2 case is mandatory. No unresearched manual stock picker or bypass exists. Starting the proposal revalidates the saved research and exact market data, computes quantity/stop/risk with code, then displays the full proposal for human approve/edit/reject. Resume rechecks the research digest and current evidence. Final quote, risk, kill-switch and idempotency checks remain unchanged. The broker remains a local simulator.

### Commands and caching

Install the market dependency if using a fresh environment:

```bash
.venv/bin/python -m pip install -r requirements-market.txt
```

Download/resume the current-constituent prototype:

```bash
.venv/bin/python -m scripts.download_nifty20
```

Use a genuine pre-period constituent snapshot for a new scientific run:

```bash
.venv/bin/python -m scripts.download_nifty20 --constituents path/to/official_dated_snapshot.csv --membership-asof 2021-10-29 --start 2021-11-08 --end 2026-11-08 --output data/nse_nifty20_historical
```

The example date is a user-supplied provenance declaration, not a claim that the repository includes that historical membership file. Do not relabel today's file with an older date. The tool does not purchase or fabricate membership history.

The warm-up rows cannot be used to evaluate an earlier trading window: that would evaluate dates preceding the frozen-universe selection. UI and backend enforce the evaluation start boundary while retaining earlier rows for indicators.

Requests are made in sub-40-day intervals through nsepython and cached. A provider error aborts rather than silently omitting a stock or falling back to synthetic/Yahoo prices. Re-running resumes cached intervals. SHA-256 and universe checks protect the completed cache from accidental modification; a minimum session-coverage check detects major truncation but is not a full exchange-calendar audit.

### Verification and limits

The NSE sample and full download succeeded. A ₹200,000 ROUTER replay across the evaluation window completed with 1,242 sessions, 24,840 selection-audit rows and 326 ledger events; it made zero paid LLM calls. Its run ID is recorded in `reports/nse20_simulation_smoke.json` and the complete saved result is in `data/simulation_runs/`. These are provisional raw-price replay outputs, not a return-performance claim.

All 72 tests pass. The UI was also exercised against the actual downloaded cache, including Market Data rendering, CSV export, the research screen and no-spend stock screening.

Tests check schema normalization, vetted aliases, bounded/resumable cache requests, future-data exclusion, selection feature causality, affordability and discontinuity filters, no model spend for an empty shortlist, dataset integrity and the interactive UI hand-off. The pre-existing mandatory-C2 and human-approval tests remain in force.

Two limitations are especially material: current constituent membership introduces survivorship bias; raw prices do not reconstruct splits, bonuses, mergers/demergers, distributed holdings or cash dividends. The new-entry discontinuity filter cannot repair an already-held position affected by a corporate action. Resolve those issues before interpreting returns as valid real-market strategy evidence. The data pipeline and the engineering workflow can still be demonstrated and evaluated honestly.

Official references: NSEPython source https://github.com/aeron7/nsepython ; documentation https://unofficed.com/nse-python/documentation/nsepy/ ; Nifty 50 constituents https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50 ; constituent-data products https://niftyindices.com/offerings/data-subscription .

## Appendix E. Verified RAG implementation and knowledge data

### RAG implementation and knowledge data

Updated 9 November 2026.

### Is RAG implemented?

Yes. C2's strategy and compliance-critic specialists call `search_policy` through an actual FastMCP connection. The tool retrieves source-labelled passages, and its observations are sent back to the LLM before it generates a cited typed response. Citations, required tool evidence, a project-policy source and the current corpus fingerprint are checked before a supervised proposal is allowed.

The earlier implementation had 16 short policies and an active BM25/TF-IDF teaching baseline. The project now has 81 curated passages, actual local neural embeddings, a neural reranker and persistent Chroma storage. The private retrieval mode has been changed to `neural` after successful index verification. Restart the running API/dashboard to load it.

The language generation still uses the project's OpenRouter integration and paid-run gates. The embedding and reranking models run locally on CPU; this update made no paid OpenRouter request. Retrieval is a component of GenAI, not proof of generation by itself: the Policy Knowledge page lists evidence, while C2 uses that evidence to generate an explanation.

### What data was added?

| Material | Count | Examples |
|---|---|---|
| Project policies and code-derived specifications | 72 passages | Exact EMA/RSI/breakout rules, regime precedence, top-20 liquidity selection, scoring weights, money/risk rules, C2 completion gate, approvals, stale quotes, reconciliation, memory and evaluation limits |
| Source-linked background references | 9 passages | Official Nifty 50/index-data descriptions, NSE daily-price field definitions and verified symbol-change circulars; upstream NSEPython project description |

The corpus is `knowledge/corpus.jsonl`, with a scope manifest in `knowledge/manifest.json`. The code-derived material is authored from the current implementation and explicitly marked pending team review. External summaries carry original-source URLs. They are not new trading rules, company research reports or independently reviewed gold labels.

The original POL-01 through POL-16 identifiers remain. Additional project passages extend through POL-72. Background references use REF-prefixed identifiers. Passage metadata retains title, source, date, date kind, authority, topic, code/document locator or original URL, publication/retrieval dates where known, and review status.

More rows are not automatically better RAG data. The corpus adds relevant missing concepts rather than stuffing price tables into embeddings. The 26,580 OHLCV rows remain numerical data accessed by code; an LLM must not reconstruct prices or money from approximate vector matches.

### Retrieval and generation sequence

1. The specialist chooses its policy query inside its role/tool budget.
2. The runtime sends that query and the locked case date to the knowledge MCP server.
3. Controlled query rewriting expands a few known aliases while retaining the original query.
4. BM25 retrieves lexical matches. MiniLM embeds the query and searches the persistent cosine-vector index.
5. Reciprocal Rank Fusion combines the two rankings using 1/(60 + rank).
6. The cross-encoder scores the candidate query/passage pairs and reranks them. The configured top passages are returned with source and corpus metadata.
7. The tool observation is appended to the specialist conversation, linked by tool-call ID. The OpenRouter model reads the observations and generates its typed answer.
8. Code checks that cited IDs were actually retrieved and that at least one cited source is a project policy. Public background alone cannot ground route approval. Typed strategy/risk/approval checks remain independent controls.

Current models are `sentence-transformers/all-MiniLM-L6-v2` for 384-dimensional embeddings and `cross-encoder/ms-marco-MiniLM-L6-v2` for reranking. They use public pretrained weights, CPU execution and no remote custom model code. Exact cached model revisions are recorded by the index build. Model scores are ranking values, not calibrated confidence or a probability of profitable trading.

The persistent index is in `data/rag/chroma/`; reusable embeddings are in `data/rag/embedding_cache/`; public model weights are in `data/model_cache/`. `data/rag/index_status.json` records the verified corpus fingerprint, model identity, collection and smoke queries. The corpus is versioned source data; caches and weights are local runtime data.

Qdrant remains an alternative Docker/configured endpoint. Local Chroma was actually exercised. This does not claim that the Qdrant HTTP deployment or a clean-machine Docker run has been demonstrated.

### Historical availability and authority

An external reference is available to a historical case only if its verified publication date is on or before the case date. When publication is unknown, its retrieval date is used conservatively. The model cannot choose a later cutoff: the runtime takes the date from the locked case. The Policy Knowledge page also offers a historical cutoff for inspection.

Project policies describe the experiment's declared settings and are identified separately. They are not represented as company news published in a past market session. Current news, future returns and held-out answers have not been added to the historical decision corpus. A genuine historical-news or company-filings service would require separate point-in-time ingestion, licensing/provenance and evaluation; it is outside this RAG scope.

C2 results record the corpus SHA-256. Changing the corpus, or trying to approve an older result without corpus provenance, requires rerunning current C2 before a new supervised proposal/approval. This keeps an earlier explanation from silently becoming an approval under changed knowledge.

### Measured development results

`reports/rag_development.json` records the configurations and per-query results. The expanded development set contains 101 unique query IDs; the earlier file's repeated IDs were corrected while keeping its query text and labels. These are authored development candidates, not independently labelled held-out data.

| Same expanded corpus, 101 development queries | Passage Recall@5 |
|---|---|
| Offline BM25/TF-IDF plus rewriting | 0.9208 |
| Neural hybrid plus reranker, without rewriting | 0.9505 |
| Neural hybrid plus reranker, with rewriting | 0.9703 |

The rewriting comparison holds corpus, models, vector store and reranker fixed and changes only the query-side technique. MRR@5 and nDCG@5 are also recorded. These scores describe current-knowledge lookup without a historical cutoff; the temporal filter is separately contract-tested and exercised in the MCP path.

A regression is retained: on the old 36-query labels, the original 16-passage offline corpus scored 0.9444 Recall@5, while the expanded neural corpus scored 0.9167. More passages create competing evidence, and the legacy labels are not exhaustive across the expanded corpus. Do not claim universal improvement or silently change labels to make the score rise. The team should review relevance independently.

Retrieval scores do not establish generated-answer faithfulness, useful stock-selection performance, trading profitability or different-family judge calibration. Those still need actual funded C1/C2 runs, human/independent assessment and the capstone evaluation protocol.

### UI and viva demonstration

Open Policy Knowledge after restarting the app. It shows passage counts, project/reference counts, the active pipeline and whether the verified index matches the current corpus. Searches display passage text, authority, indexed/reviewed date, original publication date when known, and original-source/code links.

Useful queries include:

- “Is the RSI entry threshold 30 or 42?”
- “Why were these twenty stocks selected?”
- “What happens if C2 research changes before human approval?”
- “Are NSE prices adjusted for splits, bonuses and demergers?”

Then show a C2 trace containing a search_policy observation, source IDs, corpus fingerprint and typed specialist response. Be explicit about whether that trace is a real paid-provider run or a mocked contract test. Actual stdio MCP neural retrieval has passed with no paid generation. The UI's actual neural search and source display are verified separately; this is evidence of the retrieval path rather than a model-benefit claim.

A viva explanation is: “We retrieve lexical and semantic evidence, fuse and rerank it, then give source-labelled passages to the LLM. Code validates provenance and enforces policy. We measured retrieval separately from explanation quality.”

### Rebuild and extend

For a fresh environment install the project requirements. Linux/Docker/CI use CPU-only Torch to avoid unnecessary GPU dependencies. Model downloads need network access once; after successful caching the project sets HF_HUB_OFFLINE=1 for local model loading. OpenRouter generation still uses its normal internet connection.

```bash
.venv/bin/python -m scripts.build_rag_index --mode neural --activate
HF_HUB_OFFLINE=1 .venv/bin/python -m evaluation.run_rag_eval
```

If deliberately fetching new model weights, temporarily set HF_HUB_OFFLINE=0 for the build command. No OpenRouter key is needed to build or evaluate retrieval.

To curate a replacement corpus, preserve stable IDs and the core policies; add short, source-labelled passages with publication metadata rather than unreviewed prompts or draft proposal instructions. Validate JSON/JSONL with `scripts/ingest_policies.py`, set the intended corpus path, rebuild, repeat evaluation and obtain team review. A custom path replaces the corpus rather than appending hidden extra instructions.

For a new Docker data volume, populate the model/index cache before the paid demonstration, for example `docker compose run --rm -e HF_HUB_OFFLINE=0 api python -m scripts.build_rag_index --mode neural`. The local cache is not automatically copied into a Docker named volume. The existing neural Compose override selects Qdrant; that runtime path remains separately unverified.

### Evidence and remaining work

The source corpus, schema, index builder, persistent store, evaluation runner, MCP source metadata, historical cutoff and UI are implemented. Tests cover provenance, bad source links, corpus changes invalidating approval, background-only citations being rejected, date filtering, persistent-vector round trips and retrieval/UI integration.

The team still needs independent relevance review/held-out queries and calibrated semantic evaluation of real generated explanations. There is no need to add company news or thousands of price chunks merely to increase document count. Add such sources only if expanding the project's actual research question and point-in-time controls.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
