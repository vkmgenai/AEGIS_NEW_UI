"""Launch, preserve, list, inspect and replay capstone experiments.

The ledger stores configuration and outputs, not secrets. Paid C1/C2 work still
requires both the project's enable flag and an explicit --consent-paid flag.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "reports" / "capstone_runs"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True))
    tmp.replace(path)


def append_event(run_dir: Path, event: str, **details) -> None:
    record = {"at_utc": utc_now(), "event": event, **details}
    with (run_dir / "events.jsonl").open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def public_command(args: dict, run_dir: Path) -> list[str]:
    report = run_dir / "report.json"
    if args["experiment"] == "DETERMINISTIC":
        return [sys.executable, str(ROOT / "evaluation" / "run_eval.py"),
                "--split", args["split"], "--retrieval-mode", args["retrieval_mode"],
                "--output", str(report)]
    command = [sys.executable, str(ROOT / "evaluation" / "run_capstone.py"),
               "--experiment", args["experiment"], "--split", args["split"],
               "--repeats", str(args["repeats"]), "--max-paid-calls", str(args["max_paid_calls"]),
               "--output", str(report)]
    if args.get("cases_file"):
        command += ["--cases-file", str(run_dir / "cases.jsonl")]
    if args.get("consent_paid"):
        command.append("--consent-paid")
    return command


def create_run(ns) -> tuple[str, Path]:
    paid = ns.experiment in {"E1", "E2", "E3"}
    if paid and not ns.consent_paid:
        raise ValueError(f"{ns.experiment} can make external model calls; pass --consent-paid only after reviewing the maximum allowance")
    root = ns.ledger_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = root / run_id
    run_dir.mkdir()
    args = {
        "experiment": ns.experiment,
        "split": ns.split,
        "retrieval_mode": ns.retrieval_mode,
        "repeats": ns.repeats,
        "max_paid_calls": ns.max_paid_calls,
        "consent_paid": ns.consent_paid,
        "cases_file": bool(ns.cases_file),
    }
    inputs = {}
    if ns.cases_file:
        source = ns.cases_file.resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copyfile(source, run_dir / "cases.jsonl")
        inputs["cases.jsonl"] = sha256(run_dir / "cases.jsonl")
    manifest = {
        "schema": "aegistrade-capstone-ledger-v1",
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "started_at_utc": None,
        "finished_at_utc": None,
        "status": "QUEUED",
        "pid": None,
        "configuration": args,
        "inputs_sha256": inputs,
        "report_sha256": None,
        "exit_code": None,
        "paid_inference_authorized": bool(ns.consent_paid),
        "provenance": {
            "requested_by": ns.requested_by,
            "request_note": ns.request_note,
            "launched_via": "AegisTrade automated experiment ledger",
            "execution_assistance": "Codex-assisted background execution" if ns.assisted_execution else "Team-operated launcher",
            "human_review_status": "PENDING",
            "independent_validation_status": "PENDING",
            "statement": "Automation executes the frozen configuration; it does not replace the named person's design contribution, result review or sign-off."
        },
        "limitations": [
            "A retained run is not independent evidence until the referenced human labels and review records are complete.",
            "Replay repeats the configuration but provider output may vary; it never overwrites the original run directory."
        ],
    }
    manifest["command"] = public_command(args, run_dir)
    manifest["replay_hint"] = f"python3 evaluation/experiment_ledger.py replay {run_id}"
    atomic_json(run_dir / "manifest.json", manifest)
    append_event(run_dir, "queued")
    return run_id, run_dir


def update_index(ledger_root: Path, manifest: dict) -> None:
    entry = {k: manifest.get(k) for k in ("run_id", "created_at_utc", "finished_at_utc", "status", "exit_code")}
    entry["experiment"] = manifest["configuration"]["experiment"]
    with (ledger_root / "index.jsonl").open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def worker(run_dir: Path) -> int:
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(status="RUNNING", started_at_utc=utc_now(), pid=os.getpid())
    atomic_json(manifest_path, manifest)
    append_event(run_dir, "started", pid=os.getpid())
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    with (run_dir / "stdout.log").open("w") as out, (run_dir / "stderr.log").open("w") as err:
        completed = subprocess.run(manifest["command"], cwd=ROOT, env=env, stdout=out, stderr=err)
    report = run_dir / "report.json"
    manifest.update(
        status="COMPLETED" if completed.returncode == 0 and report.is_file() else "FAILED",
        finished_at_utc=utc_now(), exit_code=completed.returncode,
        report_sha256=sha256(report) if report.is_file() else None,
    )
    atomic_json(manifest_path, manifest)
    append_event(run_dir, "finished", status=manifest["status"], exit_code=completed.returncode,
                 report_sha256=manifest["report_sha256"])
    update_index(run_dir.parent, manifest)
    return completed.returncode


def launch(ns) -> int:
    run_id, run_dir = create_run(ns)
    command = [sys.executable, str(Path(__file__).resolve()), "_worker", str(run_dir)]
    if ns.foreground:
        code = subprocess.run(command, cwd=ROOT).returncode
        print(json.dumps({"run_id": run_id, "status": "finished", "run_dir": str(run_dir), "exit_code": code}, indent=2))
        return code
    log = (run_dir / "launcher.log").open("w")
    proc = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True, close_fds=True)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    manifest["worker_pid"] = proc.pid
    atomic_json(run_dir / "manifest.json", manifest)
    append_event(run_dir, "background_worker_launched", worker_pid=proc.pid)
    print(json.dumps({"run_id": run_id, "status": "QUEUED", "worker_pid": proc.pid,
                      "run_dir": str(run_dir), "show_command": f"python3 evaluation/experiment_ledger.py show {run_id}"}, indent=2))
    return 0


def resolve_run(root: Path, run_id: str) -> Path:
    path = root.resolve() / run_id
    if not path.is_dir() or path.parent != root.resolve():
        raise FileNotFoundError(f"Unknown run ID: {run_id}")
    return path


def show(root: Path, run_id: str) -> int:
    run_dir = resolve_run(root, run_id)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    print(json.dumps({**manifest, "run_dir": str(run_dir), "files": sorted(p.name for p in run_dir.iterdir())}, indent=2))
    return 0


def list_runs(root: Path) -> int:
    if not root.exists():
        print("No experiment ledger exists yet.")
        return 0
    rows=[]
    for path in sorted(root.glob("*/manifest.json"), reverse=True):
        m=json.loads(path.read_text());rows.append({"run_id":m["run_id"],"experiment":m["configuration"]["experiment"],"status":m["status"],"created":m["created_at_utc"],"exit_code":m["exit_code"]})
    print(json.dumps(rows, indent=2))
    return 0


def replay(root: Path, run_id: str, consent_paid: bool, foreground: bool) -> int:
    old = json.loads((resolve_run(root, run_id) / "manifest.json").read_text())
    cfg=old["configuration"]
    class NS: pass
    ns=NS();ns.ledger_root=root;ns.experiment=cfg["experiment"];ns.split=cfg["split"]
    ns.retrieval_mode=cfg.get("retrieval_mode","offline");ns.repeats=cfg.get("repeats",1)
    ns.max_paid_calls=cfg.get("max_paid_calls",24);ns.consent_paid=consent_paid
    provenance=old.get("provenance",{})
    ns.requested_by=provenance.get("requested_by","Unspecified")
    ns.request_note="Replay of "+run_id
    ns.assisted_execution=provenance.get("execution_assistance")=="Codex-assisted background execution"
    cases=resolve_run(root,run_id)/"cases.jsonl";ns.cases_file=cases if cases.exists() else None
    ns.foreground=foreground
    if old.get("paid_inference_authorized") and not consent_paid:
        raise ValueError("Replay of a paid experiment requires fresh explicit --consent-paid authorization")
    return launch(ns)


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger-root",type=Path,default=DEFAULT_LEDGER)
    sub=p.add_subparsers(dest="action",required=True)
    q=sub.add_parser("launch")
    q.add_argument("--experiment",choices=["DETERMINISTIC","E1","E2","E3","E4"],required=True)
    q.add_argument("--cases-file",type=Path);q.add_argument("--split",choices=["dev","development","heldout","both"],default="dev")
    q.add_argument("--retrieval-mode",choices=["offline","neural"],default="offline")
    q.add_argument("--repeats",type=int,choices=[1,3],default=1);q.add_argument("--max-paid-calls",type=int,default=24)
    q.add_argument("--consent-paid",action="store_true");q.add_argument("--foreground",action="store_true")
    q.add_argument("--requested-by",default="Unspecified",help="Person who requested/authorized the experiment; not an automatic reviewer signature")
    q.add_argument("--request-note",default="",help="Short purpose or team decision recorded in the manifest")
    q.add_argument("--assisted-execution",action="store_true",help="Disclose that an assistant launched the frozen background command")
    sub.add_parser("list")
    q=sub.add_parser("show");q.add_argument("run_id")
    q=sub.add_parser("replay");q.add_argument("run_id");q.add_argument("--consent-paid",action="store_true");q.add_argument("--foreground",action="store_true")
    q=sub.add_parser("_worker");q.add_argument("run_dir",type=Path)
    return p


def main() -> int:
    p=parser();ns=p.parse_args()
    try:
        if ns.action=="launch":
            if ns.experiment!="DETERMINISTIC" and ns.split in {"dev","both"}: ns.split="development"
            if ns.experiment=="DETERMINISTIC" and ns.split=="development": ns.split="dev"
            if ns.experiment=="E4": ns.split="development"
            return launch(ns)
        if ns.action=="list":return list_runs(ns.ledger_root)
        if ns.action=="show":return show(ns.ledger_root,ns.run_id)
        if ns.action=="replay":return replay(ns.ledger_root,ns.run_id,ns.consent_paid,ns.foreground)
        if ns.action=="_worker":return worker(ns.run_dir.resolve())
    except (ValueError,FileNotFoundError) as exc:
        p.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
