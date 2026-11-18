# Independent Recall@5 relevance review

This packet validates 36 queries against a frozen 87-passage corpus. It is
separate from the 102 agent/security cases.

## Steps

1. Open `corpus_catalog_87.jsonl` and read the passage IDs, titles and text.
2. Open `relevance_review_36.jsonl` and work only on records assigned to you.
3. For each query, list **every** passage ID that directly answers it in
   `reviewed_relevant_ids`. Do not choose only the first plausible passage.
4. Set `review_decision` to `ACCEPT`, or `QUARANTINE` if the query is ambiguous
   or cannot be labelled from this corpus.
5. Add a query-specific rationale, your name, UTC time and set
   `independently_reviewed` to `true`.
6. Do not inspect retrieval rankings or prior `relevant_ids` while labelling.

Assignments are round-robin: 12 each for Karthika, Mathangi and Vineet. After
all reviews, run `evaluation/validate_retrieval_review.py` and freeze the folder.
Only accepted queries enter the final before/after Recall@5 calculation.
