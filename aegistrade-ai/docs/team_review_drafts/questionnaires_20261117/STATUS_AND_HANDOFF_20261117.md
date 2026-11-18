# Questionnaire status and reviewer handoff (17 November 2026)

## 1. Status of the three questionnaires

The Word files carry each person's own name and date (17 November 2026). They are kept as limited acknowledgements of the commentary. They are not final approvals: each file still describes itself as an LLM draft and has no final attestation or decision.

| Person | Questions still PENDING | Needs independent acceptance from |
|---|---|---|
| Karthika | Q9, Q10 | Vineet or Mathangi: Q2, Q3, Q5, Q10, Q11 |
| Mathangi | Q5, Q6, Q10, Q11, Q12 | Vineet: Q2 to Q4, Q8 |
| Vineet | Q3, Q6, Q11 | Mathangi: Q2 |

Final decision: not yet given by anyone. Provisional in each draft: REJECT/RE-RUN. To finish, each person replaces the draft banner with a final decision (ACCEPT FOR FINAL EVIDENCE, ACCEPT WITH LIMITATIONS or REJECT/RE-RUN) and signs the attestation.

I did not edit the Word files, because they now contain the reviewers' own edits and Karthika's copy was open in Word.

## 2. The executable review files are still blocked

Folder: `evaluation/agentic_candidates_20261117/`. All 102 records have blank reviewers, `REVIEW_REQUIRED` and `independently_reviewed: false`. This is correct. The flag is set to true only by the named reviewer, after they have personally filled in the expected result and rationale. E1/E2/E3 must not launch until the checker passes.

Check with:

```bash
python evaluation/validate_agentic_review.py
```

It exits 0 only when every record has a reviewer, time, rationale, decision, expected strategy and blocked value, a true flag, a matching evidence-pack hash, distinct attacks and no development/held-out family leakage.

## 3. Message for Vineet and Mathangi

Hi both. The 102 agentic review records are in `evaluation/agentic_candidates_20261117/`. Please work from your own copy of the files and do not open `observed_results/` until your labels are frozen.

- **Vineet:** `agentic_development_20_REVIEW_TEMPLATE.jsonl` (20) and `agentic_heldout_40_REVIEW_TEMPLATE.jsonl` (40). For each record read the input and evidence pack, then fill `expected.strategy`, `expected.blocked`, `review_decision` (ACCEPT, CORRECT or QUARANTINE), `review_rationale`, your name in `reviewer` and the time in `reviewed_at_utc`. Any conflict goes in `conflict_disclosure`.
- **Mathangi:** `e2_attacks_32_DISTINCT_REVIEW_TEMPLATE.jsonl` (32) and `e2_clean_10_REVIEW_TEMPLATE.jsonl` (10). Confirm each attack's failure condition, forbidden text and forbidden tools, and label each clean case.
- Set `independently_reviewed` to true only on a record you reviewed yourself.
- Cross-review: Mathangi samples Vineet's labels and Vineet samples Mathangi's. Keep any disagreement as a separate note and do not overwrite the other person's answer.
- Return your files on separate branches or copies. Then Karthika runs the checker, freezes the files, records their SHA-256 hashes, and only then launches E1/E2/E3.
