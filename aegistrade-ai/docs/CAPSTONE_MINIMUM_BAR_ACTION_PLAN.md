# AegisTrade capstone minimum-bar action plan

**Version 1.0 · 17 November 2026**  
**Team:** Veneet, Karthika and Mathangi (three-member arrangement approved by the professor)  
**Purpose:** turn the capstone guideline’s minimum bar into an executable checklist with owners, commands, evidence and acceptance criteria.

This document is a completion plan, not a claim that unfinished evidence exists. `DONE` means an implementation or artifact already exists. `PARTIAL` means the feature exists but the final-review proof is incomplete. `TEAM ACTION` requires a named person to inspect, label, demonstrate or sign evidence; an LLM cannot do that on the person’s behalf.

## 1. What “minimum bar achieved” means

The project is ready only when all of the following are true:

1. Every minimum-bar area has an artifact that can be opened during the review.
2. The 60+ golden cases have independently reviewed expected outcomes before the final held-out run.
3. E1, E2, E3 and E4 use frozen configurations, retain failures and are recorded in the experiment ledger.
4. A different-family judge is calibrated against at least 20 human-labelled outputs and Cohen’s kappa is reported.
5. The final held-out comparison is repeated three times and reports spread, errors and timeouts.
6. The repository starts with one command on a clean machine, CI contains a visible failed-gate demonstration and a monitoring alert is visibly fired.
7. The repository contains the required report, diagrams, threat model, memory policy, experiment log, contribution log, slides and backup recording, with no secrets or private/unlicensed data.

The existing portfolio simulations, including run `dc354841097240e0bc88d8430953fa22`, are useful **development and workflow evidence**. They do not replace the controlled E1–E4 protocol.

## 2. Recommended execution order

Do the work in this order. Do not run the paid held-out experiments before the labels, policies and configuration are frozen.

| Phase | Outcome | Owner | Independent check |
|---|---|---|---|
| 1 | Freeze scope, code, data, prompts and evaluation rules | All; Karthika records versions | Veneet and Mathangi |
| 2 | Independently review golden cases and retrieval labels | Veneet | Mathangi |
| 3 | Complete code-first checkers and judge calibration | Veneet | Mathangi resolves disagreements |
| 4 | Finish missing minimum-bar demonstrations | Component owner | Teammate who did not build it |
| 5 | Create, review and freeze development lessons | Karthika | Veneet or Mathangi |
| 6 | Run final E1–E4 held-out experiments three times | Veneet launches frozen runs | All interpret results |
| 7 | Capture deployment, CI, dashboard and alert evidence | Mathangi | Veneet |
| 8 | Assemble submission package and rehearse viva | All | Cross-review |

## 3. Phase 1 — freeze the experiment before final testing

**Current status: PARTIAL.** Versioned prompts, simulator versions, corpus hashes and run manifests already exist. A final signed freeze record is still required.

### Steps

1. Pull the final branch and run the complete test suite.
2. Record the Git commit SHA, Python version, provider adapter, exact model ID, prompt version, corpus hash, universe manifest and evaluation-case hashes.
3. Decide which cases are development and which are held-out by **scenario family**, not by individual row.
4. Move every case already used to tune prompts, rules or lessons into development.
5. Confirm that held-out expected labels are unavailable to model prompts, RAG, MCP tools and lesson retrieval.
6. Create `reports/final_freeze_manifest.json` containing the recorded identifiers and sign-off names.
7. After freezing, do not alter prompts, policies or lessons based on held-out results. If a defect forces a change, relabel affected held-out families as development and disclose it.

### Evidence to retain

- `reports/final_freeze_manifest.json`
- final Git commit link
- complete test output
- development/held-out family intersection check showing zero overlap
- reviewer names and dates

### Acceptance criterion

A teammate can reproduce the exact configuration, and no held-out family has influenced tuning.

## 4. Retrieval minimum bar

**Guideline requirement:** source/date metadata; hybrid BM25 + vectors with RRF; reranker; one query-side method; passage-ID citations; Recall@5 on 30+ labelled queries before and after one change.  
**Current status: PARTIAL.** The implementation and 36/101-query development evaluations exist, but the final 30+ labels have not been independently reviewed.

### Steps

1. Veneet opens `evaluation/retrieval/queries_36.jsonl` without looking at system results first.
2. For every query, verify the relevant passage IDs against the underlying dated source. Record `ACCEPT`, `CORRECT` or `QUARANTINE` with a short reason.
3. Mathangi independently checks corrected/quarantined items and resolves disagreements with Veneet.
4. Freeze the reviewed query file and hash it.
5. Run the baseline and improved retrieval configurations on the same queries. The change may be query rewriting, reranking or the current combined configuration, but only one declared change should distinguish before/after.
6. Run:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.run_rag_eval \
     --offline-only --output reports/final_rag_evaluation.json
   ```

7. Report Recall@5 before and after, the delta, per-family failures and any regressions. Do not hide queries where performance worsened.
8. In the demo, open one retrieved passage and show source, publication/availability date and passage ID used by C2.

### Evidence to retain

- independently reviewed 30+ query file and hash
- `reports/final_rag_evaluation.json`
- before/after table and failed-query examples
- one screenshot/trace showing passage-ID citation and date cutoff

### Acceptance criterion

At least 30 independently labelled queries are evaluated on the same frozen corpus, and the report accurately shows before/after Recall@5.

## 5. Tools and MCP minimum bar

**Guideline requirement:** at least three FastMCP servers, typed inputs/outputs, structured errors, read/write classification, writes available only to the correct agent, and one test per tool.  
**Current status: implementation DONE; final inventory evidence PARTIAL.** Six servers and tests exist.

### Steps

1. Generate the tool inventory and verify every tool’s name, schema, read/write classification and permitted caller.
2. Confirm generation agents have no live broker-write tool. The project remains simulation only.
3. Run the MCP smoke tests and the complete tool test set.
4. Demonstrate one valid tool result and one structured error, such as missing historical evidence, without crashing the graph.
5. Export a table mapping every tool to its server, schema, agent access and test.

### Suggested commands

```bash
PYTHONPATH=. .venv/bin/python scripts/export_tool_inventory.py
PYTHONPATH=. .venv/bin/python scripts/mcp_smoke.py
```

### Evidence to retain

- tool inventory with schemas
- test output proving at least one test per tool
- valid-result and structured-error trace
- permission matrix

### Acceptance criterion

The reviewer can identify at least three FastMCP servers, inspect typed contracts and see that unauthorised writes are impossible.

## 6. Orchestration minimum bar

**Guideline requirement:** LangGraph typed state, conditional edges, one self-correction loop, persistent checkpointer, stop mid-run and resume.  
**Current status: PARTIAL.** Graphs, conditional validation/correction and durable portfolio checkpoints exist; final live resume evidence is required.

### Steps

1. Use the current architecture diagram to identify graph nodes, typed state and conditional edges.
2. Retain one trace where validation rejects an output and a bounded correction succeeds or terminates safely.
3. Start a short C2 run, record its run ID, pause it at a safe boundary, restart the API/dashboard and resume the same run.
4. Show that completed dates, model-call allowance, cash, positions and ledger events were not duplicated.
5. Capture before-pause and after-resume status plus the final ledger.
6. Explain separately that LangGraph approval state uses a checkpointer and the long portfolio replay uses its own durable checkpoint files.

### Evidence to retain

- current graph diagram
- self-correction trace
- pause/resume screen recording or screenshots
- saved run ID and before/after checkpoint hashes
- no-duplicate-event verification

### Acceptance criterion

A live run survives restart and resumes from its saved boundary without repeating a paid case or fill.

## 7. Memory minimum bar

**Guideline requirement:** short-term trimming/summarisation, a long-term store, and a written save/read/correct/delete policy; memory-on versus memory-off comparison.  
**Current status: PARTIAL.** Governed reviewed/frozen lesson storage and policy exist; final E3 and correction/deletion evidence remain.

### Steps

1. Review the memory policy and verify it covers content, purpose, writer, readers, retention, correction and deletion.
2. Demonstrate short-term context budgeting and the explicit `CONTEXT_BUDGET_EXCEEDED` behaviour—evidence must never be silently removed.
3. From development outcomes only, create conditional lesson candidates that say when they apply.
4. Have a person accept or reject every candidate; retain at least one rejected lesson and rationale.
5. Freeze accepted lessons into an immutable playbook version and record its hash.
6. Demonstrate correction/deletion by changing or deleting a test lesson through the governed path, not by manually editing the database.
7. Run E3 on untouched held-out cases with the frozen playbook off and on.

### Evidence to retain

- one-page memory policy
- context-budget trace
- accepted and rejected lesson records
- frozen playbook manifest/hash
- correction/deletion audit record
- E3 memory-off/on result

### Acceptance criterion

The team can explain exactly what memory stores and show measured held-out impact without learning from held-out cases.

## 8. Planning and ReAct minimum bar

**Guideline requirement:** show a plan object, replan when a tool contradicts it, and use ReAct in specialists.  
**Current status: PARTIAL.** Planning/replanning code exists; a retained contradiction trace is still needed.

### Steps

1. Choose a development case where the first hypothesis expects sufficient evidence.
2. Make the evidence tool return a truthful contradiction, such as an adverse filing or missing readable data.
3. Save the initial plan, tool observation, revised plan and final safe action.
4. Show at least one specialist’s thought/action/observation sequence in the permitted trace format without exposing secrets.
5. Verify the revised plan does not simply repeat the failed tool call.

### Evidence to retain

- initial plan JSON
- contradictory tool result
- replan event and final plan
- bounded ReAct trajectory

### Acceptance criterion

The trace proves that new evidence changes the plan and that the specialist uses tools within a budget.

## 9. Multi-agent minimum bar and E1

**Guideline requirement:** supervisor plus at least three specialists with separate tools and typed hand-offs; a single-agent baseline using the same tools and budget.  
**Current status: implementation DONE; final controlled evidence TODO.** C0, C1 and C2 exist in AI Agent Experiments.

### Steps

1. Freeze one model ID for C1 and C2. C0 uses no LLM; clearly mark research-only fields as not applicable rather than treating C0 as automatically superior.
2. Give C1 and C2 identical case inputs, read tools, evidence cutoff, response budget and maximum inference allowance.
3. Use independently reviewed cases. Start with development to validate the harness, then run held-out only after freezing.
4. Launch the final retained run:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.experiment_ledger launch \
     --experiment E1 --split heldout --repeats 3 \
     --consent-paid --max-paid-calls <APPROVED_LIMIT> --foreground
   ```

5. Report per architecture: task-success count, grounded evidence, adverse-risk flags, safe abstentions, hard failures, policy violations, tool-trajectory correctness, inference use/cost, median/p95 latency, errors and timeouts.
6. Show at least one C2 trace containing market specialist, strategy specialist and independent critic typed hand-offs.
7. Interpret benefit against additional cost; do not use portfolio P&L as the sole architecture-quality measure.

### Evidence to retain

- E1 ledger run ID and manifest
- exact config/model/tool/budget record
- three-repeat aggregate and spread
- one C1 and one C2 trace
- failure and timeout rows

### Acceptance criterion

C1 and C2 are compared fairly on identical held-out cases and the report explains whether the team adds value at what cost.

## 10. Improvement/Reflexion minimum bar and E3

**Guideline requirement:** score development runs, use a judge only where code cannot decide, reflect failures into conditional lessons, obtain human review, retrieve only relevant lessons, freeze before held-out, and compare held-out before/after.  
**Current status: PARTIAL.** Workflow exists; final reviewed lesson set and controlled E3 are pending.

### Steps

1. Treat existing portfolio outcomes as development evidence only.
2. Use code to detect citation, route, schema, forbidden-action and ledger failures first.
3. Use the calibrated judge only for semantic support or explanation-quality questions.
4. Generate short candidate lessons from development failures. Each lesson must include an applicability condition and must not name a stock as a universal recommendation.
5. Have a human review each candidate. Retain one rejected lesson and reason.
6. Freeze accepted lessons and record reflection/judge inference cost.
7. Launch E3 on untouched held-out cases with memory off/on and three repeats:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.experiment_ledger launch \
     --experiment E3 --split heldout --repeats 3 \
     --consent-paid --max-paid-calls <APPROVED_LIMIT> --foreground
   ```

8. Report improvements, regressions, added cost and any lesson that made an outcome worse.

### Candidate lessons from the current development run

The following may be reviewed; they are not automatically accepted:

- Do not override an evidence-blocked breakout merely because the technical signal is strong.
- “No confirmed adverse event” is not the same as sufficient positive evidence.
- Keep reduced risk for evidence overrides.
- Evaluate human intervention across the linked entry-to-exit lifecycle.

Avoid stock-specific lessons such as “always buy INFY” or “always override C2.”

### Acceptance criterion

The frozen playbook is derived only from development cases, every lesson is human-reviewed, and held-out memory-on/off results are retained.

## 11. Evaluation, golden set and judge calibration

**Guideline requirement:** 60+ development/held-out cases, outcome/trajectory/tool checks, a different-family judge calibrated against 20+ human labels, traces and Grafana.  
**Current status: PARTIAL.** 20 development + 40 held-out candidate cases exist; labels are seeded hypotheses pending independent review.

### Steps

1. Veneet independently reviews expected outcomes before seeing final system outputs.
2. Mathangi checks policy correctness and resolves disputed labels. Quarantine defective cases rather than quietly changing them after results.
3. Verify scenario-family separation and held-out isolation.
4. Complete at least 20 human labels in `evaluation/judge_calibration.json`.
5. Choose a judge from a model family different from the evaluated agents.
6. Run:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.judge_agreement \
     --labels evaluation/judge_calibration.json
   ```

7. Report confusion matrix, raw agreement and Cohen’s kappa. If agreement is inadequate, refine the rubric on development examples—not on held-out outputs—and recalibrate.
8. Verify code-first checks for final state, citations, required/forbidden tools, approval integrity and policy violations.

### Evidence to retain

- reviewed golden set with provenance
- family-split audit
- 20+ human/judge paired labels
- confusion matrix and Cohen’s kappa
- code-checker test results
- trace links for all final cases

### Acceptance criterion

No final semantic score relies on an uncalibrated judge, and no seeded/LLM-generated label is represented as independent human truth.

## 12. Security minimum bar and E2

**Guideline requirement:** one-page threat model, input/output guardrails, least-privilege tools, 30+ attacks through the real data path, defence-off/on attack success and legitimate false-block rate.  
**Current status: PARTIAL.** Threat model and 32 attacks exist; the 93.8% scanner result is only a development proxy.

### Steps

1. Veneet owns or independently reviews final attack texts because Mathangi owns the defences.
2. Confirm at least 30 attacks include retrieved-document injection, poisoned tool content, data leakage, approval tampering and forbidden action attempts.
3. Freeze ten or more legitimate clean cases.
4. Define precisely which model-facing defences are disabled in the OFF arm. Never disable deterministic money, permission or simulated-execution safety controls.
5. Run E2 with the same cases/model/budget for defence OFF and ON, retaining all traces.
6. Launch through the ledger:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.experiment_ledger launch \
     --experiment E2 --split heldout --repeats 3 \
     --consent-paid --max-paid-calls <APPROVED_LIMIT> --foreground
   ```

7. Report attack-success rate, clean false-block rate, policy violations, harmful tool attempts, cost, latency, failures and timeouts.
8. Open one injected historical document in the demo and show that its instruction is treated as data.

### Acceptance criterion

The final report contains model-level OFF/ON results, not only regex-scanner results, and legitimate-work blocking is quantified.

## 13. Human control and hooks minimum bar

**Guideline requirement:** every world-changing action uses `interrupt()` with approve/edit/reject tied to the exact payload; pre-tool permission/budget hooks and post-tool logging.  
**Current status: PARTIAL.** Approval, reviewer authentication, payload integrity, budgets and audit ledgers exist; the final edit-invalidates-approval demonstration is needed.

### Steps

1. Use the supervised simulated-action graph for the exact-payload demonstration. Explain that portfolio replay uses upfront rule approval plus `HUMAN_EVIDENCE_OVERRIDE` checkpoints; neither route sends live orders.
2. Generate a proposed simulated order and record its payload hash.
3. Approve it, then edit the quantity or price.
4. Demonstrate that the old approval is rejected because the payload hash changed.
5. Approve or reject the new exact payload and inspect the audit event.
6. Show a pre-tool budget/permission denial and a post-tool scrubbed log.
7. Demonstrate the human-review bell and a BUY/SELL override card with signal price, entry price for SELL, rationale and linked outcome.

### Evidence to retain

- before/after payloads and hashes
- invalidated approval response
- approve/edit/reject audit events
- hook permission/budget denial and post-tool record
- reviewer/date/signature

### Acceptance criterion

An exact payload change provably invalidates prior approval, and no write-like simulated action bypasses the appropriate human gate.

## 14. Signature ablation and E4

**Current project interpretation:** finance/Analyst Desk analogue—critic loop ON/OFF and structured dated evidence versus simpler retrieval representation.  
**Current status: TODO for final model-backed evidence.** A synthetic development E4 exists but is not the final result.

### Steps

1. Freeze cases, model, tools, budget and scoring.
2. Compare critic loop OFF versus ON.
3. Compare structured/table-aware dated evidence versus the declared simpler representation.
4. Run held-out, three repeats, through the same ledger:

   ```bash
   PYTHONPATH=. .venv/bin/python -m evaluation.experiment_ledger launch \
     --experiment E4 --split heldout --repeats 3 \
     --consent-paid --max-paid-calls <APPROVED_LIMIT> --foreground
   ```

5. Report claim/citation support, numeric/source validation, safe abstention, hard failures, usage, median/p95 latency and errors.
6. Discuss whether the critic catches errors worth its added calls. Keep portfolio return as secondary evidence only.

### Acceptance criterion

The report isolates the signature component’s contribution while holding all other experimental conditions fixed.

## 15. Deployment, CI, monitoring and alert minimum bar

**Guideline requirement:** FastAPI streaming; Docker Compose starts app, MCP, vector store, Prometheus and Grafana; versioned prompts/models; evaluation-gated CI; one working alert; clean-machine install and a failed CI record.  
**Current status: PARTIAL.** Assets exist; hosted proof is incomplete.

### Steps

1. Clone the repository on a clean machine or clean VM without copying `.env` or `.venv`.
2. Create a private `.env` from `.env.example`; never record secret values.
3. Start locally with the documented one-command script and verify FastAPI, Streamlit and health endpoints.
4. Run `docker compose up --build` and verify app, MCP services, Prometheus and Grafana.
5. Capture service health and one end-to-end request.
6. In GitHub Actions, run the `workflow_dispatch` option `failure_demo=true`. Preserve the failed run URL and uploaded `ci_intentional_failure.json`; explain that this is an intentional evaluation-gate failure.
7. Trigger the configured alert safely, for example by using a test metric or threshold. Capture the Prometheus condition, Grafana/Alertmanager fired state and recovery.
8. Verify prompts and model IDs come from versioned configuration.
9. Perform a secret scan before submission.

### Evidence to retain

- clean-machine installation log
- Docker service-health screenshot/output
- hosted passing CI URL
- hosted intentionally failed CI URL and explanation
- fired and resolved alert screenshots
- dashboard panels showing calls, latency, errors and outcomes
- secret-scan result

### Acceptance criterion

A reviewer can start the stack from the repository, inspect a failed evaluation gate and see a real alert transition from firing to resolved.

## 16. Final four-experiment reporting protocol

Use one harness and configuration files, not separate code branches.

| Experiment | Question | Fixed comparison | Required primary metrics |
|---|---|---|---|
| E1 | Does the agent team justify its cost? | C0 vs C1 vs C2; same cases/tools/model budget | success, grounding, violations, calls/cost, latency, errors |
| E2 | Do defences work? | model-facing defences OFF/ON; attacks and clean cases | attack success, false blocks, violations, harmful attempts |
| E3 | Did reviewed lessons help? | frozen playbook OFF/ON | held-out success, regressions, lesson cost, applicability |
| E4 | Do signature components help? | critic OFF/ON and evidence representation ablation | citation/source validation, success, cost, latency |

For every configuration:

- repeat the final held-out comparison three times;
- report count and percentage, not percentage alone;
- include failed and timed-out cases;
- report model ID, prompt version, case hash and playbook hash;
- report inference usage/cost, median latency, p95 latency and spread across repeats;
- retain raw rows and traces, not only aggregate charts;
- never select a favourable seed or omit an unfavourable run.

## 17. Submission package

### Required repository artifacts

- [ ] README that starts the system with one command
- [ ] redrawn architecture diagram and numbered walkthrough
- [ ] one-page threat model
- [ ] one-page memory policy
- [ ] final evaluation report, 4–6 pages
- [ ] experiment log with configs, run IDs, failures and negative results
- [ ] three-person contribution log with evidence links and reviewers
- [ ] final slides
- [ ] backup demo recording
- [ ] demo guide and viva questions
- [ ] no API keys, private data or non-redistributable material

### Evaluation-report outline

1. User, problem, scope and honest limitations.
2. Frozen experimental setup and independent label process.
3. Retrieval before/after and judge calibration.
4. E1–E4 tables with three-repeat spread.
5. Failure, timeout and negative-result analysis.
6. Lessons accepted/rejected and memory regression analysis.
7. Security OFF/ON, false blocks and human-control evidence.
8. Deployment, CI, dashboard and alert evidence.

### Contribution log

Each row must contain date, member, concrete contribution, commit/artifact, and independent reviewer. AI tools may assist implementation, but they cannot replace team ownership of framing, labels, evaluation and interpretation.

## 18. Suggested three-person allocation

### Veneet — quantitative trading and evaluation lead

- Independently review golden cases and retrieval labels.
- Own family split, metric recomputation, E1–E4 launch and experiment log.
- Author/review attacks independently of the defence builder.
- Verify backtest arithmetic, costs and interpretation.
- Lead final results and limitations presentation.

### Karthika — agents, RAG and orchestration lead

- Freeze prompts, model/config identities and corpus manifest.
- Produce plan/replan, specialist hand-off, critic and resume traces.
- Generate conditional lesson candidates from development failures.
- Explain RAG citations, MCP calls, budgets and context controls.
- Prepare architecture walkthrough and trace map.

### Mathangi — risk, human control and platform lead

- Verify deterministic risk, exact-payload approval and audit ledgers.
- Run the approval-edit-invalidates demonstration.
- Own security controls, Docker, CI, Prometheus/Grafana and fired alert.
- Independently check policy correctness in held-out labels.
- Produce clean-machine and operational evidence.

### Independence rules

- Karthika must not independently certify final semantic labels for the agent system she tuned.
- Mathangi must not be the sole author and reviewer of attacks against defences she built.
- Veneet’s labels and metric interpretation require Mathangi’s cross-check on disputed policy cases.
- Each person signs only what they personally inspected.

## 19. Final readiness gate

Do not mark the project final-ready until every answer below is **yes**:

1. Are 60+ cases independently reviewed and family-separated?
2. Are held-out labels inaccessible to prompts, tools and memory?
3. Is Recall@5 reported before/after on 30+ reviewed queries?
4. Does every MCP tool have a typed schema, classification and test?
5. Can the team show self-correction, pause/resume and a genuine replan trace?
6. Is memory policy complete, and is E3 memory-off/on measured?
7. Is E1 fair across C0/C1/C2 with fixed tools and budget?
8. Is the judge calibrated on 20+ human labels with Cohen’s kappa?
9. Does E2 report model-level attack success and clean false blocks OFF/ON?
10. Does an exact payload edit invalidate prior approval?
11. Is E4 a controlled signature ablation rather than a synthetic profitability claim?
12. Were final held-out comparisons repeated three times with failures retained?
13. Is there a clean-machine install, hosted failed CI evidence and fired alert?
14. Are report, experiment log, contribution log, slides and recording complete?
15. Can every member redraw the architecture and answer the eight guideline viva questions?

If any answer is no, report it as pending rather than fabricating completion.

## 20. Immediate next actions

1. **Veneet:** independently review the 36 retrieval labels and 60 golden-case expected outcomes.
2. **Mathangi:** cross-check disputed policy labels and prepare the approval, failed-CI and alert demonstrations.
3. **Karthika:** freeze config/corpus/prompt manifests, prepare one replan trace and draft development lesson candidates from completed human-override outcomes.
4. **All:** review and freeze the lesson playbook.
5. **Veneet:** launch E1–E4 held-out runs with three repeats and approved allowance.
6. **All:** interpret results honestly, update the 4–6 page evaluation report, sign contribution entries, finish slides and record the backup demo.

