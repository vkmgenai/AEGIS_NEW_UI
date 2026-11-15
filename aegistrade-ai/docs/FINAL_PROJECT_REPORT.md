# AegisTrade AI — final capstone project report

Version 0.30 · 14 November 2026 · Team size: three, approved by faculty

## Executive summary

AegisTrade is a simulation-only equity-research and historical portfolio prototype for an analyst/reviewer. It combines point-in-time technical screening, dated company evidence, hybrid RAG, MCP tools, a single-agent baseline, a three-specialist LangGraph workflow, deterministic risk controls, reviewed memory, human approval and operational monitoring. It never connects to a live broker and does not claim profitable investment advice.

The primary research question is not “can an LLM predict price?” It is: **does a grounded specialist team improve the quality, auditability and safety of regime-aware research decisions enough to justify its additional inference cost relative to deterministic and single-agent baselines?** Portfolio return is a secondary system outcome, not the sole agent-quality metric.

## Problem, users and scope

The target user is an equity-research analyst or capstone reviewer exploring historical NSE scenarios. Technical systems can generate many signals but usually provide weak dated justification; unconstrained LLMs can hallucinate evidence, calculate money incorrectly or leak future information. AegisTrade separates responsibilities: code detects signals and controls money, agents research and explain, a critic challenges claims, and a person governs any supervised simulated action.

The prototype supports frozen Nifty20, Nifty100 and diversified research30 universes. Current constituent snapshots applied backward introduce survivorship bias, and raw/unadjusted OHLCV does not fully reconstruct corporate actions or dividends. Consequently, returns demonstrate engineering behaviour, not a deployable investment edge.

## Final system design

The detailed diagram and numbered walkthrough are in [FINAL_ARCHITECTURE.md](FINAL_ARCHITECTURE.md). The numbered markers in Figure 1 match the walkthrough below.

[[FIGURE:final_architecture]]

*Figure 1: AegisTrade AI detailed design. Numbers match the execution walkthrough.*

- **C0 portfolio baseline:** zero-generation deterministic ROUTER using EMA Trend, EMA Pullback, RSI Reversion and Breakout.
- **C1 evaluation baseline:** one ReAct agent with the same model, read tools and eight-call ceiling as C2. It remains in AI Agent Experiments because the guideline explicitly requires it; it is not offered as a new portfolio flow.
- **C2 agentic system:** supervisor plus market, strategy and compliance-critic specialists. C2 adds an SMC route, dated RAG/web evidence, typed hand-offs, correction/replan, holding reviews and adverse-event exits. At each close it can research a bounded default pool of three top technical candidates; if the first is evidence-blocked, the next candidate can be considered. It selects the highest-ranked evidence-qualified candidate rather than treating missing evidence as strength.
- **Control:** Python owns arithmetic, eligibility, costs and execution. Supervised actions require an exact-payload approval hash; historical replay uses upfront-approved rules. There is no live exchange API.

### Figure 1 execution walkthrough

1. The reviewer chooses a frozen universe, C0 or C2, historical window, capital and (for C2) one of three inference adapters in Streamlit. The dashboard fixes the risk/execution policy so that C0/C2 comparisons cannot be post-hoc tuned. FastAPI authenticates the reviewer, records paid-call consent and locks the point-in-time case.
2. The experiment harness sends an identical locked case to C0, C1 and C2 when performing the architecture evaluation. C0 is deterministic; C1 uses one tool-using agent; C2 creates a bounded supervisor plan for three specialists.
3. The C2 market specialist reads the historical snapshot and dated company evidence. A bounded dated-web fallback may supplement a genuinely incomplete historical pack, but it cannot introduce evidence published after the decision cutoff.
4. The strategy specialist reads policy RAG and the code-approved route. It returns a typed strategy, cited explanation and permitted portfolio action; it cannot change the strategy catalogue or calculate an order quantity.
5. The independent critic obtains its own scoped observations and accepts or rejects the proposed interpretation. Schema or evidence contradictions can trigger a bounded correction; rejection cannot authorize execution.
6. FastMCP tools provide market, company, policy, route and reviewed-memory observations. Pre/post-tool hooks enforce permissions and budgets, scan untrusted content, scrub secrets and append the trace.
7. Deterministic validation checks schemas, dates, citations, route agreement and adverse evidence. Python then owns quantity, fixed delivery fees, slippage, stops, targets, capacity and all cash/ledger arithmetic.
8. Historical replay proceeds only under upfront-approved rules and fills at the eligible later open. A separately supervised action pauses for approve, edit or reject on the exact payload hash, then repeats freshness and risk checks before simulated submission. No live broker exists.
9. JSON/SQLite records preserve traces, checkpoints, decisions and ledger events. Human-reviewed lessons may be frozen for later development runs; the E1–E4 harness, monitoring dashboards and CI measure quality, safety, latency and cost.

### Final demonstration UI

The portfolio form deliberately exposes only the decisions needed for the capstone demonstration: C0 or C2, starting capital, start/end dates, inference allowance, reviewed-memory version, consent and replay-rule approval. The risk policy is displayed but not editable: ROUTER, 1% normal risk, 0.5% breakout risk, ATR stops/trails, 8% net target, 10 bps slippage, three C2 research candidates and five-session holding reviews. This reduces accidental configuration drift while every value remains recorded in the saved result. The inference selector retains all three adapters: **ChatGPT/Codex CLI**, **OpenRouter API**, and **Claude CLI**. C1 remains only in the controlled C0/C1/C2 agent experiment required by the evaluation protocol.

The single-stock C0/C2 comparison is grouped with Strategy Backtests. Its optional `HUMAN_EVIDENCE_OVERRIDE` study pauses evidence-insufficient C2 blocks attached to an otherwise valid technical BUY or holding SELL. Hard adverse, provider, schema, policy, route, capital and risk failures are never overrideable. `KEEP_BLOCKED` or `APPROVE_OVERRIDE` is recorded separately without rewriting C2. Approved BUYs create linked simulated positions. A later discretionary C2 EXIT on that position pauses for `KEEP_HOLDING` or `APPROVE_EXIT`, and an evidence-blocked SELL can also pause; stops, trailing stops and targets remain automatic. Realized or marked-to-market outcomes can be reviewed as conditional lesson candidates but are never learned automatically. The standard C0/C1/C2 agent experiment remains a research ablation rather than a duplicate trading approval screen.

The lifecycle distinguishes an approval from an evaluated outcome. A linked open position is `INCONCLUSIVE_OPEN`; after exit, positive realized P&L is labelled `SUPPORTED` and non-positive realized P&L `NOT_SUPPORTED`. These are auditable evaluation labels, not investment claims. Only a closed lifecycle is eligible for a subsequent human lesson review, and governed memory still requires a separate accept-and-freeze step. The local reviewer token authorizes the write to the decision ledger and is never part of the model prompt.

The UI exposes pending checkpoints through a read-only notification inbox. Every 15 seconds, the local dashboard queries only runs in `PAUSED_HUMAN_OVERRIDE`; a bell count and one-time toast identify new items. Selecting an item loads its immutable run checkpoint in Strategy Backtests, where evidence and rationale are reviewed. The bell cannot approve a decision and creates no inference call. Alerts disappear only when the persisted run is no longer awaiting human intervention. This is deliberately an in-app mechanism rather than an external email or browser-push dependency.

To reduce UI clutter, Strategy Backtests uses a two-tile landing page. The portfolio tile opens the universe-wide C0/C2 replay and governed intervention workflow; the single-stock tile opens the same-stock C0/C2 comparison. Both call the existing engines rather than implementing parallel logic. A back control returns to the landing page while retaining session and persisted-run state. Notification deep-links select the portfolio tile automatically.

C2 does not require a frontier reasoning model for routine typed extraction and policy checking. The balanced response budget is 3,600 tokens per case, with specialist turns targeted near 450 tokens and a reserve for a bounded correction. A smaller instruction-following model is appropriate only after it passes the schema, citation, breakout-evidence and adverse-event evaluations; held-out quality and failure rate govern model choice, not price alone.

## Minimum-bar assessment

| Area | Implemented evidence | Final-review status |
|---|---|---|
| Retrieval | Source/date metadata; BM25 + vectors + RRF; reranker; query rewriting; passage IDs | Partial: development Recall@5 exists, but labels need independent review and a frozen before/after rerun |
| Tools/MCP | Six FastMCP servers, typed schemas, structured errors, scoped read/write access and tests | Implemented; export final inventory and test evidence |
| Orchestration | Typed LangGraph specialist graph, bounded correction loop, durable portfolio checkpoints/resume | Partial: retain a live resume recording and do not overclaim a LangGraph-native checkpointer where file/SQLite checkpoints are used |
| Memory | Short-term workflow state; reviewed SQLite lessons; applicability, accept/reject/freeze and policy | Partial: run final memory-off/on held-out E3 |
| Planning | Visible plan object, ReAct tool use, correction/replan events | Partial: retain one successful contradiction/replan trace |
| Multi-agent | C2 supervisor + three specialists; C1 same-tool/budget baseline | Partial: final funded three-repeat E1 is still required |
| Improvement | Development reflection, conditional lessons, human review, rejected lessons and frozen versions | Partial: held-out before/after result and lesson-generation cost required |
| Evaluation/monitoring | 20 development + 40 held-out candidate cases; traces; Prometheus/Grafana | Partial: independent labels, calibrated judge and final dashboard evidence required |
| Human control/hooks | Grounded C2 BUY/SELL approve/reject with rationale; internal research binding; permission/budget/logging hooks | Partial: retain independently reviewed approve and reject demonstrations |
| Security | Threat model, scoped tools, guardrails and 32 attacks | Partial: run model-level defence-off/on plus ten clean cases and report false blocks |
| Deployment | FastAPI, Streamlit, Docker Compose, CI, Prometheus, Grafana and alert rules | Partial: clean-machine proof, fired alert and hosted failed-CI record required |

Therefore the implementation is substantial, but the **minimum bar is not yet fully evidenced for final review**. Independent human labels and reviewed held-out experiments are major gaps, but not the only gaps. The final evidence package also needs three repetitions, different-family judge calibration, E2/E3/E4 ablations, actual contribution entries, slides/video, hosted failed-CI proof and a fired-alert demonstration. These items must be linked to retained artifacts rather than replaced with generated claims. Role-specific forms are provided in [TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md](TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md), and background evaluation runs can be retained under `reports/capstone_runs/` using `evaluation/experiment_ledger.py`.

## Evaluation protocol: answers and justification

### Golden set

The repository contains 60 candidate cases: 20 development and 40 held-out, grouped by scenario family. Expected outcomes are marked as seeded hypotheses requiring independent human verification. Before the final run, a team member who did not tune the relevant component must review the labels. Held-out files must not enter prompts, retrieval or tools. Any case already used to change the system must be moved to development and disclosed.

### Code first, judge second

Code checks route outcomes, database/ledger state, quantities, citation existence, required tool calls, forbidden actions, exact approval hashes and policy violations. A different-family judge is used only for semantic support and explanation quality. `evaluation/judge_calibration.json` contains 20+ items but its human labels are intentionally blank. The team must label them independently, run `evaluation/judge_agreement.py` and report Cohen’s kappa before trusting judge scores.

### E1 — does the agent justify its cost?

Run C0, C1 and C2 on identical locked cases. C0 has no agent decisions; C1 and C2 use the same inference model, available read tools, output limits and eight-call ceiling. Report task success, grounded claims, policy violations, tool-trajectory correctness, usage/cost, median/p95 latency, errors and timeouts. Portfolio C0/C2 P&L is secondary because C2 additionally has SMC and holding research; it is not the pure architecture ablation.

The dashboard presents E1 as a capability-oriented comparison, not a single quality score. C0 is the routing reference by construction, so agreement with it is not an achievement for C0 and research-only columns are marked N/A. For C1 and C2 the table reports, per architecture:

| Column | Meaning |
|---|---|
| Route validation | Decided cases whose route and citations passed the code guard. Cases that ended in a safe evidence abstention are counted separately, not as failed validations. |
| Grounded company evidence | Cases whose company assessment cites at least one dated source. |
| Adverse-risk flags | Cases where the assessment reports a cited adverse event. |
| Decision coverage | Cases that reached an ENTER, EXIT or HOLD decision. |
| Safe evidence abstentions | Cases blocked for an evidence reason, such as a cited adverse finding that needs review. This lowers coverage but is the intended behaviour. |
| Hard model/policy failures | Cases with a model or policy error that is not an evidence abstention, such as a strategy that conflicts with the code route. |

In the retained three-case run (BHARTIARTL, LT, TCS), C2 shows 3/3 grounded, one adverse-risk flag and one safe abstention on BHARTIARTL, and no hard failure; C1 shows 2/3 grounded and one hard failure, a route conflict on BHARTIARTL. This is three cases and is evidence about behaviour, not about profitability. The raw task-success, policy-violation, model-error, call and latency figures remain available in the collapsed "Technical audit metrics" section, so no unfavourable figure is hidden.

### E2 — do the defences work?

Run 32 attacks with defences off/on and ten clean cases with defences off/on. Hard execution controls remain enabled in both conditions; the ablation concerns model-facing injection/output defences. Report attack success and legitimate false-block rate. The existing regex scanner result is only a development proxy, not the final E2 result.

### E3 — did lessons help?

Freeze reviewed lessons produced only from development failures. Run untouched held-out cases with memory off and with the frozen playbook on. Include reflection/judge inference used to create lessons, retrieve only applicable lessons, show one rejected lesson and its rationale, and identify any accepted lesson that worsened a result.

### E4 — signature ablation

For this finance project, use the Analyst Desk analogue: compare the compliance critic loop on/off and structured/table-aware dated evidence with the simpler retrieval representation. Hold cases, model, tools and budgets fixed. Report citation/claim support, numeric/source validation, task success, usage and latency. Portfolio returns may be reported separately but cannot replace research-quality measures.

### Repeats and reporting

Repeat the final held-out comparison three times. Preserve failures and timeouts. For every configuration report task-success counts, policy violations, attack success, false blocks, inference usage/cost, median and p95 latency and errors, plus the spread across repeats. Never select parameters from held-out performance.

## Current measured development evidence

- Full local test suite: **361 passed** on 14 November 2026 after the final UI consolidation, including the three-adapter provider contract, C0/C2 UI payload checks and authenticated human C2 review audit.
- Golden development checker: 20/20 seeded development cases in `reports/capstone_review_dev.json`; the report itself states that labels require independent review.
- Fresh v0.27 offline development evidence is saved in `reports/final_dev_offline_v027.json` and `reports/final_rag_offline_v027.json`. On the current expanded corpus, the 36 legacy queries improved from 0.6944 to 0.7500 Recall@5 with rewriting; the 101 authored development queries scored 0.9010. The original 16-passage/36-query setup scored 0.9444, so corpus expansion regressed the old labels even though rewriting improved the current configuration. These labels are not independently reviewed and this is not a held-out claim.
- The deterministic scanner detected 93.8% of 32 authored attack strings with zero false blocks on ten clean strings. This is a scanner proxy only; model-level E2 remains required.
- A synthetic E4 technical report exists, but it is not a final C2 agent evaluation and must not be presented as profitable real-market evidence.
- Judge human labels are not complete; no valid final Cohen’s kappa is claimed.

## Security, privacy and human control

The threat model covers prompt injection through evidence, hallucinated quantities, approval tampering, retries/duplicates, stale prices, credential leakage, excessive tools, denial-of-service loops and held-out leakage. Secrets remain in ignored environment files and are scrubbed from traces. LLM specialists receive no broker-write tool. The demo bearer token is not production authentication; internet deployment would require accounts, MFA/RBAC, encryption, retention automation and independent testing.

## Deployment and operation

`bash scripts/start_unix.sh` or the Windows script creates the environment and launches FastAPI and Streamlit. Docker Compose additionally starts MCP services, Prometheus and Grafana. Prompt/model IDs are versioned, and saved portfolio runs pin data, corpus, prompt, backend and engine versions. A mismatch requires a fresh run rather than silently changing an old experiment.

## Limitations and conclusion

AegisTrade does not establish profitable advice. Survivorship bias, unadjusted prices, incomplete historical evidence, model variation and limited independent labels prevent that claim. Its defensible contribution is an auditable architecture that separates model interpretation from deterministic financial controls, compares single-agent and multi-agent research under bounded resources, and preserves failures instead of hiding them. Final grading readiness depends on completing the independent and held-out evidence listed in the completion checklist.

