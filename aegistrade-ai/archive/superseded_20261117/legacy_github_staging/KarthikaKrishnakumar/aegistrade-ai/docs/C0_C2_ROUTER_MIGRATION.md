# C0/C2 Router migration checkpoint

Status: planned on 2026-11-14; use this file as the restart checklist if the coding session is interrupted.

## Target design

- Remove C1 as a user-selectable portfolio flow. Retain C1 in the AI Experiment as the guideline-required single-agent baseline with the same tools and budget.
- C0 remains the zero-inference deterministic ROUTER baseline so that C0 and C2 share a defensible technical opportunity set. No random-selection comparator is included.
- C2 performs dated company research before final candidate choice and uses the multi-agent market, strategy and critic workflow.
- The C2 ROUTER catalogue contains EMA Trend, EMA Pullback, RSI Reversion, Breakout and SMC.
- Preserve a deterministic technical reference so the capstone can report both:
  - controlled comparison: C2 versus the same-signal C0 technical reference.
- No live orders; all fills remain historical later-open simulations.

## Implementation checklist

- [ ] Keep deterministic C0 ROUTER selection and its point-in-time ranking audit.
- [x] Add SMC to the C2 ROUTER regime/strategy contracts and candidate ranking while retaining the four-route C0 view.
- [ ] Change C2 selection into bounded fundamental research followed by final ranking, without future data.
- [x] Remove C1 from new portfolio choices and portfolio comparison; preserve legacy saved-run compatibility.
- [x] Retain the same-case C0/C1/C2 AI Experiment required by E1 and the multi-agent minimum bar.
- [x] Update result labels, health metadata and final-review documentation/disclaimers.
- [x] Add migration/regression tests and run the full suite (346 passed).
- [ ] Restart API/UI and verify saved-run compatibility messaging.

## Evaluation warning

C0 and C2 must retain a common technical opportunity set. Report separately how C2 evidence screening, SMC routing, specialist review and critic decisions change trades; do not attribute every P&L difference to agent architecture alone.
