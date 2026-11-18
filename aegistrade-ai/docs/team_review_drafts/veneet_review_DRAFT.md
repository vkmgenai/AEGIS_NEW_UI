# Veneet: questionnaire answers (LLM DRAFT, not signed)

Prepared 2026-11-14 from runs `20261114T154041-1dd60bf8` and `20261114T153948-3dfe8a63`. Every answer below must be checked and accepted, corrected or rejected by Veneet personally. Items marked PENDING have no evidence yet.

**Must personally verify before signing:** Q3 case decisions, Q8 retrieval relevance, Q9 profitability.

## Question 1

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Two retained runs exist: 20261114T154041-1dd60bf8 (deterministic dev reference) and 20261114T153948-3dfe8a63 (synthetic E4). Case-file hashes are recorded below; both manifests show inputs_sha256 empty because no case file was passed.

**Evidence:** reports/capstone_runs/20261114T154041-1dd60bf8/report.json; reports/capstone_runs/20261114T153948-3dfe8a63/report.json; evaluation/golden/development.jsonl; evaluation/golden/heldout/heldout.jsonl

**Method:** Read manifest.json and report_sha256 for both runs; compared to shasum of report.json (matches: 93b54ff73e3f..., 952e0dd94b58...). Hashed case files: development c3ae84fd0142..., heldout 2d7856767edc....

**Exceptions:** No E1/E3 runs exist; Veneet must re-run shasum locally.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** No

## Question 2

**Status:** PARTIALLY SUPPORTED

**Conclusion:** By the family field there is no overlap: development has 4 families (20 cases), held-out has 8 families (40 cases).

**Evidence:** evaluation/golden/development.jsonl, evaluation/golden/heldout/heldout.jsonl (field: family)

**Method:** Set intersection of family values = empty (LLM-computed; Veneet to repeat).

**Exceptions:** Leakage by content similarity (not just family name) has not been reviewed by a human.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Question 3

**Status:** PENDING

**Conclusion:** No independent case decisions exist. Every case still carries label_origin = seeded_hypothesis_requires_independent_human_verification.

**Evidence:** evaluation/golden/development.jsonl (label_origin)

**Method:** Not performed. Veneet must read policy and expected label for each assigned case before viewing model output, then record ACCEPT/CORRECT/QUARANTINE.

**Exceptions:** The 20 dev correct/20 result in run 20261114T154041-1dd60bf8 only shows code matches the seeded labels.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Question 4

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The synthetic runs state their limits (synthetic data, 2022-01-03 to 2024-05-17, 620 sessions, no real-market claim). Real-data dates, constituent and unadjusted-price limits cannot be checked from these runs.

**Evidence:** reports/capstone_runs/20261114T153948-3dfe8a63/report.json (data_source, synthetic_warning, period, limitation)

**Method:** Read the fields listed.

**Exceptions:** No real-data run is retained; survivorship and corporate-action notes need a real-data dataset manifest.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Question 5

**Status:** PENDING

**Conclusion:** Cannot be answered: no C0/C1/C2 run exists. The golden case files have no symbol/date/evidence for agentic cases.

**Evidence:** None (no E1 manifest)

**Method:** PENDING: required experiment has not been run.

**Exceptions:** Preflight blocked E1: 0 reviewed cases, no agentic case pack.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** No

## Question 6

**Status:** PENDING

**Conclusion:** Cannot be answered: no repetitions of E1 exist. E4 ran with repeats=1.

**Evidence:** reports/capstone_runs/20261114T153948-3dfe8a63/manifest.json (configuration.repeats=1)

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** No

## Question 7

**Status:** PENDING

**Conclusion:** Cannot be answered for E1. Only the deterministic run reports metrics (accuracy 1.0, 20/20, errors []); it has no calls, cost, latency or timeouts.

**Evidence:** reports/capstone_runs/20261114T154041-1dd60bf8/report.json (case_results)

**Method:** Checked count=20, correct=20, accuracy=1.0, errors=[] directly.

**Exceptions:** Latency/cost/timeouts do not apply to a deterministic run.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** No

## Question 8

**Status:** PARTIALLY SUPPORTED

**Conclusion:** 36 retrieval queries exist (meets the 30+ minimum) with relevant_ids, but all labels are author-mapped and unreviewed. Offline before/after: hit@5 0.6944 -> 0.75.

**Evidence:** evaluation/retrieval/queries_36.jsonl; reports/capstone_runs/20261114T154041-1dd60bf8/report.json (retrieval_before, retrieval_after)

**Method:** Read counts and metrics; sha256 of query file e7830f9778c7...

**Exceptions:** label_origin = author_mapped_pending_independent_review. Veneet must judge relevance and add short reasons per query. Neural mode not run.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Question 9

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Run 20261114T153948-3dfe8a63 must not support a profitability claim: it is synthetic data, ROUTER total return 3.28% vs equal-weight benchmark 76.66%, and the report says no real-market or LLM-return claim.

**Evidence:** reports/capstone_runs/20261114T153948-3dfe8a63/report.json (metrics, benchmark, limitation, disclaimer)

**Method:** Compared ROUTER metrics to benchmark.metrics; fee model nse-delivery-screenshot-zero-brokerage-v1, slippage 10 bps.

**Exceptions:** Open-position marks and survivorship/corporate-action limits not reviewed. Recompute at least one trade from ledgers.ROUTER.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Question 10

**Status:** PARTIALLY SUPPORTED

**Conclusion:** In the available evidence the ROUTER ablation trails its buy-and-hold benchmark (3.28% vs 76.66%) and has a 36.09% win rate; this must stay in the report. No C2-vs-C1 underperformance can be named yet.

**Evidence:** reports/capstone_runs/20261114T153948-3dfe8a63/report.json (metrics[ROUTER], benchmark.metrics)

**Method:** Read metrics.

**Exceptions:** Synthetic data; do not generalize.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** No

## Question 11

**Status:** PENDING

**Conclusion:** Cannot decide yet. Recommended provisional state: REJECT/RE-RUN for E1 (not run), not an accept.

**Evidence:** All of the above

**Method:** Pending E1 and independent labels.

**Exceptions:** None noted.

**Reviewer:** Veneet, date: ________

**Independent acceptance required:** Yes: Mathangi

## Final decision (provisional)

REJECT/RE-RUN until the missing experiments exist. This is an evidence finding, not a verdict on the project.
