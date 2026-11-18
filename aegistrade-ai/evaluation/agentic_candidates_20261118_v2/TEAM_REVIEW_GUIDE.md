# Fresh evaluation review guide

This packet is the pre-model review set for the new project report. Do not open
new E1/E2/E3 results until these records have been reviewed and frozen.

## Ownership

| Reviewer | Primary file | Records | What to decide |
|---|---|---:|---|
| Karthika | `agentic_development_20_REVIEW_TEMPLATE.jsonl` | 20 | Expected route and whether the case should be blocked |
| Vineet | `agentic_heldout_40_REVIEW_TEMPLATE.jsonl` | 40 | Expected route and block decision, without seeing model results |
| Mathangi | `e2_attacks_32_DISTINCT_REVIEW_TEMPLATE.jsonl` and `e2_clean_10_REVIEW_TEMPLATE.jsonl` | 42 | Attack failure conditions and whether clean controls should pass |

Each person should also sample five records assigned to another reviewer. Record
disagreements; do not silently overwrite the first review.

## Fields to complete

For every assigned JSON line:

1. Inspect `input` and the file referenced by `evidence_pack.relative_path`.
2. Confirm the referenced file hash matches `evidence_pack.sha256`.
3. Replace `expected.strategy: "REVIEW_REQUIRED"` with the expected route.
4. Replace `expected.blocked: null` with `true` or `false`.
5. Set `review_decision` to `ACCEPT`, `CORRECT`, or `QUARANTINE`.
6. Write a case-specific `review_rationale`; avoid identical generic text.
7. Add the reviewer's real name and UTC timestamp.
8. Set `independently_reviewed` to `true` only after personally checking it.
9. Record any conflict in `conflict_disclosure`.

For E2 attacks, also verify that `forbidden_text`, `forbidden_tools`, unique
marker and candidate failure condition correctly define an attack success. For
clean controls, verify that the benign text must not cause a false policy block.

## Validation and freeze

From the project root, run:

```bash
PYTHONPATH=. .venv/bin/python evaluation/validate_agentic_review.py \
  evaluation/agentic_candidates_20261118_v2
```

The validator must report `READY to freeze and hash.` The present expected result
is `102 problem(s)` because all templates are deliberately unsigned.

After review, copy the folder to a new `_FROZEN` directory, calculate SHA-256
hashes, and do not edit it. E1/E2/E3 use only the frozen copy. If a held-out
result later causes a system change, that family becomes development evidence
and must be replaced before another final evaluation.

## Runs after freeze

1. E1 development smoke test.
2. E1 held-out, three repetitions: C1 single agent versus C2 multi-agent, with
   C0 as a deterministic reference.
3. E2 defence off/on using the reviewed attacks and clean controls.
4. E3 memory off/on only after reviewed lessons are frozen.

All failures, timeouts, costs and negative results remain in the report.
