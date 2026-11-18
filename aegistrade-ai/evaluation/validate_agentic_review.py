"""Check returned agentic review files before E1/E2/E3 may launch.

Usage: python evaluation/validate_agentic_review.py [DIR]
Exit code 0 only when every record is fully reviewed. It never edits a file.
"""
from __future__ import annotations
import hashlib, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "evaluation" / "agentic_candidates_20261117"
FILES = {
    "agentic_development_20_REVIEW_TEMPLATE.jsonl": ("development", 20, "Vineet"),
    "agentic_heldout_40_REVIEW_TEMPLATE.jsonl": ("heldout", 40, "Vineet"),
    "e2_attacks_32_DISTINCT_REVIEW_TEMPLATE.jsonl": ("e2_attack", 32, "Mathangi"),
    "e2_clean_10_REVIEW_TEMPLATE.jsonl": ("e2_clean", 10, "Mathangi"),
}
PLACEHOLDERS = {"", "REVIEW_REQUIRED", "ACCEPT | CORRECT | QUARANTINE"}


def load(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def symbol_of(rec):
    return str(rec.get("input", {}).get("symbol") or rec.get("family", "")).split("_")[1:2] or [""]


def main(folder: Path) -> int:
    problems: list[str] = []
    blocked: Counter = Counter()
    families: dict[str, set] = {"development": set(), "heldout": set()}
    for name, (kind, count, owner) in FILES.items():
        path = folder / name
        if not path.exists():
            problems.append(f"{name}: file missing")
            continue
        rows = load(path)
        if len(rows) != count:
            problems.append(f"{name}: expected {count} records, found {len(rows)}")
        ids = Counter(r.get("id") for r in rows)
        problems += [f"{name}: duplicate id {i}" for i, n in ids.items() if n > 1]
        if kind == "e2_attack":
            payloads = Counter(r.get("attack_definition", {}).get("payload") for r in rows)
            problems += [f"{name}: duplicate attack payload ({n}x): {p[:60]}" for p, n in payloads.items() if n > 1]
        for r in rows:
            rid, why = r.get("id", "?"), []
            exp = r.get("expected", {})
            if not str(r.get("reviewer", "")).strip(): why.append("reviewer blank")
            if not str(r.get("reviewed_at_utc", "")).strip(): why.append("time blank")
            if not str(r.get("review_rationale", "")).strip(): why.append("rationale blank")
            if str(r.get("review_decision", "")).strip() in PLACEHOLDERS: why.append("decision blank")
            if exp.get("strategy", "REVIEW_REQUIRED") in PLACEHOLDERS: why.append("expected.strategy not set")
            if exp.get("blocked") is None: why.append("expected.blocked not set")
            if r.get("independently_reviewed") is not True: why.append("independently_reviewed is not true")
            if r.get("independently_reviewed") is True and not str(r.get("reviewer", "")).strip():
                why.append("flag true but no reviewer name")
            if kind == "e2_attack" and not exp.get("forbidden_text") and not exp.get("forbidden_tools"):
                why.append("no failure condition")
            pack = r.get("evidence_pack") or {}
            rel = pack.get("relative_path")
            if not rel or not (ROOT / rel).exists():
                why.append("evidence pack missing")
            elif hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != pack.get("sha256"):
                why.append("evidence pack hash mismatch")
            if kind in families: families[kind].add(r.get("family", "").rsplit("_", 1)[0])
            if why:
                blocked[name] += 1
                problems.append(f"{name}: {rid}: " + "; ".join(why))
    leak = families["development"] & families["heldout"]
    problems += [f"family leakage between development and held-out: {sorted(leak)}"] if leak else []
    print("Records still blocked per file:")
    for name in FILES: print(f"  {name}: {blocked.get(name, 0)}")
    print(f"\n{len(problems)} problem(s).")
    for p in problems[:40]: print(" -", p)
    if len(problems) > 40: print(f" ... and {len(problems) - 40} more")
    print("\nREADY to freeze and hash." if not problems else "\nNOT READY: do not launch E1/E2/E3.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT))
