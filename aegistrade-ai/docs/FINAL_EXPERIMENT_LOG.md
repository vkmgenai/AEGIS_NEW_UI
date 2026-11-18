# Final experiment log

Do not overwrite failed runs. Add one row per configuration, repeat and code/prompt version. Attach immutable JSON output paths.

| Date/time | Experiment | Split | Repeat | Config | Model/backend | Prompt/corpus/engine version | Cases | Budget | Result artifact | Decision/change |
|---|---|---|---:|---|---|---|---:|---:|---|---|
| 2026-11-14 | Local regression | n/a | 1 | pytest | none | source v0.27.0 | 346 tests | 0 | terminal result: 346 passed | C0/C2 migration retained, including C2 SMC/C0 reference separation |
| 2026-11-14 | Offline development | development | 1 | code/retrieval/scanner | none | corpus recorded in report | 20 + 36/101 queries + 32/10 security strings | 0 | `reports/final_dev_offline_v027.json`, `reports/final_rag_offline_v027.json` | Development evidence only; labels require independent review |
| 2026-11-17 | E1 engineering smoke | development | 1 | C0/C1/C2 | OpenRouter `openai/gpt-4.1-mini` | JSON transport v19 | 2 each | 48 units | `reports/openrouter_e1_development2_v19_smoke.json` | C0 2/2, C1 2/2; C2 1/2 because critic JSON was truncated; corrected in v20 and covered by regression tests |
| 2026-11-17 | E1 engineering development | development | 1 | C0/C1/C2 | OpenRouter `openai/gpt-4.1-mini` | JSON transport v18 | 20 each | bounded | `reports/openrouter_e1_development20_v18.json` | Engineering evidence only: C0 20/20, C1 13/20 and C2 10/20 guard pass; not labelled task accuracy |
| 2026-11-17 | Neural RAG development | development | 1 | retrieval before/after rewrite | local cached embedding model | corpus/query v18 | 101 queries | 0 paid calls | `reports/rag_development_v18.json` | Recall@5 0.9406 before and 0.9604 after rewrite; authored development labels only |
| 2026-11-17 | E4 synthetic strategy ablation | synthetic | 1 | ROUTER plus four fixed strategies | none | deterministic v18 | frozen synthetic series | 0 | `reports/capstone_e4_v18.json` | ROUTER 3.28%; negative result retained; not a real-market or LLM profitability claim |
| 2026-11-17 | Local regression after JSON truncation fix | n/a | 1 | pytest | none | JSON transport v20 | 375 tests | 0 | terminal result: 375 passed | Critic allowance raised only enough to complete bounded typed JSON; no policy gate relaxed |
| | E1 | held-out | 1 | C0 | none | | 40 | 0 | | |
| | E1 | held-out | 1 | C1 | | | 40 | 8/case | | |
| | E1 | held-out | 1 | C2 | | | 40 | 8/case | | |
| | E1 | held-out | 2 | C0/C1/C2 | | | 40 each | fixed | | |
| | E1 | held-out | 3 | C0/C1/C2 | | | 40 each | fixed | | |
| | E2 | red-team + clean | 1 | defence off/on | | | 32 + 10 | fixed | | |
| | E3 | held-out | 1–3 | memory off/on | | frozen playbook | 40 each | fixed | | |
| | E4 | held-out | 1–3 | critic off/on; parsing ablation | | | 40 each | fixed | | |

For every result record task successes, policy violations, attack successes, false blocks, usage/cost, median/p95 latency, errors and timeouts. If a held-out result changes the design, move that family to development and record the contamination.

