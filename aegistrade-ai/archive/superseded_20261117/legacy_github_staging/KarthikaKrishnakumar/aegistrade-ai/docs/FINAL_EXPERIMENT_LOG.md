# Final experiment log

Do not overwrite failed runs. Add one row per configuration, repeat and code/prompt version. Attach immutable JSON output paths.

| Date/time | Experiment | Split | Repeat | Config | Model/backend | Prompt/corpus/engine version | Cases | Budget | Result artifact | Decision/change |
|---|---|---|---:|---|---|---|---:|---:|---|---|
| 2026-11-14 | Local regression | n/a | 1 | pytest | none | source v0.27.0 | 346 tests | 0 | terminal result: 346 passed | C0/C2 migration retained, including C2 SMC/C0 reference separation |
| 2026-11-14 | Offline development | development | 1 | code/retrieval/scanner | none | corpus recorded in report | 20 + 36/101 queries + 32/10 security strings | 0 | `reports/final_dev_offline_v027.json`, `reports/final_rag_offline_v027.json` | Development evidence only; labels require independent review |
| | E1 | held-out | 1 | C0 | none | | 40 | 0 | | |
| | E1 | held-out | 1 | C1 | | | 40 | 8/case | | |
| | E1 | held-out | 1 | C2 | | | 40 | 8/case | | |
| | E1 | held-out | 2 | C0/C1/C2 | | | 40 each | fixed | | |
| | E1 | held-out | 3 | C0/C1/C2 | | | 40 each | fixed | | |
| | E2 | red-team + clean | 1 | defence off/on | | | 32 + 10 | fixed | | |
| | E3 | held-out | 1–3 | memory off/on | | frozen playbook | 40 each | fixed | | |
| | E4 | held-out | 1–3 | critic off/on; parsing ablation | | | 40 each | fixed | | |

For every result record task successes, policy violations, attack successes, false blocks, usage/cost, median/p95 latency, errors and timeouts. If a held-out result changes the design, move that family to development and record the contamination.

