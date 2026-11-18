# Evidence-quality review of the three questionnaire drafts

Review date: 17 November 2026  
Scope: the Markdown and Word drafts in this folder, checked against the retained packet and local run artifacts.  
Preservation rule: the original reviewer drafts were not edited.

## Executive verdict

The drafts are useful, unusually candid evidence maps. They correctly preserve negative results and use `PENDING` rather than inventing missing runs. They may be retained as **LLM-assisted pre-review drafts** and later corrected/signed by the named people.

They are **not yet independent human evidence** and **cannot yet be used as input to E1/E2/E3** because:

1. every reviewer/date/signature line is blank;
2. the drafter had already seen observed results, so the drafts are not blinded labels;
3. the present golden fixtures do not match the paid experiment harness schema;
4. the security set contains only 16 distinct payloads repeated twice, and is not an executable E2 case set;
5. E3 has no reviewed frozen playbook;
6. no different-family judge decisions or human calibration labels exist.

## Status inventory

| Draft | Supported | Partially supported | Pending | Overall use now |
|---|---:|---:|---:|---|
| Karthika, 12 questions | 1 | 9 | 2 | Trace-analysis draft; requires citation review, current-version rerun and independent semantic acceptance |
| Mathangi, 12 questions | 1 | 6 | 5 | Safety gap checklist; E2, approval/fault demos, hosted CI and alert remain absent |
| Vineet, 11 questions | 3 | 5 | 3 | Metric/research draft; independent golden/retrieval labels and repeated E1 remain absent |

## Facts independently recomputed during this review

- Both retained capstone report hashes match their manifests:
  - E4 `20261117T105811-138ef587`: `7e43ced6b0e815e6bca519e15f2cf05064bb567e1e20220f6b2e935bfa0c9451`.
  - Neural deterministic `20261117T110205-1c7df087`: `c93f0fb469186cfe6b8c4bcdb6ef8a10478ab6cb2ad51cb7553195ee2fed7a11`.
- The three-case AI experiment contains C0/C1/C2 over the same case IDs. C1 used 8 model calls and 14 tool calls; C2 used 16 model calls and 17 tool calls. Each had two guard-passing rows and one recorded model error.
- The C2 portfolio extract contains 104 decisions with the action counts stated in Karthika Q7. Its ledger has 42 events, of which 20 carry a human-override ID/marker. The human-override audit list contains 72 review events.
- The 32 security rows contain only 16 distinct `(path, payload)` pairs: ATT-017 through ATT-032 duplicate ATT-001 through ATT-016.
- The deterministic candidate golden set has four development families and eight held-out families with no exact family-name overlap. It is nevertheless only 12 distinct checks expanded into five variants each.

## Corrections required in Karthika's draft

1. **Q2 remains PARTIALLY SUPPORTED.** Calls and tool names were recomputed, but context packing and every output-token ceiling were not independently recomputed.
2. **Q3 cannot be finalized.** Citation IDs were listed, but exact cited text, source identity, publication/filing date and cutoff eligibility were not mapped for every result.
3. **Q5 cannot establish semantic independence.** Separate critic tool calls prove procedural separation, not independent reasoning quality.
4. **Q6 should be PARTIALLY SUPPORTED, not fully supported.** The validation-failure and replan events exist, but the rejected first payload is not retained and corrected citations have not been independently checked.
5. **Q7 needs an explicit metric note.** `model_error_count` currently combines a genuine route conflict with a fail-closed C2 evidence block. The final report must separate transport/schema failures, policy conflicts and intended evidence blocks.
6. **Q11 is only development evidence.** Equal 2/3 guard-pass counts do not establish equal research quality; the C2 evidence block may be correct. A calibrated semantic review is required.
7. Prompt v15/corpus 86 versus current prompt v16/corpus 87 is a valid configuration mismatch. Do not combine those rows into a final comparison.

## Corrections required in Mathangi's draft

1. **Q2 correctly found the duplicate attacks.** The final minimum-bar claim must say 16 distinct attacks, not 32, until 16 genuinely different cases are added and independently reviewed.
2. **Q2 and Q3 cannot count as blinded labels.** The draft was prepared after opening results and must remain an assistance draft.
3. **Q4 and Q8 are code evidence, not E2 outcome evidence.** They can support the control design section, not close the model-security experiment.
4. **Q7 should be PARTIALLY SUPPORTED.** Quantity and fee arithmetic match, but equity at the signal, raw open before slippage, ATR-derived stop, target and trailing state were not all independently reconstructed.
5. **Q9 correctly identifies missing input hashes and restart evidence.** A completed background lifecycle alone does not prove restart recovery.
6. Hosted failed-CI and fired-alert evidence remain genuinely pending; the local intentional failure must not be relabelled as hosted evidence.

## Corrections required in Vineet's draft

1. **Q1 supports artifact integrity only.** It does not establish independent label validity because both manifests have empty `inputs_sha256`.
2. **Q2 is accurate but exposes a weak case design.** The set has no exact family leakage, yet five variants repeat each deterministic mechanism and are not agentic historical research cases.
3. **Q3 and Q8 remain pending independent human work.** The LLM drafts cannot be signed unchanged merely because they appear plausible.
4. **Q5 fairness wording should be precise.** C1 and C2 used the same case IDs, model and top-level ceilings. Their available tool union is comparable, while C2 intentionally partitions tools by role; this is an architectural treatment, not automatically an unfairness.
5. **Q7 arithmetic is supported for the three-case run.** Keep the limitation that a fail-closed evidence block is counted in `model_error_count`.
6. **Q9 and Q10 correctly preserve negative results.** They are appropriate for the final limitations section after human verification.

## Compatibility with later experiments

### Current golden files

`evaluation/golden/development.jsonl` and `evaluation/golden/heldout/heldout.jsonl` contain records such as:

```json
{"kind":"route","input":{"regime":"TREND","variant":0},"expected":"EMA_TREND"}
```

The paid harness validates each input as `CaseEvidence`, which requires at minimum symbol, ISO date, regime, Close, RSI14, ADX14, EMA20, EMA50 and ATR14. It also expects an `expected` object with a strategy and optional blocked state. Therefore the existing deterministic fixtures cannot be supplied to paid E1/E2/E3 even after signing.

### Current attack and clean files

These contain scanner payloads, not full historical research cases with `tool_overrides`, agent inputs and authored unsafe-outcome conditions. They are suitable for the deterministic scanner proxy only. They cannot produce the required model-level E2 defence-off/on comparison.

### Questionnaire use

The signed questionnaires can later be used for:

- configuration and trace-review provenance;
- artifact-integrity verification;
- independent interpretation of metrics and limitations;
- post-run acceptance or rejection decisions;
- contribution records for the final report.

They cannot replace:

- independently authored and frozen executable case files;
- human expected labels and attack-success conditions;
- raw E1/E2/E3 results;
- different-family judge outputs and calibration;
- hosted CI and fired-alert operational evidence.

## Required next artifacts before paid experiments

1. Create 20 development and at least 40 held-out **agentic CaseEvidence cases**, grouped by scenario family, with point-in-time company evidence already prepared.
2. Have Vineet/Mathangi label them independently before seeing model results; store reviewer, timestamp and rationale.
3. Create at least 32 **distinct executable E2 cases**, plus clean near-miss cases, with `tool_overrides` and explicit attack-success definitions.
4. Resolve the active prompt/corpus version and freeze their hashes.
5. Review at least one accepted and one rejected development lesson, then freeze a playbook for E3.
6. Produce two separate human judge-calibration files from Vineet and Mathangi, reconcile disagreements, then run a genuinely different-family judge.
7. Only after those steps launch E1 development, E2, E3 and three untouched held-out repetitions.

## Final decision

**ACCEPT AS DRAFT REVIEW MATERIAL WITH CORRECTIONS. DO NOT USE AS FINAL INDEPENDENT EVIDENCE OR AS PAID-EXPERIMENT INPUT YET.**

