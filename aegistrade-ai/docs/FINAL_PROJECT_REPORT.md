# AegisTrade AI — final capstone project report

Version 0.27 · 14 November 2026 · Team size: three, approved by faculty

## Executive summary

AegisTrade is a simulation-only equity-research and historical portfolio prototype for an analyst/reviewer. It combines point-in-time technical screening, dated company evidence, hybrid RAG, MCP tools, a single-agent baseline, a three-specialist LangGraph workflow, deterministic risk controls, reviewed memory, human approval and operational monitoring. It never connects to a live broker and does not claim profitable investment advice.

The primary research question is not “can an LLM predict price?” It is: **does a grounded specialist team improve the quality, auditability and safety of regime-aware research decisions enough to justify its additional inference cost relative to deterministic and single-agent baselines?** Portfolio return is a secondary system outcome, not the sole agent-quality metric.

## Problem, users and scope

The target user is an equity-research analyst or capstone reviewer exploring historical NSE scenarios. Technical systems can generate many signals but usually provide weak dated justification; unconstrained LLMs can hallucinate evidence, calculate money incorrectly or leak future information. AegisTrade separates responsibilities: code detects signals and controls money, agents research and explain, a critic challenges claims, and a person governs any supervised simulated action.

The prototype supports frozen Nifty20, Nifty100 and diversified research30 universes. Current constituent snapshots applied backward introduce survivorship bias, and raw/unadjusted OHLCV does not fully reconstruct corporate actions or dividends. Consequently, returns demonstrate engineering behaviour, not a deployable investment edge.

## Final system design

The detailed diagram and twelve-step walkthrough are in [FINAL_ARCHITECTURE.md](FINAL_ARCHITECTURE.md).

[[FIGURE:final_architecture]]

- **C0 portfolio baseline:** zero-generation deterministic ROUTER using EMA Trend, EMA Pullback, RSI Reversion and Breakout.
- **C1 evaluation baseline:** one ReAct agent with the same model, read tools and eight-call ceiling as C2. It remains in AI Agent Experiments because the guideline explicitly requires it; it is not offered as a new portfolio flow.
- **C2 agentic system:** supervisor plus market, strategy and compliance-critic specialists. C2 adds an SMC route, dated RAG/web evidence, typed hand-offs, correction/replan, holding reviews and adverse-event exits. At each close it can research a bounded default pool of three top technical candidates; if the first is evidence-blocked, the next candidate can be considered. It selects the highest-ranked evidence-qualified candidate rather than treating missing evidence as strength.
- **Control:** Python owns arithmetic, eligibility, costs and execution. Supervised actions require an exact-payload approval hash; historical replay uses upfront-approved rules. There is no live exchange API.

## Review of the Claude/Fable implementation

The parallel repository at `/Users/karthikakrishnakumar/Claude_Repo/aegistrade-ai` was reviewed read-only and compared at source level without copying credentials or private runtime data.

Useful idea adopted: its offline retuning study separates a development window from a later-period window, freezes candidate defaults and states that short replays do not prove durable edge. This structure is carried into the final evaluation protocol.

Idea rejected: `coverage_fallback.py` changes a blocked entry into ENTER whenever no cited adverse finding exists. Missing evidence is not adverse evidence, but it is also not proof of strength. The final project records coverage limits, permits only explicitly defined signal-specific behaviour and never labels missing evidence as a clean fundamental conclusion.

The current project already has newer evidence-library/OCR controls, fixed delivery fees, SMC stop recovery, portfolio memory, C0/C2 comparison, live progress and a broader UI/test suite. Wholesale merging would regress these controls.

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
| Human control/hooks | Exact-payload approve/edit/reject; permission/budget/logging hooks | Partial: record the edit-invalidates-approval demonstration |
| Security | Threat model, scoped tools, guardrails and 32 attacks | Partial: run model-level defence-off/on plus ten clean cases and report false blocks |
| Deployment | FastAPI, Streamlit, Docker Compose, CI, Prometheus, Grafana and alert rules | Partial: clean-machine proof, fired alert and hosted failed-CI record required |

Therefore the implementation is substantial, but the **minimum bar is not yet fully evidenced for final review**. The missing items are experimental or independent-human evidence; they must not be replaced with generated claims.

## Evaluation protocol: answers and justification

### Golden set

The repository contains 60 candidate cases: 20 development and 40 held-out, grouped by scenario family. Expected outcomes are marked as seeded hypotheses requiring independent human verification. Before the final run, a team member who did not tune the relevant component must review the labels. Held-out files must not enter prompts, retrieval or tools. Any case already used to change the system must be moved to development and disclosed.

### Code first, judge second

Code checks route outcomes, database/ledger state, quantities, citation existence, required tool calls, forbidden actions, exact approval hashes and policy violations. A different-family judge is used only for semantic support and explanation quality. `evaluation/judge_calibration.json` contains 20+ items but its human labels are intentionally blank. The team must label them independently, run `evaluation/judge_agreement.py` and report Cohen’s kappa before trusting judge scores.

### E1 — does the agent justify its cost?

Run C0, C1 and C2 on identical locked cases. C0 has no agent decisions; C1 and C2 use the same inference model, available read tools, output limits and eight-call ceiling. Report task success, grounded claims, policy violations, tool-trajectory correctness, usage/cost, median/p95 latency, errors and timeouts. Portfolio C0/C2 P&L is secondary because C2 additionally has SMC and holding research; it is not the pure architecture ablation.

### E2 — do the defences work?

Run 32 attacks with defences off/on and ten clean cases with defences off/on. Hard execution controls remain enabled in both conditions; the ablation concerns model-facing injection/output defences. Report attack success and legitimate false-block rate. The existing regex scanner result is only a development proxy, not the final E2 result.

### E3 — did lessons help?

Freeze reviewed lessons produced only from development failures. Run untouched held-out cases with memory off and with the frozen playbook on. Include reflection/judge inference used to create lessons, retrieve only applicable lessons, show one rejected lesson and its rationale, and identify any accepted lesson that worsened a result.

### E4 — signature ablation

For this finance project, use the Analyst Desk analogue: compare the compliance critic loop on/off and structured/table-aware dated evidence with the simpler retrieval representation. Hold cases, model, tools and budgets fixed. Report citation/claim support, numeric/source validation, task success, usage and latency. Portfolio returns may be reported separately but cannot replace research-quality measures.

### Repeats and reporting

Repeat the final held-out comparison three times. Preserve failures and timeouts. For every configuration report task-success counts, policy violations, attack success, false blocks, inference usage/cost, median and p95 latency and errors, plus the spread across repeats. Never select parameters from held-out performance.

## Current measured development evidence

- Full local test suite: **346 passed** on 14 November 2026, including an end-to-end C2 SMC entry with a four-route, non-SMC C0 reference.
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

