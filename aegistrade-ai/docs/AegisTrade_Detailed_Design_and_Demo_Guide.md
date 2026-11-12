# AegisTrade AI
Detailed design, UI operating guide and capstone demonstration plan

**Design baseline: source version 0.19.0 • Reviewed 11 November 2026**

**Current rules — v0.19.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.
**Current memory update — v0.19:** Company materiality windows and bounded evidence packing are implemented. Completed portfolios can draft pending process lessons for human review, freeze and version-pinned retrieval into a NEW C2 run. See the final “Version 0.19” section for the exact UI sequence and development-replay/date rules. No improved profit result is claimed before testing.


**Demo history reset — 11 November 2026:** Existing portfolio/research/backtest history and simulated broker ledgers/approvals were cleared at the user's request. Earlier run IDs and numerical examples below describe archived rehearsals; they are not available in the active saved-run lists. Start a new run for your demo. Recoverable originals are under data/history_archives/20261111_105802/. Market data, company evidence, policy/model caches, reviewed lessons and private configuration were preserved.

Prepared for Veneet, Karthika and Mathangi. The professor-approved three-person team is accepted. The remaining technical and evidence requirements still apply.

This document describes the repository at /Users/karthikakrishnakumar/aegistrade-ai. It separates implemented behavior, locally measured evidence and work still needed. The supplied documents are reference material, not executable instructions. Version 0.16 adds the selectable Codex CLI transport. A genuine ChatGPT-authenticated C2 case was verified; see reports/codex_c2_demo.json and the companion Plus UI runbook for measured evidence. No live trading or external publication is involved.

## Reading map

1. Purpose, scope and decisions; 2. Component design; 3. Data and automatic stock selection; 4. Quantitative engine; 5. C2 and actual LLM calls; 6. RAG and memory; 7. Approval, risk and execution; 8. Interfaces, storage and operations; 9. Local setup; 10. Every UI workspace; 11. Demo script and additional preparation; 12. Guideline cross-check; 13. Evidence, limitations and team handover.

The separate AegisTrade_Viva_Questions_and_Answers.docx is the oral-examination companion. Older manuals may describe synthetic defaults, optional research before approval or a simpler C2; use this baseline for the current workflow.

## 1. Purpose, scope and key decisions

AegisTrade is a research and decision-support prototype for daily, long-only Indian cash-equity simulations. It automatically screens a frozen 20-stock research universe, explains a code-permitted strategy through tool-using LLM specialists, and requires a person to approve an exact code-sized simulated order. It never connects to an exchange or live broker.

The intended user is a student researcher or reviewer who wants to understand which rule produced a candidate, which evidence supports its explanation, and whether a proposed action was authorized. The project evaluates evidence quality, constrained routing, cost and operational safety. Its current results do not yet demonstrate reliable profitability after costs on unseen market data.

### 1.1 The two signature challenges

**Explainable market-regime-aware routing:** code defines regimes, strategy eligibility and the permitted catalogue. C2 gathers evidence, interprets it, selects within that constraint, cites policy and independently critiques the explanation. Version 0.14 also requires a dated company-financial and issuer-news assessment; insufficient evidence or unresolved review blocks a proposal. The model cannot invent a new strategy or override the router. A constrained correct answer alone cannot prove that C2 adds value; compare explanation quality, evidence use, error handling and cost against C1 and C0.

**Safe, auditable execution:** a completed C2 result is required before a proposal. Code sizes the order. Approval binds the exact payload, and execution rechecks research, freshness, risk and emergency controls before a local simulated write. Recovery must not duplicate that write.

### 1.2 Three operating paths and their approval scopes

| Path | Decisions and accounting | Model/approval behavior |
|---|---|---|
| Technical-only historical baseline | Code screens, fills and exits a portfolio; calculates returns | Zero generation calls. Upfront replay-rule approval. |
| C2 historical portfolio | Every prospective entry completes dated C2; scheduled holding reviews produce HOLD/EXIT; code handles risk, fills and accounting | C2 under a total inference allowance (OpenRouter requests or Codex CLI invocations). Upfront approval authorizes automatic historical fills under the stated policy, without a per-fill human pause. |
| Supervised single action | One passing C2 case becomes one code-sized proposal and simulated broker action | Exact approve/edit/reject interrupt before that individual action. |

The C2 historical portfolio is now connected end to end: **historical evidence → technical shortlist → dated financial/news research → accepted C2 critic/code checks → code-sized next-open entry → portfolio holding review and exits → realized/unrealized P&L**. Its returns come from its own researched fills; technical ROUTER returns remain a separate reference.

The supervised sequence remains **completed C2 → code-sized proposal → exact human approval → final checks → local simulated broker**. Upfront historical-rule approval is a distinct evaluation scope; it does not grant unattended permission for the supervised workflow or real trading.

Ending the replay does not require selling holdings. A position survives when no protective, strategy or accepted C2 exit fills inside the requested window. Its value contributes to ending equity as unrealized P&L, with the last mark/date disclosed. No model is paid merely to liquidate on the final date.

## 2. Component and deployment design

[[FIGURE:architecture]]

Figure 1. Implemented local architecture. Generation is cloud-hosted; data, retrieval models, state and the simulated broker are local. The C2 historical portfolio uses upfront approved automatic fills; the supervised branch retains exact human interrupts. The technical-only baseline remains separate.

| Component | Responsibility and boundary | Main source |
|---|---|---|
| Streamlit | Eight workspaces; forms, charts, consent, exact order review and trace display | app/ui.py |
| FastAPI | Validate requests, paid-run gates, authenticated reviewer actions, research binding, health and metrics | app/api.py |
| Market/data services | Load persisted source choice, validate/download NSE cache and compute indicators | aegistrade/market.py; nse_data.py; strategies.py |
| Screening/replay | Technical baseline plus checkpointed C2 entry/holding/exit loop, actual cash/positions and mark accounting | selection.py; engine.py; simulation_service.py; c2_portfolio.py |
| Research orchestration | Typed LangGraph supervisor, scoped specialist loops, shared call/tool budget | agentic.py; llm_research.py; research_service.py |
| MCP evidence | Actual protocol calls to market, strategy and knowledge servers | mcp_runtime.py; agent_tools.py; mcp_servers/ |
| RAG | Validated corpus, BM25/vector fusion, reranking and dated passage provenance | corpus.py; knowledge.py |
| Historical company evidence | 180-day official announcement scan, bounded PDF extraction, reviewed news imports, exact daily-close cutoff and pack digest | company_research.py; scripts/prepare_company_research.py |
| Human-action graph | Proposal, risk/critic checks, persistent interrupt, edited payload and resumed action | workflow.py; research_gate.py; safety.py |
| Learning | Reviewed, relevant, frozen lessons and development-only reflection | memory.py; lessons.py; reflection.py |
| Experiments/operations | E1–E4 runners, contract tests, CI threshold, metrics and dashboards | evaluation/; tests/; monitoring/; .github/workflows/ci.yml |

Six FastMCP server modules are defined: market, strategy, risk, knowledge, records and action. Research uses three of them. The LLM tool set contains no broker-write capability. The action server is omitted from Compose; the authenticated deterministic action graph performs the simulator write. Fourteen tools have protocol contract tests and an exported inventory in docs/MCP_TOOL_INVENTORY.json.

Local research uses FastMCP stdio sessions. Docker config uses HTTP MCP endpoints. Adapter discovery has been exercised, but the research runtime uses the FastMCP client directly rather than langchain-mcp-adapters. Inputs are typed; some dictionary outputs remain generic rather than strict domain response models. These are implementation details and remaining quality gaps, not reasons to describe direct Python calls as MCP.

## 3. Market data and automatic stock selection

### 3.1 Downloaded research dataset

| Item | Current value |
|---|---|
| Downloader | NSEPython 2.101; scripts/download_nifty20.py |
| Evaluation request | 8 November 2021 to 8 November 2026 |
| Warm-up | Begins 1 July 2021; excluded from evaluation start |
| Cache | data/nse_nifty20/ohlcv.csv; 26,580 rows, 20 symbols |
| Sessions | 1,329 rows per symbol including warm-up; 1,242 evaluation sessions |
| Active source | nsepython, persisted in data/market_config.json |
| Universe basis | Current Nifty 50 membership, then top 20 by pre-period liquidity proxy |
| Price quality | Raw/unadjusted; corporate actions and dividends unresolved |

The official membership snapshot comes from NSE's ind_nifty50list.csv. The universe is frozen using up to 60 pre-evaluation sessions of mean Close × Volume, with at least 20 sessions. This is a liquidity proxy, not a recommendation and not the true exchange turnover field. The later daily ranking uses only information available by the selected completed session.

The selected symbols are TMPV, RELIANCE, TATASTEEL, BHARTIARTL, INFY, TCS, SBIN, HDFCBANK, BAJFINANCE, ICICIBANK, KOTAKBANK, AXISBANK, HCLTECH, ITC, BAJAJFINSV, MARUTI, TECHM, HINDALCO, ADANIENT and HINDUNILVR. Symbol aliases are normalized using documented NSE references. Alias normalization does not repair demerger economics or other corporate actions.

Downloads use bounded date chunks, a resumable cache, checksums and a minimum coverage gate of 80% of weekdays. That gate is not a complete exchange-calendar audit. Download failures do not silently substitute synthetic or Yahoo data.

**Validity limits:** using today's constituents on the past introduces survivorship bias. Unadjusted splits, bonuses and demergers can distort prices, signals and marked portfolio value; dividends are omitted. The 20-session large-jump exclusion reduces some bad new entries, but cannot repair existing holdings or make the series adjusted. Show the dataset as provisional research data and avoid profitability claims.

### 3.2 Daily screening and ranking

[[FIGURE:selection]]

Figure 2. Selection separates frozen-universe construction, daily causal screening and the next eligible fill. Completed-bar evidence is not permission to submit a supervised action.

1. Restrict evaluation to the frozen universe and valid evaluation dates. Require at least 60 sessions and ready indicators.
2. Reject HIGH_VOL, UNCERTAIN and WARMUP regimes. Require positive ATR and ATR/Close no greater than 6.5%.
3. Require 20-session mean Close × Volume of at least ₹1 crore. Reject new candidates for 20 sessions after an absolute raw close jump above 30%.
4. Require an entry signal under the permitted strategy. Exclude held symbols; respect the daily-loss gate, position capacity, cash and affordability of a whole share.
5. Rank remaining candidates by 70% strategy strength + 20% current liquidity percentile + 10% preference for a lower ATR fraction. Break equal scores by symbol for reproducibility.
6. Allocate under current capital and risk constraints; recalculate fill size at the actual next eligible open during replay. A screening estimate is not the final quantity.

Strategy strength is strategy-specific: EMA trend combines ADX and 20-session momentum; RSI reversion scores the extent RSI is below 42; breakout combines distance over the prior high and relative volume. These are authored ranking heuristics, not learned probabilities of profit. No LLM chooses the top 20 or changes the score.

## 4. Quantitative strategy and simulation design

### 4.1 Indicators, regimes and routes

Indicators include EMA20, EMA50, RSI14, ATR14, ADX14, realized volatility over 20 sessions, relative volume and the prior 20-session high. The prior high is shifted to exclude the current bar.

| Regime precedence | Test | Permitted route |
|---|---|---|
| WARMUP | Required indicators/history unavailable | NONE |
| HIGH_VOL | Realized volatility > 0.48 or ATR/Close > 0.065 | NONE |
| BREAKOUT | Close > prior 20-session high and ADX ≥18 | BREAKOUT |
| TREND | ADX ≥22 and EMA20 > EMA50 | EMA_TREND |
| RANGE | ADX <22 after earlier tests | RSI_REVERSION |
| UNCERTAIN | Remaining evidence | NONE |

| Strategy | Entry | Exit |
|---|---|---|
| EMA_TREND | Ready indicators, EMA20 > EMA50 and Close > EMA20 | EMA20 < EMA50 |
| RSI_REVERSION | RSI <42 and Close >0.88 × EMA50 | RSI >58 |
| BREAKOUT | Close > prior high and ADX ≥18 | Close < EMA20 |

Router selection and entry eligibility are separate. A permitted route can have no current entry. HIGH_VOL takes precedence over a breakout, so a visually strong move may still be rejected.

### 4.2 Sizing and fill accounting

Default trade risk is 1% of equity, maximum position value 20%, maximum open positions four and daily-loss circuit breaker 3%. Default fee and slippage assumptions are each 10 basis points in historical replay. The proposal's 0.5%/five positions/2% figures were illustrative; they are not the current defaults.

For a long proposal, initial stop = entry − 2 × ATR, subject to a positive price floor. Quantity is the whole-share minimum allowed by risk budget, position-value cap and fee-inclusive available cash. Reject zero quantity or invalid/nonfinite prices.

Example: equity ₹200,000, entry ₹500, ATR ₹10. Stop ₹480; risk budget ₹2,000 permits 100 shares; 20% value cap permits 80; cash permits more than 80. Therefore 80 shares is the upper size before other checks, with ₹1,600 initial stop-distance exposure. A gap can exceed that modeled exposure; it is not a guaranteed loss limit.

The replay evaluates a completed-session signal, then fills at the next eligible session open with adverse slippage and fees. Gap-through-stop logic uses executable bar assumptions, not an impossible guaranteed stop price. Missing holding bars retain the last mark and disclose staleness; pending orders wait for an eligible bar. No same-close look-ahead fill is claimed.

A passive equal-weight buy-and-hold comparator uses the same selected universe and cost assumptions, enters at initial selected opens and marks to final closes. It does not share the active strategy's stops or capacity rules, so it is a contextual benchmark, not risk-matched proof of superiority.

The recorded ₹200,000 ROUTER smoke completed 1,242 sessions, 24,840 screening audit rows and 326 ledger events with zero paid model calls. These are execution/completeness observations, not validated financial-effectiveness results.

### 4.3 End-to-end C2 historical portfolio and exit lifecycle

[[FIGURE:portfolio]]

Figure 3. Chronological C2 portfolio loop. Protective stops and strategy exits are code rules; scheduled C2 HOLD/EXIT reviews supplement them. Remaining holdings are marked at the period end.

At each open, process queued exits before entries, revalidate C2-linked decisions, recalculate affordable quantity using actual gap/cost/risk conditions and fill only eligible orders. Existing protective stops apply independently of research. At each completed close, ratchet enabled trailing stops before any C2 research can pause the close, then evaluate code exits and scheduled holding reviews. C2 cannot veto a stop or code exit.

A remaining holding receives a C2 review every N market sessions (default 5) using current dated technical, company and position evidence. The three specialists produce an accepted HOLD or EXIT with citations. An EXIT queues SELL_C2; HOLD preserves the stop. A blocked review records unavailable evidence and retains existing code protection; it does not invent a buy/hold assurance. New ranked candidates complete a separate full C2 ENTRY case before any entry is queued.

No final-day entry/review generation is performed when no subsequent fill can occur inside the window. A code exit signalled at the final close remains pending, and unsold positions remain in open_holdings with quantity, cost, stop, last review/date, last mark/date, market value and unrealized P&L. A new independent run starts with its own cash; holdings are not automatically transferred between newly created runs.

Historical jobs persist OPEN/CLOSE phases, queue, ledger, holdings and per-decision research files under data/c2_portfolio_runs/RUN_ID/. Resume does not repeat an already applied opening phase or paid successful case. A total allowance defaults to48 calls; eight requests are reserved durably before each research case and unused requests released when actual usage is known. Unknown calls after a crash remain charged conservatively. PAUSED_BUDGET needs explicit additional consent; PAUSED_PROVIDER stops repeated provider failures and requires resolution plus consented resume. Pause requests stop at safe boundaries. Changing data, model/prompt configuration, simulator version or policy corpus requires a new run.

Cash + marked holdings must equal initial capital + realized P&L + unrealized P&L. Entry costs are assigned once; no sale or exit fee is invented for unsold holdings. Actual provider charges are reported separately in USD and are not silently subtracted from INR returns using an assumed exchange rate. Missing cost remains unknown. Full-period baseline metrics are withheld until the C2 window completes; partial reference curves stop at the visible C2 date.

The complete report includes C2 versus technical ROUTER/passive references, model usage, decisions, fill-linked research IDs, source/critic traces, gaps, pending intentions and open holdings. COMPLETED_WITH_GAPS means the window finished with blocked/unavailable evidence; a return difference then reflects availability/abstention as well as model judgment. It is not automatic proof of useful AI or profitability. See C2_HISTORICAL_PORTFOLIO.md for the operational/state contract.

### 4.4 Trailing-stop design (0.17.0)

New historical portfolios default to trailing_stop_enabled:true and trailing_atr_multiple:2.0. The initial stop is still fixed at the signal close minus2ATR before a later open fill; next-open sizing uses that actual distance. On each completed close after entry, code computes stop = max(previous stop, highest completed close since fill − multiplier × entry-signal ATR14). ATR distance stays fixed for the holding and the stop only rises. Intraday highs do not drive this daily-close policy.

The OPEN phase processes opening gaps and intraday lows against the previously active stop. The CLOSE phase raises survivors' stops for the next session, saves stop_updates and checkpoints before research. A per-position trailing_last_close marker makes a resumed CLOSE idempotent. Missing bars do not update the peak or stop. Entry-signal ATR is taken from the saved validated research snapshot, never from the later fill-day ATR. A final close can raise a surviving stop without inventing a sale beyond the window.

Raised-stop exits are labelled SELL_TRAILING_STOP, while the untouched initial stop remains SELL_STOP. A queued strategy/C2 exit that gaps below the stop is classified as a protective-stop exit. Fills use the opening price when it gaps below the stop, otherwise the stop when the low crosses it, with adverse slippage and fees. Initial/current stop and the adjustment audit are visible in results. Strategy exits and accepted C2 EXIT remain active; HOLD cannot loosen a code stop. No extra generation requests are needed.

Both C2 portfolios and the active technical reference use the selected trailing parameters. The passive comparator has no stops. UI controls are Enable trailing stop and Trailing distance (× ATR14 at entry signal), default2.0 and validated0.5–10. Disabled trailing retains the initial fixed stop. This is a historical-portfolio feature; Supervised Trading does not continuously monitor an approved single action. Lower-level TradePolicy defaults remain fixed for existing direct research/evaluation callers; UI/API SimulationSettings explicitly enable trailing.

Engine c2-portfolio-v2-trailing and updated policy passage POL-43 bind new runs to this behavior. Older runs remain readable with their original settings/results; changed engine/corpus requires a new run. Regression evidence covers monotone adjustment, next-session timing, gaps, missing bars, disabled mode, no terminal sale, accounting and close-phase pause/resume. reports/trailing_stop_verification.json uses synthetic prices and mocked C2, with zero real generation calls; it establishes mechanics, not financial performance. See TRAILING_STOP_POLICY.md for the formula and worked example.

### 4.5 Measured three-month C2 portfolio and comparison

User run95ef3724c1a94eb6bf69286a4c60272a completed63 sessions from1 December2023 to29 February2024 with gaps, using ₹500,000,1% risk,10/10 bps costs,2ATR trailing and five-session holding reviews. It recorded313 CLI invocations,14 buys,10 stop exits and four surviving holdings. Ending equity₹521,314.06 comprised₹5,310.26 realized and₹16,003.80 unrealized profit:4.26% return, approximately2.92% maximum drawdown. The matched technical reference returned4.41% with2.41% drawdown; the passive20-stock comparator returned8.68% with different exposure/risk rules. These results do not establish an AI financial edge. Missing/insufficiently readable financial evidence prevented some reference winners, while other entry paths favored C2; observed differences netted to about−₹727. All27 accepted holding reviews returned HOLD, so all ten actual C2 sales were code-driven trailing stops.

The supplied CSV matched the complete saved ledger and every stop/fill was checked against entry-signal ATR and daily OHLC. No stop arithmetic or accounting mismatch was found; all additional review/sensitivity analysis used zero model calls. See AegisTrade_Three_Month_Portfolio_Performance_Review.docx and reports/portfolio_performance_review_20261111.json for trade-level evidence, comparison attribution, hypothesis-only candidate lessons and technical-only lower-risk sensitivity checks. Current-membership/raw-price, source-coverage and independent evaluation limits remain.

## 5. C2 design and the complete LLM-call portion

### 5.1 Paid-run gates explained

“FastAPI paid-run gates” means the API refuses external inference unless the reviewer token is valid, the selected backend is ready (OpenRouter API key or ChatGPT-authenticated Codex CLI), AEGIS_ENABLE_LLM_EXPERIMENTS=true, the user explicitly consents for this run, and the requested case/call budget is allowed. It does not mean the trading order is paid, that a credit balance is verified, or that a dollar spending ceiling is enforced by the app.

Runtime generation is selectable using AEGIS_LLM_BACKEND=openrouter or codex_cli. The private local configuration now selects codex_cli with the existing ChatGPT login; this consumes plan allowance, not OpenRouter credit. OpenRouter remains the default if unset and is reversible through configuration plus restart. AEGIS_LLM_MODEL overrides the selected model; leave it blank to use the backend default. Keep the reviewer token, supported CLI authentication and API key separate. No Claude adapter or automatic provider fallback is implemented.

config/agents.json records default model openai/gpt-4.1-mini, temperature 0, role prompts and budgets. Environment configuration may override the effective model; record the effective run metadata rather than assuming the default ran. Context sent to the provider includes the selected historical case, relevant tool observations and applicable lessons; it is not the entire dataset or private .env file.

### 5.2 Normal six-request C2 sequence

[[FIGURE:llm]]

Figure 4. Normal C2 generation requests and MCP observations. MCP tool execution is local computation/retrieval, not an additional paid LLM request. Correction can add requests within the shared ceiling.

| Step | Generation or code operation | Evidence and output |
|---|---|---|
| 0 | Code creates and displays a plan; locks the case | Symbol/date, indicators, approved route, selection provenance, corpus version |
| 1 | Market specialist: first inference unit | Chooses market_snapshot and company_evidence together |
| 2 | Code validates permission/budget; MCP executes | Market snapshot and dated company pack become observations |
| 3 | Market specialist: second inference unit | Typed regime/explanation plus company status, summary, citations, event risks and limitations |
| 4 | Strategy specialist: first inference unit | Chooses search_policy and check_strategy |
| 5 | MCP evidence executes; strategy second request interprets it | Typed strategy, retrieved passage IDs and explanation |
| 6 | Compliance critic: first inference unit | Independently requests policy/strategy and company evidence |
| 7 | MCP evidence executes; critic second request interprets it | Typed accept/reject and reason |
| 8 | Deterministic final validation and save | Route/company agreement, policy and financial citations, accepted critic, usage, snapshot/corpus/company-pack hashes |

There are normally **six inference units**, not three: one tool-selection request and one observation-interpretation request per specialist. Multiple tools can be requested in one generation response. C2 has a shared maximum of eight inference units and 16 MCP tool calls, with normally 4,800 aggregate allocated response tokens; the UI offers 6,400. For OpenRouter a unit is an HTTP generation request with provider max_tokens. For Codex it is one CLI invocation, whose internal provider requests are unknown; response tokens are conciseness guidance and local response-size checks, not a hard provider/reasoning-token cap. Actual reported input/output usage can greatly exceed the final JSON target. One case is the sensible live-demo default.

Each specialist has its own prompt, scoped tools and typed hand-off. Market returns regime/explanation and a typed company assessment; strategy returns permitted strategy/policy citations/explanation and purpose-constrained ENTER/HOLD/EXIT; critic returns acceptance/reason after independently reading company evidence. C1 returns the strategy and company assessment together. Normal C2 invokes seven tools within its six generation requests. Prompts use role, context, task, constraints, output format and example slots. Provider transport errors and budget exhaustion fail closed; there is no hidden retry until success.

Typed validation or contradictory evidence may return feedback for a bounded correction. A tested contradictory market response was corrected with seven total requests. A critic rejection remains blocking: a revised strategy cannot inherit the old critic's acceptance. The workflow now ends immediately on critic rejection; it makes no extra unreviewed strategy-revision call. Show the actual trace rather than describing unlimited autonomous replanning.

### 5.3 C0, C1 and C2 comparison

C0 is the fixed deterministic reference and makes zero generation requests; agreement with its own rule is true by construction. C1 is one tool-using LLM agent with the same union of technical, company, strategy and policy tools. C2 is the deterministic supervisor plus three LLM specialists. C1 and C2 share model, available tool union and budget ceilings; actual costs can differ. The supervisor is code, which avoids another paid planner request.

The AI Agent Experiments workspace caps its single-case comparison run at three cases; the C2 historical portfolio instead uses its total job-call allowance. C2 can therefore attempt up to 24 calls; ALL includes C1 and C2 and can attempt up to 48. Output-token caps are not input-token or dollar caps. Capture actual usage, provider-reported cost when supplied, failures and latency.

A saved C2 result includes specialist hand-offs, tool trace, cited IDs, selected strategy, critic verdict, guard outcome, model errors, usage, timing and case snapshot. Completed result JSON is persisted; the research graph itself has no durable mid-generation resume. Supervised actions persist SQLite interrupts; C2 historical jobs separately persist portfolio phases and completed research files.

**Current generation evidence:** genuine Codex C2 run 290874d24eeb498b868949c2796b3424 passed the research gate for HINDUNILVR on 2023-03-31 using 7 CLI invocations, 7 actual MCP tool calls and neural retrieval. Recorded latency was 66.433 seconds and reported tokens 59,069; per-run USD cost is unknown. See reports/codex_c2_demo.json. The selected label codex-default does not establish a resolved fixed model ID. The earlier OpenRouter check returned HTTP 402; Plus does not fund that provider. Mocked reports remain explicitly separate from genuine inference.


### 5.4 Codex transport design and isolation

The adapter in aegistrade/llm_backend.py invokes codex exec with JSONL events, an output schema and an ephemeral session in a temporary directory. It ignores user configuration/rules, requests read-only sandboxing, disables native shell, apps, web search, memories, hooks and multi-agent tools, and passes a minimal environment without provider/reviewer API secrets. Supported CLI authentication stays in the credential store. It checks ChatGPT login, validates the envelope and rejects unexpected native-tool events or malformed tool arguments. It does not invoke the CLI inside the repository or give it the full market dataset.

The adapter translates a specialist's structured virtual-tool requests into the existing assistant/tool conversation format. AegisTrade applies role permissions and JSON schemas, executes real MCP calls, then supplies observations to the next invocation. This preserves model-selected tools and observation-driven interpretation; the CLI is not a substitute supervisor or a new unrestricted trading agent. Date-filtered retrieval cannot guarantee that pretrained model knowledge contains no later facts; claims must be grounded in supplied historical sources.

Timeout terminates the CLI process group. Quota/login/transport failures are recorded and block research; historical runs pause as PAUSED_PROVIDER and need explicit consent to retry. No automatic OpenRouter fallback occurs. Backend, model, adapter and budget unit are pinned in each historical job; changing them blocks resume. Completed results retain provenance. The local host's CLI/auth is required; Docker does not inherit it automatically. For final comparative experiments use a supported explicit model and record CLI version, actual usage and limits; do not claim CLI invocation caps equal provider request or dollar caps.

## 6. RAG, provenance and memory design

[[FIGURE:rag]]

Figure 5. Local hybrid retrieval and generation grounding. Source date filtering happens before evidence reaches the specialist; project policy and external background have different authority.

### 6.1 Knowledge ingestion and search

knowledge/corpus.jsonl contains 81 passages: 72 project policy/specification passages and nine external reference summaries covering seven unique external URLs. It remains a trading-policy and system-design corpus. Version 0.14 company filings/news use a separate dated evidence-pack store, not this policy index. OHLCV stays structured tool evidence; embedding every candle is unnecessary for the current task.

Each passage retains a stable ID, title, text, source, dates and authority; external passages also require a source URL. Authored/indexed date is distinguished from publication and retrieval dates. A code locator is not an externally published source. The manifest and corpus SHA-256 bind retrieval to the current knowledge version.

The active neural pipeline uses BM25 lexical retrieval plus 384-dimensional all-MiniLM-L6-v2 embeddings, fused by Reciprocal Rank Fusion, then cross-encoder/ms-marco-MiniLM-L6-v2 reranking of a shortlist and a controlled query rewrite. RRF combines reciprocal ranks, avoiding an assumption that keyword and vector scores share a scale. Chroma persists vectors; cached model weights and embedding files avoid repeat downloads. A separately labelled offline TF-IDF baseline remains available; it is not silently reported as neural retrieval.

MCP search_policy is locked to the selected case's as_of date. External passages with publication after that date are withheld; unknown publication uses retrieval date conservatively. Project policy describes the current experiment's rules rather than pretending those policies were historical company information. This prevents a narrow source-date leak; it does not fix current-universe survivorship bias.

The model must cite IDs actually observed in successful search results, including at least one project-policy passage. A background document alone cannot authorize a route. Citation existence and retrieval membership are code checks; semantic faithfulness still needs independent human/judge evaluation.

### 6.2 Historical company fundamentals and news

C2 now reads an exact-symbol, exact-cutoff company_evidence pack. Public NSE announcements are scanned over 180 days; up to six selected archive PDFs cover results, annual-report candidates, issuer news and another announcement. Availability is the later of exchange publication/dissemination at or before 15:30 IST on the signal date. Future releases are excluded even if the accounting quarter ended earlier.

Coverage requires a readable recent financial filing containing statement labels and numeric content, plus a verified bounded exchange scan. A notice linking an annual report cannot alone satisfy it. The LLM reports SUFFICIENT, INSUFFICIENT_EVIDENCE or REVIEW_REQUIRED, cited CMP IDs, company summary, event risks and limitations. New entries/HOLD require SUFFICIENT; a cited REVIEW_REQUIRED assessment may support a critic-accepted EXIT of an existing holding only. This is not an investment-quality rating. Tables may mix units, periods and standalone/consolidated columns; quote or compare figures only if their basis is explicit in the original evidence. Ratio/valuation accuracy is not established.

The downloader is host/size/page bounded, has no OCR or unrestricted browser, and does not assume complete independent press coverage. Reviewed historical news/newsletter excerpts can be imported separately with original source/publication metadata; date-only sources become available at the next IST midnight. The pack is retrieved today from the archive; exchange timestamps are availability evidence, not a certified content-revision history. See HISTORICAL_COMPANY_RESEARCH.md for exact import instructions.

A real TCS pack is prepared for 2026-10-23 with readable results and issuer releases. The INFY pack currently lacks a readable qualifying financial attachment and remains blocked. Missing evidence stops service-level research before any paid generation. Existing packs are reused; refresh/import changes the digest and invalidates older research/approval. The market and critic must both observe the matching current pack. No extra specialist or extra normal generation request was added.

### 6.3 Measured retrieval evidence

| Authored development evaluation | Recall@5 | Interpretation |
|---|---|---|
| Expanded neural corpus, 101 queries, rewrite off | 0.9505 | Same development set baseline |
| Expanded neural corpus, 101 queries, rewrite on | 0.9703 | +0.0198 absolute, about 1.98 percentage points |
| Original 16-passage offline corpus, original 36 queries | 0.9444 | Historical baseline on a different corpus |
| Expanded neural corpus, original 36 queries | 0.9167 | Regression remains on the older query subset |

The labels are authored development judgments and not exhaustive or independently held out. Do not combine different query sets into one improvement claim. Macro Recall@5 averages the fraction of each query's relevant passage IDs retrieved in its top five; any-hit rate is a different metric. Reports are in reports/rag_development.json.

### 6.4 Memory and learning

Short-term context contains the case, messages and tool observations. The current implementation rejects context beyond 26,000 characters rather than trimming or summarizing it. That is a real gap against PDF p.3 and must be implemented and tested before claiming that row complete.

Long-term lessons live in SQLite with pending/accepted/rejected state, rationale and applicability. A development failure with an actual model response can trigger one separately consented paid reflection request. Credit/transport failures are excluded because they contain no reasoning failure to learn from. Generated lessons stay pending until a human reviews them; rejected and pending lessons never enter research context.

Memory-on research requires a frozen playbook. Only relevant accepted lessons are retrieved; matching is currently simple and does not guarantee semantic relevance. Freeze records version/hash/reviewer/time, and held-out cases must not teach the playbook. The written policy covers correction and deletion; these are administrative operations, not a complete self-service retention/deletion UI. Do not delete a user's SQLite files as a demo shortcut.

A generated lesson is a hypothesis. E3 must establish unseen-case benefit, regressions and generation cost. That evidence is still missing.

## 7. Safe supervised action and approval design

[[FIGURE:approval]]

Figure 6. Persistent human-control state flow. Edits create a new action identity/hash and require new review; final submission remains conditional on current research and risk.

### 7.1 Research-to-proposal contract

research_gate.py validates C2 configuration, guard_pass, critic_accept, absence of model errors, all three typed hand-offs, expected observed tools, consistent regime/route and retrieved citation IDs. It checks the corpus fingerprint and requires project-policy authority. It also requires a SUFFICIENT company assessment, an observed financial-content CMP citation and a company-pack digest matching both market/critic observations and current storage. Evidence refresh invalidates pending approvals. FastAPI reloads the saved research and compares current evidence instead of trusting browser-supplied success flags.

The proposal binds research run/case, the research-result digest, snapshot and corpus version. Start, resume and execution context validate this linkage. A changed saved result, changed corpus or changed market evidence invalidates eligibility and requires new C2 research/proposal/approval. Legacy runs without the required provenance cannot be reused as current approved evidence.

### 7.2 Approval lifecycle

1. Code plans, loads market/strategy evidence, forms the code-sized BUY payload and runs risk and deterministic critic checks.
2. LangGraph saves an interrupt in SQLite and returns WAITING_HUMAN with the exact payload, research explanation/citations, payload hash, request ID and expiry.
3. A reviewer approves, edits or rejects through an authenticated API action. The UI defaults to reject; merely opening the page is not consent.
4. Reject ends the action. Edit reruns validation and creates a new identity/hash/expiry, with at most two edit loops; another explicit approval is required.
5. Approve must match the current hash. Before writing, code checks quote age/deviation, approval expiry, current research, risk and kill switch again.
6. The local simulated broker writes by request ID/hash. A timeout after commit is reconciled against the durable record; retries do not imply a second fill.

Standard quote-age policy is 90 seconds; the replay UI uses a 600-second allowance. Approval expires after ten minutes and allowed price deviation is 2%. These timestamps refer to generated replay quotes, not a live exchange subscription. A long viva interruption can cause a legitimate expiry; prepare a fresh proposal instead of weakening the checks.

The emergency kill switch blocks new proposals/submissions and invalidates outstanding approval tokens. Turning it off does not revive earlier approvals. It does not liquidate positions or provide a live-market emergency stop.

The supervised reference capital sizes **one proposal**. It is not a persistent forward portfolio shared with historical replay. Therefore do not describe multiple supervised submissions as a complete portfolio performance simulation.

### 7.3 Failure outcomes and controls

| Failure | Expected behavior | What to demonstrate |
|---|---|---|
| Missing/failed/rejected C2 | Proposal blocked | Disabled hand-off or API validation error |
| Fabricated/unobserved policy ID | Research blocked | Cited ID absent from successful tool observations |
| Stale quote or expired approval | Block; require fresh review | No accepted simulated write |
| Invalid edit | Reject on revalidation | No unsafe quantity accepted |
| Old hash after edit | Reject | Changed hash and pending new approval |
| Timeout after broker commit | Reconcile existing request | One committed action, recovered status |
| Kill switch | Invalidate prior approvals | No submission until control off and fresh review |
| Process restart at interrupt | SQLite state remains | Resume same thread without auto-approval |

## 8. Interfaces, persistence, security and observability

### 8.1 API and trust boundaries

FastAPI exposes /health, /docs and /metrics, data/backtest/research services, /workflow/start, /workflow/start/stream, /workflow/status/{thread_id}, /workflow/resume and emergency controls. Use the generated /docs schemas for exact current request fields. SSE is available for the action workflow; the Streamlit page mainly uses synchronous requests. Do not claim the UI streams C2 tokens or provides a chat interface.

The reviewer token is a local demonstration credential, not enterprise identity/role management. Model keys remain server-side. Internal Docker MCP HTTP endpoints do not implement production-grade authentication. Untrusted retrieved text and tool output must never change role permissions or grant a write tool.

Pre-tool validation checks tool allowlists, schemas and budget; post-tool handling captures observations/errors. Input/output scanners, finite-value validation, citation checks and exact action approval provide layers of defense. A lexical scanner alone is not a complete injection defense. Logs and saved outputs need review for sensitive content before sharing.

### 8.2 Core request and data contracts

| Contract | Key fields and validation | Why it matters |
|---|---|---|
| CaseEvidence | symbol/date, regime, Close, RSI14, ADX14, EMA20/50, ATR14; optional selection score/rank/turnover; extra fields forbidden and nonfinite numbers rejected | Locks historical evidence independently of gold labels |
| MarketJudgement | regime enum; explanation up to800 characters; typed company assessment/status/citations/risks/limitations | Stops a specialist inventing a new regime |
| StrategyJudgement | strategy enum;1–16 cited IDs; explanation up to800 characters | Enables route and observed-citation checks |
| CriticJudgement | strict boolean accept; reason up to800 characters | Keeps research verdict distinct from human approval |
| OrderProposal | request_id, symbol, side, positive integer quantity≤100,000, MARKET order type, positive reference/stop, strategy, DEMO_ONLY account, ISO signal date and timezone-aware expiry | Canonical serialized fields determine the SHA-256 approval hash; the current gate supports BUY only despite the shared side enum |
| Workflow start/resume | Start: research_run_id, research_case_id, capital_reference and optional fault flags. Resume: thread_id, decision, payload_hash and changes | Browser identifies saved research/action; server reloads and verifies it |

Important endpoints are POST /research/experiments/run, POST /knowledge/search, POST /simulation/run, POST /market/selection and the workflow routes above. Reviewer-authenticated actions use X-Reviewer-Token; a missing/invalid reviewer token returns403. Consult /docs for schemas rather than copying stale payloads from old manuals. The legacy disable_llm field on workflow start does not disable the mandatory completed-C2 gate; it reflects that proposal preparation itself makes no additional model call.

### 8.3 Persisted artifacts

| Location/type | Contents and purpose |
|---|---|
| data/market_config.json and data/nse_nifty20/ | Active source, cached OHLCV and download metadata |
| knowledge/corpus.jsonl and manifest.json | Versioned policy/background passages and provenance |
| data/model_cache and data/rag/ | Local model weights, embeddings, index and verification status |
| data/company_research/packs/ | Full extracted company text, source/timestamps, checksums and coverage; bounded excerpts go to models |
| data/c2_portfolio_runs/ | Checkpointed C2 portfolio phases, fills, holdings, usage and per-decision research traces |
| data/simulation_runs/ | Saved replay settings, metrics, ledger and screening audit |
| Saved research JSON under data/ | Case outputs, hand-offs, usage and traces, not a model checkpoint |
| SQLite databases under data/ | Action checkpoints, broker request/audit records and reviewed lessons |
| reports/ | Local test/development/experiment evidence with limitations |

Back up needed data and SQLite files after stopping writers. Do not mix mocked generation smoke artifacts with authentic provider runs. Keep secret-bearing files, private DBs and cache data out of a public repository.

### 8.4 Monitoring and deployment boundary

The Compose file starts API, dashboard, five read/compute MCP servers, Qdrant, Prometheus and Grafana. Local neural retrieval uses Chroma; starting Qdrant does not mean it is used. The Qdrant override is an alternative unverified path, not required for the single recommended local demo.

Grafana currently includes request volume, blocked trade events, API health, approved proposals, completed simulations and attempted inference units (backend-specific requests/invocations). C2 portfolio counters additionally expose known attempts, uncertain reservations and completed windows. Detailed specialist/token/cost/tool trajectories are saved in JSON; dedicated Grafana panels for all those dimensions are not implemented. LangSmith/Langfuse tracing is not configured. Inspect actual recorded traces rather than promising external trace hosting.

Alerts define API-down after one minute and more than five risk blocks over ten minutes. Rule configuration is not evidence of an alert firing or notification delivery. CI includes tests, a development evaluation threshold and a deliberate failure-demo option. A local 17/20 =85% result correctly fails the 90% gate; a hosted GitHub run has not been demonstrated. This directory currently has no .git metadata.

## 9. Local setup and preflight

### 9.1 Recommended single demo setup: local API and Streamlit

Use the existing local NSE cache and neural Chroma index. Do not switch among variants during the main demonstration. Internet is required for the selected inference transport even when data and retrieval weights are cached.

1. Close an older launcher with Ctrl+C. Stop only the processes you started; do not blindly kill unrelated port users. Restart both services after source/configuration changes so the UI and API agree on version 0.16.2.
2. In Terminal, use the project path and launcher below. The first command installs dependencies; for an already installed environment use the fast restart command instead.

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
bash scripts/start_unix.sh
```

Fast restart in an already installed environment:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
.venv/bin/python scripts/launch_local.py
```

3. Open http://127.0.0.1:8501 and confirm http://127.0.0.1:8000/health responds. Open /docs separately for API evidence.
4. Privately open .env in your editor. Verify AEGIS_LLM_BACKEND, its supported ChatGPT CLI login or OpenRouter API key, AEGIS_ENABLE_LLM_EXPERIMENTS=true, AEGIS_REVIEWER_TOKEN and neural retrieval configuration. Never display this file during screen sharing. Paste only the reviewer token into the UI sidebar, not the OpenRouter key.
5. Use Market Data to verify the NSE cache is active. Persisted market_config.json takes precedence over a stale synthetic setting. Use Policy Knowledge to verify the neural index before attempting generation.
6. Confirm the selected backend is ready and has account allowance. For Plus follow AegisTrade_ChatGPT_Plus_Full_UI_Demo_Runbook.docx; the verified one-case run is loadable without another invocation. For OpenRouter confirm separate funding/access. Then run one explicitly consented C2 case if a fresh call is wanted.

No data/model download should be necessary for the already prepared local cache. If the neural index is missing or the corpus changed, rebuild it before the demo:

```bash
.venv/bin/python -m scripts.build_rag_index --mode neural --activate
```

If weights are missing and offline mode prevents downloading, run the one-time build with HF_HUB_OFFLINE=0 in that terminal command. The script activates neural mode and offline cache settings only after verification. Restart the launcher afterwards. This uses public model downloads, not paid OpenRouter generation.

Use scripts/download_nifty20.py only if refreshing/resuming data is actually needed; the present cache is complete for the recorded request. A changed dataset can invalidate saved research, so download and rehearse before assessment day.

### 9.2 Separate terminals for the backend-restart demonstration

Use these instead of the combined launcher when rehearsing crash/resume. From the project root in Terminal A:

```bash
.venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --env-file .env
```

From the same root in Terminal B:

```bash
.venv/bin/python -m streamlit run app/ui.py --server.address 127.0.0.1 --server.port 8501
```

The API reads private configuration from .env; the UI defaults to the local API and receives the reviewer token through its sidebar. Pause an order, keep Terminal B/browser alive, stop only Terminal A with Ctrl+C and rerun its command. Verify the same thread/hash remains waiting before submitting a reviewer decision. Do not use an auto-reloading development server for a staged restart proof. If ports are already occupied by the combined launcher, stop it first.

### 9.3 Optional deployment evidence session: full Compose

This is a separate qualification step, not needed for the recommended local presentation. Docker Desktop must be running. The stack has only configuration validation so far, not a proven clean-machine installation.

1. Stop the local launcher to release ports 8000/8501. Preserve .env privately. Check Docker daemon health and available disk space.
2. Validate with docker compose config --quiet, then build/start with docker compose up --build -d. Use docker compose ps and service logs to diagnose health; do not treat a successful YAML parse as a running stack.
3. Named Docker volumes do not inherit the host data directory. For a fresh demo volume, copy the already downloaded folder using docker compose cp data/nse_nifty20 api:/app/data/. Do not overwrite a populated dataset without a backup. Activate it through Market Data after the copy.
4. Build neural weights/index inside the shared volume with docker compose run --rm -e HF_HUB_OFFLINE=0 api python -m scripts.build_rag_index --mode neural. Ensure AEGIS_RETRIEVAL_MODE=neural in private .env for both API and knowledge service, then restart them. Verify retrieval through the running knowledge MCP service, not only the API.
5. API and knowledge/records services share the data volume. The market MCP server now shares /app/data with API for company packs. The strategy service generic dataset tools still lack that shared dataset mount; the locked research-case tools receive their case evidence, but broader Docker data consistency remains to be checked before claiming complete equivalence.
6. Verify UI, /health, actual HTTP MCP tool calls and a one-case consented C2 on the deployed stack. This may expose further setup work; allow rehearsal time.
7. Open Grafana at http://127.0.0.1:3000 using admin and the private AEGIS_GRAFANA_PASSWORD; Prometheus is at http://127.0.0.1:9090. Keep passwords out of the recording.

To demonstrate the API-down alert safely after the stack is healthy, stop only the API container with docker compose stop api, keep Prometheus running, and inspect its Alerts page until AegisAPIDown is firing after the configured hold plus scrape/evaluation delay. Capture evidence, then docker compose start api and confirm recovery. This proves a firing rule, not delivery to email/Slack. Do not stop the entire stack because that also stops the evaluator.

## 10. Step-by-step operation in all eight UI workspaces

### 10.1 Market Data — establish provenance first

1. In the visible Workspace selector, choose Market Data.
2. Read source, requested/effective dates, symbol count, coverage and quality limitations. Confirm 20 stocks and NSEPython rather than synthetic.
3. Inspect the frozen-universe ranking and excluded-symbol reasons. Explain liquidity selection and current-membership survivorship bias.
4. If the dataset is downloaded but inactive, enter the reviewer token, acknowledge “Use this provisional research dataset with the displayed limitations understood” and choose “Use downloaded NSE data”. Do not reactivate needlessly when already active.
5. Use “Refresh download status” to reread status. For evidence export, prepare the OHLCV CSV then download the active CSV. Record provenance alongside it and respect redistribution limits.

Expected result: charts, screening, backtests and research cases refer to the same active dataset. Missing data is a setup problem, not a reason to silently use synthetic data.

### 10.2 Overview — inspect one instrument

1. Choose Overview, then an Instrument and History window; 360 sessions is manageable for the screen.
2. Inspect price/indicator overlays and the regime/strategy summary. Identify one value behind the route, such as ADX or EMA alignment.
3. Explain that an indicator chart and route are market analysis, not completed C2 or an approved order.

### 10.3 Strategy Backtests — complete C2 historical portfolio

1. Choose Simulation engine = **C2 historical portfolio**. Enter capital, historical period, risk, fee and slippage assumptions. C2 uses automatic ROUTER screening; Technical-only baseline remains the separate no-generation option.
2. For the first C2 rehearsal choose a short period, such as2026-10-23 through2026-11-06. Public source coverage varies by stock/date. The TCS2026-10-23 pack is already prepared; other required dates are prepared/checked on demand. A prepared entry pack does not imply every later review date has sufficient sources.
3. Set Total inference allowance (requests or CLI invocations; default 48) and holding-review interval (default 5 market sessions). A new entry and each scheduled review can normally use six calls, with an eight-call reservation/ceiling. Five-year jobs can require many explicit allowance extensions; the app never silently removes the cap.
4. Enter the reviewer token. Select paid consent and the upfront historical rule approval. This authorizes automatic historical entries/exits under those rules, not real orders. There is no per-fill approval pause in this evaluation path.
5. Click **Run historical portfolio simulation**. This creates a background job. Open **C2 portfolio progress, resume and saved jobs**, note the run ID and click **Refresh C2 progress**. Read date, OPEN/CLOSE phase and completed-session count.
6. For PAUSED_BUDGET, select additional allowance and explicit resume consent, then **Resume C2 portfolio**. For PAUSED_PROVIDER inspect the failed trace, resolve credits/access/configuration and consent to resume. **Pause C2 portfolio** requests a safe pause. A saved job/run ID restores progress after a browser restart; a compatible process restart resumes the persisted phase.
7. Inspect **C2 entry / holding-review decisions and traces**. Read ENTER/HOLD/EXIT/BLOCKED/provider failures, policy/financial citations, actual calls and the corresponding full research record. A code shortlist is not an executed entry.
8. Inspect the simulated ledger: BUY, SELL_STOP, SELL_SIGNAL and SELL_C2. Verify a model-driven order fills after its signal/review date, with risk/cash checks at the actual open.
9. Inspect **Open holdings, unrealized P&L and pending orders**. Ending the replay does not force their sale. The cash/marked-equity/P&L identity should reconcile; stale marks and final-close exit intentions remain visible.
10. After completion compare C2, technical ROUTER and passive results over the same window. A partial run withholds full-period reference metrics; COMPLETED_WITH_GAPS requires interpreting source/decision failures. Model charges are separate USD, not included in INR trading returns. Download the complete JSON/ledger for evidence.

For a zero-generation foundation demo select **Technical-only baseline**, then ROUTER or ALL, approve assumptions and run. Its source/selection audit supports the earlier single-case hand-off to AI Agent Experiments. Do not label those baseline returns as C2 returns. The five-year saved technical run remains useful reference evidence, not a paid C2 performance result.

### 10.4 AI Agent Experiments — genuine LLM research

Lesson memory is optional. “Use frozen human-reviewed lessons” is disabled until accepted lessons have been explicitly frozen; a first run needs no lessons. Use “Preview selected-date stock shortlist (no model calls)” to submit your chosen dates and inspect candidates before authorizing research. Memory readiness is checked before company downloads/model calls. Errors now display the exact API reason and corrective action inline; an unfrozen playbook is not a provider-credit error.

1. Choose AI Agent Experiments after the hand-off. Verify provider-enabled/key-configured status; these status flags do not prove available credits.
2. For a no-spend rehearsal, use “Inspect latest stock screening”. It is deterministic preview, not LLM output.
3. Set Experiment configuration = C2 and case count =1. Keep the transferred screening capital. Explicitly set “Latest case date” to the selection-audit date you noted; verify the date inputs even when prefilled, because previous browser widget state can retain older values. Keep “Earliest case date” on or before that date and automatic candidate ranking on. The backend validates candidates against the saved simulation at that final date. Keep output budget 4,800 and memory off for the first demo unless a reviewed frozen playbook is ready.
4. Expand “Historical company research — prepare before paid calls”, select TCS and 2026-10-23 for the saved example, and choose “Prepare historical company evidence” or “Inspect cached company evidence”. Inspect source URLs, exact availability times, CMP IDs and coverage. Public download/extraction makes no paid model call. INFY currently has insufficient readable financial evidence; do not bypass that outcome. The research service also prepares/checks required packs automatically before generation.
5. Read the visible pre-run plan and maximum attempted paid calls. Enter the reviewer token and explicitly select the paid-run consent checkbox. Click “Run AI experiment”. This is the point at which the selected inference transport starts.
6. Inspect market, strategy and critic hand-offs, observed tools, retrieved passage IDs, corpus fingerprint, guard outcome, actual call count, latency, usage and errors. Successful completion should have all three typed hand-offs, SUFFICIENT company coverage/assessment, observed policy and financial citations, accepted critic, passing code guard and no model errors. The Company research result expander shows summary, event risks, limitations and pack hash.
7. Expand the full trace to identify a tool-selection request, actual MCP observation and subsequent model interpretation. Explain normal six-call behavior and the shared eight-call ceiling.
8. Select an eligible case and click “Use this C2 case in Supervised Trading”. The backend will revalidate it; a visible button alone is not approval authority.

If 402/401/429, a timeout, missing citation or rejected critic occurs, keep the error evidence, resolve the cause and run a new explicitly consented case as appropriate. Never substitute C0, a mocked output or a partial research response to unlock a proposal. Old saved results without the current corpus provenance require a new C2 run.

### 10.5 Supervised Trading — exact approval and local submission

1. Choose Supervised Trading. Confirm the linked researched case. Without it, the proposal button should be disabled.
2. Set “Reference capital for this supervised proposal (₹)”; this sizes one proposal and does not import the historical portfolio's cash/holdings ledger.
3. Leave both failure-injection checkboxes off for the primary success story. Click “Prepare researched order for human review”. There is no new generation call at this stage: validated completed research is reused.
4. At WAITING_HUMAN read symbol, side, whole-share quantity, reference and stop prices, strategy, dates, request identity and approval hash. Read research explanation and citations before deciding.
5. Demonstrate edit first: select “edit”, choose a lower positive quantity that remains valid, and click “Submit reviewer decision”. The UI's suggested +1 may exceed limits; enter a deliberate feasible edit. If original quantity is one, choose another suitable case rather than assuming an increase is safe.
6. Confirm a new hash/payload and WAITING_HUMAN again. Explain why the old approval cannot apply. Then select “approve” and submit the new decision within its expiry.
7. Confirm ACCEPTED_SIMULATED or the returned safe outcome. Inspect Broker Audit for the corresponding durable event. A blocked result is not an accepted fill.

Show reject on a separate proposal if time permits. Failure demonstrations should use fresh proposals and explicit reviewer actions, not an already consumed approval.

**Restart/resume demonstration:** leave Streamlit/browser running while a proposal waits; note thread ID/hash privately, restart only the FastAPI process using a separately launched API terminal, then use “Load persisted workflow state” and resume through the retained UI session or /docs schemas. The combined launcher stops both processes, so rehearse a separate API/UI launch for this segment. A fresh browser session does not automatically reconstruct its waiting-order form from a thread ID; the status/resume APIs are the fallback. Persistent state does not imply unrestricted cross-session UI restoration.

### 10.6 Policy Knowledge — RAG without paid generation

1. Choose Policy Knowledge. Confirm 81 passages, authority breakdown and verified neural/persistent-index status.
2. Query “What happens if completed C2 research changes before approval?” and click “Search policy knowledge”. Inspect source IDs, policy text, code locators and rank.
3. Enable the historical-date option and choose the case date. Inspect which external references are available, and distinguish publication/retrieval dates from indexed date.
4. Explain that retrieval uses local embedding/reranking models but does not launch generation; generative explanation occurs in C2. Neural retrieval alone is not a completed GenAI research response.

### 10.7 Learning & Lessons — review before memory

1. Choose Learning & Lessons and inspect pending, accepted/rejected and frozen-playbook state.
2. The candidate template button is a deterministic teaching example, not actual Reflexion. A real reflection is drafted from a scored development C2 failure in AI Agent Experiments using a separately consented model call.
3. Review one valid conditional lesson and accept with a reason; reject a bad/overbroad lesson with a reason. Do this before freezing. Do not create fake evidence of unseen-case benefit.
4. Freeze the reviewed playbook using the displayed confirmation. The UI does not provide a simple freeze undo. Preserve an existing frozen playbook rather than resetting it for presentation.
5. Memory-on research now uses relevant accepted lessons. For the academic claim, compare frozen memory-off/on on untouched held-out cases and include lesson-generation cost.

### 10.8 Broker Audit — reconcile actions with approvals

1. Choose Broker Audit and refresh after a supervised submission.
2. Match request identity, symbol, quantity and status to the reviewed payload. Check the exact event type rather than expecting one total audit row, because decisions and recovery may also be logged.
3. Export the audit CSV for the evidence pack after checking it contains no secrets.
4. On a fresh proposal, enable “Inject timeout after simulated commit (expect reconciliation)”, complete approval and verify one committed action with recovered status. On another proposal, “Inject stale quote (expect rejection)” should block safely.
5. Emergency controls are in Supervised Trading: enter a reason, enable the block checkbox and apply. Old approvals must remain invalid after disabling the control; create a fresh proposal.

## 11. Additional work to prepare a reliable demonstration

### 11.1 Must do before the live success demonstration

- Restart current services on source 0.16.2; confirm API/UI version agreement and active NSE data.
- Confirm provider credit/model access, then capture one genuine, successful, current-corpus C2 run and a short C2 historical portfolio with explicit consent before presenting real C2 returns. Save run/case ID, tool trace, call/token/cost data and errors, if any. A valid key and mocked tests do not replace this step.
- Choose and rehearse a ROUTER audit date with an eligible affordable candidate and quantity large enough for a valid reduced-quantity edit. Record the date/run ID on a private cue card.
- Verify neural retrieval and cached weights; test network access and readiness for the selected inference backend from the assessment environment. Keep a labelled backup recording in case of connectivity failure.
- Rehearse edit → new hash → new approval → simulated broker record, then one safe failure and timeout reconciliation. Work within approval expiry.
- Save sanitized screenshots of provenance, selection reasons, all three specialist hand-offs, policy citation, exact approval, broker record and metrics. Do not record .env, private tokens or billing pages.

### 11.2 Additional work for final guideline evidence

Validate the implemented extractive context packing on additional evidence shapes; tighten domain output schemas and structured tool-error coverage; harden held-out file isolation. Independently review the gold set and relevance labels. Run E1/E2/E3 with actual provider results and final held-out comparisons repeated three times, calibrate a genuinely different-family judge against at least 20 human labels, and produce the 4–6-page evaluation report. Retain rejected lessons and negative results.

Verify full Compose on a clean machine, actual HTTP MCP data consistency, one firing alert and an actual failed hosted CI run. Current source is not a Git repository; publishing a sanitized private repository and running GitHub Actions is a separate team action. The failure-demo workflow uses an altered copy of development expectations to produce 85% versus a 90% gate; explain the deliberate trigger and keep the original data unchanged.

Complete experiment and contribution logs, final 10–12-slide deck and backup recording. Verify whether the custom trading topic/signature ablation needs a specific faculty sign-off in addition to the already approved team size. The supplied general PDF describes five reference projects; do not assume team approval alone resolves any separate topic process.

### 11.3 Suggested 15-minute, three-person script

| Time | Presenter | Screen and proof |
|---|---|---|
| 0–2 min | Veneet | Problem, scope, dataset provenance and raw-price/survivorship limits |
| 2–4 min | Veneet | Saved or fresh ROUTER replay, ranking audit, capital/selection rationale |
| 4–8 min | Karthika | C2 plan, live one-case generation, actual MCP evidence, citations, critic and usage; use measured latency rather than promising a fixed duration |
| 8–11 min | Mathangi | Linked research, exact payload, quantity edit, new hash, fresh approval, audit |
| 11–13 min | Mathangi | One rehearsed stale/timeout/restart scenario and actual metrics/alert evidence |
| 13–15 min | All | E1–E4 results or accurately identified pending evidence, design tradeoffs and individual responsibilities |

If model latency is long, show a pre-recorded genuine run while it completes and label both honestly. If no real C2 success is available, demonstrate the failure-closed path and explain the missing provider evidence. Never present a mocked or C0 run as live multi-agent generation.

### 11.4 Troubleshooting checklist

| Symptom | Likely cause | Correct response |
|---|---|---|
| Old UI/version mismatch | Old process still bound to port | Stop the known launcher and restart reviewed source |
| 403/reviewer failure | Wrong/missing reviewer token | Use private AEGIS_REVIEWER_TOKEN; it is not the provider key |
| Lesson memory unavailable | No frozen playbook with accepted lessons | Keep memory off; review/freeze lessons explicitly only when ready |
| OpenRouter 402 | Funding/access issue at provider | Resolve in provider account; preserve failure evidence; do not bypass C2 |
| Neural cache error/offline download | Missing weights or stale index | Build and verify index with public downloads allowed, then restart |
| No selected stocks | No entry/cash/capacity on that date | Inspect another eligible audit date; explain exclusions |
| C2 not eligible for order | Guard/critic/provenance/entry failed | Inspect errors and rerun appropriate current research |
| Approval fails after delay/edit | Expiry/hash/current-evidence mismatch | Prepare/review a fresh valid payload |
| No Grafana on local launch | Monitoring is in Compose | Use a separately rehearsed full stack; local launcher starts only API/UI |
| Docker data differs from host | Named volume lacks cache/config | Seed/activate dataset and rebuild index inside volume; verify MCP views |

## 12. Cross-check against the capstone guideline

Sources reviewed: capstone_fullstack_projects.pdf, especially pp.2–6 and 17; the supplied proposal/design DOCX and four-slide initial PPT; current source, tests and reports. Page numbers below refer to the supplied PDF. “Implemented” is a code statement; “demonstrated” requires corresponding run evidence. The guideline's formal marking rubric is supplied separately and cannot be inferred from this PDF.

### 12.1 Minimum-bar matrix: all eleven rows on PDF p.3

| Area | Current implementation/evidence | Remaining requirement or qualification |
|---|---|---|
| Retrieval | 81 dated/source-labelled passages; BM25 + MiniLM + RRF + cross-encoder + rewrite; 101-query before/after development metric | Independently review relevance and generated faithfulness; disclose old-subset regression. Local Chroma verified; Qdrant not verified. |
| Tools and MCP | Six FastMCP modules, 14 tool contract tests/inventory; real stdio research tools; read/write separation | Tighten generic output schemas and uniform structured-error results; prove deployed HTTP path. |
| Orchestration | Typed graphs, conditions/correction, SQLite action interrupt and rebuild/edit test | Record live stop/resume; research graph itself does not persist mid-generation. |
| Memory | SQLite reviewed lessons, written policy and frozen relevant retrieval | Bounded extractive evidence projection and duplicate-window references are implemented; remaining overflow fails closed. Actual held-out memory-off/on benefit missing. |
| Planning | Visible plan and bounded contradiction/schema feedback | Retain real model replan trace. Rejected critic currently remains blocking, not proven successful reacceptance. |
| Multi-agent | Supervisor + three scoped specialists/typed hand-offs; C1 same union/model/ceilings | Successful authentic provider run and fair quality/cost comparison still required. |
| Improvement | One-call dev reflection, human review, rejection reasons, freeze and E3 runner | Run genuine scored dev failures; record accepted/rejected lessons, unseen benefit/regression and all learning cost. |
| Evaluation and monitoring | 60 candidate fixtures; scorer/runners; traces; Grafana panels and judge-agreement script | Independent ≥60 gold cases, ≥40 protected held-out, real different-family judge +≥20 human labels/kappa; repeated actual model results. |
| Human control/hooks | Persistent interrupt, exact hash, approve/edit/reject; permission/budget logging; stale/kill/idempotency checks | Record live edit invalidation/resume. Simulation does not establish production identity or real execution safety. |
| Security | Threat model, allowlists/guards, 32 seeded attacks and 10 clean; E2 poisoning support | Scanner 30/32 and 0/10 false blocks are proxies. Need actual model-level off/on attacks incl own-data path and meaningful attack outcomes. |
| Deployment | FastAPI SSE, Compose services, versioned prompts/models, CI gate, alert rules | Clean-machine running stack, shared-data consistency, real firing alert and hosted failed CI proof missing. |

### 12.2 Four required experiments, PDF pp.5–6

| Experiment | Fair protocol | Current position |
|---|---|---|
| E1 C0/C1/C2 | Same cases, C1/C2 model/tools/budget ceiling; include quality, constraints, calls, cost and latency | Harness implemented; independently reviewed real model comparison missing. C0 self-agreement is not a quality result. |
| E2 defenses off/on | Same independent attacks and clean tasks; isolate injected research data; report attack success and false blocks | Runner toggles scanner while hard permission/approval remains. Current success metric is forbidden-tool attempt/forbidden final text, not actual unauthorized broker write. Need actual runs and explicit outcome definition. |
| E3 lessons off/on | Freeze reviewed playbook before held-out; include rejected lesson, generation cost and regressions | Runner exists; actual held-out effectiveness and total learning-cost accounting remain to be completed. |
| E4 signature ablation | Router vs fixed strategies + passive benchmark under equal data/cost assumptions; add safety-failure evidence for the second signature | Current evaluation CLI E4 is synthetic deterministic routing. The C2 historical portfolio now provides actual researched-entry/holding-review accounting and same-window ROUTER/passive comparisons, but real independent model performance remains unmeasured. |

Use at least 60 independently reviewed cases, roughly20 development and at least40 held-out, and keep scenario families together. The solver must not receive hidden labels. Current repository/process isolation is insufficient to assert the agent cannot read held-out files merely because no file-read tool is offered. Protect labels from the solver process/container and tuning team. If held-out results guide a change, reclassify those cases as development and disclose it.

For final comparisons repeat held-out runs three times and report spread. Include success counts, violations, attacks, false blocks, cost/case, median/p95 latency, errors and timeouts. Provider cost can be unavailable: mark unknown rather than zero. The judge script checks model metadata but a different provider prefix alone does not prove a genuinely different model family; the team must verify that choice and obtain real predictions.

### 12.3 Submission package, PDF p.6

| Required artifact | Available starting point | Team action before submission |
|---|---|---|
| One-command README | README.md; scripts/start_unix.sh | Verify from clean installation; link this current guide |
| Original architecture + numbered walkthrough | Five diagrams and Sections2–10 in this guide | Rehearse redraw and request trace |
| Tool list, schemas/tests | docs/MCP_TOOL_INVENTORY.json; tests/ | Review all read/write classifications and output contracts |
| One-page threat and memory policies | docs/THREAT_MODEL.md; docs/MEMORY_POLICY.md | Keep current; include actual context/retention limits |
| 4–6-page evaluation report | docs/EXPERIMENT_REPORT_TEMPLATE.md | Fill with genuine E1–E4, judge and repeated-held-out results |
| Experiment log | Existing reports and versioned configs | Add dated decisions, negative findings, costs and trace links |
| Contribution log | docs/TEAM_WORK_SPLIT.md is a plan | Record actual dated contributions and peer review; do not call the plan a log |
| Final slides | Initial four-slide concept PPT | Update architecture, actual rules/results/limits; remove obsolete team-exception wording |
| Backup demo | Not established by source | Record a genuine sanitized end-to-end success and failure path |
| No secrets/private redistribution | Ignore rules and private .env | Audit repository/export; verify data/source redistribution permission |

### 12.4 Proposal and initial-slide alignment

The original slide flow and both signature challenges remain useful. “AI router” needs precise wording: models explain/check the code-permitted route, and their measured added value is a research question. The updated design places completed C2 before human approval, whereas a conceptual arrow diagram alone did not establish this gate.

Keep actual risk/strategy thresholds consistent across code, report and slides. Proposed notifications, production authentication, comprehensive financial-data adjustments and full research resume must not be presented as completed features. The initial PPT is a concept deck and needs a results/limitations section. Team-size approval is already settled; no fourth member is needed.

## 13. Evidence references and team handover

Version 0.16 verification records 141 passing tests, including mocked model contracts, genuine stdio MCP, exact researched-order linkage, fabricated-citation rejection and bounded correction. This update downloaded real TCS/INFY archive evidence and added controlled company-research tests. The genuine Codex one-case and tiny portfolio evidence is recorded separately in reports/codex_c2_demo.json and reports/codex_c2_portfolio_demo.json. An isolated actual-NSE/stdio-MCP/neural-RAG C2 portfolio smoke with mocked generation completed 11 sessions, one entry and one unsold holding; accounting reconciled within floating-point tolerance. The report is reports/c2_portfolio_integration.json and is not a genuine model-performance result. Refer to docs/BUILD_AND_VERIFICATION_STATUS.json for dated scope, plus reports/rag_development.json, rag_ui_smoke.json, rag_mcp_smoke.json, rag_agent_integration_smoke.json and nse20_simulation_smoke.json. The agent-integration generation smoke is explicitly mocked.

Recommended responsibilities remain: Veneet leads data/quant/evaluation and independent attack cases; Karthika leads RAG/MCP/agents/reflection; Mathangi leads risk/approval/UI/platform. Keep hidden-label authorship separate from agent tuning and attack authorship separate from defense construction. A second member reviews lessons and safety assumptions. Each member must understand every diagram and the eight PDF p.17 viva topics.

Use the companion viva document to rehearse answers with actual trace IDs and measured results. Replace placeholders only after performing the corresponding experiment. Accurate limits and a defensible trace are stronger evidence than an unsupported claim of complete compliance.

## 14. Plus demo companion and transport switching

Use AegisTrade_ChatGPT_Plus_Full_UI_Demo_Runbook.docx for exact Mac login/configuration, a verified historical case, all eight workspaces, approval/edit/reject/recovery, a short C2 portfolio including exits/open holdings, quota handling and switching back to OpenRouter. The current private .env selects codex_cli. The source default remains openrouter. To switch back set AEGIS_LLM_BACKEND=openrouter and clear AEGIS_LLM_MODEL so OPENROUTER_MODEL applies, then restart; keep the private provider key. Switching a paused historical job requires restoring its original identity or creating a new run.

## 15. Specific validation feedback and evidence short-circuit (0.16.2)

Hard field constraints are derived from Pydantic schemas and included in each specialist's prompt. For example, company.summary has a600-character maximum. A failed response receives exact field/constraint feedback within the existing three-turn specialist and eight-unit case ceilings. The code retains strict bounds, citations, source hashes and material-risk checks; it never truncates an assessment into compliance. Structured failures distinguish schema/JSON, evidence, provider, budget, policy and execution problems.

A completed market hand-off of INSUFFICIENT_EVIDENCE blocks further specialists for that case. REVIEW_REQUIRED blocks an entry, but may proceed through strategy/critic for a risk-reducing holding EXIT. Research insufficiency cannot be repaired by buying more inference allowance. Existing code protective/strategy exits remain independent.

Saved older generic schema failures can be diagnosed from recorded model JSON. The portfolio status view adds a derived field-level explanation and retains recorded_errors; original research/state files and trading decisions are unchanged. Historical prompt identity is preserved: the affected August–November job was paused and requires a new job to use changed prompts. A UI notice explains this before users attempt to resume. See reports/research_validation_diagnosis.json for the specific screenshot records.

## 16. Exact critic citations and specific provider failures (0.16.3)

Strategy citations are reloaded independently by the critic's existing read-only MCP search. Exact requested IDs are retained before semantic-ranked matches and still obey external-source historical date filtering and corpus provenance. This prevents a valid strategy citation from being lost merely because it did not rank in the critic's different semantic query. No model acceptance is manufactured; contradictory or unsupported evidence still blocks.

The supervisor ends at the critic. Rejection returns CRITIC_REJECTED and makes no further strategy call. Within-specialist schema/evidence correction remains bounded by the existing three turns/eight-unit ceiling. The removed post-rejection revision had no path to a fresh accepted critic and therefore spent allowance without a possible authorized outcome.

Specific saved usage codes such as CODEX_TIMEOUT and CODEX_OUTPUT_INVALID are carried into portfolio decisions/banner rather than replaced with a generic account/connection hint. Historical generic records receive a read-only derived diagnosis; original records/counters remain untouched. Timeouts retain the configured local bound and terminate the process group; no automatic retry/fallback or account-balance claim is made.


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

[[FIGURE:portfolio_memory]]


## Codex response-format correction — version 0.19.1

A saved RELIANCE entry case dated 1 February 2024 paused with CODEX_OUTPUT_INVALID after two CLI invocations. The usage record identifies JSONDecodeError, not an established quota/authentication failure. The original trace did not retain the parsing stage, so the precise malformed text cannot be reconstructed. The CLI envelope previously required the specialist JSON to be encoded again as a string; the adapter now supplies the exact specialist object schema directly, removing that extra encoding layer. Legacy valid JSON strings remain readable. Malformed JSON is not repaired or accepted; stage and line/column diagnostics are recorded without retaining arbitrary raw private output. Native tools and all C2 evidence/risk gates remain restricted.

This transport correction preserves the portfolio engine, policy corpus, prompts, memory version and backend identity. The current paused run can be resumed after restarting the API and dashboard together. In Strategy Backtests, open the paused saved C2 portfolio, set Additional inference units on resume to 0 (the observed run used 2 of its existing 48 units), tick the resume authorization and click Resume C2 portfolio. Failed calls remain counted. Resume starts a fresh research attempt for the failed case; it does not continue inside the broken CLI response. Later budget exhaustion can still require a deliberate allowance increase. No automatic retry, backend fallback or simulation is started by the patch.

If the error recurs, inspect the new validation_stage and json_error fields in the saved research usage; do not assume that buying API credits addresses a response-format error. Mocked schema/transport and regression tests validate the correction; actual account-backed success remains to be tested by an explicitly resumed run.
