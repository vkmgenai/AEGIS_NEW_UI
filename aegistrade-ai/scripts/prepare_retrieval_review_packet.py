"""Create a blinded 36-query relevance-review packet for final Recall@5.

Author-suggested relevance IDs are deliberately not copied into the worksheet.
The three named reviewers choose relevant IDs from the frozen corpus catalogue.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

from aegistrade.corpus import corpus_digest, load_corpus


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "evaluation" / "retrieval_review_20261118_v1"
REVIEWERS = ("Karthika", "Mathangi", "Vineet")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite review packet: {out}")
    if ROOT not in out.parents:
        raise ValueError("Output directory must be inside the project")

    source = ROOT / "evaluation" / "retrieval" / "queries_expanded_dev.jsonl"
    authored = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
    # Use a stable 36-query subset that is separate from the old 36-query legacy set.
    selected = [q for q in authored if q["id"].startswith("RAG-DEV-")][:36]
    if len(selected) != 36:
        raise ValueError(f"Expected 36 RAG development queries, found {len(selected)}")
    corpus = load_corpus()
    packet = []
    for index, query in enumerate(selected):
        packet.append({
            "id": query["id"],
            "query": query["query"],
            "assigned_reviewer": REVIEWERS[index % len(REVIEWERS)],
            "reviewed_relevant_ids": [],
            "review_decision": "REVIEW_REQUIRED",
            "review_rationale": "",
            "reviewed_by": "",
            "reviewed_at_utc": "",
            "independently_reviewed": False,
            "conflict_disclosure": "",
        })

    out.mkdir(parents=True)
    write_jsonl(out / "relevance_review_36.jsonl", packet)
    write_jsonl(out / "corpus_catalog_87.jsonl", corpus)
    manifest = {
        "schema": "aegistrade-retrieval-review-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query_count": len(packet),
        "corpus_passages": len(corpus),
        "corpus_sha256": corpus_digest(corpus),
        "source_query_file_sha256": digest(source),
        "assignment": {name: 12 for name in REVIEWERS},
        "blinding": "Author-suggested relevant_ids and retrieval rankings are withheld.",
        "status": "PENDING_INDEPENDENT_REVIEW",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (out / "README.md").write_text("""# Independent Recall@5 relevance review

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
""")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
