# Executable-after-review agentic evaluation templates

These files replace neither a signature nor a label. They are syntactically complete historical `CaseEvidence` candidates selected without model outcomes. Every record is intentionally blocked with `REVIEW_REQUIRED` and `independently_reviewed=false`.

## Assignment

- Vineet: review the 20 development and 40 held-out agentic cases. Fill expected strategy/block, rationale, name and time.
- Mathangi: independently review the 32 distinct E2 attacks and ten clean near-miss cases, including each success/failure condition.
- Cross-review: Mathangi samples golden labels; Vineet samples E2 labels. Preserve disagreements.

Do not open paid-run results before labels and hashes are frozen. A conversion/validation step should reject placeholders, family leakage, duplicate attacks, missing evidence packs and blank reviewer fields before launching E1/E2/E3.
