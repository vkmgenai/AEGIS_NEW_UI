# AegisTrade final capstone completion checklist

Last updated: 2026-11-14. This file is the durable restart point across inference-allowance resets.

Status meanings: `DONE` verified now; `PARTIAL` implemented but final-review evidence is incomplete; `TODO` still required; `BLOCKED-TEAM` requires independent team/human work and must not be fabricated by code.

## A. Product architecture migration

- [x] DONE — Portfolio UI exposes C0 deterministic ROUTER and C2 agentic ROUTER; C1 portfolio is removed from new-run choices.
- [x] DONE — C2 ROUTER supports EMA Trend, EMA Pullback, RSI Reversion, Breakout and SMC.
- [x] DONE — Random C0 selection rejected; C0 remains a deterministic zero-LLM technical baseline.
- [x] DONE — C0 and C2 comparison uses a common point-in-time opportunity set and clearly labels additional C2 research/SMC effects.
- [x] DONE — C2 uses a bounded ranked research pool (default three) so an evidence-blocked first candidate can fall through to the next; missing evidence is not scored as fundamental strength.
- [x] DONE — Legacy C1 saved runs remain readable; new C1 creation returns an explicit retirement message.
- [x] DONE — Streamlit, FastAPI health metadata, tests and final documentation agree on the two portfolio flows.

## B. Required E1 evaluation architecture

- [x] DONE — C0 deterministic research baseline exists.
- [x] DONE — C1 single tool-using agent exists with the same available tools and per-case budget.
- [x] DONE — C2 supervisor plus market, strategy and critic specialists exists with typed hand-offs.
- [x] DONE — Keep C1 in AI Experiment only; label it `evaluation baseline`, not a portfolio product flow.
- [ ] TODO — Run same-case/model/tools/budget C0/C1/C2 comparison three times and report spread, failures, timeouts, cost/usage and latency.

## C. Claude/Fable repository review

- [x] DONE — Compared source trees without reading/copying secrets or generated private data.
- [x] DONE — Rejected permissive `coverage_fallback.py`: missing evidence must not silently become a clean fundamental finding.
- [x] DONE — Identified reusable evaluation pattern in `run_retune_study.py`: development window, later-period window, frozen settings and explicit limits.
- [x] DONE — Current project confirmed newer in evidence library/OCR, SMC recovery, portfolio comparison, live progress and portfolio UI.
- [x] DONE — Final project report contains adopted/rejected Claude/Fable items and test evidence.

## D. Minimum-bar audit

- [ ] PARTIAL — Retrieval: hybrid BM25/vector/RRF, reranking and query rewriting exist; 36 and 101-query development sets exist. Need independently reviewed 30+ labels and before/after final evidence.
- [x] DONE — Tools/MCP: six FastMCP servers exist with typed tools and tests.
- [ ] PARTIAL — Orchestration: LangGraph typed specialist graph, correction loop and durable portfolio checkpoints exist. Need faculty-ready graph diagram and recorded live stop/resume evidence; verify use of a persistent LangGraph checkpointer where specifically claimed.
- [ ] PARTIAL — Memory: reviewed/frozen long-term lessons and policy exist. Need final memory-on/off held-out comparison and deletion/correction demo evidence.
- [ ] PARTIAL — Planning/ReAct: plan and replan events exist. Need one retained trace showing contradiction and successful replan.
- [ ] PARTIAL — Multi-agent: C1/C2 code exists. Need funded/repeatable fair E1 results.
- [ ] PARTIAL — Improvement: reflection/review/freeze workflow exists. Need held-out before/after playbook, total lesson cost and one retained rejected lesson with reason.
- [ ] PARTIAL — Evaluation/monitoring: 20 development + 40 held-out seeded cases, 32 attacks, traces, Prometheus/Grafana assets exist. Labels explicitly require independent review; judge predictions/calibration and final dashboard evidence remain.
- [ ] PARTIAL — Human control/hooks: exact-payload approval/edit/reject and tool hooks exist for supervised simulated actions. Need recorded edit-invalidates-approval demonstration and careful explanation that historical replay uses upfront rule approval.
- [ ] PARTIAL — Security: threat model and 32 attacks exist. Need model-level defence-off/on results plus clean false-block rate and independent attack ownership.
- [ ] PARTIAL — Deployment: FastAPI, Streamlit, Docker Compose, CI, Prometheus/Grafana and alerts exist. Need clean-machine proof, one working alert and a hosted failed-CI record with explanation.

## E. Evaluation protocol and final-review evidence

- [x] DONE — Golden-set files contain 20 development and 40 held-out cases.
- [ ] BLOCKED-TEAM — Independently verify expected outcomes before final runs; keep related families in one split and held-out inaccessible to agents.
- [ ] TODO — Code-first checks for outcomes, citations, tool trajectories and forbidden actions.
- [ ] BLOCKED-TEAM — Obtain 20+ human labels for judge calibration; use a different-family judge and report Cohen's kappa.
- [ ] TODO — E1 C0/C1/C2 fair comparison.
- [ ] TODO — E2 defences off/on on attacks and clean cases.
- [ ] TODO — E3 memory/playbook off/on on untouched held-out cases.
- [ ] TODO — E4 critic-loop on/off and evidence parsing/retrieval ablation, adapted from Analyst Desk.
- [ ] TODO — Repeat final held-out comparison three times; include task success, policy violations, attack success, false blocks, usage/cost, median/p95 latency, errors and timeouts.
- [ ] BLOCKED-TEAM — If any held-out result has already influenced tuning, relabel it development and disclose that decision.

## F. Submission package

- [x] DONE — Main README includes one-command startup and final-submission navigation; existing sections retain prerequisites, model/config and limitations.
- [x] DONE — Separate final-presentation README/Word guide contains demo order and speaking cues.
- [x] DONE — Redrawn architecture diagram and numbered walkthrough match current code.
- [x] DONE — Threat model source exists; verify final one-page formatting/current architecture.
- [x] DONE — Memory policy source exists; verify final one-page formatting/current architecture.
- [x] DONE — Final project report (Markdown and Word) includes minimum-bar matrix and evaluation-protocol answers.
- [ ] TODO — Evaluation report, 4–6 pages, based on actual final results only.
- [ ] TODO — Experiment log with configs and negative/failed runs.
- [ ] BLOCKED-TEAM — Contribution log for the faculty-approved three-person team.
- [ ] BLOCKED-TEAM — Final slides and backup demo recording.
- [x] DONE — Secret scan found no committed key/token value; the only match was a documented `.env` placeholder. Runtime/private/unlicensed data remains excluded by policy and ignore rules.
- [x] DONE — Full tests pass (346); v0.27 health, UI contracts and local smoke endpoints pass after service restart, with no real trades placed.

## G. Required honesty statements

- [x] DONE — Simulation only; no live exchange orders.
- [x] DONE — No claim of guaranteed profitability or investment advice.
- [x] DONE — Current/frozen constituents applied backward create survivorship bias.
- [x] DONE — Raw/unadjusted OHLCV leaves corporate-action limitations.
- [x] DONE — Team size of three is recorded as faculty-approved; guideline default of four is disclosed rather than silently changed.
- [x] DONE — AI-generated seeded labels are not represented as independent human labels.
