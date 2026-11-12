# AegisTrade AI
Three-month portfolio review and lessons to test

**Source 0.17.0 • Reviewed 11 November 2026 • Actual saved C2 research; simulated trading**

The completed portfolio made ₹21,314.06 including final marked holdings, a 4.26% return on ₹500,000. Seven of ten closed trades lost money, but three larger winners outweighed them. The technical reference returned 4.41%; the approximately₹727 gap does not establish that C2 improves financial performance. The first engineering priority is more complete dated financial evidence, followed by controlled entry-quality tests. No strategy, risk setting, model, active lesson memory or completed run was changed for this review.

## 1. What was checked

The supplied Desktop export contains 24 events: 14 BUYs and 10 sells. All dates, symbols, event types, quantities, prices and fees match saved run 95ef3724c1a94eb6bf69286a4c60272a. The run completed 63 sessions with status COMPLETED_WITH_GAPS. Four holdings remain open, as required by the no-forced-sale design. Saved state and CSV checksums are recorded in reports/portfolio_performance_review_20261111.json.

| Measure | Result |
|---|---|
| Starting capital | ₹500,000.00 |
| Ending cash plus marked holdings | ₹521,314.06 |
| Realized profit after modeled closed-trade costs | ₹5,310.26 |
| Unrealized profit including remaining entry fees | ₹16,003.80 |
| Total return | 4.26% |
| Maximum equity drawdown | Approximately2.92% |
| Closed wins / losses | 3 / 7 |
| Average winning / losing closed trade | ₹8,180.53 / −₹2,747.33 |
| Closed-trade profit factor | 1.276 |
| All recorded trading fees | ₹2,257.01 |
| Recorded-quantity adverse slippage price impact | Approximately₹2,256.65 |
| Research usage | 313 CLI invocations; provider/subscription cost excluded from INR returns and unknown per run |

The slippage amount holds the recorded quantities fixed; it is not a complete zero-cost counterfactual. Modeled fees are a flat proxy, not an itemized Indian tax/broker bill. Remaining gains can change after the chosen end date; no exit fee or future sale is invented for unsold holdings. Three-month annualized CAGR and Sharpe should not be presented as reliable long-term forecasts.

[[FIGURE:review]]

## 2. Why 30% winners still produced a profit

Closed winning trades earned₹24,541.58; losing trades lost₹19,231.32; net closed profit was₹5,310.26. Average winners were almost three times the size of average losses. This sample's result is consistent with allowing favorable trends to run; it does not prove that future trades have the same distribution. Optimizing win rate alone or forcing small take-profits could remove the larger gains supporting this quarter.

| Symbol | Entry | Exit | Net closed P&L |
|---|---|---|---|
| BHARTIARTL | 2023-12-04 | 2023-12-07 | ₹-3,428.74 |
| TMPV | 2023-12-04 | 2023-12-20 | ₹-1,766.27 |
| ICICIBANK | 2023-12-06 | 2023-12-20 | ₹-1,162.66 |
| BHARTIARTL | 2023-12-11 | 2023-12-20 | ₹-2,806.91 |
| AXISBANK | 2023-12-04 | 2023-12-21 | ₹-2,812.96 |
| ICICIBANK | 2023-12-21 | 2024-01-17 | ₹-2,310.18 |
| RELIANCE | 2023-12-28 | 2024-01-17 | ₹4,318.80 |
| ADANIENT | 2024-01-11 | 2024-01-18 | ₹-4,943.59 |
| BHARTIARTL | 2024-01-18 | 2024-01-31 | ₹6,141.87 |
| TMPV | 2024-01-03 | 2024-02-13 | ₹14,080.91 |

## 3. Why C2 finished behind the technical reference

Both active portfolios used the same data window, capital, costs, daily code exits and selected trailing settings. The technical reference entered eligible rule-based signals directly. C2 additionally required readable dated company evidence, an acceptable company assessment, valid citations and critic/code acceptance. These gates changed entries, sizes, cash and capacity. All 27 successful holding reviews returned HOLD; all 10 C2 sales came from the code trailing stop. The LLM did not initiate an EXIT in this run.

| Portfolio | Ending equity | Return | Maximum drawdown |
|---|---|---|---|
| C2 | ₹521,314.06 | 4.26% | 2.92% |
| Technical ROUTER | ₹522,040.73 | 4.41% | 2.41% |
| Passive equal-weight 20-stock comparator | ₹543,413.18 | 8.68% | 3.15% |

The passive comparator is not the Nifty 50 index and is not risk matched: it holds all 20 names without the active four-position/stop rules. This one quarter establishes neither AI superiority nor general superiority of passive investing. The active comparison also excludes model/subscription cost from financial return.

The per-stock differences below include both closed P&L and final marks. They reconcile the observed portfolios; adding or removing one trade would change other allocations, so these are not causal promises of extra profit.

| Symbol | C2 contribution | Technical contribution | C2 minus technical |
|---|---|---|---|
| HCLTECH | ₹0.00 | ₹5,351.80 | ₹-5,351.80 |
| HINDALCO | ₹0.00 | ₹3,063.99 | ₹-3,063.99 |
| HDFCBANK | ₹0.00 | ₹1,709.82 | ₹-1,709.82 |
| BHARTIARTL | ₹-3,058.36 | ₹-1,796.44 | ₹-1,261.92 |
| ICICIBANK | ₹-3,472.84 | ₹-3,262.43 | ₹-210.41 |
| RELIANCE | ₹12,000.90 | ₹11,590.54 | ₹410.36 |
| ADANIENT | ₹873.58 | ₹0.00 | ₹873.58 |
| SBIN | ₹0.00 | ₹-1,256.88 | ₹1,256.88 |
| AXISBANK | ₹-2,812.96 | ₹-4,428.65 | ₹1,615.69 |
| INFY | ₹0.00 | ₹-1,958.46 | ₹1,958.46 |
| TMPV | ₹17,783.73 | ₹13,027.44 | ₹4,756.29 |

HCLTECH's technical holding contributed₹5,351.80, including its final unrealized mark. C2 rejected its 18 January entry because the latest quarterly release excerpt lacked substantive results. HINDALCO contributed₹3,063.99 realized in the reference; C2's 1 December market assessment found review-report context rather than substantive results. HDFCBANK contributed₹1,709.82 realized in the reference; C2 lacked a readable qualifying financial filing. Those three missing contributions total₹10,125.61. These are data availability/extraction explanations, not proof that the companies were financially weak or that the model should have known they would rise.

Offsets were substantial: C2's TMPV contribution was₹4,756.29 higher because its entry/holding path differed, while missing some SBIN/INFY trades and a later AXISBANK trade avoided losses in the observed reference. Other allocation/timing differences nearly canceled the missed gains, leaving C2 only₹726.67 behind. The evidence supports a workflow/coverage limitation; it does not show a reliable profit edge from C2.

There were 13 blocks for no readable qualifying filing and 22 company-assessment blocks, plus 2 critic rejections. A specific BHARTIARTL rejection correctly caught a financial claim attributed to the wrong source ID. Do not disable that critic because the subsequent price path is known. Missing data and adverse financial evidence need separate diagnostics.

## 4. Lessons supported by observations; rules still need testing

### Entry gaps are the strongest specific next hypothesis

The three 4 December purchases—TMPV, BHARTIARTL and AXISBANK—followed approximately1.43–2.10% opening gaps and together lost₹8,007.98 when closed. Their actual opening prices were less favorable than the preceding signal closes, and signal stretch above EMA20 also varied. Test a predefined maximum opening gap/ATR or overextension condition on a separate period. Do not optimize a threshold solely to exclude these known losers. Some losses occurred without a large gap, and filtering these trades changes replacement candidates and cash use;₹8,008 is not a guaranteed counterfactual improvement.

### Re-entry is not uniformly bad

ICICIBANK's next-session re-entry after its 20 December stop lost₹2,310.18 when later closed. However, next-session RELIANCE and TMPV re-entries had final unrealized gains of₹7,682.10 and₹5,469.10. Requiring a renewed setup or testing a cooldown is a hypothesis; banning all re-entry could remove positive continuations. Do not blacklist particular stocks based on this quarter.

### Protect against correlated losses

Initial holdings included both AXISBANK and ICICIBANK. Several stop exits clustered on 20–21 December. Individual 1% price-distance risk limits do not eliminate common market/sector risk. Consider a time-appropriate sector/correlation exposure policy and test it separately. Expanding the candidate universe alone does not enforce diversified holdings. Gaps and costs can exceed planned stop-distance exposure.

### A raised stop can still realize a loss

All ten stop prices were independently reconstructed using initial protection, the highest prior completed close and fixed entry-signal ATR; all ten fills matched the daily OHLC/slippage rule. No stop/fill mismatch was found. SELL_TRAILING_STOP means the stop rose above its initial level, not necessarily above the entry price or fee-adjusted break-even. ADANIENT's closed loss was₹4,943.59 against initial price-distance exposure of about₹4,880.31; costs explain why its loss exceeded 1R slightly. Including estimated costs in planned risk sizing would be a calculation enhancement if that is the intended risk definition; gaps still prevent a guaranteed loss ceiling.

Do not automatically tighten the stop, widen it or add a small take-profit to make the old ledger look better. Any alternative can change both early losses and the large winners. Stop execution and short-term fluctuation risks are described in the SEC investor bulletin listed below.

## 5. Lower-risk sensitivity check — technical reference only

Using existing settings, two risk levels were checked on the reviewed quarter and a separate following quarter selected before this calculation. These are zero-generation technical ROUTER checks, not new C2 runs, not a broad parameter search and not an independently held-out evaluation programme.

| Period | Risk per trade | Return | Maximum drawdown |
|---|---|---|---|
| 2023-12-01 to2024-02-29 | 1.0% | 4.41% | 2.41% |
| 2023-12-01 to2024-02-29 | 0.5% | 3.31% | 1.52% |
| 2024-03-01 to2024-05-31 | 1.0% | -1.59% | 5.67% |
| 2024-03-01 to2024-05-31 | 0.5% | -1.19% | 3.18% |

Lower risk reduced drawdown in both checks; it also reduced the reviewed quarter's gain. This supports 0.5% as a lower-risk experiment, not a proven way to maximize C2 profit. The sizer uses multiple constraints, so changing risk does not simply halve every position. Do not compare these zero-model results to genuine C2 as if they were new LLM research.

## 6. Practical improvement order

1. Preserve this completed run and its current parameters as the development baseline. Keep realized/unrealized P&L and unknown model costs explicit.
2. Improve dated filings/excerpts for all candidates, not just stocks known to have risen. Preserve publication cutoffs, source hashes, reporting period/basis/units and strict citation validation. Freeze the improved data/research version for a new experiment; do not rewrite the completed run.
3. Test one entry-gap/extension condition against the unchanged baseline on separately chosen windows. Compare net return, drawdown, exposure, turnover and missed winners. A better result on this already inspected quarter is development evidence only.
4. For a lower-loss experiment, use the existing 0.5% risk control and compare honestly, accepting that gains may be smaller. Do not increase risk to recover prior losses.
5. Review re-entry/correlation policies only with broader evidence. Do not ban re-entry or remove entire strategies after two losing breakout trades.
6. Improve research efficiency separately from alpha. The 27 HOLD reviews used 163 of 313 invocations, about 52.1%. A 10-session review interval is an existing option for a NEW run; daily code protection continues, but later LLM exit detection can change, so it is not automatically equivalent. Fewer calls do not directly increase the application's INR return because inference costs are currently separate.

## 7. What happens to lesson memory?

Candidate observations are saved in reports/portfolio_candidate_lessons_20261111.json. They have not been inserted, accepted, frozen or indexed as active memory. The current reflection feature reviews research failures, not automatic portfolio P&L learning. C2 historical portfolios do not currently inject the reviewed playbook into their calls. Wiring these candidates into portfolio research would require explicit version/provenance binding, human review and date controls so future outcomes cannot leak into earlier decisions. Hard code risk and stop rules remain authoritative.

Use this quarter as a development observation. Freeze any hypothesis before evaluating separate later periods, assess multiple market conditions and retain unfavorable results. Improving one known ledger is not proof of future profitability.

## Sources and reproducibility

- Supplied Desktop export: 2026-11-11T07-42_export.csv; 24 rows checked against the completed saved portfolio.
- Full report:reports/portfolio_performance_review_20261111.json; closed-trade audit:reports/portfolio_closed_trade_review_20261111.csv; lower-risk comparison:reports/portfolio_risk_sensitivity_20261111.json. All additional analysis used zero new model calls.
- [CFA Institute: Backtesting & Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation). Supports separate-window/rolling testing, sensitivity checks and attention to survivorship/look-ahead bias.
- [SEC investor bulletin: Stop, Stop-Limit and Trailing Stop Orders](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-15). Supports the limits of stop execution and the risk of short-term fluctuations triggering exits.

Current-membership and unadjusted-price limitations remain. No live trades, production-policy changes or model-memory updates were made.
