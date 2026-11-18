"""Resume the bounded three-repeat development E1 run used in the report.

The script never deletes results. Re-running it counts matching completed runs and
creates only the missing repetitions. Final held-out E1 remains separately gated
by independently reviewed labels.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from app.api import market_snapshot_context
from aegistrade.llm_backend import identity, model_name
from aegistrade.research_service import ResearchSettings, execute_research

RUNS = ROOT / "data" / "research_runs"
STATUS = ROOT / "reports" / "report_ai_repeat_status.json"
TARGET_REPEATS = 3
CASE_DATE = "2026-09-30"


def matching_runs() -> list[dict]:
    rows = []
    for path in sorted(RUNS.glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            settings = item.get("settings", {})
            if (
                item.get("status") == "COMPLETED"
                and settings.get("configuration") == "ALL"
                and settings.get("cases") == 3
                and settings.get("start_date") == CASE_DATE
                and settings.get("end_date") == CASE_DATE
                and item.get("model") == model_name()
            ):
                rows.append(item)
        except (OSError, ValueError):
            continue
    return rows


def write_status(runs: list[dict], error: str | None = None) -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(
        json.dumps(
            {
                "updated_utc": datetime.now(timezone.utc).isoformat(),
                "target_repeats": TARGET_REPEATS,
                "completed_repeats": len(runs),
                "run_ids": [r["run_id"] for r in runs],
                "backend": identity(),
                "case_date": CASE_DATE,
                "status": "COMPLETED" if len(runs) >= TARGET_REPEATS else "PAUSED_OR_INCOMPLETE",
                "last_error": error,
                "note": "Development evidence only. Final held-out E1 requires independently reviewed labels.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    runs = matching_runs()
    write_status(runs)
    if len(runs) >= TARGET_REPEATS:
        print("All report development repeats already exist:", [r["run_id"] for r in runs])
        return
    frame, source, provenance = market_snapshot_context()
    settings = ResearchSettings(
        configuration="ALL",
        cases=3,
        start_date=CASE_DATE,
        end_date=CASE_DATE,
        consent_to_paid_calls=True,
        max_output_tokens_per_case=3600,
        automatic_stock_selection=True,
        reference_capital=200_000,
        use_memory=False,
        dataset_split="development",
        research_purpose="ENTRY",
    )
    try:
        while len(runs) < TARGET_REPEATS:
            result = execute_research(
                frame,
                settings,
                source=source,
                provenance=provenance,
                model=model_name(),
                save_dir=RUNS,
            )
            runs.append(result)
            write_status(runs)
            print(f"Completed repeat {len(runs)}/{TARGET_REPEATS}: {result['run_id']}", flush=True)
    except Exception as exc:
        write_status(runs, f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    main()
