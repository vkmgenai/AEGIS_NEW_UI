"""Cost-capped provisional C0/C1/C2 inference run, never final labelled evidence."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

from aegistrade.agent_tools import CaseEvidence, approved_route
from aegistrade.llm_backend import backend_info, identity, model_name
from aegistrade.llm_research import run_research_case
from scripts.launch_local import read_env

ROOT = Path(__file__).resolve().parents[1]


def costs(output: dict) -> float:
    values = [u.get("cost") for u in output.get("usage", [])]
    return sum(float(v) for v in values if isinstance(v, (int, float)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, choices=range(1, 61), default=2)
    parser.add_argument("--split", choices=["development", "heldout"], default="development")
    parser.add_argument("--backend", choices=["openrouter", "codex_cli", "claude_cli"], default="openrouter")
    parser.add_argument("--max-cost-usd", type=float, default=0.15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    os.environ.update(read_env(ROOT / ".env"))
    requested_model = os.getenv("OPENROUTER_MODEL") if args.backend == "openrouter" else None
    info = backend_info(backend=args.backend, model=requested_model, probe=True)
    if not info["ready"]:
        raise ValueError(info["reason"])
    if args.backend == "openrouter" and info["model"] != "openai/gpt-4.1-mini":
        raise ValueError("OpenRouter preflight requires the configured gpt-4.1-mini model")
    if os.getenv("AEGIS_ENABLE_LLM_EXPERIMENTS", "false").lower() != "true":
        raise ValueError("AEGIS_ENABLE_LLM_EXPERIMENTS=true is required")
    filename = ("agentic_development_20_REVIEW_TEMPLATE.jsonl" if args.split == "development"
                else "agentic_heldout_40_REVIEW_TEMPLATE.jsonl")
    source = ROOT / "evaluation/agentic_candidates_20261117" / filename
    candidates = [json.loads(line) for line in source.read_text().splitlines() if line.strip()][:args.cases]
    if len(candidates) != args.cases:
        raise ValueError(f"Requested {args.cases} cases but {source.name} contains {len(candidates)}")
    outputs = []
    spent = 0.0
    for case in candidates:
        evidence = CaseEvidence.model_validate(case["input"]).model_dump(mode="json")
        snapshot = {**evidence, "approved_candidate": approved_route(evidence["regime"])}
        for config in ("C0", "C1", "C2"):
            if spent >= args.max_cost_usd:
                raise RuntimeError(f"Preflight cost ceiling reached before {case['id']} {config}")
            out = run_research_case(snapshot, config, model=info["model"], max_calls=8,
                                    max_output_tokens=3600, backend=args.backend)
            cost = costs(out); spent += cost
            outputs.append({"case_id": case["id"], "config": config, "cost_usd": cost, "output": out})
            print(json.dumps({"case": case["id"], "config": config, "guard_pass": out.get("guard_pass"),
                              "calls": out.get("llm_calls", 0), "cost_usd": round(cost, 8),
                              "cumulative_cost_usd": round(spent, 8), "errors": out.get("model_errors", [])}), flush=True)
    report = {
        "run_type": "PROVISIONAL_UNLABELLED_INFERENCE_NOT_FINAL_EVIDENCE",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "inference": identity(backend=args.backend, model=info["model"]),
        "case_source": str(source.relative_to(ROOT)), "split": args.split, "cases": args.cases,
        "authorized_overall_account_spend_usd": 1.0,
        "preflight_stop_ceiling_usd": args.max_cost_usd,
        "actual_provider_reported_cost_usd": spent,
        "outputs": outputs,
        "limitations": [
            "Mechanically selected candidates; not independently human-labelled.",
            "Used for inference, reliability, schema, failure and cost planning only.",
            "Labels must be completed blind to these outputs before any accuracy scoring.",
            "No profitability or held-out-quality claim is permitted.",
        ],
    }
    target = args.output or ROOT / "reports" / ("openrouter_e1_cost_preflight_" + dt.datetime.now().strftime("%Y%m%dT%H%M%S") + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, allow_nan=False))
    print(json.dumps({"report": str(target), "actual_cost_usd": round(spent, 8)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
