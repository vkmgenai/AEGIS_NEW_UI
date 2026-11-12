# Approved three-member team: suggested implementation split

**Veneet — Quantitative Trading & Evaluation (lead)**
- OHLCV quality, corporate actions, universes, baseline strategies and costs.
- Walk-forward/out-of-sample backtests and strategy ablations.
- Independently authored 60-case reference labels, at least 30 retrieval queries,
  final metrics, security red-team input cases, experiment log and final slides.

**Karthika — AI Agents & Orchestration (lead)**
- LangGraph typed state, plan/replan, multi-specialist handoffs, checkpointer,
  tools/MCP client, RAG, query-side rewriting and optional neural retrieval.
- OpenRouter experiments C1/C2, per-run budgets, Reflexion candidate generation,
  approved lesson retrieval and prompt/version record.

**Mathangi — Risk, Execution & Platform (lead)**
- Deterministic money/risk rules, order payload hash, human approval gate,
  simulated broker idempotency, stale-data and failure recovery.
- FastAPI and Streamlit, security hooks, Docker Compose, Prometheus/Grafana,
  CI/CD, monitoring and demonstration environment.

**Independence**: Karthika must NOT author/rewrite final held-out labels. Mathangi
must NOT author the final red-team attack texts; Veneet does. Mathangi independently
reviews held-out policy correctness. Veneet reviews risk formulas, and all three
can redraw and defend the complete system in the viva.

**Shared conventions**: use Pydantic typed messages, one issue board, weekly
integration demos, code reviews, versioned configuration, per-member contribution log.
