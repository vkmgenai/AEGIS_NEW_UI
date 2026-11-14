"""Build the fillable team experiment-review questionnaire as a Word file."""
from pathlib import Path

from scripts import build_design_and_viva_docs as builder


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = builder.build(
        "TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES",
        {},
        "TEAM EXPERIMENT REVIEW QUESTIONNAIRES",
        version="1.0",
        document_date="14 November 2026",
    )
    print(path)


if __name__ == "__main__":
    main()
