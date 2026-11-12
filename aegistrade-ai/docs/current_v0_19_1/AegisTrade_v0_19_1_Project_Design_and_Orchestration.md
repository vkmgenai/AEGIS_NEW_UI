# AegisTrade AI — Current Project Design and Orchestration

Version 0.19.1 • Prepared 11 November 2026 • Team of three approved by the professor

## 1. Read this first

AegisTrade is a daily-bar, long-only equity research and simulated portfolio system. It screens historical stocks, asks tool-using language-model specialists to assess dated company evidence and explain the permitted strategy, validates their responses, and simulates entries, holding reviews and exits. It keeps source citations, decision traces, cash, holdings and trading costs for inspection.

The application has two execution paths. C2 historical portfolios use upfront human approval of the replay rules and then fill eligible historical orders automatically. Supervised Trading requires completed C2 research followed by human approval of each exact simulated order. Neither path submits live exchange orders.

This is a fresh description of the current code, rather than a collection of release notes. Read the separate UI Demo and Test Guide for clicks and settings, and the separate Viva Questions and Answers for examination preparation. The configured backend is Codex CLI with ChatGPT authentication; OpenRouter remains selectable by configuration. This document does not initiate inference or change a running job.

## 2. What the project demonstrates

The first signature challenge is explainable market-regime-aware routing. Code defines the market regime and permitted strategy catalogue; LLM specialists interpret observed evidence, explain the permitted route and critique its support. They do not invent unrestricted strategies or discover a guaranteed profitable strategy.

The second signature challenge is safe, auditable execution. Completed research precedes proposals, sizing stays in code, execution permissions are checked, exact approvals are bound to payload hashes in the supervised path, and historical portfolio actions retain dated evidence and accounting. Losses and abstention are legitimate outcomes.

GenAI generates company assessments, explanations and critic judgments. The agentic part is bounded model-selected read-only tool use, observation-driven responses, specialist hand-offs, limited correction turns, and integration with persistent application workflows. The supervisor plan and graph order are deterministic code; the supervisor is not an additional free-running LLM.

## 3. Overall design

[[FIGURE:current_architecture]]

| Layer | Responsibility | Principal source |
|---|---|---|
| Streamlit | Eight workspaces, configuration, consent, progress, lesson reviews and result inspection | app/ui.py |
| FastAPI | Typed requests, reviewer-token checks, backend readiness and job controls | app/api.py |
| Data and quant | Load bars, calculate indicators, classify regime, screen and rank | aegistrade/nse_data.py; strategies.py; selection.py |
| C2 research | LangGraph orchestration, model calls, tool conversations and typed outputs | aegistrade/agentic.py |
| Model adapter | OpenRouter requests or isolated Codex CLI structured inference | aegistrade/llm_backend.py |
| MCP | Read-only market/company, strategy and knowledge tools for research | aegistrade/mcp_runtime.py; mcp_servers/ |
| Retrieval | BM25, sentence embeddings, RRF, cross-encoder and exact-ID verification | aegistrade/knowledge.py; corpus.py; vector_store.py |
| Historical execution | OPEN/CLOSE replay, reservations, research validation, fills, exits, accounting | aegistrade/c2_portfolio.py |
| Supervised execution | Exact-payload human interrupt, rechecks and simulated broker audit | aegistrade/workflow.py; safety.py |
| Portfolio memory | Draft, review, immutable versions, temporal binding and bounded retrieval | aegistrade/portfolio_memory.py |

## 4. Market data and point-in-time decisions

The active dataset is selected by data/market_config.json. This persisted selection takes precedence over the AEGIS_DATA_SOURCE fallback in .env. Therefore seeing synthetic in .env alone does not establish that the current UI uses synthetic data. Inspect the dashboard source and dataset provenance.

The observed active dataset is NSEPython, using a frozen 20-stock subset of current Nifty 50 membership. Its manifest requests 8 November 2021 through 8 November 2026, with additional warm-up history. These are requested bounds; actual trading sessions and per-symbol coverage come from the cached bars. The universe is selected using the repository's frozen liquidity procedure, not a retrospective list of the best-returning stocks. Current-membership survivorship bias remains.

OHLCV means open, high, low, close and volume. Daily bars cannot reveal the precise intraday path. Prices remain unadjusted for unresolved corporate actions. A large raw-price jump is quarantined by a discontinuity filter; that does not reconstruct split-adjusted returns. Exchange-calendar reconciliation and historical constituent membership remain limitations.

A decision uses the completed trading session. Company evidence is restricted to information available by 15:30 Asia/Kolkata on that date. An old reporting period is not sufficient: publication/availability timestamps must also precede the decision. Current internet news is not automatically valid historical evidence. The archive pack contains selected official disclosures and readable attachments; optional imported newsletters require dated reviewed provenance. It is not a comprehensive point-in-time news terminal.

## 5. Indicators, regime and stock selection

Indicators include EMA20, EMA50, RSI14, ATR14, ADX14, prior 20-session high and annualized 20-session realized volatility. Indicators are code calculations, not LLM estimates.

| Code regime, evaluated in order | Main condition | Permitted route |
|---|---|---|
| WARMUP | Required indicators not ready | NONE |
| HIGH_VOL | Realized volatility above 0.48 or ATR/close above 0.065 | NONE |
| BREAKOUT | Close above prior 20-session high and ADX at least 18 | BREAKOUT |
| TREND | ADX at least 22 and EMA20 above EMA50 | EMA_TREND |
| RANGE | ADX below 22 after preceding checks | RSI_REVERSION |
| UNCERTAIN | Remaining cases | NONE |

Entry rules: EMA_TREND requires EMA20 > EMA50 and close > EMA20; RSI_REVERSION requires RSI < 42 and close > 0.88 × EMA50; BREAKOUT requires close above the prior high and ADX at least 18. A permitted route alone is not an entry signal.

The daily selector excludes already held names, insufficient history, low liquidity, unsuitable regimes, excessive ATR fraction, unresolved recent discontinuities, absent entry signals, and capital/risk/position-limit failures. Minimum history is 60 sessions; minimum average 20-session turnover is ₹1 crore; maximum ATR/close is 6.5%. A recent absolute raw close change above 30% triggers the discontinuity quarantine for its rolling window.

Eligible stocks are ranked using 70% strategy strength, 20% relative liquidity rank and 10% lower ATR fraction. Strength is strategy-specific; ties use the symbol. Available slots and cash constrain selections. The maximum portfolio position count is four, with a 20% equity exposure cap per position. Screening produces candidates, not researched orders.

## 6. Historical portfolio lifecycle

[[FIGURE:current_portfolio]]

1. The user selects capital, dates, costs, exit/risk settings, inference allowance and optional frozen memory. Protected API gates check reviewer token, explicit inference consent, replay-rule approval, feature enablement and backend readiness.
2. Creation freezes settings, input-data fingerprint, model/backend identity, prompt version, policy-corpus hash and optional lesson manifest. It computes an identical-rule technical reference and a separate equal-weight passive benchmark.
3. Each session enters OPEN. Queued sales are considered before buys. Missing bars can defer orders. Eligible buys must still pass current research/provenance and code sizing/cash/risk checks at their executable open.
4. Protective stop and profit rules use that day's OHLC with conservative sequencing. The portfolio then reaches completed-close processing, strategy exits and due holding reviews.
5. A scheduled holding review runs C2 with HOLDING_REVIEW and the holding context. A supported HOLD keeps shares; an accepted EXIT queues a later-open sale. A blocked review does not manufacture a sale or disable existing protective rules.
6. Code screens close-based entry candidates. Friday/pre-gap candidates are deferred without generation at that stage; the next actual trading close must produce fresh eligibility and research before a later-open fill. A normal eligible candidate proceeds to C2 entry research.
7. Passing ENTER decisions queue historical buys. Quantity is sized in code at fill using stop distance, available cash and position exposure. Research results, phase and processed-close keys are saved to make resumption consistent.
8. Cash plus marked holdings forms equity. The end date marks unsold holdings rather than forcing liquidation. Final-close intentions without a later executable bar remain unfilled.

A run can pause for inference budget, provider failure or a user pause request. A job's progress sessions are market sessions, not ChatGPT conversation sessions. Original failed usage remains counted. Version/data/corpus changes are not silently mixed into a paused job; incompatible runs require a new run.

## 7. Exact C2 orchestration and calls

[[FIGURE:current_orchestration]]

C2 compiles a LangGraph StateGraph: START → plan → market → strategy → critic → END. The plan node is code. The market node can stop the graph early when company assessment or adverse-risk status makes the action ineligible. Each specialist owns a conversation and a declared tool allowlist.

| Specialist | Normal first response | Application-executed MCP tools | Normal second response |
|---|---|---|---|
| Market | Requests market snapshot and company evidence | market_snapshot; company_evidence | Typed regime, explanation and company assessment |
| Strategy | Requests route check and policy retrieval | check_strategy; search_policy | Typed permitted route, policy citations, explanation and ENTER/HOLD/EXIT |
| Critic | Independently requests company evidence, route check and policy retrieval | company_evidence; check_strategy; search_policy | Typed accept/reject and reason |

Normal complete C2 therefore uses six inference calls and seven tool invocations. The shared case ceiling is eight inference calls, sixteen tool calls and 4800 requested output tokens. Per specialist there are at most three loop turns; the shared budget is checked first. Normally one call requests tools and one produces a final response. Invalid typed fields may receive one bounded correction if a turn and budget remain. A genuine final critic rejection ends the case, rather than starting an unbounded debate.

A model call returns either virtual tool intents or a final specialist response. AegisTrade validates tool names and arguments and executes tools through MCP. The model cannot execute shell, browser, broker writes or arbitrary MCP directly. Tools are separated into three persistent research MCP sessions per case: market, strategy and knowledge. Additional risk/records/execution surfaces in the wider project do not become unrestricted C2 tools.

Market and critic independently read the same current company pack. The critic additionally receives market and strategy hand-offs, and strategy-cited policy IDs are pinned into its retrieval for exact verification. Roles share evidence constraints but have different tasks; independence means a separate critique step, not proof of an independent model family or unbiased judgment.

Final code validation checks typed hand-offs, code-compatible regime/route, action/purpose, exact retrieved policy citations, company assessment/citations and dated pack provenance. A supervised proposal additionally revalidates completed C2. Passing schema alone never authorizes a trade.

### Codex CLI in version 0.19.1

The selected model is codex-default under the ChatGPT-authenticated CLI backend. The adapter launches isolated, ephemeral, read-only CLI invocations with native tools/apps/MCP disabled. Authentication stays in the supported CLI credential store; the application's private API/reviewer keys are not injected into the inference subprocess.

Version 0.19.1 supplies the specialist's actual object schema directly to the CLI output schema. This removes the previous extra JSON-inside-a-string layer for known specialists. Tool intents retain the allowed name and JSON arguments. Valid legacy response strings remain readable; malformed JSON is not repaired or trusted. Error records identify event-stream, outer-envelope, tool-argument or specialist-content parsing stages and JSON line/column where available, without storing arbitrary raw private output.

One CLI inference unit is one invocation, not a known count of internal provider requests. ChatGPT plan allowance applies; per-run USD cost is unknown, not zero. The response-token target is not a hard provider reasoning-token cap. There is no automatic switch to OpenRouter and no automatic retry after a transport pause. A six-call C2 case can take appreciable wall time; prepare long-run results before a short examination slot.

OpenRouter instead uses its configured API key and model, with provider-reported usage when supplied. Backend/model configuration is recorded and bound to a job. ChatGPT Plus authentication and an OpenRouter API key are separate credentials.

## 8. Company research, materiality and context management

Selected official disclosures are cached in dated company packs with text checksums, availability metadata, coverage and a content hash. Immutable snapshots preserve earlier versions. Attachment extraction is bounded: downloads up to 32 MB and PDF extraction up to 35 pages, with text limits. Full source in this context means the retained extracted source, not proof that every page or historical revision was captured.

The adverse-disclosure scan searches bounded dated official metadata and matched readable attachments. Its ready flag depends on scan completeness, timestamp validity, bounded candidate coverage and readable selected risk attachments. Financial evidence can qualify separately. The application does not silently replace missing historical evidence with current facts.

| Company/adverse assessment | Meaning for action |
|---|---|
| SUFFICIENT + NO_MATERIAL_ADVERSE_FOUND | May support ENTER/HOLD after all other checks |
| LIMITED + completed cited ready scan + NO_MATERIAL_ADVERSE_FOUND | May support a technical entry/HOLD with explicit financial/news limitations |
| UNKNOWN or MATERIAL_ADVERSE | Cannot support ENTER/HOLD |
| INSUFFICIENT_EVIDENCE / incomplete required coverage | Blocks the unsupported action |
| Cited REVIEW_REQUIRED in a holding review | Can support a justified risk-reducing EXIT, subject to critic/code checks |

NO_MATERIAL_ADVERSE_FOUND means none found in the stated bounded observed scope. It is not proof that no adverse information exists. The materiality rubric considers the event amount with its unit, issuer-reported impact, severity, operational restrictions, recency, unresolved consequences and resolution. Negative keywords or routine penalties alone do not establish material downside. An issuer's statement of Nil impact must be attributed and is not independent verification. Missing critical impact remains unknown.

The company view extracts action, amount, impact, status and event windows. Overlapping windows from the same source offsets are merged; identical windows share verbatim-text references while each document keeps its citation and field mapping. This preserves selected materiality context without repeatedly sending boilerplate. One historical example had an issuer Nil-impact section beyond the old excerpt boundary; the new view retains it. It is not a universal finding that every previous block was wrong.

Context uses a 26,000-character conversation bound. Full validated observations remain in the audit while compact views go to inference. Optional lessons yield space to dated evidence. Seven previously overflowing saved cases fit under this limit in mocked checks; one still blocked for incomplete adverse coverage. The bound is not exact token accounting and does not guarantee that all future evidence shapes will fit. Remaining overflow fails closed.

## 9. RAG and the difference between three evidence stores

[[FIGURE:current_rag_memory]]

Policy RAG uses 81 passages: 72 authored project policies and 9 external-reference passages. Neural mode combines BM25 lexical scores and MiniLM sentence embeddings, fuses rankings with reciprocal rank fusion, then applies a cross-encoder to the candidate set. Local Chroma stores the vectors; embeddings and model weights are cached. Query rewrite adds controlled aliases. Exact policy IDs requested by the critic are pinned alongside semantic results.

Passages carry IDs, dates, source and authority metadata. External references are filtered by their available publication/retrieval dates; authored project rules describe the experiment's fixed policy and are not historical market facts. Project rules, rather than public background alone, must support route authorization. Neural failure does not silently fall back to offline lexical retrieval.

The official-company archive is a separate symbol/date evidence store, not an unrestricted web search over the policy corpus. Portfolio lesson memory is a third store: reviewed process reminders, not company facts or strategy rules. The fact that all three contribute to a prompt does not make them interchangeable sources.

## 10. Reviewed portfolio memory

Completed portfolio decisions can produce deterministic candidate lessons for context handling, materiality, missing coverage and citation problems. Drafting uses source decisions and dated research; later price and P&L are deliberately excluded as teaching labels. Provider timeouts do not become trading lessons. A deterministic template draft is a review aid, not an LLM discovery or a finding that each source decision was incorrect.

The user inspects original assessments and source links/windows, edits the conditional text if appropriate, and accepts or rejects with a rationale. Authentication uses the local reviewer token. Only accepted candidates can enter a frozen version; pending/rejected candidates remain outside research context. Versions include hash, accepted text, source date range and review provenance.

A new portfolio optionally selects one immutable version. Relevant lessons are retrieved using current evidence/context; at most three and 2400 characters are selected, with fewer or none when source context needs priority. The manifest and selected IDs are saved for each research attempt. A new version never silently changes an existing run.

Evaluation dates must start strictly after trained_through, the latest source-run end. Overlapping dates require explicit DEVELOPMENT_REPLAY; such results are not unseen-period evidence. LATER_PERIOD_EVALUATION describes chronological separation only. It does not prove the dates were untouched during all earlier development.

Observed memory at document preparation: the three process lessons were accepted and a three-lesson version was frozen with trained_through 29 December 2023. Another one-lesson version also exists. Select by lesson count, creation metadata and hash, not merely the first UUID. Draft/review/freeze/retrieval adds no generation calls. This is retrieval memory, not fine-tuning model weights.

## 11. Sizing, exits and accounting

Quantity is the whole-share minimum of the risk limit, 20% equity exposure limit and fee-aware cash limit. Planned stop risk uses equity × risk percentage divided by entry-minus-stop distance. A 1% setting is planned stop-distance risk, not a 1% guaranteed maximum realized loss and not the fraction of capital invested. Costs and gaps can change realized loss.

| Exit mechanism | Trigger and execution |
|---|---|
| Initial stop | Code stop from entry signal close minus 2 × ATR14; gaps through stop fill at modeled opening reference |
| Trailing stop | max(previous stop, highest completed close since entry minus configured multiple × entry-signal ATR); raises apply next session |
| Take profit | Configured net holding return; default UI value 8%; fees/slippage included in target reference calculation |
| EMA_TREND exit | EMA20 falls below EMA50 at a completed close; queues later-open sale |
| RSI_REVERSION exit | RSI rises above 58; queues later-open sale |
| BREAKOUT exit | Close falls below EMA20; queues later-open sale |
| C2 EXIT | Accepted cited holding-review EXIT; queues later-open sale with provenance validation |
| End of requested period | Mark holdings; no forced sale |

The trailing distance uses ATR frozen at the entry signal, not a fresh widening ATR every day. It never lowers the stop. A raised stop cannot be applied retroactively to the same day's earlier low. When both stop and target are touched inside a daily bar without an earlier opening event, the conservative stop takes priority. Opening events are considered before intraday touches.

The target percentage applies to a holding's modeled net return, not the entire portfolio. A stop may also realize profit after trailing upward. HOLD changes no share quantity; it means keeping the current holding subject to the existing code rules. Repeated HOLD reviews do not imply repeated purchases.

Equity = cash + marked value of holdings. Total P&L = realized + unrealized P&L, with modeled trading fees included. Model usage/cost is reported separately, not deducted from INR trading equity. Unsold holdings contribute unrealized P&L and remain exposed. Unknown model USD cost must not be reported as free inference.

The technical reference uses the same bars, starting cash, trading-cost assumptions and code entry/exit settings without the C2 filters/reviews. C2 can differ through blocks, timing, exits and invested exposure. The passive equal-weight benchmark uses different allocation/risk characteristics and is context, not an identical-risk counterfactual.

## 12. Separate supervised-order orchestration

[[FIGURE:current_supervised]]

A selected completed, passing C2 experiment supplies linked research provenance to Supervised Trading. The order graph validates the historical bar and signal, creates a typed code-sized proposal, checks code risk/compliance, then interrupts for human review. The internal nodes called market/strategy/risk/critic in this order graph are validation/proposal workflow functions; they are not an additional six-call research cycle. The required research already completed before proposal.

The human can approve the exact payload, reject it or edit permitted fields. An edit invalidates the previous hash, passes validation again and needs another approval. Final submission rechecks research provenance, payload authorization, quote age/deviation, expiry, cash/risk and emergency controls. Quotes are explicit simulated snapshots, not a live brokerage market feed. Missing/stale quotes can correctly block submission.

The local simulated broker stores request IDs, approval/audit records and reconciliation. A timeout after commit triggers reconciliation by request ID rather than a blind duplicate submission. The reviewer token is a local demo access control, not production identity management. There are no live broker credentials or exchange-order permissions.

## 13. Front-end workspace map

| Workspace | What to show | Common misunderstanding |
|---|---|---|
| Market Data | Active source, universe, coverage, cached historical bars | Downloaded data is not adjusted or historically unbiased merely because it is real |
| Overview | Indicators, regime and route for a symbol/date | A technical candidate is not a completed C2 decision |
| Strategy Backtests | C2/technical engine, capital/dates/rules, progress, comparisons, ledgers, stops, research traces | Historical rule approval replaces per-fill pauses only in this path |
| AI Agent Experiments | C0/C1/C2 research comparison, historical evidence and genuine tool/LLM traces | A research-case experiment is not a portfolio replay |
| Supervised Trading | Research-linked proposal and exact human approval | Approval is after completed C2, not before research |
| Policy Knowledge | Retrieval query, passage IDs, sources and policy authority | Policy RAG is not an exhaustive historical news database |
| Learning & Lessons | Portfolio candidate review, freeze and versions; legacy experiment lessons below | Acceptance alone does not apply a lesson to all existing runs |
| Broker Audit | Simulated order/approval/reconciliation events | Historical portfolio fills have their own ledger and need not appear as supervised broker orders |

## 14. Persistence and interfaces

| Location | Retained evidence |
|---|---|
| data/market_config.json | Active data source and dataset directory |
| data/nse_nifty20/manifest.json | Dataset bounds, universe, raw-price caveats, coverage and hashes |
| data/company_research/packs and snapshots | Current dated company packs and immutable source versions |
| data/c2_portfolio_runs/<run_id>/state.json | Settings, phase, cash, holdings, curves, decisions, usage and version fingerprints |
| data/c2_portfolio_runs/<run_id>/research/<case_id>.json | Specialist hand-offs, full tool observations, company assessment, failure and memory IDs |
| data/portfolio_lessons.sqlite | Portfolio candidates, reviews and immutable versions |
| data/reviewed_lessons.sqlite | Separate legacy research-experiment lessons |
| data/rag | Embedding/vector cache and index verification metadata |
| Other data/*.sqlite | Order graph checkpoints, run context and simulated broker audit |

Key API groups: /health and /market/*; /research/experiments/*; /company/research/*; /simulation/c2/run, /recent, /status/{id}, /research/{run}/{case}, /resume/{id}, /pause/{id}; /portfolio-lessons and its /draft, /review, /freeze writes; /workflow/start and /resume; /audit/events. Interactive API documentation at /docs is the authoritative endpoint schema.

Paid-run gates means local permission/readiness checks before inference. It does not mean FastAPI charges a fee. CLI runs still require explicit external-inference consent because they consume plan allowance.

## 15. Current verification and real saved example

The latest code verification recorded 185 passing tests, including mocked specialist-object response parsing, schema definitions, malformed JSON stage diagnostics, source materiality/context packing, memory temporal binding, no extra lesson generation, execution/accounting and UI review/freeze/select behavior. Mocked transport tests establish controlled contracts; they are not profit tests.

A real saved run created on 11 November 2026 used 1–31 March 2024, ₹300,000, risk 1%, fees 5 bps, slippage 10 bps, target 6%, ATR trailing 2×, five-session holding reviews and no portfolio lessons. Its actual last observed session was 28 March. It completed with gaps and used 101 typed-specialist CLI invocations after allowance increases to 144.

The saved ending equity is ₹301,578.23 (approximately +0.526%). The technical reference ended at ₹299,480.43 (approximately −0.173%). Four BUYs, one take-profit exit, one stop exit and two remaining holdings are present. The decision log contains 32 BLOCKED cases, four ENTERs, one HOLD and deferred/cancelled candidates. This is a usable source-backed workflow example, including successful typed CLI responses after the adapter correction. It is one selected historical example with gaps, not evidence of robust profitability, universal superiority or a memory benefit. Its 6% target differs from the current UI default of 8%.

Saved example run ID: da8d6838ad194143bd374086a890b364. These figures are copied from its retained state, not generated as a forecast. Other jobs can run while you read this document; statuses are a preparation-time snapshot. Do not clear ledgers or restart active work for presentation convenience.

## 16. Capstone evidence and remaining limits

The previously prepared guideline cross-check identifies the relevant coverage areas: multi-agent/tool orchestration; neural hybrid retrieval/reranking; contextual and reviewed long-term memory; human approval; safety/injection defenses; evaluation/judge calibration; monitoring/deployment; and the two signature challenges. Professor approval of three members is accepted.

The original guideline PDF was not available at its supplied external path during this fresh build. This document uses the repository's retained cross-check rather than claiming a new page-by-page audit of that PDF. Exact assessment thresholds should be confirmed against the current official rubric.

| Area | Implemented / evidenced | Still needed for stronger capstone claims |
|---|---|---|
| Orchestration | Three specialist research roles, real MCP, bounded calls and hand-offs | Broader real-model quality/robustness evaluation |
| RAG | BM25 + neural embeddings + RRF + cross-encoder + local Chroma | Independent relevance/faithfulness review and retained held-out results |
| Memory | Human-reviewed versioned portfolio retrieval and chronology guards | Controlled memory-off/on benefit and regression measurement |
| Safety | Allowlisted tools, injection checks, typed validation, code risk and approval audit | Independent model-level attack evaluation beyond scanner proxies |
| Evaluation | C0/C1/C2 and experiment harnesses, technical/passive comparisons | Independently reviewed gold/held-out tasks, repeated model runs, different-family judge/human calibration and complete cost/error accounting |
| Operations | Local API/UI, checkpoints, telemetry/configuration artifacts | Verify deployment/alerts/CI in the actual presentation environment |
| Financial interpretation | Costs, causal fills, protective exits, marked holdings | Corporate-action adjustments, historical membership, stronger news coverage, calendar validation and untouched multi-period testing |

Do not equate a single profitable replay, a passing test suite, or accepted lessons with proven investment performance. Explain what was measured and what remains a research question.

## 17. Team explanation and reading order

All three members should explain the full sequence and both execution paths. A useful responsibility split is data/quant/evaluation; RAG/agents/memory; and risk/UI/audit/platform, with cross-review of safety and lessons. It is a proposed work split rather than a claim about completed individual contributions.

Read this document first, rehearse the separate UI Demo and Test Guide next, and use the new viva bank to practise concise answers supported by actual screens and saved artifacts.
