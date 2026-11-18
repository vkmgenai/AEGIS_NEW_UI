# AegisTrade AI — final capstone project report

Version 0.35 · 17 November 2026 · Team size: three, approved by faculty

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

- **C0 deterministic reference:** zero-generation ROUTER using EMA Trend, EMA Pullback, RSI Reversion and Breakout. It is not the single-agent baseline.
- **C1 evaluation baseline:** one ReAct agent with the same model, read tools and eight-call ceiling as C2. It remains in AI Agent Experiments because the guideline explicitly requires it; it is not offered as a new portfolio flow.
- **C2 agentic system:** supervisor plus market, strategy and compliance-critic specialists. C2 adds an SMC route, dated RAG/web evidence, typed hand-offs, correction/replan, holding reviews and adverse-event exits. At each close it can research a bounded default pool of three top technical candidates; if the first is evidence-blocked, the next candidate can be considered. It selects the highest-ranked evidence-qualified candidate rather than treating missing evidence as strength.
- **Control:** Python owns arithmetic, eligibility, costs and execution. Supervised actions require an exact-payload approval hash; historical replay uses upfront-approved rules. There is no live exchange API.

### Figure 1 execution walkthrough

1. The reviewer chooses a frozen universe, historical window, capital and one of three inference adapters for the C2 portfolio in Streamlit. AI Agent Experiments separately lock identical cases for C0, C1 and C2. FastAPI authenticates the reviewer and records inference consent.
2. The experiment harness sends an identical locked case to C0, C1 and C2 when performing the architecture evaluation. C0 is deterministic; C1 uses one tool-using agent; C2 creates a bounded supervisor plan for three specialists.
3. The C2 market specialist reads the historical snapshot and dated company evidence. A bounded dated-web fallback may supplement a genuinely incomplete historical pack, but it cannot introduce evidence published after the decision cutoff.
4. The strategy specialist reads policy RAG and the code-approved route. It returns a typed strategy, cited explanation and permitted portfolio action; it cannot change the strategy catalogue or calculate an order quantity.
5. The independent critic obtains its own scoped observations and accepts or rejects the proposed interpretation. Schema or evidence contradictions can trigger a bounded correction; rejection cannot authorize execution.
6. FastMCP tools provide market, company, policy, route and reviewed-memory observations. Pre/post-tool hooks enforce permissions and budgets, scan untrusted content, scrub secrets and append the trace.
7. Deterministic validation checks schemas, dates, citations, route agreement and adverse evidence. Python then owns quantity, fixed delivery fees, slippage, stops, targets, capacity and all cash/ledger arithmetic.
8. Historical replay proceeds only under upfront-approved rules and fills at the eligible later open. A separately supervised action pauses for approve, edit or reject on the exact payload hash, then repeats freshness and risk checks before simulated submission. No live broker exists.
9. JSON/SQLite records preserve traces, checkpoints, decisions and ledger events. Human-reviewed lessons may be frozen for later development runs; the E1–E4 harness, monitoring dashboards and CI measure quality, safety, latency and cost.

### Final demonstration UI

The portfolio form deliberately exposes only the decisions needed for the capstone demonstration: C2 starting capital, start/end dates, inference allowance, reviewed-memory version, consent and replay-rule approval. The risk policy is displayed but not editable: ROUTER, 1% normal risk, 0.5% breakout risk, ATR stops/trails, 8% net target, 10 bps slippage, three C2 research candidates and five-session holding reviews. This reduces accidental configuration drift while every value remains recorded in the saved result. The inference selector retains **ChatGPT/Codex CLI**, **OpenRouter API**, and **Claude CLI**.

The optional `HUMAN_EVIDENCE_OVERRIDE` study in C2 Strategy Backtests pauses evidence-insufficient blocks attached to an otherwise valid technical BUY or holding SELL. Hard adverse, provider, schema, policy, route, capital and risk failures are never overrideable. `KEEP_BLOCKED` or `APPROVE_OVERRIDE` is recorded separately without rewriting C2. Approved BUYs create linked simulated positions. A later discretionary C2 EXIT on that position pauses for `KEEP_HOLDING` or `APPROVE_EXIT`, and an evidence-blocked SELL can also pause; stops, trailing stops and targets remain automatic. Realized or marked-to-market outcomes can be reviewed as conditional lesson candidates but are never learned automatically. AI Agent Experiments remains a research ablation rather than a duplicate trading approval screen.

The lifecycle distinguishes an approval from an evaluated outcome. A linked open position is `INCONCLUSIVE_OPEN`; after exit, positive realized P&L is labelled `SUPPORTED` and non-positive realized P&L `NOT_SUPPORTED`. These are auditable evaluation labels, not investment claims. Only a closed lifecycle is eligible for a subsequent human lesson review, and governed memory still requires a separate accept-and-freeze step. The local reviewer token authorizes the write to the decision ledger and is never part of the model prompt.

The UI exposes pending checkpoints through a read-only notification inbox. Every 15 seconds, the local dashboard queries only runs in `PAUSED_HUMAN_OVERRIDE`; a bell count and one-time toast identify new items. Selecting an item loads its immutable run checkpoint in Strategy Backtests, where evidence and rationale are reviewed. The bell cannot approve a decision and creates no inference call. Alerts disappear only when the persisted run is no longer awaiting human intervention. This is deliberately an in-app mechanism rather than an external email or browser-push dependency.

To reduce UI clutter, Strategy Backtests displays only the universe-wide C2 portfolio and governed intervention workflow. The controlled architecture comparison is confined to AI Agent Experiments. Legacy C0/single-stock endpoints and saved runs are retained for reproducibility but are not prominent UI workflows.

A separate v0.35 redesign proposal is available on port 8504 without replacing the current port-8501 application. It converts the supplied visual proposal into four question-led demo tiles: Data & Stock, C2 Portfolio, Agent Comparison and Evaluation Evidence, plus a secondary Knowledge & Lessons page. The shell reads the same FastAPI records and displays real repeat/portfolio state; it does not implement a parallel engine. New C2 execution is intentionally disabled in the proposal until the reviewer approves the design.

The redesign uses a high-contrast navy sidebar and solid blue workspace tiles; the original UI remains the operational fallback. Because the proposal is not yet frozen, no result is promoted to final held-out evidence from this revision. The original 102 unreviewed templates remain in `evaluation/agentic_candidates_20261117/` as historical candidate material. After UI/code approval, a newly versioned case set must be generated, independently reviewed, frozen and then used for final E1–E4 runs. The exact sequence is recorded in `POST_UI_FREEZE_EVALUATION_PLAN.md`.

C2 does not require a frontier reasoning model for routine typed extraction and policy checking. The balanced response budget is 3,600 tokens per case, with specialist turns targeted near 450 tokens and a reserve for a bounded correction. A smaller instruction-following model is appropriate only after it passes the schema, citation, breakout-evidence and adverse-event evaluations; held-out quality and failure rate govern model choice, not price alone.

## Minimum-bar assessment

| Area | Implemented evidence | Final-review status |
|---|---|---|
| Retrieval | Source/date metadata; BM25 + vectors + RRF; reranker; query rewriting; passage IDs | Partial: development Recall@5 exists; independent label review and a held-out rerun remain required |
| Tools/MCP | Six FastMCP servers, typed schemas, structured errors, scoped read/write access and tests | Implemented; export final inventory and test evidence |
| Orchestration | Typed LangGraph specialist graph, bounded correction loop, durable portfolio checkpoints/resume | Partial: retain a live resume recording and do not overclaim a LangGraph-native checkpointer where file/SQLite checkpoints are used |
| Memory | Short-term workflow state; reviewed SQLite lessons; applicability, accept/reject/freeze and policy | Partial: run final memory-off/on held-out E3 |
| Planning | Visible plan object, ReAct tool use, correction/replan events | Partial: retain one successful contradiction/replan trace |
| Multi-agent | C2 supervisor + three specialists; C1 same-tool/budget baseline | Partial: final funded three-repeat E1 is still required |
| Improvement | Development reflection, conditional lessons, human review, rejected lessons and frozen versions | Partial: held-out before/after result and lesson-generation cost required |
| Evaluation/monitoring | 20 development + 40 held-out executable-after-review CaseEvidence templates; traces; Prometheus/Grafana | Partial: independently signed case labels, calibrated judge and final dashboard evidence remain required |
| Human control/hooks | Grounded C2 BUY/SELL approve/reject with rationale; internal research binding; permission/budget/logging hooks | Partial: retain independently reviewed approve and reject demonstrations |
| Security | Threat model, scoped tools, guardrails, 32 distinct executable-after-review attacks and ten clean templates | Partial: named human ratification and model-level defence-off/on results remain required |
| Deployment | FastAPI, Streamlit, Docker Compose, CI, Prometheus, Grafana and alert rules | Partial: clean-machine proof, fired alert and hosted failed-CI record required |

Therefore the implementation is substantial, but the **minimum bar is not yet fully evidenced for final review**. Independent human labels and reviewed held-out experiments are major gaps, but not the only gaps. The final evidence package also needs three repetitions, different-family judge calibration, E2/E3/E4 ablations, actual contribution entries, slides/video, hosted failed-CI proof and a fired-alert demonstration. These items must be linked to retained artifacts rather than replaced with generated claims. Role-specific forms are provided in [TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md](TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md), and background evaluation runs can be retained under `reports/capstone_runs/` using `evaluation/experiment_ledger.py`.

## Evaluation protocol: answers and justification

### Golden set

The repository now contains two separate 60-case resources. The original deterministic route/risk/broker fixtures remain development references. The newer `evaluation/agentic_candidates_20261117/` set contains 20 development and 40 held-out historical `CaseEvidence` templates, grouped by disjoint symbol/regime families and bound to cached evidence-pack hashes. Expected outcomes are intentionally `REVIEW_REQUIRED`. Before a final paid run, a named reviewer who did not tune the relevant component must personally review the labels. Held-out files must not enter prompts, retrieval or tools. Any case already used to change the system must be moved to development and disclosed.

### Code first, judge second

Code checks route outcomes, database/ledger state, quantities, citation existence, required tool calls, forbidden actions, exact approval hashes and policy violations. A different-family judge is used only for semantic support and explanation quality. `evaluation/judge_calibration.json` contains 20+ items but its human labels are intentionally blank. The team must label them independently, run `evaluation/judge_agreement.py` and report Cohen’s kappa before trusting judge scores.

### E1 — does the agent justify its cost?

Run C0, C1 and C2 on identical locked cases. The required architecture comparison is **C1 single agent versus C2 multi-agent team**: same inference model, case, evidence, available tool capabilities, total response-token budget and eight-call ceiling. C0 has no agent decisions and is a secondary deterministic reference. Report task success, grounded claims, policy violations, tool-trajectory correctness, usage/cost, median/p95 latency, errors and timeouts.

For an intuitive but secondary financial outcome, each entry case is evaluated after inference using a fixed ₹100,000 notional from the next eligible open to the 20th later-session close, with 10 bps slippage and modeled NSE delivery fees. A non-entry remains in cash with zero return. The price path is never available to any agent or tool during the decision. Cases without the full future window are marked unavailable rather than shortened. This standardized outcome makes C1/C2 decisions financially interpretable without turning E1 into a portfolio-strategy comparison.

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

Run 32 distinct attacks with defences off/on and ten clean cases with defences off/on. Hard execution controls remain enabled in both conditions; the ablation concerns model-facing injection/output defences. Report attack success and legitimate false-block rate. The earlier scanner file contained 16 payloads duplicated to 32 rows and is retained only as a development proxy. The replacement E2 templates contain 32 distinct payloads and unique markers, but remain unsigned and have not yet produced model-level results.

### E3 — did lessons help?

Freeze reviewed lessons produced only from development failures. Run untouched held-out cases with memory off and with the frozen playbook on. Include reflection/judge inference used to create lessons, retrieve only applicable lessons, show one rejected lesson and its rationale, and identify any accepted lesson that worsened a result.

### E4 — signature ablation

For this finance project, use the Analyst Desk analogue: compare the compliance critic loop on/off and structured/table-aware dated evidence with the simpler retrieval representation. Hold cases, model, tools and budgets fixed. Report citation/claim support, numeric/source validation, task success, usage and latency. Portfolio returns may be reported separately but cannot replace research-quality measures.

### Repeats and reporting

Repeat the final held-out comparison three times. Preserve failures and timeouts. For every configuration report task-success counts, policy violations, attack success, false blocks, inference usage/cost, median and p95 latency and errors, plus the spread across repeats. Never select parameters from held-out performance.

## Current measured development evidence

This section is a dated evidence snapshot, not part of the fixed system design. Additional inference runs are currently being collected. Their retained run IDs, failures and independently reviewed labels should replace or extend this section only after completion; the architecture, controls and evaluation definitions above must not be rewritten to make a later score look favorable.

- Full local regression suite: **377 passed** on 17 November 2026 after the C2-only portfolio UI, fair C1/C2 experiment contract and standardized forward-outcome update. The warnings are Streamlit/NumPy deprecation notices, not test failures.
- Golden development checker: 20/20 seeded development cases in `reports/capstone_review_dev.json`; the report itself states that labels require independent review.
- Fresh neural RAG development evidence is saved in `reports/rag_development_20261117.json`. On 101 authored development queries, Recall@5 was 0.9406 without rewriting and 0.9604 with rewriting; MRR@5 increased from 0.8667 to 0.8815. The legacy 36-query neural score was 0.9167. These are authored development labels, not independently ratified held-out claims.
- Retained deterministic neural run `20261117T110205-1c7df087` completed against candidate labels. It checks routing, risk/broker reference behaviour, retrieval and the scanner proxy; it is not C1/C2 model-quality evidence.
- The earlier deterministic scanner detected 93.8% of 32 rows with zero false blocks on ten clean strings, but those rows contained only 16 distinct attack payloads. This is a scanner proxy only. The new 32 distinct E2 templates remain pending review and execution.
- Fresh v0.35 E4 deterministic strategy ablation is retained in `reports/capstone_e4_v035.json`. On synthetic data, ROUTER returned 3.28%, EMA Trend 10.64%, EMA Pullback −0.91%, RSI Reversion 3.14% and Breakout 3.80%; the negative relative router result is preserved and is not a real-market profitability claim.
- Three fresh development repetitions are retained as `1eac0a24d4e04453ab9bbab9e7c935da`, `e26275b0e9f34b22b7a7315cbbea0475` and `51ab85a7df0b4abf94fed845595adc4f`. They used OpenRouter `openai/gpt-4.1-mini`, the same IDEA/LT/HINDALCO cases dated 30 September 2026, identical evidence/tool capabilities, 3,600-token case budget and eight-call ceiling. C1 guard passes were 0/3, 1/3 and 1/3; it used 11 calls each time, cost $0.0506416 in total and had mean per-run median latency 26.881 seconds. C2 was stable at 1/3 guard pass in all repeats; it used 12 calls each time, cost $0.03462 in total and had mean per-run median latency 12.703 seconds. C2 entered LT in every repeat and abstained on losing IDEA/HINDALCO cases, producing the same standardized +₹3,371.19 per run. C1 entered LT in two repeats, producing ₹0, +₹3,371.19 and +₹3,371.19. C0 entered all three and produced −₹11,402.08 per run. This small development sample suggests more stable C2 behaviour and lower observed latency/cost with this adapter, but it cannot establish held-out superiority or future profitability. All abstentions, citation failures and negative C0 outcomes remain visible.
- Judge human labels are not complete; no valid final Cohen’s kappa is claimed.
- OpenRouter development engineering runs used `openai/gpt-4.1-mini`. The corrected 20-case v18 artifact records 20/20 C0, 13/20 C1 and 10/20 C2 guard passes. These counts are **not task accuracy** because the historical candidate outcomes are not independently labelled and some fail-closed evidence outcomes are legitimate. The later v19 two-case smoke isolated one C2 critic response truncated by an overly tight output ceiling; v20 raises only that typed critic allowance and the full regression suite passes. No held-out score is claimed from these tuning runs.
- Recorded OpenRouter spend for the preflight, correction and development runs was approximately **US$0.5483**, below the user-authorized US$1 ceiling. Claude CLI was installed but unauthenticated, so no Claude result is claimed. A two-case Codex development probe is retained in `reports/codex_e1_development2_v18.json` as provisional adapter evidence, not as a cross-model comparison.

## Security, privacy and human control

The threat model covers prompt injection through evidence, hallucinated quantities, approval tampering, retries/duplicates, stale prices, credential leakage, excessive tools, denial-of-service loops and held-out leakage. Secrets remain in ignored environment files and are scrubbed from traces. LLM specialists receive no broker-write tool. The demo bearer token is not production authentication; internet deployment would require accounts, MFA/RBAC, encryption, retention automation and independent testing.

## Deployment and operation

`bash scripts/start_unix.sh` or the Windows script creates the environment and launches FastAPI and Streamlit. Docker Compose additionally starts MCP services, Prometheus and Grafana. Prompt/model IDs are versioned, and saved portfolio runs pin data, corpus, prompt, backend and engine versions. A mismatch requires a fresh run rather than silently changing an old experiment.

## Limitations and conclusion

AegisTrade does not establish profitable advice. Survivorship bias, unadjusted prices, incomplete historical evidence, model variation and limited independent labels prevent that claim. Its defensible contribution is an auditable architecture that separates model interpretation from deterministic financial controls, compares single-agent and multi-agent research under bounded resources, and preserves failures instead of hiding them. Final grading readiness depends on completing the independent and held-out evidence listed in the completion checklist.

