# AegisTrade AI v0.35 — final architecture and walkthrough

This is the original AegisTrade detailed-design diagram for final review. Its numbered layered presentation follows the capstone guideline's diagram convention, while every component and connection describes this repository. The system is simulation-only.

![AegisTrade detailed design — numbered execution architecture](assets/design_final_architecture_v027.png)

*Figure 1: AegisTrade AI detailed design. Numbers match the walkthrough below.*

```mermaid
flowchart TB
  U[Researcher / reviewer] --> UI[Question-led Streamlit shell<br/>Data · C2 Portfolio · Agent Comparison · Evidence]
  UI --> API[FastAPI<br/>auth, consent, sessions, budgets, streaming/status]
  API --> IG[Input guardrails<br/>scope, typed schemas, injection scan, cutoff]

  subgraph DATA[Point-in-time data and retrieval]
    NSE[NSEPython OHLCV cache<br/>frozen Nifty20 / Nifty100 / research30]
    ING[Ingestion<br/>filings, issuer releases, reviewed excerpts]
    IDX[Hybrid index<br/>BM25 + vectors + RRF + reranker<br/>query rewriting]
    LIB[Dated evidence library<br/>source, publication, availability, hash]
    ING --> LIB
    LIB --> IDX
  end

  IG --> LOCK[Locked historical case<br/>symbol, close, regime, cutoff, purpose]
  NSE --> LOCK
  IDX --> KMCP[Knowledge MCP<br/>search/get passages]
  LIB --> MMCP[Market MCP<br/>snapshot + dated company evidence]

  subgraph C0[C0 — zero-generation baseline]
    R0[Four-route deterministic ROUTER<br/>EMA trend · EMA pullback<br/>RSI reversion · breakout]
  end

  subgraph E1[E1 primary architecture comparison]
    C1[C1 single ReAct agent<br/>same capabilities and total budget as C2]
  end

  subgraph C2[C2 — agentic research workflow]
    PLAN[Supervisor / plan object<br/>typed LangGraph state]
    MA[Market specialist<br/>regime + company evidence]
    SA[Strategy specialist<br/>five-route catalogue incl. SMC]
    CR[Independent compliance critic]
    FIX[Correction / replan loop<br/>bounded retries]
    PLAN --> MA --> SA --> CR
    CR -->|schema or evidence contradiction| FIX --> MA
  end

  LOCK --> R0
  LOCK --> C1
  LOCK --> PLAN
  C1 --> MMCP
  C1 --> KMCP
  MA --> MMCP
  SA --> KMCP
  CR --> KMCP
  SA --> SMCP[Strategy MCP<br/>approved route]
  CR --> SMCP
  PLAN --> RMCP[Records MCP<br/>accepted frozen lessons]

  subgraph CONTROL[Code and human control]
    HOOK[Pre/post tool hooks<br/>permission, budget, trace, scrub]
    TYPED[Typed hand-offs + deterministic validation<br/>citations, dates, route, adverse evidence]
    RISK[Python risk/execution engine<br/>whole shares, fees, slippage, stops, targets]
    GATE{WAITING_HUMAN gate<br/>approve · reject + rationale<br/>no repeated C2 call}
    FRESH[Final freshness / risk / kill-switch checks]
    MOCK[Local simulated broker / historical later-open fill]
  end

  MMCP --> HOOK
  KMCP --> HOOK
  SMCP --> HOOK
  RMCP --> HOOK
  CR --> TYPED
  C1 --> TYPED
  R0 --> RISK
  TYPED --> RISK
  RISK -->|eligible evidence-uncertainty block| GATE
  GATE -->|approve explicit override| FRESH --> MOCK
  RISK -->|upfront-approved historical replay| MOCK

  MOCK --> AUDIT[(SQLite / JSON audit<br/>trade ledger, decision ledger<br/>checkpoints, traces)]
  GATE --> OUT[Linked position/exit outcome<br/>review evidence, not causal proof]
  OUT --> AUDIT
  AUDIT --> MEM[Reviewed Reflexion lessons<br/>accept/reject/freeze/retrieve]
  MEM --> RMCP

  subgraph OPS[Evaluation and operation]
    GOLD[60-case golden set<br/>20 development + 40 held-out]
    EVAL[E1–E4 harness<br/>code checks + different-family judge]
    SEC[32-attack red-team suite]
    PROM[Prometheus + Grafana<br/>usage, latency, errors, outcomes]
    CI[GitHub Actions evaluation gate]
  end
  GOLD --> EVAL
  SEC --> EVAL
  AUDIT --> EVAL
  API --> PROM
  EVAL --> CI
```

## Numbered walkthrough

1. The reviewer runs the C2 portfolio in Strategy Backtests or selects C0/C1/C2 locked cases in AI Agent Experiments. C2 can use ChatGPT/Codex CLI, OpenRouter API or Claude CLI.
2. FastAPI validates authentication, explicit inference consent and a bounded allowance. Historical replay receives upfront approval of deterministic rules; supervised actions use exact-payload approval later.
3. Code creates a locked case from completed daily bars. No future price or post-cutoff evidence is available.
4. C0 routes the case through four deterministic strategies and makes zero model calls. The primary E1 comparison is C1 versus C2: identical locked cases, model, evidence, available tool capabilities, total response-token budget and eight-call ceiling; C1 uses one agent and C2 uses the specialist team.
5. C2 creates a plan and invokes market, strategy and critic specialists. Its catalogue adds SMC to the four C0 routes. Each specialist has scoped read tools.
6. Market/company tools return dated evidence. Hybrid policy retrieval combines BM25 and vectors with RRF, reranking and query rewriting. Every result retains source/date/passage IDs.
7. Typed hand-offs are validated. A contradiction causes a bounded correction/replan. Missing evidence is recorded honestly; it is never described as a positive fundamental finding. Breakouts require stricter corroboration.
8. Python—not the LLM—calculates ranking, quantity, fees, slippage, stops, profit targets and portfolio limits.
9. Only an eligible C2 evidence-uncertainty block attached to a technically valid BUY or holding SELL may enter `PAUSED_HUMAN_OVERRIDE`. Hard adverse, provider, schema, policy and risk failures are not overrideable. The reviewer keeps the block or explicitly overrides it with a rationale; no research call is repeated.
10. Human decisions are stored separately from model traces and trade ledgers and linked through position exit. Separately, AI Agent Experiments attach a fixed post-decision 20-session outcome on ₹100,000 notional for C1/C2 interpretation. Neither association is a causal or profitability claim.
11. Decisions, model/tool traces, checkpoints and ledger events are persisted. Interrupted portfolio jobs resume only when data, prompt, corpus, backend and engine versions still match.
12. Failed development cases and eligible reviewed outcomes can inform conditional Reflexion lesson candidates. Nothing is learned automatically: a human accepts or rejects each lesson and freezes a version before later-period evaluation.
13. The evaluation harness runs code-first checks, C0/C1/C2 comparisons, security trials, memory ablations and critic/retrieval ablations. The resumable report runner has completed three development E1 repetitions; final held-out E1/E2/E3 stays gated by independently reviewed labels. Prometheus/Grafana and CI expose operational evidence.

## Decision ownership

| Decision | Owner |
|---|---|
| Technical indicator, route eligibility, score and SMC pattern | Tested Python code |
| Evidence interpretation and explanation | LLM specialist |
| Cross-checking the proposed interpretation | Independent LLM critic plus code validation |
| Quantity, fees, risk, stop, target and fill mechanics | Tested Python code |
| Exact supervised simulated action | Human reviewer |
| Historical replay fills | Code under upfront-approved replay rules |
| Live exchange order | Not implemented |

