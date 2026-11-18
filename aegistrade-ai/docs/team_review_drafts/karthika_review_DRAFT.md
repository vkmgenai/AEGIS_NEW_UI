# Karthika: questionnaire answers (LLM DRAFT, not signed)

Prepared 2026-11-14 from runs `20261114T154041-1dd60bf8` and `20261114T153948-3dfe8a63`. Every answer below must be checked and accepted, corrected or rejected by Karthika personally. Items marked PENDING have no evidence yet.

**Must personally verify before signing:** Q3 citations, Q6 replan.

## Question 1

**Status:** PENDING

**Conclusion:** No E1/E3 run exists, so there is no actual-provider prompt version, corpus hash, model ID or lesson version to inspect. Preflight reported backend Codex CLI, model pinned.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** Record exact IDs once E1/E3 run.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** No

## Question 2

**Status:** PENDING

**Conclusion:** No C1/C2 trajectories retained.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** No

## Question 3

**Status:** PENDING

**Conclusion:** No final-run citations to check. Development traces exist from earlier work.

**Evidence:** reports/c2_decision_quality_audit_20261111.json (development only)

**Method:** PENDING: required experiment has not been run. Development traces can be used as examples but not as final evidence.

**Exceptions:** Citation-to-passage mapping requires observed passages with source/date.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 4

**Status:** PENDING

**Conclusion:** No typed hand-offs in a retained final run.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 5

**Status:** PENDING

**Conclusion:** No critic traces retained in a final run.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 6

**Status:** PENDING

**Conclusion:** A final contradiction/replan trace is not retained. Check development artifacts (e.g. reports/c2_*.json) for a candidate, then re-capture in E1.

**Evidence:** reports/c2_materiality_context_verification_20261111.json (candidate only)

**Method:** Not verified; I did not open the candidate traces in this draft.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 7

**Status:** PENDING

**Conclusion:** No final E1 failure records.

**Evidence:** reports/context_budget_fix_20261112.json, reports/codex_timeout_diagnosis_20261111.json (development)

**Method:** PENDING: required experiment has not been run.

**Exceptions:** Development files show past provider/context issues; classify after E1.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** No

## Question 8

**Status:** PENDING

**Conclusion:** Feature and tests exist (reports/dated_web_fallback_verification_20261112.json), but no held-out result.

**Evidence:** reports/dated_web_fallback_verification_20261112.json

**Method:** Not reviewed in this draft.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 9

**Status:** PENDING

**Conclusion:** No E3 run, no lesson IDs.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** No

## Question 10

**Status:** PENDING

**Conclusion:** Cannot confirm. The workflow exists but no frozen lesson manifest with timestamp is retained.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 11

**Status:** PENDING

**Conclusion:** Cannot state what C2 improves over C1: no E1 run. Do not infer from architecture.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Question 12

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Proven by code/tests: the 348-test suite passed on commit a636e56 (per earlier session report). Supported by actual runs: only the two deterministic/synthetic runs. Unmeasured: all C1/C2 quality, memory (E3), critic/retrieval agent ablation (E4 agent-level), model security (E2).

**Evidence:** tests/; reports/capstone_runs/20261114T154041-1dd60bf8/report.json; reports/capstone_runs/20261114T153948-3dfe8a63/report.json

**Method:** Compared claims to retained run IDs.

**Exceptions:** Test pass count is from the earlier session, not re-run here.

**Reviewer:** Karthika, date: ________

**Independent acceptance required:** Yes: Veneet or Mathangi

## Final decision (provisional)

REJECT/RE-RUN until the missing experiments exist. This is an evidence finding, not a verdict on the project.
