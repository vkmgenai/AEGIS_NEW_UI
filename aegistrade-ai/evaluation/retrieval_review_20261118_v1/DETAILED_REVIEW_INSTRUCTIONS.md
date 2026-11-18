# AegisTrade independent Recall@5 review instructions

Prepared: 18 November 2026  
Review packet: `retrieval_review_20261118_v1`

## 1. Purpose of this review

The capstone minimum bar requires Recall@5 on at least 30 labelled retrieval
queries, measured before and after one frozen retrieval change. A development
measurement already exists, but its relevance labels were authored during
development. This review supplies an independent relevance judgement from
Karthika, Mathangi and Vineet before the result is promoted to final evidence.

This task evaluates whether the RAG retriever finds the correct passages. It
does **not** ask whether a trade was profitable, whether C2 should buy a stock,
or whether an LLM explanation sounds convincing.

## 2. Initial run already completed

The fresh initial run used the frozen 87-passage corpus and 101 authored
development queries. It made zero paid LLM calls.

| Metric | Before query rewriting | After query rewriting |
|---|---:|---:|
| Recall@5 | 0.9406 | 0.9604 |
| MRR@5 | 0.8667 | 0.8815 |
| nDCG@5 | 0.8852 | 0.9013 |

The full machine-readable result is `rag_initial_20261118.json`. These numbers
are initial development evidence. They become final independently reviewed
evidence only after the blinded worksheet is completed, validated, frozen and
rescored.

## 3. Files in this bundle

| File | Use |
|---|---|
| `relevance_review_36.jsonl` | The only file reviewers edit. It contains 36 queries and assignments. |
| `corpus_catalog_87.jsonl` | The frozen passage catalogue used to decide which passage IDs answer a query. |
| `manifest.json` | Corpus hash, query count, assignments and packet provenance. Do not edit. |
| `rag_initial_20261118.json` | Initial unreviewed before/after retrieval metrics. Do not inspect its row-level rankings until labels are finished. |
| `validate_retrieval_review.py` | Validator run after all reviews are merged. |
| `README.md` | Short version of the review instructions. |
| `DETAILED_REVIEW_INSTRUCTIONS.md/.docx` | This complete guide. |

## 4. Reviewer assignments

The worksheet assigns 12 questions to each reviewer using the
`assigned_reviewer` field:

- Karthika: 12 queries
- Mathangi: 12 queries
- Vineet: 12 queries

Each person should edit a personal copy of `relevance_review_36.jsonl` and
change only records assigned to their name. Return the completed copy to
Karthika for merging. Do not use model output or the initial retrieval rankings
to decide labels.

## 5. What to do for every query

For every record assigned to you:

1. Read the `query` in `relevance_review_36.jsonl`.
2. Open `corpus_catalog_87.jsonl`.
3. Search the catalogue by relevant words from the query.
4. Read the candidate passage's `title` and full `text`; do not label from the
   title alone.
5. Identify **every passage that directly answers the query**.
6. Enter all those passage IDs in `reviewed_relevant_ids`.
7. Set `review_decision` to `ACCEPT`, or `QUARANTINE` when the query is
   ambiguous or cannot be reliably labelled from this corpus.
8. Write a query-specific explanation in `review_rationale`.
9. Set `reviewed_by` to exactly the name in `assigned_reviewer`.
10. Add the current UTC time in `reviewed_at_utc`.
11. Set `independently_reviewed` to `true` only after personally checking it.
12. Record any conflict or uncertainty in `conflict_disclosure`.

Do not simply choose the first passage containing the same word. A passage is
relevant only when its content helps answer the question. If two or more
passages independently provide necessary parts of the answer, include all of
them. Recall@5 is understated when the relevance list omits genuinely relevant
passages.

## 6. Which file answers which question?

For a query such as "What volatility thresholds produce HIGH_VOL?":

1. The question itself and its assigned reviewer are in
   `relevance_review_36.jsonl`.
2. The possible answers are in `corpus_catalog_87.jsonl`.
3. Search the catalogue for `HIGH_VOL`, `volatility`, `ATR`, or related terms.
4. Read the complete matching passages.
5. Put the chosen passage IDs—not copied passage text—into
   `reviewed_relevant_ids`.

Useful catalogue fields are:

| Field | Meaning |
|---|---|
| `id` | Passage identifier to enter in the worksheet, for example `POL-20` |
| `title` | Short description; use only as a navigation aid |
| `text` | Primary content used to decide relevance |
| `source` | Where the passage came from |
| `date` / `published_date` | Date provenance |
| `authority` | `project_policy` or `external_reference` |
| `source_url` / `source_locator` | Source location when available |

## 7. Example of editing one record

Before review:

```json
{"id":"RAG-DEV-004","query":"What volatility thresholds produce HIGH_VOL?","assigned_reviewer":"Karthika","reviewed_relevant_ids":[],"review_decision":"REVIEW_REQUIRED","review_rationale":"","reviewed_by":"","reviewed_at_utc":"","independently_reviewed":false,"conflict_disclosure":""}
```

Illustrative format after review—the passage ID below is only an example of
formatting and must be personally verified against the catalogue:

```json
{"id":"RAG-DEV-004","query":"What volatility thresholds produce HIGH_VOL?","assigned_reviewer":"Karthika","reviewed_relevant_ids":["POL-20"],"review_decision":"ACCEPT","review_rationale":"The passage explicitly states the implemented HIGH_VOL thresholds and therefore directly answers the query.","reviewed_by":"Karthika","reviewed_at_utc":"2026-11-18T09:30:00Z","independently_reviewed":true,"conflict_disclosure":""}
```

Keep every JSON record on one line. Use valid double-quoted JSON and do not add
comments inside the JSONL file.

## 8. When to quarantine

Choose `QUARANTINE` rather than guessing when:

- no passage directly answers the query;
- the wording admits two materially different interpretations;
- a required source is missing from the frozen catalogue;
- the question depends on facts outside the corpus; or
- you cannot confidently determine a complete relevance set.

Explain the reason. Quarantined questions are retained in the audit trail but
excluded from the final Recall@5 denominator. At least 30 accepted questions
must remain to satisfy the minimum bar.

## 9. What not to look at before labelling

Do not use:

- row-level `returned` results in `rag_initial_20261118.json`;
- prior `relevant_ids` in development query files;
- another reviewer's answers before completing your own assignment; or
- an LLM-generated answer that has access to the hidden prior labels.

An LLM may help explain the file format, but it must not select passage IDs on
behalf of the named reviewer. The named reviewer remains responsible for the
actual relevance judgement.

## 10. Validation after merging

From the project root run:

```bash
PYTHONPATH=. .venv/bin/python evaluation/validate_retrieval_review.py \
  evaluation/retrieval_review_20261118_v1
```

The validator checks:

- all 36 records are present and unique;
- accepted queries contain at least one known passage ID;
- the reviewer matches the assignment;
- rationale and UTC time are present; and
- `independently_reviewed` is true.

The correct status before human review is `NOT READY`. After all valid reviews,
it must print `READY to freeze and score.`

## 11. Final scoring after review

After validation:

1. Make an immutable `_FROZEN` copy of the reviewed packet.
2. Calculate and retain SHA-256 hashes.
3. Run neural retrieval before rewriting on the accepted reviewed queries.
4. Run neural retrieval after rewriting on exactly the same queries and corpus.
5. Compute Recall@5, Hit@5, MRR@5 and nDCG@5.
6. Report all failures and quarantined queries.

Recall@5 for a query is:

```text
number of independently labelled relevant passage IDs found in the top 5
--------------------------------------------------------------------------
total number of independently labelled relevant passage IDs for that query
```

The final report must distinguish this reviewed result from the initial
author-labelled development result.

## 12. Summary from the previous project response

The initial Recall@5 run and labelling packet are ready. The fresh execution
measured Recall@5 of 0.9406 before rewriting and 0.9604 after rewriting, with
zero paid LLM calls. The review packet has 36 blinded queries against a frozen
87-passage corpus, assigned equally across Karthika, Mathangi and Vineet.

For every assigned query, the reviewer must identify every directly relevant
passage, record the IDs, accept or quarantine the query, add a case-specific
rationale, name and UTC timestamp, and mark it independently reviewed. Prior
author labels and retrieval rankings are withheld. Once completed, the packet
will be validated, frozen and rescored to produce the final independently
reviewed before/after Recall@5 evidence.
