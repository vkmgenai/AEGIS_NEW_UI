# 🛡️ AegisTrade AI

**Current final-review source: v0.28.0 — C0/C2 portfolio design with C1 retained as the required evaluation-only baseline.**

Final submission navigation:

- [Final project report](docs/FINAL_PROJECT_REPORT.md)
- [Final detailed architecture and numbered walkthrough](docs/FINAL_ARCHITECTURE.md)
- [Team experiment-review questionnaires](docs/TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md)
- [Evidence and LLM-assistance guide for answering team questionnaires](docs/TEAM_REVIEW_EVIDENCE_AND_LLM_ASSISTANCE_GUIDE.md)
- [Background experiment ledger and replay guide](docs/CAPSTONE_EXPERIMENT_LEDGER_GUIDE.md)

Retained capstone runs are also visible in Streamlit under **Workspace → Capstone Evaluation**. This read-only viewer shows manifests, summaries, lifecycle events and report downloads without making model calls.
- [Final presentation and UI demo guide](FINAL_PRESENTATION_README.md)
- [Capstone completion checklist](docs/FINAL_CAPSTONE_COMPLETION_CHECKLIST.md)
- [Threat model](docs/THREAT_MODEL.md) and [memory policy](docs/MEMORY_POLICY.md)

One-command local start on macOS/Linux: `bash scripts/start_unix.sh`. Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_windows.ps1`.

**GitHub-ready local capstone research application**  
**SIMULATION ONLY — no broker connection, real-money order placement, leverage, or intraday execution.**

AegisTrade is a human-governed multi-agent algorithmic trading research platform. It combines cached NSEPython daily OHLCV (with explicit synthetic test mode), automatic stock screening, EMA/RSI/breakout strategies, a deterministic risk engine, policy retrieval, a LangGraph approval workflow, a mock order gateway and an audit trail. A selectable Codex CLI or OpenRouter transport provides actual model inference for evidence-grounded specialist research.

> **Academic status:** An integrated research prototype. Passing unit tests does **not** prove profitable trading or satisfy all final capstone evaluation requirements. The README and `docs/COMPLIANCE_AND_REMAINING_WORK.md` distinguish implemented code from missing research evidence.


## New: configurable capital and web-based C0/C1/C2

In **Strategy Backtests → C0 Technical baseline**, enter a starting capital (e.g. ₹200,000) and historical start/end dates. The dashboard uses the fixed ROUTER risk/cost policy documented below so C0 and C2 remain directly comparable. Compare returns, drawdown, equity curves, order ledger and reopen saved simulations.

In **AI Agent Experiments**, select C0 (no key, zero LLM calls), C1 (one tool-using agent), C2 (LangGraph supervisor plus market, strategy and compliance-critic specialists; normally six inference units) or ALL. C1/C2 share an eight-inference-unit ceiling per case and the same available tools. The UI caps cases at three and requires explicit consent for inference. The reviewer credential is loaded internally from `.env`, not typed or displayed, and the system does **not** place any trading orders.

External inference is **disabled by default**. Select `AEGIS_LLM_BACKEND=claude_cli` for Claude login, `codex_cli` for supported ChatGPT login or `openrouter` for a private API key, or choose the provider later from the dashboard dropdown; set `AEGIS_ENABLE_LLM_EXPERIMENTS=true` and consent to each run. The current local configuration uses Codex with ChatGPT sign-in. Plus has usage limits and does not fund OpenRouter. Never commit `.env`.

For update instructions see [docs/CAPITAL_AND_AGENT_UI_UPDATE.md](docs/CAPITAL_AND_AGENT_UI_UPDATE.md).


### End-to-end C2 historical portfolio (v0.27)

In **Strategy Backtests**, select **C2 historical portfolio**, dates/capital and total inference allowance. Configure reviewer authorization in `.env`, then provide inference consent and upfront replay-rule approval. C2 uses five routes: EMA Trend, EMA Pullback, RSI Reversion, Breakout and SMC. A bounded ranked pool (fixed at three) lets C2 consider the next technical candidate when a higher-ranked candidate is evidence-blocked; missing evidence is never labelled fundamental strength. Every prospective entry requires completed dated C2; five-session holding reviews return HOLD/EXIT. Code applies fixed stops/strategy exits, next-open sizing/fills and portfolio accounting. Jobs pause/resume at bounded checkpoints and retain research traces. **The end date does not force a sale**: open holdings remain marked with unrealized P&L. The **C0 Technical baseline** runs the same ROUTER financial policy without generation. C1 is no longer a portfolio flow; it remains in AI Agent Experiments for the fair single-agent comparison.

## Quick start: local computer

**Prerequisites:** Python 3.11 or 3.12, internet for installing packages, and a terminal. No GPU, OpenRouter key, or real trading account is necessary.

### Windows (PowerShell)

```powershell
cd path\to\aegistrade-ai
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_windows.ps1
```

This creates `.venv`, installs packages, creates a private `.env`, and launches the API and dashboard. For manual steps, use [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

### macOS / Linux

```bash
cd /path/to/aegistrade-ai
bash scripts/start_unix.sh
```

This performs the same actions using a local `.venv`.

**Open these local addresses:**

| Service | Address | Description |
|---|---|---|
| Streamlit frontend | http://127.0.0.1:8501 | Main visual dashboard |
| API landing page | http://127.0.0.1:8000/ | Links to dashboard, API documentation and health |
| FastAPI backend | http://127.0.0.1:8000/docs | Interactive API documentation |
| API health | http://127.0.0.1:8000/health | Connection check |

To use **Approve / Edit / Reject**, copy `AEGIS_REVIEWER_TOKEN` from your private, ignored `.env` into the Streamlit sidebar. **Do not paste this secret in GitHub or screenshots.**

Stop both services with `Ctrl+C` in the launch terminal.

### Docker Desktop (alternative)

```bash
python scripts/bootstrap.py     # creates local .env with random demo credentials
# Main app only, fast to start:
docker compose up --build api dashboard
# Or start everything (Prometheus, Grafana and internal read-only MCP servers):
docker compose up --build
```

Grafana is at http://127.0.0.1:3000, user `admin`, password `AEGIS_GRAFANA_PASSWORD` in `.env`.
Docker builds require an internet connection on the first build.


### Updated UI and hands-on testing

The Streamlit frontend uses a high-contrast native light theme and an always-visible Workspace selector. Its capstone workspaces are **Market Data**, **Overview**, **Strategy Backtests**, **AI Agent Experiments**, **Capstone Evaluation**, **Policy Knowledge**, and **Learning & Lessons**. The single-stock C0/C2 comparison now sits beside the portfolio workflows. Grounded C2 BUY/SELL recommendations, human approve/reject consent and their audit ledger sit inside AI Agent Experiments; separate Supervised Trading and Broker Audit navigation was removed. Use the [Simplified UI Demo Guide](docs/SIMPLIFIED_UI_DEMO_GUIDE.md).

For your Plus account, start with the [ChatGPT Plus Full UI Demo Runbook](docs/AegisTrade_ChatGPT_Plus_Full_UI_Demo_Runbook.docx). It includes verified genuine C2 research and a tiny portfolio, all UI steps, approvals, exit behavior, quotas and reversible configuration switching. OpenRouter remains a separate option.

For free OpenRouter account practice, use the [Free OpenRouter UI Demo Runbook](docs/AegisTrade_Free_OpenRouter_UI_Demo_Runbook.docx): local-only rehearsal, one bounded free-model C2 attempt and an optional tiny portfolio.

Start with the [Project Summary and UI Overview](docs/AegisTrade_Project_Summary_and_UI_Overview.docx) for a plain-language introduction to the project and all eight workspaces.

For the current source-reviewed documentation (11 November 2026), use the separate [Detailed Design and Demo Guide](docs/AegisTrade_Detailed_Design_and_Demo_Guide.docx) and [Viva Questions and Answers](docs/AegisTrade_Viva_Questions_and_Answers.docx). The design guide includes seven diagrams, all eight UI workspaces, demo preparation and the guideline gap matrix. The viva handbook now has 101 questions and answers. Version 0.15 retains mandatory dated company filings/issuer-news research through the existing three specialists; see [Historical Company Research](docs/HISTORICAL_COMPANY_RESEARCH.md) for source scope, cutoff rules, preparation and reviewed newsletter imports. Completed C2 research is mandatory before a supervised order proposal; technical-only replay uses no generation; C2 historical replay uses dated entry research, scheduled holding reviews and explicit exits under upfront rule approval. Earlier manuals may describe superseded behavior. For changes see [docs/UI_CHANGELOG.md](docs/UI_CHANGELOG.md). Restart both services after source or configuration updates.

## Repository layout

```text
aegistrade-ai/
├── .github/workflows/ci.yml       # GitHub Actions unit testing
├── .env.example                   # Safe config template (copy via bootstrap)
├── .gitignore, .dockerignore      # Keep secrets, virtualenv, DBs out of Git
├── Dockerfile, docker-compose.yml # Local containers, monitoring, MCP servers
├── pyproject.toml                 # Python package metadata
├── requirements.txt              # Local installation entry point
├── aegistrade/                   # Core domain logic (NO live broker)
│   ├── market.py                  # Synthetic and opt-in research data
│   ├── strategies.py              # Indicators and regime-aware routing
│   ├── engine.py                  # Daily-bar backtesting & portfolio
│   ├── safety.py                  # Typed orders, risk, approval hash, mock broker
│   ├── workflow.py                # LangGraph supervisor and specialists
│   ├── knowledge.py               # Hybrid policy retrieval (offline / neural)
│   ├── openrouter.py              # Optional budget-limited explanation
│   ├── memory.py, lessons.py      # Memory and human-reviewed Reflexion lessons
│   └── evaluation.py, experiments.py, security.py, ...
├── app/
│   ├── api.py                     # FastAPI backend routes
│   └── ui.py                      # Streamlit frontend (port 8501)
├── mcp_servers/                  # Five read-only + one restricted-write FastMCP server
├── evaluation/                   # 60 candidate cases, 36 retrieval queries, 32 attacks
├── scripts/
│   ├── bootstrap.py               # Generate private .env
│   ├── launch_local.py            # Launch API + dashboard together
│   ├── smoke_local.py             # Verify local API endpoints
│   ├── start_windows.ps1          # Windows one-command setup/start
│   ├── start_unix.sh              # macOS/Linux one-command setup/start
│   └── demo_safety.py, demo_lessons.py, ...
├── tests/                        # pytest unit/integration tests
├── monitoring/                   # Prometheus, Grafana, alert definitions
├── docs/                         # Runbook, research gaps, threat/memory policy
├── reports/                      # Clearly marked synthetic reference outputs
├── notebooks/                    # OPTIONAL historical Colab notebooks, not required
└── data/                         # Runtime SQLite DBs (ignored by Git)
```

## Three commands for development

After installing dependencies, from the repository root:

```bash
python -m pytest -q
python -m evaluation.run_eval --split dev
python scripts/smoke_local.py         # Run while API is online
```

Other scenarios:

```bash
python -m scripts.demo_safety         # Exact order/hash, stale quote, timeout recovery
python -m scripts.demo_lessons        # Human-reviewed/rejected lessons
python -m scripts.mcp_smoke           # Requires installed FastMCP/adapters
```

## How to demonstrate the capstone

1. In **Dashboard**, inspect one synthetic symbol, closing prices, EMA20/EMA50 and the detected regime.
2. In **Strategy Backtests**, run the comparison and plot a router/fixed-strategy equity curve.
3. In **AI Agent Experiments**, review a grounded C2 recommendation and record APPROVE or REJECT with a rationale.
4. Enable **stale quote injection** and verify rejection. Enable **timeout injection** and inspect reconciliation.
5. In **Policy Knowledge**, retrieve numbered, dated approval/risk policy passages.
6. In **Learning & Lessons**, accept a valid development lesson and reject the unsafe lesson; freeze the playbook.
7. Expand **Human C2 decisions and simulated-action audit**, then open `/docs` or Grafana for operational evidence.

More detail: [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) and [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

## Optional OpenRouter access

The technical-only baseline uses no generative inference. C2 research and supervised researched orders require the selected inference backend. To use OpenRouter rather than Codex, set `AEGIS_LLM_BACKEND=openrouter`, clear `AEGIS_LLM_MODEL`, configure its private API key and enable experiments, then restart:

1. Put `OPENROUTER_API_KEY` into your **private `.env`**, never source code.
2. Set `OPENROUTER_MODEL` to the exact approved model identifier.
3. Run a small, separately recorded experiment:
   ```bash
   python -m evaluation.run_llm_experiments --config all --cases 1 --max-calls 8 --consent-paid --max-paid-calls 24
   ```
4. Preserve cost, token, latency, accuracy and failure traces. For a full claim of agentic benefit, compare the same inputs, tools and budget across C0/C1/C2.

The human-decision section in `AI Agent Experiments` requires completed, critic-accepted C2 research. Recording APPROVE/REJECT adds no model call and retains the validated research digest internally. Protected inference requires reviewer authentication and explicit consent.

## Publish the folder to GitHub

See [docs/GITHUB_PUBLISH.md](docs/GITHUB_PUBLISH.md). This ZIP is the **folder-based repository**; you do not need Google Colab. The optional notebooks are only retained as additional research artifacts.

## Important limitations

- **Synthetic-only by default.** Price levels and backtest results are not real NSE quotes or investment advice.
- **Local demo credentials are not production authentication.** Do not expose services to the public internet.
- **AI routing gains are not yet established.** Portfolio backtests use deterministic rules; C1/C2 research results require separate provider experiments and independent evaluation.
- **Evaluation labels are candidate synthetic cases.** Independent review, judge calibration, held-out repeats, independent retrieval labels and model-level red-teaming still need to be completed.
- **Local verification is not full deployment.** Tests, actual MCP stdio calls and SQLite resume passed. Docker configurations validate, but the daemon was stopped; paid-model and full Docker evidence remain outstanding; local neural RAG is verified.

Team: **Veneet** (quant/evaluation), **Karthika** (agents/orchestration), **Mathangi** (risk/platform). Three-member arrangement is faculty-approved.

Current documentation: [Viva handbook](docs/AegisTrade_Capstone_Review_and_Viva_Guide.md), [source-to-code gap review](docs/CAPSTONE_GAP_REVIEW.md), [tool schemas](docs/MCP_TOOL_INVENTORY.json), and [verification status](docs/BUILD_AND_VERIFICATION_STATUS.json).

Completed, critic-accepted C2 research is required before a BUY/SELL recommendation can be presented for human review in **AI Agent Experiments**. The run enters `WAITING_HUMAN`; the reviewer sees the explanation, policy citations and company evidence and records APPROVE or REJECT with a rationale and name/initials. This appends to a separate decision ledger and does **not** repeat any C2 model call. A fixed 10-session return is attached when historical data permits, only as outcome-review evidence. It can become a candidate for a later conditional lesson after human review; it is never learned automatically. Research memory-on requires a frozen reviewed playbook.

Use `python -m evaluation.run_capstone --experiment E4` for a free deterministic routing ablation. E1/E2/E3 require independently reviewed case inputs, explicit paid consent and an adequate call cap; see the handbook before running them.

The enforced sequence is market analysis → completed C2 research → critic/code checks → code-sized order → human approval → final freshness/risk checks → simulated submission. C0/C1 or pending/failed research cannot unlock approval. Start and resume revalidate the saved result and market evidence; changed research requires a new proposal. Older workflows without C2 provenance must be replaced after restarting the app.


## NSEPython data and automatic stock selection

The local cache now contains 26,580 OHLCV rows for 20 stocks, with an evaluation window of 2021-11-08 through 2026-11-08 and earlier indicator warm-up. `data/market_config.json` activates it after restarting the app. The chosen universe is frozen by pre-period liquidity; daily candidates are screened/ranked with only then-available data and capital constraints.

Use **Market Data** for provenance/coverage/export, **Strategy Backtests** for approved automatic historical replay and selection audits, then send ranked candidates to **AI Agent Experiments** for C2 and mandatory supervised approval. No C2 calls are made just by opening the shortlist or running the historical backtest.

[Data, selection and UI guide](docs/NSE20_DATA_AND_UI_GUIDE.md). The current snapshot has survivorship bias and unadjusted corporate actions; financial return outputs remain provisional. Genuine dated membership and corporate-action handling are still needed for rigorous market-effectiveness claims.


## Verified local RAG

The knowledge base now contains 81 passages: 72 project policies/specifications and nine source-linked background references. Local CPU MiniLM embeddings, BM25/RRF and a cross-encoder reranker use persistent Chroma. Actual neural API/UI and MCP retrieval passed; private mode is activated after restart. No paid LLM calls were needed for this work.

[Detailed RAG guide](docs/RAG_IMPLEMENTATION_GUIDE.md). Development Recall@5 was 0.9505 before and 0.9703 after rewriting on 101 authored queries; independent labels and semantic answer evaluation are still required. Legacy-query regressions are retained in the report. OHLCV data stays in the numerical market pipeline, not approximate text retrieval.

Rebuild: `python -m scripts.build_rag_index --mode neural --activate`. Evaluate: `HF_HUB_OFFLINE=1 python -m evaluation.run_rag_eval`. Cached local models need no Hugging Face token. C2 uses the selected inference transport with explicit consent; this policy RAG is not company-news/fundamentals research.

Current detailed RAG/viva documentation: [RAG Word guide](docs/RAG_IMPLEMENTATION_GUIDE.docx), [RAG source corpus](knowledge/corpus.jsonl), and [current full viva handbook](docs/AegisTrade_Capstone_Review_and_Viva_Guide.docx). The Policy Knowledge screen shows actual active mode, source links and historical cutoff; every C2 result must bind to the current knowledge-corpus fingerprint.

Research preflight fix (0.15.1): lesson memory is disabled until a nonempty reviewed playbook is frozen. Unavailable memory is rejected before archive/model work; the UI displays the actual API cause and next action. Screening previews use the submitted case date.

### Claude CLI transport and provider dropdown (0.28.0)

`aegistrade/llm_backend.py` now supports three transports: `claude_cli` (Claude Code CLI, Claude login), `codex_cli` (ChatGPT login) and `openrouter` (API key). One is active at a time and there is no automatic fallback.

- **Choosing in the dashboard.** The *Strategy Backtests* C2 flow and *AI Agent Experiments* show a **Run AI agents using** dropdown with all three retained adapters: **Claude CLI**, **ChatGPT/Codex CLI**, and **OpenRouter API**. Each is marked ready or not ready. Configure `AEGIS_REVIEWER_TOKEN` in `.env`, then press **Use this provider**. The credential is never displayed. The switch takes effect without a restart and is saved in `data/inference_backend.json`, which holds only the provider name. `AEGIS_LLM_BACKEND` in `.env` remains the start-up default.
- **Claude setup.** Install Claude Code and run `claude auth login` in Terminal. No API key is used: `ANTHROPIC_API_KEY`, the OpenRouter key and the reviewer token are not passed to the CLI. Optional settings: `AEGIS_CLAUDE_BIN`, `AEGIS_CLAUDE_MODEL`, `AEGIS_CLAUDE_TIMEOUT_SECONDS`, `AEGIS_CLAUDE_HOME`.
- **Same contract as Codex.** The CLI runs in print mode with a JSON schema, no native tools, no MCP servers, no slash commands and no saved session, from an empty temporary folder. AegisTrade executes every tool call and validates every answer. Limits count CLI invocations; the USD figure the CLI reports is recorded as notional and is not billed.
- **Saved runs.** A C1 or C2 run stays tied to the provider, model and adapter it started on. Switch back to that provider to resume it, or start a new run.
- **API.** `GET /inference/backends` lists the three providers with readiness; `POST /inference/backend` (reviewer token) switches. `AEGIS_LLM_MODEL` applies only to the provider named in `.env`.

### Codex / ChatGPT Plus transport (0.16.0)

`aegistrade/llm_backend.py` supports `openrouter` (default) and `codex_cli`; there is no automatic fallback. Codex uses documented `exec` structured output and supported ChatGPT login, with native tools disabled and AegisTrade retaining real MCP execution/validation. Set `AEGIS_CODEX_BIN` if necessary. CLI budgets count invocations, not internal provider requests; response-token settings are guidance, not hard provider token caps, and per-run USD cost is unknown. Historical jobs pin transport/model/adapter/unit and reject changed identity on resume. Use the local launcher: host CLI/auth are not automatically available inside Docker.

Genuine evidence: [one-case C2 check](reports/codex_c2_demo.json) and [tiny cached-evidence portfolio](reports/codex_c2_portfolio_demo.json). The portfolio completed with an evidence gap, one researched simulated buy and an open holding; this is a flow check, not profitability evidence. Tests cover both transports with mocked inference.

### Research formatting diagnostics (0.16.1)

Specialist prompts now include real schema field limits (company.summary:600 characters); correction feedback names the failing field/constraint. Evidence/policy gates and shared call limits are unchanged. Insufficient market evidence stops before unnecessary strategy/critic calls. Older generic schema errors are diagnosed read-only in portfolio status, with original records retained. Prompt-version changes require a new run; see the updated Plus UI runbook.

### Portfolio rehearsal and interface stability (0.16.2)

Use [Portfolio Simulation: Step-by-Step Demo](docs/AegisTrade_Portfolio_Simulation_Demo_Step_by_Step.docx) for exact capital/dates/risk/costs/allowance, evidence prerequisites and result interpretation. UI/API compatibility uses interface contract1 rather than an exact patch version. Company evidence now preserves financial context and announcement bodies, prioritizes bounded relevant excerpts and caches extracted public attachments up to32 MB. Full source/audit snapshots remain available; changes require fresh research.

### Critic policy IDs and precise provider pauses (0.16.3)

Critic MCP retrieval now independently pins the strategy's exact cited passage IDs. A rejected critic ends the case without an extra unreviewed strategy call. Paused decisions preserve specific CODEX_TIMEOUT / CODEX_OUTPUT_INVALID codes and elapsed time, including read-only diagnosis of older records. These errors alone do not establish a credit/login failure.141 tests pass; this fix used no new model generation. See the portfolio demo guide's Section10.


### Fresh Friday signals, adverse-disclosure research and net profit targets (0.18.0)

Friday/pre-gap entry candidates are re-screened and researched at the next trading close before any later-open fill. Financial incompleteness can support a clearly LIMITED assessment after a completed cited bounded adverse-disclosure review; material/unknown risk still blocks entries. New historical portfolios default to an8% net take-profit target, alongside existing stop/strategy exits. Both active portfolios use matching execution rules. Start a new run; older results remain unchanged. See [policy and demo timing](docs/ENTRY_ADVERSE_AND_PROFIT_POLICY.md). No paid model calls were used for implementation tests.


Version 0.19 adds lossless duplicate-window references, source-impact preservation and human-reviewed portfolio lesson versions. See [C2 tuning and portfolio memory](docs/AegisTrade_C2_Tuning_and_Reviewed_Memory_Plan.docx) for UI steps. No lesson is automatically accepted; unseen-date evaluation and development replays are distinguished. The current viva guide contains 101 questions.


### Fresh documentation for version 0.19.1

Use the new [design and orchestration document](docs/current_v0_19_1/AegisTrade_v0_19_1_Project_Design_and_Orchestration.docx), [72-question viva bank](docs/current_v0_19_1/AegisTrade_v0_19_1_Viva_Questions_and_Answers.docx) and [UI demo/test guide](docs/current_v0_19_1/AegisTrade_v0_19_1_UI_Demo_and_Test_Guide.docx). This set provides a consolidated current description rather than release-note appendices; earlier documents remain available.


### Configurable initial stops (0.19.2)

Strategy Backtests supports an initial ATR distance (default 2×) or percentage below the completed signal close. C2, screening/sizing and the technical reference use the same selected rule. Trailing remains a separate control. See [Initial Stop-Loss UI Guide](docs/AegisTrade_Configurable_Stop_Loss_UI_Guide.docx). Existing jobs retain their settings; finish or pause active work before restarting services to load the new API capability.


### Universe selector (0.20.0)

Market Data supports the retained Nifty 50 top-20 dataset, a frozen official Nifty 100 snapshot, and the custom 30-stock 21/6/3 research set. Public history preparation is cached/asynchronous; activate a complete dataset explicitly. Saved C2 portfolios resolve their original data on resume. See [Universe Selection and Data Preparation](docs/AegisTrade_Universe_Selection_and_Data_Preparation_Guide.docx).

### Dated web evidence fallback (0.21.0)

Code-qualified C2 cases with missing or UNKNOWN company evidence can use the optional MCP `search_dated_web` tool before abstaining. Two bounded public searches retrieve trusted dated source pages for market reassessment and independent critic review. Search snippets, future/known later-updated pages and unverifiable publication dates cannot support an order. Unresolved risk still blocks entry. No search API key is needed; public search and publisher access are best effort. `AEGIS_DATED_WEB_SEARCH=false` disables the fallback. Restart services and start a new C2 run to use the changed research fingerprints.

See [design, UI demo and viva addendum](docs/AegisTrade_Dated_Web_Evidence_Fallback_Guide.docx) and its [editable source](docs/AegisTrade_Dated_Web_Evidence_Fallback_Guide.md). Verification: 233 passing tests; public query access checked, with honest abstention where fetched dated sources were unusable. No live generation calls were made for verification.

### Context-budget correction (0.21.1)

C2 now shares unchanged company evidence within each specialist conversation through explicit references and sends exact JSON Pointer updates for changed packs. Updates are reconstructed and checked for equality before inference; full source observations remain in the audit, and the critic receives its own complete first projection. The serialized conversation guard is 36,000 characters. Oversize requests still stop before inference, without hiding risk or dropping sources to force a fit. The inference-call and output-token ceilings are unchanged. Start a new simulation after updating; adding call allowance or resuming an older run does not revisit candidates already blocked. See the context-budget troubleshooting section in the [dated evidence guide](docs/AegisTrade_Dated_Web_Evidence_Fallback_Guide.docx). Verification: 243 tests pass; cached-failure projection checks made no generation calls.

### Strategy-specific evidence and adverse-news exits (0.22.0)

Strong trend and RSI-reversion signals may proceed after attempted dated research with explicit LIMITED/COVERAGE_LIMITED when no concrete adverse event remains unresolved. This accepts residual coverage risk; it does not label missing evidence as clean fundamentals. Breakouts require readable dated corroboration and breakout_support. Supported adverse findings block entries and require critic-validated EXIT for holdings, filling at a later eligible open. A bounded daily official-disclosure metadata watch can trigger C2 between scheduled holding reviews; empty checks make no generation call. Routine trading-window notices and address fragments are distinguished from substantive adverse events. Existing stops, profit targets, sizing, costs and no-terminal-liquidation rules remain.

Start a new run after updating: research, corpus and engine fingerprints changed. See the [policy, orchestration, UI demo and viva guide](docs/AegisTrade_Signal_Specific_Research_and_Adverse_Exit_Guide.docx). Verification: 256 tests pass with mocked generation; no profitability improvement is claimed.

### Quoted breakout corroboration and structural-action quarantine (0.22.1)

Breakout approval now requires a recent exact visible source quote supporting a reported earnings/operating improvement or completed commercial event with a reported benefit metric. The accepting independent critic must separately corroborate the same source. A readable filing and prose alone, provider selection or a sole forecast are insufficient. Known recent structural-action disclosures quarantine new entries on the unadjusted simulator; this does not repair entitlement accounting or establish that a demerger is adverse news. Underlying EMA/RSI/breakout technical thresholds are unchanged. Start a new run after updating. See the [ITC/ONGC audit and correction guide](docs/AegisTrade_Breakout_Entry_Audit_20261112.docx). Verification uses synthetic/mocked generation and stored-source checks, not a claim of improved profitability.

### Breakout recovery and trend pullbacks (0.23.0)

Four strategies are available, including EMA_PULLBACK; BREAKOUT is retained with separate risk/stop controls. A stopped breakout can make one confirmed recovery entry after fresh C2 research. See [rules and UI demo guide](docs/AegisTrade_Breakout_Reentry_and_Pullback_Guide.md). Start a fresh run; historical results are preserved.

### Three portfolio flows (0.24.0)

Strategy Backtests now offers C2 specialist research, C1 evidence-first SMC and technical-only simulation. C1 checks dated company RAG/filings/news/newsletters before evaluating the SMC pattern, uses one tool-using LLM agent without an independent critic, and defaults to a configurable 4% net trading profit target with protective stops. Existing C2 strategies and universes remain. See [C1 design, UI demo and viva guide](docs/AegisTrade_C1_SMC_Three_Flow_Guide.md). Start a fresh run for the new engine/policy version.

### Live flow progress correction (0.24.1)

C1/C2 progress is shown above the run form, with separate per-flow saved results, live source/model activity and research-versus-signal-versus-fill counts. SMC stage diagnostics explain a missing entry without changing trading rules or retrospectively inventing signals. Existing 0.24.0 runs can resume with their original fingerprints and allowance.

### SMC stopped-position recovery (0.25.0)

C1 can now sell at its protective/trailing stop and make one evidence-first recovery entry after a later bullish close reclaims the stopped price, previous high and original order-block upper level. Default watch: ten sessions; configurable in Strategy Backtests. A second stop exhausts the retry; source/adverse, sizing and profit/stop gates remain. Start a fresh run; earlier runs are preserved under their original execution rules. See the [C1 guide](docs/AegisTrade_C1_SMC_Three_Flow_Guide.md).

### Historical issuer evidence library (0.25.1)

All configured universes share a dated 103-stock source library. View **Policy Knowledge → Historical company evidence library** for coverage and remaining gaps. See [backfill report](docs/AegisTrade_RAG_Evidence_Backfill_Report.md) for the repeatable download/OCR/audit commands. Company facts remain date-filtered and separate from policy RAG. Downloaded sources stay local and are excluded from Git. Start fresh research after source/corpus updates.

### Capstone comparison UI (0.26.0)

Strategy Backtests can clear the displayed saved run and begin a new C2 session and also hosts the single-stock C0/C2 portfolio comparison. AI Agent Experiments keeps only the same-case C0/C1/C2 research ablation and human review of grounded C2 recommendations. The minimum-bar evidence matrix remains in Capstone Evaluation rather than cluttering the experiment page. See the [simplified UI guide](docs/SIMPLIFIED_UI_DEMO_GUIDE.md).
