"""Read-only, path-safe views over retained capstone experiment runs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{5,79}$")


def ledger_root() -> Path:
    configured = os.getenv("AEGIS_CAPSTONE_LEDGER_DIR")
    return Path(configured).resolve() if configured else (ROOT / "reports" / "capstone_runs").resolve()


def _run_dir(run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise ValueError("Invalid capstone run ID")
    base = ledger_root()
    path = (base / run_id).resolve()
    if path.parent != base:
        raise ValueError("Invalid capstone run path")
    if not path.is_dir():
        raise FileNotFoundError(run_id)
    return path


def _json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Unreadable ledger artifact: {path.name}") from exc


def _manifest(path: Path) -> dict:
    value = _json(path / "manifest.json")
    if not isinstance(value, dict) or not isinstance(value.get("run_id"), str):
        raise ValueError("Invalid experiment manifest")
    return value


def list_runs() -> list[dict]:
    base = ledger_root()
    if not base.exists():
        return []
    rows=[]
    for manifest_path in base.glob("*/manifest.json"):
        try:
            m=_manifest(manifest_path.parent)
            cfg=m.get("configuration") if isinstance(m.get("configuration"),dict) else {}
            rows.append({
                "run_id":m["run_id"],"experiment":cfg.get("experiment","UNKNOWN"),
                "status":m.get("status","UNKNOWN"),"created_at_utc":m.get("created_at_utc"),
                "finished_at_utc":m.get("finished_at_utc"),"exit_code":m.get("exit_code"),
                "split":cfg.get("split"),"repeats":cfg.get("repeats"),
                "paid_inference_authorized":bool(m.get("paid_inference_authorized")),
                "requested_by":(m.get("provenance") or {}).get("requested_by"),
                "human_review_status":(m.get("provenance") or {}).get("human_review_status"),
                "report_available":(manifest_path.parent/"report.json").is_file(),
            })
        except ValueError:
            continue
    return sorted(rows,key=lambda x:(x.get("created_at_utc") or "",x["run_id"]),reverse=True)


def _report_preview(report: dict) -> dict:
    rows=report.get("rows") if isinstance(report.get("rows"),list) else []
    preview={k:report.get(k) for k in (
        "experiment","run_type","split","repeats","inference","case_file_sha256",
        "max_possible_paid_calls","summary","case_results","retrieval_before",
        "retrieval_after","retrieval_mode","security","limitation","limitations",
    ) if k in report}
    preview["row_count"]=len(rows)
    preview["variants"]=sorted({str(r.get("variant")) for r in rows if isinstance(r,dict) and r.get("variant")})
    preview["failed_rows"]=sum(bool(r.get("output",{}).get("model_errors")) for r in rows if isinstance(r,dict))
    return preview


def run_detail(run_id: str) -> dict:
    path=_run_dir(run_id);manifest=_manifest(path)
    events=[]
    event_path=path/"events.jsonl"
    if event_path.is_file():
        try:
            events=[json.loads(line) for line in event_path.read_text().splitlines()[-1000:] if line.strip()]
        except (json.JSONDecodeError,UnicodeDecodeError) as exc:
            raise ValueError("Unreadable experiment events") from exc
    report_path=path/"report.json"
    preview=_report_preview(_json(report_path)) if report_path.is_file() else None
    return {"manifest":manifest,"events":events,"report_preview":preview,
            "files":sorted(p.name for p in path.iterdir() if p.is_file()),
            "report_download_available":report_path.is_file()}


def report_path(run_id: str) -> Path:
    path=_run_dir(run_id)/"report.json"
    if not path.is_file():raise FileNotFoundError(run_id)
    return path
