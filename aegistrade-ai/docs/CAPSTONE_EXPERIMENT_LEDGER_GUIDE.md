# Capstone background experiment ledger

The ledger keeps every experiment in a unique directory under `reports/capstone_runs/RUN_ID/`. It never overwrites an earlier run.

Each run retains:

- `manifest.json`: status, configuration, timestamps, process ID, authorization flag, input and result hashes, exact command and replay hint;
- `events.jsonl`: queued, started and finished lifecycle events;
- `cases.jsonl`: exact copied case input when supplied;
- `stdout.log` and `stderr.log`;
- `report.json`: complete row-level experiment output;
- `launcher.log`: background-worker launcher diagnostics.

## Verified non-billable background run

Run `20261114T153948-3dfe8a63` completed E4 in the background with exit code 0. Its report hash is `952e0dd94b58613c082f42351f7d0ebe5c3b467997e8585ce59165a0f365c357`. This is the existing synthetic deterministic routing ablation; it is not a C1/C2 model result or profitability evidence.

Run `20261114T154041-1dd60bf8` completed the non-generation development reference checks in the background with exit code 0. Its labels are still seeded development hypotheses until the assigned teammate reviews them; completion does not turn them into independent evidence.

## Commands

From the project root with the virtual environment available:

```bash
.venv/bin/python evaluation/experiment_ledger.py list
.venv/bin/python evaluation/experiment_ledger.py show 20261114T153948-3dfe8a63
```

Launch the zero-generation deterministic check:

```bash
.venv/bin/python evaluation/experiment_ledger.py launch \
  --experiment DETERMINISTIC --split dev --retrieval-mode offline
```

Replay creates a new run directory and preserves the original:

```bash
.venv/bin/python evaluation/experiment_ledger.py replay 20261114T153948-3dfe8a63
```

E1–E3 require an independently reviewed agentic case file, complete point-in-time company evidence, a pinned reproducible model, the enable flag, an allowance covering the computed maximum, and fresh explicit consent. Example only after those conditions are satisfied:

```bash
.venv/bin/python evaluation/experiment_ledger.py launch \
  --experiment E1 \
  --cases-file evaluation/reviewed/agentic_cases.jsonl \
  --split heldout --repeats 3 --max-paid-calls MAXIMUM \
  --consent-paid
```

The launcher refuses paid E1–E3 work without `--consent-paid`. Passing the flag does not bypass `AEGIS_ENABLE_LLM_EXPERIMENTS`, label validation, family-split validation, evidence readiness, model pinning or the harness allowance check.

## Review sequence

1. Independently review labels without seeing model outputs.
2. Freeze the case file and record its hash.
3. Launch the background experiment once with the approved maximum allowance.
4. Wait for `COMPLETED` or retain and explain `FAILED`; never delete an unfavourable run.
5. Give the run ID to the assigned reviewer using `TEAM_EXPERIMENT_REVIEW_QUESTIONNAIRES.md`.
6. Store the signed response in `evaluation/team_reviews/`.
7. Incorporate only reviewed results into the final evaluation report. If a result changes the system, it is development evidence and must not remain held-out.
