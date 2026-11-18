"""Build a sanitized, shareable team-review packet from retained AegisTrade runs.

The packet deliberately separates blinded label sheets from observed results. It
never copies .env, reviewer tokens, SQLite databases, or cached source documents.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261117"
OUT = ROOT / "docs" / f"team_review_packet_{STAMP}"
RUNS = [
    "20261117T105811-138ef587",  # fresh E4
    "20261117T110205-1c7df087",  # fresh deterministic neural reference
]
AI_RUN = "026512e1f9054db09011c4e9e611ef8d"
PORTFOLIO_RUN = "dc354841097240e0bc88d8430953fa22"


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def blinded_case(row: dict) -> dict:
    return {k: v for k, v in row.items() if k not in {
        "expected", "suggested_machine_label", "human_label", "reviewer",
        "independently_reviewed", "note"
    }}


def write_blinded_sheet(source: Path, target: Path, kind: str) -> None:
    rows = read_jsonl(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w") as f:
        for row in rows:
            item = blinded_case(row)
            item["human_review"] = {
                "reviewer": "",
                "reviewed_at_utc": "",
                "decision": "ACCEPT | CORRECT | QUARANTINE",
                "independent_expected_result": "",
                "reason": "",
                "policy_or_source_reference": "",
                "conflict_of_interest": ""
            }
            item["review_kind"] = kind
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def copy_run(run_id: str) -> None:
    src = ROOT / "reports" / "capstone_runs" / run_id
    dst = OUT / "observed_results" / "capstone_runs" / run_id
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("manifest.json", "events.jsonl", "report.json", "stdout.log", "stderr.log"):
        if (src / name).is_file():
            shutil.copy2(src / name, dst / name)


def ai_summary() -> dict:
    data = json.loads((ROOT / "data" / "research_runs" / f"{AI_RUN}.json").read_text())
    outputs = []
    for row in data.get("outputs", []):
        outputs.append({
            "config": row.get("config"), "case_id": row.get("case_id"),
            "symbol": row.get("symbol"), "date": row.get("date"),
            "selected_strategy": row.get("selected_strategy"),
            "guard_pass": row.get("guard_pass"), "model_errors": row.get("model_errors"),
            "llm_calls": row.get("llm_calls"), "tool_calls": row.get("tool_calls"),
            "latency_s": row.get("latency_s"), "citations": row.get("citations"),
        })
    return {
        "run_id": data.get("run_id"), "status": data.get("status"),
        "created_utc": data.get("created_utc"), "settings": data.get("settings"),
        "inference": data.get("inference"), "prompt_version": data.get("prompt_version"),
        "knowledge_corpus": data.get("knowledge_corpus"), "summary": data.get("summary"),
        "case_observations": outputs,
        "limitations": [
            "This is an earlier three-case development run, not independently reviewed held-out evidence.",
            "C0 agreement is deterministic self-agreement, not proof that C0 is higher quality than C1/C2.",
            "One model error occurred in both C1 and C2 and must remain visible."
        ]
    }


def portfolio_extract() -> dict:
    state = json.loads((ROOT / "data" / "c2_portfolio_runs" / PORTFOLIO_RUN / "state.json").read_text())
    return {
        "run_id": state.get("run_id"), "status": state.get("status"),
        "created_utc": state.get("created_utc"), "updated_utc": state.get("updated_utc"),
        "settings": state.get("settings"), "inference": state.get("inference"),
        "model_calls": state.get("model_calls"), "call_limit": state.get("call_limit"),
        "consents": state.get("consents"), "execution_policy": state.get("execution_policy"),
        "benchmark": state.get("benchmark"), "reference": state.get("reference"),
        "human_override_ledger": state.get("human_override_ledger", []),
        "ledger": state.get("ledger", []), "decisions": state.get("decisions", []),
        "last_error": state.get("last_error"),
        "limitations": [
            "Development portfolio evidence; current-member selection and unadjusted-price limitations apply.",
            "COMPLETED_WITH_GAPS is not equivalent to clean final held-out completion.",
            "Profitability does not establish research correctness or future performance."
        ]
    }


def questionnaire(role: str, responsibility: str, questions: list[str], evidence: list[str]) -> str:
    numbered = "\n\n".join(
        f"### Q{i}. {q}\n\nStatus: PENDING\n\nConclusion:\n\nEvidence (run ID / artifact / field):\n\nMethod and recomputation:\n\nExceptions or missing evidence:\n\nReviewer/date:"
        for i, q in enumerate(questions, 1)
    )
    return f"""# {role} — independent review questionnaire

Responsibility: {responsibility}

## Review rules

1. Complete and sign the blinded sheets before opening `observed_results/`.
2. Use SUPPORTED, PARTIALLY SUPPORTED, PENDING, REJECTED or NOT APPLICABLE.
3. Cite a run ID, artifact path and field/case/event for every material answer.
4. Do not treat candidate labels, LLM drafts or architecture claims as independent evidence.
5. Preserve negative results. If an observed held-out result changes the system, disclose contamination and replace the held-out family.

## Evidence currently supplied

{chr(10).join('- ' + item for item in evidence)}

{numbered}

## Final decision

Decision: ACCEPT FOR FINAL EVIDENCE | ACCEPT WITH LIMITATIONS | REJECT / RE-RUN

Rationale:

Conflict disclosure:

Independent acceptor required/name:

Attestation: I personally inspected the cited artifacts. I did not infer or fabricate missing results.

Signature/date:
"""


def markdown_to_docx(markdown: str, path: Path) -> None:
    """Render the packet's deliberately simple Markdown as a readable Word form."""
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(0.65)
    section.left_margin = section.right_margin = Inches(0.75)
    doc.styles["Normal"].font.name = "Aptos"
    doc.styles["Normal"].font.size = Pt(10)
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            doc.add_paragraph()
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=2)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=0)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif len(line) > 2 and line[0].isdigit() and ". " in line[:5]:
            doc.add_paragraph(line.split(". ", 1)[1], style="List Number")
        else:
            doc.add_paragraph(line.replace("`", "").replace("**", ""))
    doc.save(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "blinded_review").mkdir(parents=True)
    (OUT / "observed_results").mkdir(parents=True)

    write_blinded_sheet(ROOT / "evaluation/golden/development.jsonl", OUT / "blinded_review/golden_development_20_BLINDED.jsonl", "golden_development")
    write_blinded_sheet(ROOT / "evaluation/golden/heldout/heldout.jsonl", OUT / "blinded_review/golden_heldout_40_BLINDED.jsonl", "golden_heldout")
    write_blinded_sheet(ROOT / "evaluation/redteam/attacks_32.jsonl", OUT / "blinded_review/security_attacks_32_BLINDED.jsonl", "security_attack")
    write_blinded_sheet(ROOT / "evaluation/redteam/clean_10.jsonl", OUT / "blinded_review/security_clean_10_BLINDED.jsonl", "security_clean")
    write_blinded_sheet(ROOT / "evaluation/retrieval/queries_36.jsonl", OUT / "blinded_review/retrieval_queries_36_BLINDED.jsonl", "retrieval_relevance")

    judge = json.loads((ROOT / "evaluation/judge_calibration.json").read_text())
    for row in judge:
        row.pop("suggested_machine_label", None)
        row["human_label"] = None
        row["reviewer"] = ""
        row["reviewed_at_utc"] = ""
        row["reason"] = ""
    dump(OUT / "blinded_review/judge_calibration_24_BLINDED.json", judge)

    for run_id in RUNS:
        copy_run(run_id)
    shutil.copy2(ROOT / "reports/rag_development_20261117.json", OUT / "observed_results/rag_development_20261117.json")
    shutil.copy2(ROOT / "data/research_runs" / f"{AI_RUN}.json", OUT / f"observed_results/ai_experiment_{AI_RUN}_FULL_TRACE.json")
    dump(OUT / f"observed_results/ai_experiment_{AI_RUN}_SUMMARY.json", ai_summary())
    dump(OUT / f"observed_results/c2_portfolio_{PORTFOLIO_RUN}_REVIEW_EXTRACT.json", portfolio_extract())
    shutil.copy2(ROOT / "reports/ci_intentional_failure_local.json", OUT / "observed_results/ci_intentional_failure_LOCAL_ONLY.json")

    common = [
        f"E4 run `{RUNS[0]}` (completed; synthetic deterministic ablation)",
        f"Deterministic neural run `{RUNS[1]}` (completed; candidate labels)",
        "Neural RAG development report `rag_development_20261117.json` (101 authored queries)",
        f"AI experiment `{AI_RUN}` summary (three cases; C0/C1/C2; one C1 and one C2 model error)",
        f"C2 portfolio `{PORTFOLIO_RUN}` review extract (development evidence and human overrides)",
        "Local intentional-CI failure record (not hosted failed-CI evidence)",
    ]
    kq = [
        "Record prompt, corpus, backend/model and run versions for each inspected agent run.",
        "Did C1/C2 remain within declared call/tool/context budgets and read-tool permissions?",
        "Map every reviewed citation to evidence observed before the historical cutoff.",
        "Did market, strategy and critic typed hand-offs agree with the locked route and purpose?",
        "Did the critic independently inspect evidence rather than repeat another agent?",
        "Identify one validation failure/replan trace, or mark PENDING if none is retained.",
        "Classify blocks as evidence, provider, schema, budget, timeout or context failures.",
        "Did dated-web fallback preserve historical date, source ID and persisted hash?",
        "Which reviewed lessons were retrieved and did any worsen an outcome?",
        "Were accepted lessons development-only, human reviewed and frozen before evaluation?",
        "What measured benefit did C2 provide over C1, and where did added cost fail to help?",
        "Separate implementation claims, measured run claims and unmeasured claims."
    ]
    mq = [
        "List security, approval, portfolio and deployment artifacts inspected.",
        "Independently define the success condition for each of the 32 blinded attacks.",
        "Independently label the ten clean cases and later compute false blocks off/on.",
        "Confirm hard permissions, typed validation and broker isolation stay enabled during E2.",
        "Demonstrate approve, reject and edit with old-payload-hash invalidation.",
        "Demonstrate stale quote, changed evidence, duplicate request and timeout recovery.",
        "Recompute one portfolio order: shares, fees, slippage, stop/target and cash effect.",
        "Can any LLM write to a broker, change risk limits or bypass human review? Cite enforcement.",
        "Does a background run preserve inputs, lifecycle events, logs, report and hashes?",
        "Provide hosted failed-CI evidence; distinguish it from the supplied local-only demo.",
        "Provide a controlled fired-alert and restoration record.",
        "Give the final safety/platform evidence decision and limitations."
    ]
    vq = [
        "List inspected run IDs and independently verify artifact hashes.",
        "Verify development/held-out family separation and identify leakage.",
        "Independently label assigned golden cases before opening observed results.",
        "Verify dates, point-in-time boundaries, current-member bias and unadjusted prices.",
        "Did C0/C1/C2 receive identical cases and fair model/tool/budget settings?",
        "Were three frozen repetitions completed without choosing the best result?",
        "Recompute success, violations, calls/cost, latency, timeouts and errors.",
        "Independently review at least 30 retrieval queries and relevant passage IDs.",
        "Audit every profitability statement, fees, marks, benchmark and limitations.",
        "Name negative results and C2 underperformance that must remain reported.",
        "Give the final research/evaluation decision and required reruns."
    ]
    questionnaires = {
        "KARTHIKA": questionnaire("Karthika", "agents, RAG, MCP, orchestration and learning", kq, common),
        "MATHANGI": questionnaire("Mathangi", "safety, approvals, ledger, UI and deployment", mq, common),
        "VINEET": questionnaire("Vineet", "datasets, backtesting, golden labels and metrics", vq, common),
    }
    for name, content in questionnaires.items():
        (OUT / f"QUESTIONNAIRE_{name}.md").write_text(content)
        markdown_to_docx(content, OUT / f"QUESTIONNAIRE_{name}.docx")

    readme = f"""# AegisTrade distributed team-review packet — {STAMP}

## Correct order of use

1. Each reviewer records the Git commit they pulled.
2. **Before viewing results**, complete assigned files in `blinded_review/` and sign with name/date/reason.
3. Return blinded reviews to Karthika. Preserve the originals and resolve disagreements explicitly.
4. Freeze reviewed cases and hashes. Only then run paid E1/E2/E3.
5. Open `observed_results/` for metric, trace, safety and limitation review.
6. Complete the role questionnaire. PENDING is required when evidence is absent.

## Why no additional paid run was added

The present blocker is independent review, not run count. Running E1/E2/E3 before reviewers freeze labels would undermine the held-out protocol. Current runs are sufficient for the team to perform phase-one review and inspect implementation/development evidence. They are not sufficient to claim the minimum bar is closed.

## Included evidence

{chr(10).join('- ' + item for item in common)}

## Still required after review

- Reviewed/frozen 20 development and 40 held-out golden cases with family separation.
- Independently authored/reviewed 32 attack and 10 clean labels.
- At least 20 human judge-calibration labels and a different-family judge run.
- Paid E1 development, then three untouched held-out repetitions.
- Actual model-level E2 defence off/on and clean false-block evaluation.
- A human-reviewed frozen playbook, including accepted and rejected lessons, followed by E3 off/on.
- Hosted failed-CI evidence, fired-alert evidence, contribution records, final slides and video.

## Security

This packet excludes `.env`, API keys, reviewer tokens, SQLite databases and cached/licensed source documents. The full raw local databases remain on Karthika's machine and should not be emailed.
"""
    (OUT / "README_FIRST.md").write_text(readme)
    markdown_to_docx(readme, OUT / "README_FIRST.docx")

    rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        rows.append({"path": str(path.relative_to(OUT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    with (OUT / "EVIDENCE_INDEX.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader(); writer.writerows(rows)
    (OUT / "SHA256SUMS.txt").write_text("\n".join(f"{sha256(p)}  {p.relative_to(OUT)}" for p in sorted(x for x in OUT.rglob('*') if x.is_file() and x.name != 'SHA256SUMS.txt')) + "\n")

    archive = ROOT / "docs" / f"AegisTrade_Team_Review_Packet_{STAMP}.zip"
    if archive.exists(): archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
            z.write(path, Path(OUT.name) / path.relative_to(OUT))
    print(json.dumps({"packet": str(OUT), "archive": str(archive), "files": len(list(OUT.rglob('*'))), "archive_bytes": archive.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
