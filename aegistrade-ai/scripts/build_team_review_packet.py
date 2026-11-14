"""Build the fillable team experiment-review questionnaire as a Word file."""
from pathlib import Path

from scripts import build_design_and_viva_docs as builder


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    questionnaire = builder.build(
        "TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES",
        {},
        "TEAM EXPERIMENT REVIEW QUESTIONNAIRES",
        version="1.0",
        document_date="14 November 2026",
    )
    guide = builder.build(
        "TEAM_REVIEW_EVIDENCE_AND_LLM_ASSISTANCE_GUIDE",
        {},
        "TEAM REVIEW EVIDENCE & LLM ASSISTANCE GUIDE",
        version="1.0",
        document_date="14 November 2026",
    )
    print(questionnaire)
    print(guide)


if __name__ == "__main__":
    main()
