---
title: "AegisTrade AI: Current Design and Learning Guide"
subtitle: "Version 0.35 · Simulation Only · Updated 18 November 2026"
author: "AegisTrade AI Capstone Team"
date: "18 November 2026"
---

# 1. What the project does

AegisTrade AI is a simulation-only research platform for testing whether a
multi-agent evidence-review system improves the quality, grounding and safety of
historical trading decisions compared with a single agent using the same tools,
model, evidence and call budget.

The project replays historical NSE daily OHLCV data. Python detects technical
signals and applies deterministic risk, sizing, fee, stop, target and fill
rules. Language-model agents are used only where unstructured evidence must be
interpreted: dated company filings, issuer announcements, reviewed web evidence
and written project policy. No component connects to a live broker.

The four principles are:

1. **Code finds and constrains the signal.** Indicators, routes and strategy
   eligibility are deterministic.
2. **Agents interpret evidence.** They retrieve dated sources, explain the
   decision and cite what they observed.
3. **Code controls money.** Quantity, exposure, stops, fees and fills are never
   delegated to a model.
4. **Everything is retained.** Runs, calls, hand-offs, failures, human decisions
   and simulated fills remain auditable.

The project tests research correctness and architecture quality. It does not
claim that an LLM discovers a profitable strategy or provides investment advice.

# 2. Current end-to-end design

The numbered architecture below replaces the v0.28 diagram.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. HUMAN + STREAMLIT UI (127.0.0.1:8501)                                │
│ Original project UI · workspace selector · notification bell             │
│ Market Data · Overview · Strategy Backtests · AI Agent Experiments        │
│ Capstone Evaluation · Policy Knowledge · Learning & Lessons               │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ HTTP + reviewer authorization/consent
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 2. FASTAPI SERVICE (127.0.0.1:8000, API v0.35.0)                         │
│ Typed request validation · paid-call consent · background jobs            │
│ progress/status · call budgets · pause/resume · retained results           │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ locked point-in-time case
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 3. DATA + TECHNICAL SCREENING                                             │
│ Daily NSE OHLCV · named universes · EMA/RSI/ADX/ATR · breakout/SMC         │
│ automatic ranking · evidence cutoff · cached issuer filings/news           │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ identical case/evidence/tool contract
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 4. ARCHITECTURE EXPERIMENT                                                │
│ C0: deterministic reference, 0 LLM calls                                  │
│ C1: one agent with the complete shared read-tool set                       │
│ C2: supervisor → market → strategy → independent critic                    │
│ Primary capstone comparison: C1 single agent versus C2 multi-agent         │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ typed tool calls and typed hand-offs
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 5. RAG + MCP + INFERENCE                                                  │
│ 87-passage policy corpus · hybrid retrieval/reranking · passage IDs        │
│ market snapshot · company evidence · policy search · strategy check        │
│ Claude CLI · ChatGPT/Codex CLI · OpenRouter adapter                        │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ output must pass deterministic gates
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 6. CONTROL + PORTFOLIO SIMULATION                                         │
│ citation/date/quote validation · critic acceptance · route enforcement     │
│ position sizing · stops/targets/trailing stops · fees · later-open fills   │
│ optional HUMAN_EVIDENCE_OVERRIDE for eligible evidence-blocked cases       │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ immutable audit and evaluation records
┌───────────────────────────────▼──────────────────────────────────────────┐
│ 7. PROOF + LEARNING                                                       │
│ decision/trade/tool ledgers · human-override lifecycle and attributed P&L  │
│ reviewed lessons · E1/E2/E3/E4 · Recall@5 · security · 377 tests           │
└──────────────────────────────────────────────────────────────────────────┘
```

## Walkthrough

1. A reviewer selects a workspace in the Streamlit UI. The official interface
   remains the original design on port 8501; the rejected blue preview is not
   part of the submitted design.
2. The UI calls FastAPI. State-changing or inference-spending operations require
   configured reviewer authorization and explicit consent.
3. Code builds a locked historical case using only completed daily bars and
   evidence available at the case cutoff.
4. In AI Agent Experiments, exactly the same case is sent to C1 and C2. They use
   the same model, dated evidence, available read tools, output-token guidance
   and eight-call ceiling. C0 is included only as a deterministic reference.
5. Agents obtain facts through typed tools. Provider CLIs have no autonomous
   shell, browser or broker tools from the project workflow.
6. Python checks output schemas, citations, source quotes, dates, route and
   critic verdict before a decision can affect the simulator.
7. A C2 portfolio job uses the accepted decision in the deterministic portfolio
   engine, checkpoints progress and records every result.

# 3. C0, C1 and C2: the corrected comparison

| Flow | Architecture | Tools and budget | Where used | Meaning |
|---|---|---|---|---|
| C0 | Deterministic router and code rules | No LLM calls | AI experiment reference; technical code/tests | Secondary no-AI reference, not the single-agent baseline |
| C1 | One LLM agent performs the whole research task | Same read-tool union and eight-call ceiling as C2 | AI Agent Experiments only | Guideline-required single-agent baseline |
| C2 | Supervisor plus market, strategy and independent critic specialists | Same model, case, evidence, read tools and ceiling as C1 | AI Agent Experiments and C2 historical portfolio | Multi-agent system under evaluation |

The primary evaluation is **C1 versus C2**. This answers the capstone question:
does decomposition into a supervisor and at least three specialists improve task
success, grounding, failure handling or safety enough to justify its additional
latency and cost?

C0 remains useful because it shows what the deterministic route would do with
zero generation. C0 success must not be plotted as if it were directly
comparable model quality: it is code agreement, not agent research quality.

# 4. How a C2 research decision works

```text
Code-qualified case
       │
       ▼
Supervisor creates a typed plan
       │
       ▼
Market specialist reads market_snapshot + company_evidence
       │       └─ optional dated web search only when bounded evidence is missing
       ▼
Strategy specialist searches policy and selects the code-permitted route
       │
       ▼
Independent critic rechecks evidence and policy through its own tools
       │
       ▼
Python validates schema, route, passage IDs, dates and source quotes
       ├─ fail → BLOCKED with structured reason
       └─ pass → eligible deterministic portfolio action
```

### Role boundaries

- **Supervisor:** controls the typed work sequence and shared state.
- **Market specialist:** reports the code regime and company evidence. Missing
  coverage is not silently treated as good news. Strong trend, confirmed
  pullback and RSI-reversion signals are not rejected solely for missing
  coverage when no concrete adverse event is identified.
- **Strategy specialist:** selects only the route permitted by code and cites
  project-policy passages.
- **Critic:** independently re-observes sources and accepts or rejects the
  interpretation. It is the architectural feature absent from C1.
- **Python gates:** make the final research-validity decision. Fluent prose
  cannot bypass a missing citation, invalid date, wrong route or fabricated
  quote.

Breakout is deliberately stricter. It requires recent readable corroboration,
an exact source quote and independent critic support. Structural corporate
actions such as splits or demergers quarantine entries in the unadjusted-price
simulator rather than being treated as catalysts.

# 5. The C2 portfolio workflow

The Strategy Backtests workspace now focuses on the end-to-end C2 historical
portfolio. The controlled C0/C1/C2 architecture comparison belongs in AI Agent
Experiments.

```text
Named universe and date range
  → deterministic screening of up to three candidates per session
  → dated company and policy evidence
  → C2 supervisor/specialists/critic
  → deterministic evidence gates
  → code-sized whole-share order
  → later eligible market open
  → stops, targets, fees, holding reviews and adverse-news checks
  → marked-to-market ending portfolio and complete ledger
```

The simplified demonstration UI fixes the submitted simulation policy to avoid
post-hoc tuning:

- normal risk budget: 1% per trade;
- breakout risk budget: 0.5%;
- normal protective stop: 2 × ATR14;
- breakout stop: 2.5 × ATR14;
- normal trailing distance: 2 × ATR14;
- breakout trail: 2.5 × ATR14 after 1R;
- net take-profit target: 8%;
- slippage: 10 basis points per transaction plus modelled delivery charges;
- maximum screening pool: three candidates per session;
- holding review: every five sessions; and
- one confirmed stopped-setup recovery within ten sessions.

All holdings are marked to market at the end of the requested period. They are
not forcibly sold merely to finish the report.

# 6. Human-in-the-loop: HUMAN_EVIDENCE_OVERRIDE

Human intervention is not a blanket approval on every C2 BUY or SELL. It is an
optional controlled study inside the C2 portfolio workflow.

An interrupt is created only when:

1. code has a technically positive BUY or SELL situation;
2. C2 blocks it because evidence is insufficient or unresolved;
3. the block is eligible for human evidence override; and
4. the block is not a hard risk, safety, freshness, provider or schema failure.

The UI notification bell at the upper-right reports pending overrides. The
review panel displays the proposed action, current price and, for a SELL,
original entry price. A reviewer records APPROVE or REJECT, name and rationale.

Approving a blocked BUY creates a linked position marked
`HUMAN_EVIDENCE_OVERRIDE`. Its later exit remains attributable to the same
position. If a later evidence-blocked SELL needs a decision, the reviewer can
approve the exit or keep holding. Protective stops, take-profit targets and hard
safety exits never wait for human approval and cannot be overridden.

The dedicated ledger records request, decision, position opening, linked exit,
realised/unrealised P&L and final outcome. Only completed positions are eligible
for later good/bad lesson review. C2 P&L already includes override P&L; it must
not be added twice.

# 7. RAG and historical evidence

The current policy corpus contains **87 passages**: project policy plus bounded
external references. Each passage has an ID, authority, source and date
metadata. Retrieval combines lexical matching and neural similarity, fuses the
candidates and reranks them. Agents cite passage IDs; policy enforcement still
belongs to Python.

Historical company evidence is separate from the policy corpus. Point-in-time
packs contain NSE-disclosed filings and announcements with publication and
availability timestamps. A bounded dated-web search may supplement a missing
pack, but the result is persisted with its cutoff and source metadata.

### Current retrieval evaluation

The fresh development run on 101 authored queries measured:

| Metric | Before rewriting | After rewriting |
|---|---:|---:|
| Recall@5 | 0.9406 | 0.9604 |
| MRR@5 | 0.8667 | 0.8815 |
| nDCG@5 | 0.8852 | 0.9013 |

These are development results, not yet final independent evidence. A separate
36-query blinded packet assigns 12 relevance judgements each to Karthika,
Mathangi and Vineet. After review, accepted queries and the 87-passage corpus
will be frozen and the before/after Recall@5 calculation repeated.

# 8. Evaluation design and current status

The final evaluation protocol is versioned and review-first. Model outputs must
not be shown before expected labels are frozen.

| Experiment | Comparison | Required evidence |
|---|---|---|
| E1 | C1 single agent versus C2 multi-agent; C0 secondary reference | 20 reviewed development cases, then 40 untouched held-out cases × 3 repetitions |
| E2 | C2 text defences off versus on | 32 independently reviewed distinct attacks plus 10 clean controls |
| E3 | C2 reviewed memory off versus on | Frozen reviewed playbook and three held-out repetitions |
| E4 | Deterministic routing/critic/retrieval ablation | Reproducible no-paid-call engineering evidence |

The new packet under `evaluation/agentic_candidates_20261118_v2/` contains:

- 20 fresh development cases;
- 40 fresh held-out cases;
- 32 distinct security attacks; and
- 10 clean controls.

Its symbols are disjoint from the 17 November templates. The old 102 records
remain unchanged only as a historical audit trail; they do not need review and
will not enter the new final metrics.

Karthika can review the new 20 development cases in the standalone browser
editor `KARTHIKA_DEVELOPMENT_REVIEW_20.html`. It formats technical inputs and
dated evidence, autosaves progress and exports canonical JSONL.

Three small development repeats from 17 November remain engineering evidence,
not final held-out evidence. The fresh deterministic E4 ledger run is
`20261118T055107-c7102b3d`. The current regression suite has **377 passing
tests**. Negative results, model errors, timeouts and quarantined cases remain in
the final report.

# 9. Components and implementation files

| Layer | Main files | Responsibility |
|---|---|---|
| Streamlit UI | `app/ui.py`, `app/live_progress.py`, `app/portfolio_view.py` | Official 8501 dashboard, progress, notifications, ledgers and review controls |
| FastAPI | `app/api.py`, `app/security.py`, `app/backend_compat.py` | Typed API, authorization, consent, job lifecycle and UI/API compatibility |
| Market data | `aegistrade/market.py`, `nse_data.py`, `universes.py` | Cached OHLCV, source manifests and switchable universes |
| Indicators/routes | `strategies.py`, `smc.py`, `selection.py` | EMA/RSI/ADX/ATR, signal routes, SMC and automatic candidate ranking |
| Historical evidence | `company_research.py`, `evidence_library.py`, `dated_web.py` | Cutoff-safe company disclosures and bounded fallback evidence |
| RAG | `knowledge/corpus.jsonl`, `knowledge.py`, `corpus.py`, `vector_store.py` | 87 validated passages, hybrid retrieval, reranking and fingerprints |
| Agent graph | `agentic.py`, `agent_tools.py`, `config/agents.json` | C1 single agent, C2 roles, typed state/handoffs and prompt version v20 |
| MCP | `mcp_servers/`, `mcp_runtime.py` | Narrow typed read-tool boundary; broker action unavailable to agents |
| Providers | `llm_backend.py`, `llm_research.py` | Claude CLI, Codex CLI and OpenRouter adapters with fixed JSON transport |
| Evidence gates | `research_gate.py`, `c1_gate.py`, `breakout_evidence.py`, `signal_evidence.py` | Citations, dates, routes, quotes, source status and critic checks |
| Portfolio engine | `c2_portfolio.py`, `engine.py`, `execution_policy.py` | Checkpoints, C2 research loop, order sizing, fills, holdings and metrics |
| Costs/protection | `fees.py`, `trailing_stop.py`, `breakout_reentry.py`, `smc_reentry.py` | Delivery charges, stops, targets and controlled recovery entries |
| Human study | `c2_portfolio.py`, `app/ui.py` | Evidence-override interrupt, notification, lifecycle ledger and P&L attribution |
| Learning | `lessons.py`, `memory.py`, `reflection.py`, `portfolio_memory.py` | Human-reviewed conditional lessons and immutable versions |
| Evaluation | `evaluation/`, `reports/capstone_runs/` | E1–E4 harnesses, review validators, Recall@5 and retained manifests |
| Tests | `tests/` | Deterministic regression and safety checks; currently 377 passing |

# 10. Who decides what

| Decision | Owner | Why |
|---|---|---|
| Technical indicators, regime and permitted strategy route | Python | Exact, repeatable and testable |
| Candidate ranking | Python | Controls cost without hindsight selection |
| Interpretation of filings and policy | C1 or C2 model architecture | Suitable use of language models on unstructured text |
| Independent interpretation check | C2 critic, followed by Python | Separates reasoning review from deterministic validity |
| Quantity, exposure, fees, stops, targets and fills | Python | Models must not control arithmetic or money |
| Eligible evidence override | Human reviewer | Explicit accountability for departing from a C2 evidence block |
| Hard risk/safety decision | Python only | Never overridable by a model or reviewer workflow |
| Live exchange order | Nobody | No live broker integration exists |

# 11. How to demonstrate the project

1. Start the API and original Streamlit UI with `bash scripts/start_unix.sh`.
2. Open `http://127.0.0.1:8501` and confirm the sidebar says simulation only.
3. In **Market Data**, show the selected universe, source and coverage limits.
4. In **Overview**, inspect one stock's daily bars and current technical route.
5. In **Policy Knowledge**, retrieve a rule such as stop loss and show passage
   IDs and source metadata.
6. In **AI Agent Experiments**, run or open the same cases under C0, C1 and C2.
   Explain that C1 versus C2 is the primary fair architecture comparison.
7. Open a C2 trace and show supervisor, market, strategy, critic, tools,
   citations and deterministic validation.
8. In **Strategy Backtests**, open a retained C2 portfolio result. Show progress,
   decisions, fills, equity curve, benchmark, costs and failure categories.
9. If an eligible case is available, demonstrate the notification bell and
   `HUMAN_EVIDENCE_OVERRIDE` ledger. Do not claim that every run must interrupt.
10. In **Capstone Evaluation**, show retained E4/E1 artifacts and explain which
    fresh human reviews are still pending before final held-out claims.
11. Run `PYTHONPATH=. .venv/bin/pytest -q` and report the complete result rather
    than a selected subset.

# 12. Limitations that must remain in the report

- Simulation only; no live broker or guarantee of executable prices.
- Daily bars do not reproduce intraday order paths.
- Raw NSE prices are not fully corporate-action adjusted; affected cases are
  quarantined rather than treated as reliable returns.
- Current-member and curated universes create survivorship/selection bias.
- Historical filing and news coverage is uneven.
- Model outputs vary, and provider failures remain part of the measurements.
- C2 has not yet established a durable trading edge over deterministic or
  passive references. Its present value is auditable evidence review.
- Initial Recall@5 and small AI repeats are development evidence until the new
  independently reviewed datasets are frozen and rerun.
- Human evidence overrides are experiments in accountable judgement, not proof
  that overruling a block improves future performance.

# 13. Suggested code-reading order

1. `aegistrade/strategies.py` and `aegistrade/engine.py`
2. `aegistrade/safety.py` and `aegistrade/execution_policy.py`
3. `knowledge/corpus.jsonl`, `aegistrade/corpus.py` and `knowledge.py`
4. `aegistrade/company_research.py` and `dated_web.py`
5. `aegistrade/agent_tools.py` and `mcp_servers/`
6. `config/agents.json` and `aegistrade/agentic.py`
7. `aegistrade/llm_backend.py`
8. `aegistrade/research_gate.py` and `breakout_evidence.py`
9. `aegistrade/c2_portfolio.py`
10. `evaluation/run_capstone.py` and the review validators
11. `app/api.py` and `app/ui.py`

The most important viva statement is:

> C1 and C2 solve the same evidence-review task with the same case, model,
> read tools and call ceiling. C1 uses one agent; C2 uses a supervisor, market
> specialist, strategy specialist and independent critic. Python remains the
> authority for routes, validation, risk and simulated execution.
