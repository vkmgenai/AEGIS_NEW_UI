# LLM-assist drafts of blinded sheets (NOT human reviews)

Prepared 2026-11-17 so Vineet and Mathangi can accept, correct or reject each row. Reviewer, date and conflict-of-interest fields are blank on purpose: a person must fill them after checking the row.

- Vineet primary: golden_development_20, golden_heldout_40, retrieval_queries_36.
- Mathangi primary: security_attacks_32, security_clean_10.
- Not drafted: judge_calibration_24. Those labels must come from humans for the Cohen's kappa result to mean anything.
- The drafter was not blind: it had seen the seeded expected labels before drafting, so agreement with the seeded labels is not independent evidence.
- Golden rows leave `decision` empty: the hidden seeded label is compared only at the freeze step.
- Same drafter for both people: do not have both reviewers just copy it; the second reviewer should check a sample independently.
- Problem found: ATT-017..032 repeat ATT-001..016, so there are 16 distinct attacks, not 32. Replace the duplicates with new attacks before counting 32.

- Blinding disclosure: the drafter opened observed_results/ (runs, traces, portfolio extract) in the same session before drafting these sheets, and had earlier seen the seeded expected labels. The answers were derived from the blinded files, knowledge/corpus.jsonl and the code, not copied from observed_results, but these drafts are NOT blinded work. Vineet and Mathangi must complete their own blinded pass without opening observed_results/ first.
