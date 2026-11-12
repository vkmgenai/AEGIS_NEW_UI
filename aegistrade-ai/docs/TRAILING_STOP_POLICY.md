# Historical-portfolio trailing stops — 0.18.0

New historical portfolios enable trailing stops by default at **2 × entry-signal ATR14**. ATR14 measures the recent range of daily price moves. The multiplier is a configurable starting policy, not an optimized or proven profitable value. Applies to C2 simulation and active technical references; no live exchange order or additional model request is involved.

## Rule and timing

Initial stop = signal close − 2 × signal ATR14, with the existing positive-price floor. It is fixed before the later entry fill. Actual next-open sizing still checks the gap, cash and risk against that initial stop.

After a holding survives today's opening/intraday stop checks:

```
peak_close = highest completed close observed since the entry fill
distance = selected multiplier × ATR14 from the entry signal
next_session_stop = max(previous_stop, peak_close − distance)
```

The distance stays constant for that holding. The stop only rises. This is a daily-close trailing rule, not an intraday-high trailing rule. A newly raised stop cannot be used against an earlier low from the same daily bar. Missing holding bars do not update the peak or stop. All survivor adjustments are checkpointed before close-phase research; a saved close marker prevents repeated adjustments when a paused close resumes.

Example with entry-signal ATR₹10 and initial stop₹480:

| Completed-close observation | Stop effective next session |
|---|---|
| Highest close₹500 | ₹480 |
| Highest close rises to₹530 | ₹510 |
| Close pulls back to₹525 | ₹510 |
| Highest close rises to₹545 | ₹525 |

If the next open is below₹525, a simulated exit fills at that opening price with adverse slippage and fees. Otherwise an intraday low reaching the active stop fills using the stop price with adverse slippage and fees. A stop does not guarantee a fill at its stated price. Strategy exits and accepted C2 EXIT signals remain active and can sell first. Version0.18 adds an8% net take-profit target by default, alongside the trailing stop. The end date still marks surviving holdings without forcing a sale.

## UI and audit

1. Open Strategy Backtests and choose C2 historical portfolio.
2. Enter dates, capital, risk and costs. Leave Enable trailing stop checked and Trailing distance (× ATR14 at entry signal) at2.0, or deliberately choose another validated multiplier0.5–10.
3. Approve the displayed historical rules and external-inference allowance. Start a NEW run. Entry research and scheduled holding reviews use the existing C2 calls; stop calculations do not.
4. Inspect Trailing-stop settings and adjustments, the current/initial stop in open holdings and SELL_TRAILING_STOP in the ledger. A stop that has never risen remains SELL_STOP. Stop updates include date, symbol, old_stop, new_stop, highest_close, entry_signal_atr, distance and effective_after_close.

For technical-only runs the same controls apply, and results JSON includes stop_updates by strategy. The passive benchmark has no stops. The separate Supervised Trading workflow remains a single approved action and does not monitor holdings continuously.

Saved runs retain their original settings and history. Engine c2-portfolio-v3-fresh-adverse-profit and updated policy passage POL-43 require a new run rather than changing an old run's exits or rewriting earlier results. The cached policy index was rebuilt without generation calls. Refresh the browser; if backend health lacks trailing_stop_supported:true, restart your own launcher once.

## Verification and interpretation

Automated checks cover monotone stops, fixed signal ATR rather than fill-day ATR, no same-bar hindsight, opening gaps, missing bars, disabled mode, code/C2 exit coexistence, accounting, final surviving holdings and pause/resume without duplicate updates. reports/trailing_stop_verification.json records a controlled synthetic price path with MOCKED C2 responses and zero actual generation calls. It verifies execution mechanics, not a real model's decision quality or profitability.

A trailing stop can reduce some give-back after a favorable move. It can also exit before a recovery, incur more costs and still realize a loss if price never moves far enough or gaps lower. Assess it against the fixed-stop version using the same dates, data, costs and research conditions, with a separate period for evaluation. Existing unadjusted-price and current-constituent limitations still apply. General stop-order execution risks are described in the [SEC investor bulletin on order types](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-15).
