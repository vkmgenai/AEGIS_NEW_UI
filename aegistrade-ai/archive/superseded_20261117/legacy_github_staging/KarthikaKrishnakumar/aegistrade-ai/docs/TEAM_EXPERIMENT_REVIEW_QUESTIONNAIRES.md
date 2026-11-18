# AegisTrade independent experiment-review packet

Version 1.0 · prepared from the responsibilities recorded in the initial proposal

## Purpose and evidence rule

These forms convert team opinion into attributable review evidence. They do not ask reviewers to make the results look favourable. Each answer must identify the experiment run ID, inspected artifact or trace, decision, reason, reviewer and review date. A reviewer must disclose if they authored or tuned the item being judged. In that case, a different teammate must provide the independent acceptance.

Do not edit a held-out label after seeing model output. If a result exposes a genuine label defect, quarantine the case, document the defect and replace it with a newly independently labelled held-out case. Any result used to tune code, prompts, retrieval or lessons becomes development evidence.

## Evidence packet supplied to every reviewer

- Experiment ledger run ID and immutable run directory under `reports/capstone_runs/`.
- `manifest.json`, `events.jsonl`, `stdout.log`, `stderr.log` and `report.json`.
- Exact case-file copy and SHA-256 when a case file was used.
- Relevant model/tool trajectories, citations and failure records.
- Current architecture, threat model, memory policy and evaluation protocol.
- A response record using `evaluation/team_reviews/review_response_template.json`.

## Veneet — research and evaluation review

Proposal responsibility: dataset and scope; strategies and backtesting; golden-set cases and metrics.

Primary independent-review role: validate research design, labels and statistical interpretation. Veneet should not approve an item he authored without a second reviewer.

1. Which run IDs and case-file hashes did you inspect?
2. Were development and held-out scenario families separated without family leakage? List any contaminated family.
3. For every assigned golden case, is the expected route, block or simulated-broker outcome correct from the written policy and code-visible facts? Record case-level ACCEPT, CORRECT or QUARANTINE decisions.
4. Are dates, constituent assumptions, unadjusted-price limitations and point-in-time evidence boundaries stated correctly?
5. Did C0, C1 and C2 receive the same locked cases and, for C1/C2, the same available tools, model and ceiling? Identify every fairness difference.
6. Were three repetitions completed without selecting the best repetition? Report the range and failures, not only the mean.
7. Do the reported success rate, violations, calls/cost, median latency, p95 latency, timeouts and error counts recompute from the ledger?
8. Are retrieval relevance labels independently defensible? Review at least 30 queries and record relevant passage IDs plus short reasons.
9. Does any profitability statement exceed the evidence? Check fees, slippage, open-position marks, benchmark exposure and survivorship/corporate-action limits.
10. Which negative result or C2-underperformance must remain in the final report?
11. Final decision: ACCEPT FOR FINAL EVIDENCE, ACCEPT WITH LIMITATIONS, or REJECT/RE-RUN. Why?

Required outputs: reviewed golden/retrieval labels, metric recomputation sheet, signed experiment decision and dated contribution entry.

## Karthika — agents and intelligence review

Proposal responsibility: RAG retrieval; MCP tools and LangGraph; routing and improvement loop.

Primary review role: provide trace explanations and implementation provenance. Because this is Karthika's primary subsystem, another teammate must independently accept semantic-quality and grounding labels.

1. Which run IDs, prompt version, corpus hash, backend/model ID and lesson version did you inspect?
2. Does each C1/C2 trajectory use only the declared read tools and stay within call, tool, output and context budgets?
3. For each assigned output, do citations point to evidence actually observed before the historical cutoff? Identify unsupported, wrong-source or wrong-date claims.
4. Did the market, strategy and critic typed hand-offs agree with the locked code route and research purpose?
5. Did the critic independently observe required evidence, or merely repeat the strategy conclusion?
6. Retain one successful contradiction/correction trace. What failed validation, what replanned, and why was the corrected result acceptable?
7. For blocked cases, distinguish legitimate adverse/insufficient evidence from provider, schema, budget or context failures.
8. Did bounded dated-web fallback add only eligible historical sources and preserve source dates/hashes?
9. For memory-on runs, which lesson IDs were retrieved, were their preconditions applicable, and did any lesson worsen a held-out result?
10. Was every accepted lesson produced only from development evidence, human reviewed and frozen before held-out execution?
11. What does C2 improve over C1, and where does the extra specialist/critic cost fail to provide value?
12. Final implementation statement: which claims are proven by code/tests, which are supported by actual runs, and which remain unmeasured?

Required outputs: trace map, citation/grounding exceptions, replan example, memory applicability record and dated contribution entry. Independent acceptance must come from Veneet or Mathangi.

## Mathangi — safety and platform review

Proposal responsibility: risk policy and approvals; mock broker and audit trail; UI, security and deployment.

Primary independent-review role: validate controls, security outcomes and operational evidence. Mathangi should not independently certify controls she authored without a second reviewer.

1. Which E2, clean-case, approval and deployment run IDs did you inspect?
2. For all 32 attacks, what was the authored success condition and did the model attempt a forbidden tool or emit forbidden content with defences off/on?
3. For the ten clean cases, how many legitimate requests were falsely blocked with defences off/on?
4. Confirm that hard permissions, typed validation and broker isolation stayed enabled during the model-facing security ablation.
5. Demonstrate approve, edit and reject. Did edit invalidate the prior payload hash and require a new approval?
6. Demonstrate stale quote, changed evidence, duplicate request and timeout/reconciliation behaviour. Did each fail closed or recover idempotently?
7. Recompute one order's whole-share size, fixed fees, slippage, stop, target and cash effect from the ledger.
8. Can an LLM call a broker-write tool, change a risk limit, suppress a stop or bypass the human gate? Cite the enforcing code/test evidence.
9. Does a stopped/restarted background experiment preserve status, stdout/stderr, result and exact input hash in the experiment ledger?
10. Provide hosted failed-CI evidence: branch/commit, failed check, failure cause, correction and passing main result.
11. Provide a fired-alert demonstration: rule, controlled trigger, pending/firing screenshot or export, acknowledgement and restored threshold.
12. Final decision: ACCEPT FOR FINAL EVIDENCE, ACCEPT WITH LIMITATIONS, or REJECT/RE-RUN. Why?

Required outputs: E2/clean labels, approval/control checklist, ledger replay check, hosted-CI record, fired-alert record and dated contribution entry.

## Cross-review and sign-off matrix

| Evidence | Preparer | Independent reviewer | Required final artifact |
|---|---|---|---|
| Golden cases, retrieval labels and metric interpretation | Veneet | Mathangi | Reviewed label file + rationale |
| RAG, agent trajectories, citations and memory | Karthika | Veneet | Trace/citation review + E1/E3 decision |
| Security cases, approval, ledger and deployment | Mathangi | Veneet | E2/control/operations record |
| Judge-calibration human labels | Veneet and Mathangi independently | Resolve disagreements before judge run | 20+ human labels, provenance and Cohen's kappa |
| Final experiment conclusions | All three | All three sign | Final evaluation report |

## When the minimum-bar gap can be marked closed

Questionnaire completion alone is insufficient. Close an item only when the signed response identifies a completed ledger run and its artifacts. The final review still separately requires three held-out repetitions, different-family judge calibration, E2/E3/E4 ablations, contribution entries, slides/video, hosted failed-CI evidence and a fired-alert demonstration.
