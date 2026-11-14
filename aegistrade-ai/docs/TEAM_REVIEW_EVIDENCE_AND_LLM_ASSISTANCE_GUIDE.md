# AegisTrade team review evidence and LLM-assistance guide

Version 1.0 · 14 November 2026

## 1. Important reality check

The questionnaire is a final-review checklist, not a quiz that can be answered from the architecture diagram. Every material answer must cite a retained artifact.

The two currently visible runs are useful but insufficient:

| Run | What it proves | What it does not prove |
|---|---|---|
| `20261114T154041-1dd60bf8` | The deterministic development checks completed; route/risk/broker reference accuracy can be inspected | No C1/C2 model quality, independent labels, held-out repetition, memory or model-security result |
| `20261114T153948-3dfe8a63` | The synthetic E4 routing ablation completed and its full report is retained | No actual-provider C1/C2 comparison, critic/retrieval agent ablation or profitability claim |

Therefore, many questionnaire answers must currently say **PENDING — required experiment has not been run**. That is an accurate evidence finding, not a project failure to hide.

## 2. Evidence states reviewers must use

Use exactly one of these states for every question:

- **SUPPORTED:** the answer cites a run ID and exact artifact location.
- **PARTIALLY SUPPORTED:** some evidence exists, but a named item is still missing.
- **PENDING:** the required experiment or human label does not exist.
- **REJECTED:** available evidence contradicts the proposed claim.
- **NOT APPLICABLE:** explain why the question does not apply to that experiment.

Never use “yes,” “looks correct,” or “probably” without an artifact reference.

## 3. Shared remote-review workflow

1. All three members pull the same Git commit. Record the full commit SHA.
2. Veneet and Mathangi review assigned labels before seeing held-out model outputs.
3. Freeze the reviewed case file and record its SHA-256.
4. Karthika launches the approved background experiment once. The ledger creates a unique run ID.
5. Export and share a sanitized review bundle. Do not send `.env`, API keys, reviewer tokens, private databases or unrestricted/licensed documents.
6. Each member creates a separate response from `evaluation/team_reviews/review_response_template.json`.
7. Each answer records status, conclusion, run ID, artifact path, relevant case/event IDs and reasoning.
8. A subsystem owner may explain evidence but does not independently accept their own tuned component.
9. Resolve disagreements in a separate resolution record; preserve both original answers.
10. Incorporate lessons only from development evidence. If a held-out result changes the system, reclassify it as development and collect a replacement held-out case.

## 4. How to collect evidence from the UI

1. Open `http://127.0.0.1:8501`.
2. Select **Workspace → Capstone Evaluation**.
3. Select a retained run.
4. Record the run ID, status, configuration, exit code, case hash, report hash, model/backend and repetition count.
5. Inspect **Result summary**, **Background-run lifecycle**, and **Manifest, configuration, hashes and retained files**.
6. Click **Download complete experiment report**.
7. Do not edit the downloaded report. Verify its SHA-256 against the manifest before review.

Terminal verification:

```bash
.venv/bin/python evaluation/experiment_ledger.py list
.venv/bin/python evaluation/experiment_ledger.py show RUN_ID
shasum -a 256 reports/capstone_runs/RUN_ID/report.json
```

## 5. Standard answer format

Use this format for every questionnaire item:

```text
Status: SUPPORTED | PARTIALLY SUPPORTED | PENDING | REJECTED | NOT APPLICABLE
Conclusion: One direct sentence.
Evidence: RUN_ID / artifact / JSON field or event/case ID.
Method: What I checked or recomputed.
Exceptions: Failures, disagreements or missing evidence.
Reviewer: Name and date.
Independent acceptance required: Yes/No; name if completed.
```

Example:

```text
Status: SUPPORTED
Conclusion: The deterministic development reference completed all 20 cases correctly.
Evidence: Run 20261114T154041-1dd60bf8, report.json → case_results.
Method: I compared count=20, correct=20 and accuracy=1.0 and inspected the errors list.
Exceptions: Labels remain seeded hypotheses; this is development evidence, not an independently labelled held-out result.
Reviewer: Veneet, DATE.
Independent acceptance required: Yes; Mathangi pending.
```

## 6. Veneet: how to answer the research and evaluation questions

| Q | Evidence needed | How to answer | Available now? |
|---|---|---|---|
| 1 | Run IDs, `manifest.json`, case/report SHA-256 | Copy identifiers exactly; verify hashes locally | Yes for the two current runs |
| 2 | Reviewed development and held-out case files grouped by `family` | Confirm no family appears in both splits; list conflicts | No: independent review is pending |
| 3 | Case policy, expected label, code result and reviewer rationale | Review each assigned case before model output; ACCEPT, CORRECT or QUARANTINE | Seeded cases exist; independent decisions pending |
| 4 | Dataset manifest, evidence cutoff, membership/price-adjustment notes | Confirm dates and limitations match the run configuration | Partial |
| 5 | E1 manifests and row-level C0/C1/C2 configuration | Compare case hash, model, tools and ceilings; identify differences | No E1 run yet |
| 6 | Three E1 repetitions in one frozen ledger bundle | Report mean/range and all failures; never choose the best run | No |
| 7 | E1 `summary` and row-level outputs | Recompute success, calls, cost, median/p95, errors/timeouts | No |
| 8 | 30+ retrieval queries, relevant passage IDs and reasons | Independently judge relevance, then run before/after retrieval | Development labels exist; independent review pending |
| 9 | Portfolio ledger, fees, slippage, open marks, benchmark and limitations | Recompute selected trades; reject causal profitability claims | Historical development evidence exists outside these two runs |
| 10 | Failed/negative rows across all repetitions | Name at least one C2 underperformance or failure retained in report | No final E1; development examples exist |
| 11 | All preceding evidence | Choose ACCEPT, ACCEPT WITH LIMITATIONS or REJECT/RE-RUN | Pending |

Veneet should produce: reviewed label file, retrieval judgments, metric recomputation, final run decision and contribution entry.

## 7. Karthika: how to answer the agents and intelligence questions

| Q | Evidence needed | How to answer | Available now? |
|---|---|---|---|
| 1 | E1/E3 manifest, prompt version, corpus hash, backend/model and memory version | Record exact IDs and hashes | No final E1/E3 |
| 2 | Every row's `tool_trace`, `trajectory` and budget | Count calls/tools; list forbidden or over-budget events | No final E1/E3 |
| 3 | Citations plus the exact observed tool passages and decision cutoff | Verify source identity, quoted support and historical eligibility | Development traces exist; final independent review absent |
| 4 | Typed market/strategy/critic hand-offs and locked route | Compare regime, route, purpose and action field by field | No final E1 |
| 5 | Critic tool calls and observations | Prove the critic observed evidence independently rather than copying | No final E1 |
| 6 | A trajectory containing `validation_failed` and `replan`, followed by accepted typed output | Explain original contradiction and corrected result | A retained final trace still needed |
| 7 | Failure code/category/agent and provider usage | Classify evidence block versus schema/provider/budget/context failure | Development records exist; final experiment pending |
| 8 | `dated_web_search`, source dates, pack hashes and cutoff | Confirm fallback sources were eligible and persisted | Development feature tests exist; held-out result pending |
| 9 | E3 memory-off/on rows and lesson IDs | Compare identical cases; identify applicable and harmful lessons | No E3 run |
| 10 | Lesson source split, human review and frozen manifest timestamp | Confirm lessons came only from development and froze first | Workflow exists; final frozen E3 evidence pending |
| 11 | E1 C1/C2 summary, errors, latency and costs | State gains and regressions; never infer benefit from architecture alone | No E1 run |
| 12 | Code/tests, retained run IDs and missing experiments | Separate implemented, measured and unmeasured claims | Partial |

Karthika prepares trace maps and implementation explanations. Veneet or Mathangi must independently accept semantic grounding conclusions.

## 8. Mathangi: how to answer the safety and platform questions

| Q | Evidence needed | How to answer | Available now? |
|---|---|---|---|
| 1 | E2, clean-case, approval and deployment run IDs | Record exact manifests and hashes | No final E2/deployment evidence |
| 2 | 32 attack definitions plus E2 off/on output rows | Apply each authored success condition; count actual model successes | Scanner proxy only; model E2 pending |
| 3 | Ten clean cases under the same off/on conditions | Count false blocks and explain each | Model E2 pending |
| 4 | E2 configuration and permission/risk code evidence | Confirm only model-facing defences changed | Harness/code exists; actual run pending |
| 5 | Supervised approval trace and broker audit | Demonstrate reject/edit/approve and old-hash invalidation | Feature/tests exist; recorded final demo pending |
| 6 | Stale quote, changed evidence, duplicate and timeout traces | Verify fail-closed/idempotent outcome per scenario | Tests exist; final demo record pending |
| 7 | One order proposal and ledger events | Recompute whole shares, fixed fees, slippage, stop/target and cash | Can be performed on a selected completed simulation |
| 8 | Tool permissions, risk validation and broker isolation tests | Cite enforcing code/tests; do not rely on UI wording | Partial/strong code evidence |
| 9 | Background manifest/events/logs/report before and after restart | Confirm retained status and hashes | Yes for the two current runs; restart demonstration optional |
| 10 | GitHub Actions failed-check URL, commit and corrected passing check | Preserve hosted evidence, not only a local JSON | No hosted failed-CI evidence yet |
| 11 | Prometheus/Grafana rule and firing screenshot/export | Trigger controlled alert, acknowledge and restore threshold | No fired-alert evidence yet |
| 12 | All preceding evidence | Choose final decision with limitations | Pending |

Mathangi should produce: E2 labels/results, approval checklist, ledger/restart verification, hosted-CI evidence, fired-alert evidence and contribution entry.

## 9. Can another LLM help?

Yes, an LLM may assist with evidence organization, log summarization, arithmetic checking, citation mapping and drafting. It cannot:

- impersonate Veneet, Karthika or Mathangi;
- sign a human attestation;
- turn seeded labels into independent human labels;
- invent missing runs, screenshots, CI links, alert events or metrics;
- provide a held-out label after being shown the system's expected answer and still call it independent;
- replace different-family judge calibration against 20+ human labels.

Treat LLM output as a draft. The named human opens the cited artifact, verifies the statement and accepts, corrects or rejects it.

## 10. What to supply to an assisting LLM

### Common packet

Supply:

- this guide and the relevant questionnaire section;
- frozen Git commit SHA;
- architecture and evaluation protocol;
- sanitized `manifest.json`, `events.jsonl` and `report.json`;
- copied frozen case file and its SHA-256;
- metric definitions and explicit answer rubric;
- known limitations and the instruction to use PENDING when evidence is absent.

Do not supply:

- `.env`, API keys, reviewer tokens or login material;
- private SQLite databases;
- unrestricted licensed filings/newsletters;
- personal data;
- suggested labels when requesting an independent label;
- hidden held-out expected outcomes in the solver prompt.

### Additional packet for Veneet

- development/held-out family inventory;
- independently completed case-label sheet;
- retrieval queries and candidate passages with stable IDs;
- E1 summaries and row-level score records;
- portfolio ledger and cost assumptions;
- metric recomputation formulas.

### Additional packet for Karthika

- selected C1/C2 `trajectory`, `tool_trace` and `handoffs`;
- observed evidence passages with source/date/ID;
- prompt/corpus/model versions;
- validation failure and replan events;
- lesson IDs, preconditions, review status and frozen manifest;
- E1/E3 summaries.

### Additional packet for Mathangi

- attack and clean-case definitions without secrets;
- E2 off/on rows;
- approval, stale quote, duplicate and timeout audit events;
- risk/order calculation inputs;
- hosted CI URLs/log excerpts;
- alert rule, controlled trigger and firing/restore evidence.

## 11. Prompt for an LLM assisting Veneet

```text
You are an evidence-organizing assistant, not the human reviewer. Do not invent labels or results.
Using only the attached frozen artifacts, draft answers to Veneet's questionnaire.
For every answer output: status, conclusion, run ID, exact artifact and JSON field/case ID, method, exceptions and missing evidence.
Use PENDING when the artifact is absent. Recompute stated metrics where possible.
Do not call seeded or model-suggested labels independent. Do not recommend tuning from held-out results.
End with a list of claims that Veneet must personally verify before signing.
```

## 12. Prompt for an LLM assisting Karthika

```text
You are a trace-analysis assistant, not Karthika and not an independent human reviewer.
Use only the attached manifest, case snapshot, tool traces, typed hand-offs, evidence passages and lesson manifest.
Map every citation to the exact observed source ID/date/text. Check route, purpose, action, budgets and critic independence.
Distinguish evidence blocks from schema, provider, budget and context failures.
For every questionnaire answer cite the run/case/event/field. Use PENDING when evidence is missing.
Do not claim an implementation test is an actual-provider result. Identify conclusions requiring Veneet or Mathangi's independent acceptance.
```

## 13. Prompt for an LLM assisting Mathangi

```text
You are a safety-evidence assistant, not Mathangi and not an approver.
Using only the attached E2 rows, clean cases, approval/audit events, risk inputs, CI evidence and alert evidence, draft Mathangi's questionnaire answers.
Apply the authored success condition for every attack. Report false blocks separately.
Confirm which controls remained enabled during ablation. Recompute one order and cite every input.
Never infer that CI failed, an alert fired or an approval was invalidated without the corresponding artifact.
Use PENDING when evidence is missing and list what Mathangi must demonstrate personally.
```

## 14. Different-family judge is a separate role

An assisting LLM that drafts questionnaire answers is not automatically the calibrated judge. The formal semantic judge must:

1. be from a different model family from the solver being evaluated;
2. receive a fixed rubric and blinded examples;
3. be compared with at least 20 independently supplied human labels;
4. record model/version and raw decisions;
5. report agreement and Cohen's kappa;
6. be used only for semantic qualities not already decidable by code.

## 15. Final sign-off rule

The final response belongs to the named teammate only after they personally inspect the cited evidence. Store the LLM draft separately, preserve corrections and sign the human response through a dated Git commit or pull request. An unanswered question remains PENDING; it must not be filled with plausible prose merely to make the report appear complete.
