# AegisTrade — Configurable Initial Stop-Loss UI

Version 0.19.2 • 11 November 2026

## Where to find it

Open Strategy Backtests. Above Simulation settings, choose Initial stop-loss method. The setting applies to both C2 historical portfolio and Technical-only baseline, including the technical reference created inside a C2 run. It does not modify the separate Supervised Trading order editor.

| Method | Field | Calculation from completed signal close |
|---|---|---|
| ATR distance, default | Initial stop distance (× ATR14 at signal) | Close − multiple × ATR14; default multiple 2.0 |
| Percentage below signal close | Initial stop loss (% below signal close) | Close × (1 − percentage / 100) |

Select the method first. Its relevant input is enabled inside the form. ATR multiples accept 0.5–10; percentages accept 0.1–50. The displayed percentage defaults to 5.0 when that method is selected; this is a UI starting value, not an optimized trading recommendation. Stops cannot be disabled by entering zero.

## Example

If the completed signal close is ₹1,000 and you choose 5%, the initial stop price is ₹950. It is fixed before the later-open fill. If the fill is ₹1,010, the stop is still ₹950; the actual entry-to-stop distance is greater than 5%. Fees, slippage and opening gaps can further change the realized loss. A buy whose executable entry is at or below its frozen stop is blocked by sizing/risk checks.

This is separate from Maximum risk per trade (%). That control limits planned portfolio-equity risk through whole-share position sizing. The selected stop distance, 20% per-name equity exposure limit and available fee-aware cash jointly determine quantity. The LLM does not calculate the stop or increase the risk limit.

## Interaction with trailing stops

The initial stop and trailing distance are separate settings. If trailing remains enabled, a higher completed close can tighten the stop using the selected trailing ATR multiple and entry-signal ATR. The stop never moves down, and an increase applies from the following session. Trailing can tighten a percentage-based initial stop as well.

Disable Enable trailing stop if you want the initial stop price to remain fixed. Profit-target exits, strategy exits and validated C2 EXIT decisions can still close a holding. Keeping the initial stop fixed does not disable those other exits. The end date still does not force liquidation.

## Run and inspect

Version 0.26 adds **Enable protective stop loss**. Clearing it disables the initial and trailing stop for the new run and disables stop-based SMC/breakout recovery. Quantity then uses cash and maximum-position exposure because there is no stop distance from which to calculate planned loss. Take-profit, strategy and validated adverse-evidence exits remain active. This can materially increase drawdown and holding time; evaluate it as a frozen development/held-out ablation rather than choosing it from the best historical result.

1. Choose the simulation engine and initial stop method.
2. Enter its distance/percentage, then review risk, trailing and profit settings.
3. Approve the replay rules and, for C2, authorize inference with the reviewer token.
4. Create a new run. The initial stop configuration is saved in that run and applies to screening estimates, fill sizing, execution and the matching technical reference.
5. Expand Initial stop-loss settings in the results to see the frozen method and parameters. C2 BUY ledger records now include initial_stop; holdings and exits retain their stop information.

Existing saved jobs are not retroactively changed. Legacy settings without the new fields keep the previous 2× ATR initial stop. Resuming a saved job is not a way to apply newly edited UI settings to its holdings.

## Activation while other jobs are running

The API advertises configurable_stop_loss_supported in /health. The dashboard refuses new configured-stop submissions against an older API rather than allowing it to ignore the fields.

If the API is still version 0.19.1, finish or pause active work before restarting the API and dashboard together from the same project folder. Stop the existing launcher with Ctrl+C in its terminal, then run:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
.venv/bin/python scripts/launch_local.py
```

Expect `/health` version 0.26.0 with `configurable_stop_loss_supported:true` and `optional_stop_loss_supported:true`. Do not start duplicate listeners on occupied ports. Existing saved runs retain their frozen settings and must not be resumed under a changed simulator version.

## Verification

195 software tests passed. Added coverage checks ATR and percentage formulas, finite/valid configuration, stock-screen quantity estimates, C2/reference execution consistency, gaps below the frozen stop and UI payload/result wiring. Generation is mocked in the relevant research tests. These are implementation checks, not a profitability evaluation.
