# Mathangi: questionnaire answers (LLM DRAFT, not signed)

Prepared 2026-11-14 from runs `20261114T154041-1dd60bf8` and `20261114T153948-3dfe8a63`. Every answer below must be checked and accepted, corrected or rejected by Mathangi personally. Items marked PENDING have no evidence yet.

**Must personally verify before signing:** Q5-6 demos, Q7 recompute, Q10-11 hosted evidence.

## Question 1

**Status:** PENDING

**Conclusion:** Only 20261114T154041-1dd60bf8 and 20261114T153948-3dfe8a63 exist; there is no E2, approval or deployment run.

**Evidence:** None

**Method:** PENDING: required experiment has not been run.

**Exceptions:** None noted.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** No

## Question 2

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Scanner proxy only: 32 attacks, scanner_detection_rate 0.938 (about 30 of 32 detected). Model attack success is None; no E2 off/on run.

**Evidence:** reports/capstone_runs/20261114T154041-1dd60bf8/report.json (security); evaluation/redteam/attacks_32.jsonl

**Method:** Read security fields. Attack sha256 af25825a0c41...

**Exceptions:** All attacks have review_status = pending_independent_attack_validation. Which attacks the scanner missed has not been listed.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 3

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Scanner proxy only: false_blocks = 0 of 10 clean cases. Model off/on false blocks not measured.

**Evidence:** reports/capstone_runs/20261114T154041-1dd60bf8/report.json (security.false_blocks, clean_total); evaluation/redteam/clean_10.jsonl

**Method:** Read fields.

**Exceptions:** Not an E2 model result.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 4

**Status:** PENDING

**Conclusion:** Cannot confirm from retained runs; E2 has not run.

**Evidence:** code and tests (app/, tests/test_safety.py)

**Method:** Mathangi must inspect the E2 harness config once it exists.

**Exceptions:** None noted.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 5

**Status:** PENDING

**Conclusion:** No recorded demonstration of approve/edit/reject. Tests reference payload_hash (tests/test_workflow.py, tests/test_safety.py), but a recorded trace is missing.

**Evidence:** tests/test_workflow.py, tests/test_safety.py

**Method:** Not executed in this draft.

**Exceptions:** Mathangi must perform and record the demo with audit event IDs.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 6

**Status:** PENDING

**Conclusion:** No recorded stale-quote, changed-evidence, duplicate or timeout demo.

**Evidence:** tests/

**Method:** Not executed.

**Exceptions:** None noted.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 7

**Status:** PARTIALLY SUPPORTED

**Conclusion:** A selectable order exists in the E4 ledger: ROUTER BUY ICICIBANK 2022-03-29, qty 92 at 434.194, fee 47.4319, initial_stop 416.9864. Fee matches qty*price*11.874 bps (39,946.8 * 0.0011874 = 47.43). Whole-share size is explained by the 20% position cap: floor(equity x 0.20 / entry) = 92 shares (39,947 is about 20% of 199,7xx equity), so the 1% risk size (about 116 shares) was not binding.

**Evidence:** reports/capstone_runs/20261114T153948-3dfe8a63/report.json (ledgers.ROUTER[0], settings.risk_percent, settings.initial_capital)

**Method:** Hand-computed fee and risk quantity from the report.

**Exceptions:** The cap explanation should be confirmed against the portfolio equity on that date. Slippage, target and cash effect not recomputed.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 8

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Enforcement is claimed in code/tests, but I did not read those files in this draft.

**Evidence:** tests/test_safety.py, app/

**Method:** Not verified.

**Exceptions:** Mathangi must cite specific test names and code lines.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Question 9

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Both runs retain manifest, events (queued, launched, started, finished), stdout/stderr, report; report_sha256 in each manifest matches shasum of report.json. No restart demonstration was done.

**Evidence:** reports/capstone_runs/20261114T154041-1dd60bf8/; reports/capstone_runs/20261114T153948-3dfe8a63/

**Method:** Compared hashes (match).

**Exceptions:** inputs_sha256 is empty for both because no case file was supplied.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** No

## Question 10

**Status:** PENDING

**Conclusion:** No hosted failed-CI evidence. reports/ci_intentional_failure_local.json is local only. Workflow file is .github/workflows/ci.yml.

**Evidence:** None hosted

**Method:** PENDING: required experiment has not been run.

**Exceptions:** Needs GitHub Actions URL, failed check and later passing run.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** No

## Question 11

**Status:** PENDING

**Conclusion:** No fired-alert evidence. Rules exist in monitoring/alerts.yml.

**Evidence:** monitoring/alerts.yml

**Method:** PENDING: required experiment has not been run.

**Exceptions:** Needs Prometheus/Grafana firing screenshot/export.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** No

## Question 12

**Status:** PENDING

**Conclusion:** Cannot decide. Provisional: REJECT/RE-RUN until E2, hosted CI and fired alert exist.

**Evidence:** All of the above

**Method:** Pending.

**Exceptions:** None noted.

**Reviewer:** Mathangi, date: ________

**Independent acceptance required:** Yes: Veneet

## Final decision (provisional)

REJECT/RE-RUN until the missing experiments exist. This is an evidence finding, not a verdict on the project.
