# Fresh executable-after-review agentic evaluation templates

These files replace neither a signature nor a label. They are syntactically complete historical `CaseEvidence` candidates selected without model outcomes. Every record is intentionally blocked with `REVIEW_REQUIRED` and `independently_reviewed=false`.

This version uses symbols that do not occur in the 17 November agentic template set. The old 102 records remain unchanged and are not inputs to this packet.

## Assignment

- Karthika: review the 20 development agentic cases. Fill expected strategy/block, rationale, name and time.
- Vineet: independently review the 40 held-out agentic cases without opening model outputs.
- Mathangi: independently review the 32 distinct E2 attacks and ten clean near-miss cases, including each success/failure condition.
- Cross-review: each reviewer samples five records owned by another reviewer. Preserve disagreements rather than forcing consensus.

Do not open paid-run results before labels and hashes are frozen. A conversion/validation step should reject placeholders, family leakage, duplicate attacks, missing evidence packs and blank reviewer fields before launching E1/E2/E3.

## Browser review for Karthika

Open `KARTHIKA_DEVELOPMENT_REVIEW_20.html` in Chrome, Safari or Edge. It is a
standalone offline editor for the 20 development cases. It formats the technical
snapshot and dated evidence, autosaves progress in the browser, validates the
required fields and exports `agentic_development_20_REVIEWED_KARTHIKA.jsonl`.
Keep the original template unchanged and return the exported JSONL for formal
validation and freezing.
