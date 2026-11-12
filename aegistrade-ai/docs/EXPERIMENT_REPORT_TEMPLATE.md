# Experiment evaluation report (fill in actual measurements; 4-6 pages)

## Dataset audit
- Source, licensing, symbols, dated membership, split cutoffs, adjustments.
- Gold labels: who reviewed, when, number of corrected labels, leakage controls.

## E1: Does agent complexity justify cost?
C0 fixed rules, C1 single agent, C2 multiple specialists. Same models, available
tools and total budget. Record success, invalid suggestion, citation correctness,
latency p50/p95, LLM prompt/completion tokens and provider cost.

## E2: Defences on/off
Attack success measured on the ACTUAL guarded AI system (not regex proxy only);
legitimate clean workload false-block rate. Include 30+ examples, source injection.

## E3: Reviewed Reflexion lessons
Review proposed lessons on development only; freeze and hash playbook. Evaluate
before/after on held-out data with 3 repeats and include the generation cost.
Document one rejected lesson and any harmful accepted lesson.

## E4: Signature ablations
A: regime-aware router versus fixed EMA/RSI/breakout (same capital/cost rules).
B: safe execution controls on/off **only in isolated simulator**, count unsafe
proposals blocked and ensure no duplicates; document edit/stale tests.

## Reliability notes
Include missing, failed, timed-out and rate-limited runs. Never discard failures.
List context window, prompts (six slots), model IDs, temperature and seeds.

## Discussion and limitations
No real trading, model-generated explanations cannot guarantee factual validity,
market data and synthetic scenarios are not representative of live trading.
