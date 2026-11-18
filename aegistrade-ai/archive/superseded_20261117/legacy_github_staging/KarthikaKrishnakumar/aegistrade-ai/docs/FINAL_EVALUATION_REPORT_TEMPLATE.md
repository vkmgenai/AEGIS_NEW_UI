# AegisTrade final evaluation report — 4–6 page results template

Do not replace blanks with estimates. Generate tables from immutable final artifacts.

## 1. Evaluation question and frozen setup

State the version, exact model IDs/backend, prompt and corpus hashes, dataset, development/held-out split, inference limits, repetitions and date of freeze. Explain that portfolio return is secondary to research correctness, grounding and safety.

## 2. Golden set and judge calibration

Describe 20 development and at least 40 untouched held-out cases, family-level splitting and independent label ownership. Report human/judge counts, confusion matrix, agreement and Cohen’s kappa for 20+ labels. State which semantic measures use the judge and which outcomes are code-checked.

## 3. E1 — C0 versus C1 versus C2

| Metric | C0 | C1 mean [range] | C2 mean [range] |
|---|---:|---:|---:|
| Task success / total | | | |
| Grounded supported claims | | | |
| Policy violations | | | |
| Correct tool trajectories | | | |
| Inference units/case | 0 | | |
| Reported cost/case | 0 | | |
| Median / p95 latency | | | |
| Errors / timeouts | | | |

Interpret whether C2 quality gain, if any, justifies additional calls and latency. Include negative results.

## 4. E2 — security defence ablation

Report attack success off/on across 32+ attacks and false-block rate off/on across clean cases. Break down direct injection, retrieved-data injection, poisoned tool output/description, leakage and forbidden-action attempts. Hard financial/approval controls remain enabled in both conditions.

## 5. E3 — reviewed memory

Compare untouched held-out runs with memory off/on using one frozen playbook. Include lesson-generation/review cost, retrieved lesson IDs, one rejected lesson and any accepted lesson that worsened an outcome.

## 6. E4 — finance signature ablation

Compare critic loop on/off and structured dated-evidence parsing versus the simpler representation. Report citation support, source/date correctness, company-assessment validity, task success, cost and latency.

## 7. Retrieval and operations

Report Recall@5 on 30+ independently labelled queries before/after the frozen retrieval change, with MRR/nDCG as context. Include trace completeness, dashboard screenshots, alert evidence, clean-machine installation and failed-CI explanation.

## 8. Failure analysis and limits

Include provider failures, invalid output, insufficient evidence, false blocks, timeouts, data gaps and cases where C2 underperformed. Disclose survivorship bias, unadjusted prices, incomplete historical evidence, model variation and any held-out contamination.

## 9. Conclusion

Answer whether the team justifies its cost for research quality and safety. Do not convert a positive historical return into investment advice or proof of future profitability.

