# Experiment execution status — 17 November 2026

This record distinguishes completed machine evidence from final-review evidence that still requires independent human labels. It must not be read as an investment-performance claim.

## Completed in this execution cycle

| Work item | Outcome | Retained artifact |
|---|---|---|
| Full regression suite | 375 passed; 65 dependency deprecation warnings | pytest terminal result |
| OpenRouter 20-case development engineering run | C0 20/20, C1 13/20, C2 10/20 guard pass; not labelled accuracy | `reports/openrouter_e1_development20_v18.json` |
| OpenRouter two-case JSON smoke | C0 and C1 2/2; C2 1/2; isolated critic truncation | `reports/openrouter_e1_development2_v19_smoke.json` |
| Fresh three-repeat development AI Experiment | Same IDEA/LT/HINDALCO cases; C1 passes 0/1/1, C2 1/1/1; C2 +₹3,371.19 each run; C0 −₹11,402.08 each run | `reports/report_ai_repeat_status.json` and its three `data/research_runs/*.json` IDs |
| Typed-output correction | Critic output ceiling 180→300 tokens and reason bound 800→1200 characters; no route, evidence or risk gate relaxed | agent configuration v20 plus regression tests |
| Neural RAG development evaluation | Recall@5 0.9406 before rewrite and 0.9604 after rewrite on 101 authored development queries | `reports/rag_development_v18.json` |
| Fresh synthetic E4 strategy ablation | ROUTER 3.28%, EMA Trend 10.64%, EMA Pullback -0.91%, RSI Reversion 3.14%, Breakout 3.80%; negative router result retained | `reports/capstone_e4_v035.json` |
| Offline reference and scanner checks | 60/60 deterministic reference checks; scanner proxy detected 93.8% of 32 legacy rows with 0/10 clean false blocks | retained evaluation reports; scanner remains proxy evidence |
| Adapter probes | Codex available; Claude installed but not authenticated | `reports/codex_e1_development2_v18.json` for provisional Codex probe |

Approximate recorded OpenRouter spend across the retained preflight and development runs is **US$0.5483**, below the authorized US$1 ceiling.

## Why final E1/E2/E3 was not launched

The validator correctly reports `NOT READY`. It found 102 records needing independent review:

- 20 development `CaseEvidence` labels;
- 40 untouched held-out `CaseEvidence` labels;
- 32 distinct E2 attack labels;
- 10 E2 clean-case labels.

The missing fields include reviewer identity, review time, rationale, decision, expected strategy/block status and `independently_reviewed=true`. Running final held-out inference before those labels are frozen would spend money without producing a valid independently scored result. Generating these labels with the same implementation agent would not fill the minimum-bar requirement.

## Next valid sequence

1. Vineet reviews and signs the 20 development and 40 blinded held-out case templates without seeing model outputs.
2. Mathangi reviews and signs the 32 distinct E2 attacks and ten clean controls.
3. Run the review validator; it must report ready.
4. Freeze the files and record their hashes.
5. Run final E1 C0/C1/C2 on the fixed held-out cases three times with identical model, capabilities and budgets. The completed three development repeats validate the runner but do not replace held-out evidence.
6. Run E2 defence off/on, retaining attack success and clean false-block results.
7. Derive lessons only from development failures, review/freeze them, then run E3 memory off/on on untouched held-out cases.
8. Complete different-family judge calibration and report Cohen's kappa before using judge scores.

Until that sequence is complete, the available results are honest development, engineering and proxy evidence—not final held-out proof.
