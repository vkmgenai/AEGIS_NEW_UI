# Capstone Implementation Roadmap (Phase 1 → Final)

## Phase 1 — Trading and safety foundation (this ZIP)
- Build reproducible daily OHLCV pipeline and data-quality gates.
- Test 3 signal strategies and frozen regime selection. Use next-open causality, fees, slippage and gaps.
- Implement stop/position calculations in tested code.
- Demonstrate FastMCP schemas, LangGraph type state with SQLite checkpoint and edit/reject/approve.
- No real trading or unconstrained autonomous trading agent.

## Phase 2 — Source quality and robust quantitative experiments
- Curate 8–12 liquid Indian cash equities plus one ETF, using frozen inclusion criteria; document point-in-time universe limitations.
- Use real, legally permitted, provenance-tracked adjusted and unadjusted price series; quantify missing bars and dividends/splits.
- Improve backtest with corporate actions, gaps, strategy-specific exits, worst-case intrabar assumptions and multiple trading cost scenarios.
- Freeze 70/30 chronological split or walk-forward folds; do not train/tune on held-out periods.
- Add buy-and-hold ETF and equal-weight benchmarks; report CAGR, max drawdown, Sharpe, trade counts and turnover.

## Phase 3 — GenAI depth and three real MCP services
- Add neural embedding vectors, rank-BM25, reciprocal-rank fusion, cross-encoder reranking and query rewriting; cite policy IDs, dates and origin.
- Build 30+ independently labelled retrieval query/target sets; report Recall@5 before/after a single change.
- Route specialist calls through actual FastMCP clients and per-agent least privilege; typed errors instead of tool crashes.
- LangGraph typed state, plans, conditional edges, persistent checkpointer, self-correction, explicit replan and real ReAct tool turns.
- Supervisor and ≥3 specialists; fixed C0 and equal-budget single agent C1 baselines.
- Long-term memory policy, consent/retention/deletion and memory-on/off experiment.

## Phase 4 — Control, threat model and supervised app
- Add authenticated reviewers and server-side scoped approvals; payload hash invalidation on any change.
- Strict broker-simulator status machine (requested, approved, queued, accepted, filled/partial, rejected, cancelled), protective exits, event audit.
- Fail-closed stale-data checks, quote-age checks, quote mismatch, unique idempotency IDs, rollback/reconcile failures.
- Build user UI + FastAPI streaming, async safe HTTP MCP servers, Docker Compose and Postgres/Qdrant as needed.
- Prometheus + Grafana telemetry for agent latency/cost/errors/blocked actions, plus at least one alert.
- Red-team ≥30 independently written attacks, including prompt injection via own retrieval corpus and poisoned tool metadata.

## Phase 5 — Evaluation and submission evidence
- Prewrite ≥60 independently verified gold scenarios: ~20 dev and ≥40 held-out, related variants in same split.
- Use deterministic assertions first; calibrate different-family LLM judge against ≥20 human labels and report Cohen's kappa.
- E1 compare C0 fixed, C1 single agent, C2 multiagent with equal tools/model/budget.
- E2 attacks with defence off/on + legitimate false-block rate.
- E3 develop lessons from dev-only failures; human review every lesson; freeze and repeat held-out before/after; show one rejected lesson.
- E4 compare regime router on/off, explanations and/or critic, while controlling market conditions and costs.
- Report correctness, policy violations, attack success, false blocks, latency (median/p95), LLM tokens and dollar cost per case including failures/timeouts.
- Repeat held-out comparisons 3 times; document changes after seeing held-out.
- Final docs: threat model, memory policy, architecture walkthrough, 4–6-page evaluation report, experiment/contribution logs, slides, backup demo recording.

## Suggested viva demo (all values synthetic unless independently verified)
1. Input asks about a symbol; show the supervisor plan and source evidence.
2. Show regime detection + three strategy candidates + rationale/citations.
3. Show code-based risk calculations; force one over-limit trade to be blocked.
4. `interrupt` pauses on the exact order; edit quantity and show prior hash invalidated.
5. Approve revised payload; show mock order's audit row and idempotent request ID.
6. Force a stale quote and show rejection; inject broker timeout after commit and reconcile without duplicate.
7. Compare fixed vs single-agent vs multiagent on independent cases; then compare approved lessons off/on and explain limits.
