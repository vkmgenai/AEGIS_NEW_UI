"""Validate a blinded retrieval relevance-review packet without editing it."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


PLACEHOLDERS = {"", "REVIEW_REQUIRED"}


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main(folder: Path) -> int:
    corpus = load(folder / "corpus_catalog_87.jsonl")
    rows = load(folder / "relevance_review_36.jsonl")
    known = {p["id"] for p in corpus}
    problems: list[str] = []
    if len(rows) != 36:
        problems.append(f"expected 36 queries, found {len(rows)}")
    ids = Counter(r.get("id") for r in rows)
    problems += [f"duplicate query id: {key}" for key, count in ids.items() if count > 1]
    for row in rows:
        rid = row.get("id", "?")
        labels = row.get("reviewed_relevant_ids", [])
        if row.get("independently_reviewed") is not True:
            problems.append(f"{rid}: independently_reviewed is not true")
        if row.get("review_decision") not in {"ACCEPT", "QUARANTINE"}:
            problems.append(f"{rid}: review_decision is incomplete")
        if not str(row.get("review_rationale", "")).strip():
            problems.append(f"{rid}: rationale is blank")
        if row.get("reviewed_by") != row.get("assigned_reviewer"):
            problems.append(f"{rid}: reviewer does not match assignment")
        if not str(row.get("reviewed_at_utc", "")).strip():
            problems.append(f"{rid}: review time is blank")
        if row.get("review_decision") == "ACCEPT" and not labels:
            problems.append(f"{rid}: accepted query has no relevant passage IDs")
        unknown = set(labels) - known
        if unknown:
            problems.append(f"{rid}: unknown passage IDs {sorted(unknown)}")
    print(f"{len(rows)} queries; {len(problems)} problem(s).")
    for item in problems[:60]:
        print(" -", item)
    if len(problems) > 60:
        print(f" ... and {len(problems) - 60} more")
    print("\nREADY to freeze and score." if not problems else "\nNOT READY: complete independent review first.")
    return 0 if not problems else 1


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evaluation/retrieval_review_20261118_v1")
    raise SystemExit(main(target))
