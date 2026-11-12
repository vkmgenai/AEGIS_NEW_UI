# Fresh entry review, adverse disclosures and profit exits — 0.18.0

These rules apply to NEW historical portfolios. They do not rewrite the completed December–February result. Start a new run after loading version0.18.0. Historical fills remain simulated under upfront-approved rules; supervised single actions still require exact human approval.

## Friday and non-trading gaps

With daily OHLCV, Monday's full signal becomes available only after Monday closes. Friday candidates therefore receive a zero-model DEFERRED_REVIEW rather than a queued Monday-opening BUY. At the next actual trading close, code screens them again using that session's indicators, liquidity, risk/cash/capacity and ranking. Ineligible candidates are cancelled. A still-selected candidate completes fresh C2 with company evidence available by that close. Its BUY can fill only at a subsequent eligible open, after the usual risk/research validation.

Example: Friday1 December2023 candidate → Monday4 December completed-close review → earliest Tuesday5 December opening fill. If Monday is a holiday, use the next available trading close and a later open. A reversed Monday signal cannot trigger the stale Friday entry. Friday and pre-gap signals are deferred before generation, avoiding unnecessary duplicate Friday/Monday research. Scheduled holding reviews and protective exits continue independently.

This is not a Monday pre-open/intraday strategy. That would require a timestamped intraday feed and a separate evidence cutoff. Never use Monday's closing price or filings released after an opening fill to justify that earlier fill. Known session dates are used for scheduling; later prices are not used in the earlier decision.

The audit retains DEFERRED_REVIEW/ENTRY_CANCELLED decisions, the original signal date, the fresh research date and the actual fill date. OPEN/CLOSE checkpoints preserve deferrals and cached research through budget/provider pauses without duplicate fills. A last-session candidate cannot cause an out-of-window entry.

## Adverse-risk research instead of automatic financial rejection

The company tool scans official NSE issuer-disclosure metadata in the preceding180-day window, filtered to the case's15:30 IST cutoff. It prioritizes adverse-event keywords and recent generic material/regulatory disclosures, then extracts up to eight matched risk attachments in addition to the existing bounded financial/news selection. Future releases are excluded. The scan reports a source, date window, metadata fingerprint, candidate count and SCAN citation ID.

Financial evidence retains its own coverage status. A missing or uninterpretable financial table does not by itself end research when the adverse scan is ready. The market specialist can return LIMITED coverage, NO_MATERIAL_ADVERSE_FOUND, the observed SCAN citation and explicit missing-financial/independent-news limitations. The critic independently reads the same current company pack and checks claims. A code-qualified technical entry can then pass; numerical financial claims still require readable correctly attributed documents.

MATERIAL_ADVERSE or UNKNOWN does not authorize ENTER/HOLD. A cited material-risk assessment can support a risk-reducing EXIT. Incomplete metadata scans, invalid availability timestamps, too many matched attachments for the bound, unreadable risk attachments, missing/fabricated citations or rejected criticism cannot become a positive entry authorization. All claims and both specialists' observations remain bound to the current company-pack hash and policy version.

This is a bounded official-disclosure review. It is not comprehensive independent press, an assertion of clean fundamentals, a valuation or proof that no adverse event exists. The market specialist can still abstain where the observed coverage does not support a credible bounded assessment. The code's technical eligibility/entry, capital, risk and exposure rules remain mandatory; an LLM cannot simply label an ineligible stock “strong”. No new specialist or normal extra generation round is added: ordinary C2 still uses six invocations, with an eight-invocation ceiling.

## Eight-percent net profit target

New UI/API historical runs default to take_profit_percent:8.0. This is a transparent research assumption selected for the requested demo, not a validated optimum. The UI exposes Take-profit target (% net return; 0 disables). Both active C2 and technical-reference portfolios use the selected value. Passive buy-and-hold has no profit target.

The target is per holding and closes the whole position. It aims for8% over the position's entry cost, NET of modeled entry/exit fees and accounting for adverse slippage in the executable trigger:

```
entry_cost = quantity × actual_entry_price + entry_fee
trigger_reference = entry_cost × (1 + target_percent / 100)
                    / [quantity × (1 − sell_slippage) × (1 − sell_fee)]
```

An opening quote at/above the target fills at that open with modeled slippage/fees. Otherwise an intraday high reaching the target fills using the target reference with those costs. Existing stop protection remains active. Opening gap events occur first; if both the stop and target are touched later in an ambiguous daily bar, assume the stop happened first. This conservative assumption avoids choosing the favorable sequence without intraday evidence.

Profit exits are SELL_TAKE_PROFIT. Holdings and sales expose the target reference; results show target percentage and timing rules. No model call or C2 veto delays a protective stop or profit exit. Targets do not guarantee real-world fill prices or future profit. A fixed target can cut off a larger trend and reduce returns; compare new complete runs before concluding that the change helps. A fresh eligible C2 signal can still authorize a subsequent re-entry under the same timing rules. More turnover can increase fees and re-entry research usage.

The end date does not force a sale. Positions that have not triggered any exit remain open and marked to the final available close. Code strategy exits and accepted C2 EXIT remain active alongside stop and profit rules.

## UI rehearsal

1. Confirm backend health version0.18.0 and fresh_adverse_profit_policy_supported:true. Refresh the dashboard after the coordinated restart.
2. In Strategy Backtests choose C2 historical portfolio. Use a NEW run: capital₹500,000, dates2023-12-01 to2023-12-05 for the first short rehearsal, ROUTER, risk1%, fee/slippage10/10 bps, trailing2ATR and take-profit8%. Use a modest explicitly consented allowance such as32 after confirming account readiness. Friday-to-Monday alone cannot fill an entry under the new review policy.
3. Prepare or let the worker prepare the refreshed decision-date company pack. Existing packs without the new risk-scan metadata are upgraded by refetching their genuine dated sources; cached attachments are reused. Inspect financial coverage separately from adverse-scan readiness and read the limitations. Do not refresh pack hashes during an active run.
4. Approve the historical rules and inference allowance, then run once. Friday should show DEFERRED_REVIEW with zero entry-generation calls. Monday can show ENTER, cancellation or a documented adverse/unknown-risk block; Tuesday can fill a passing entry.
5. Inspect Exit rules, profit target and stop adjustments, open holdings, ledger events and saved C2 company/critic traces. A short rehearsal may not reach8%; never fabricate a rise or weaken research to make a sale appear. The profit mechanism is separately verified with synthetic deterministic tests.
6. For a new three-month experiment, retain the selected target and use the planned period/capital. Original0.17 results and candidate lessons are historical development evidence, not measurements of these new rules. Use separate periods to evaluate the new policy.

## Validation scope

Tests use synthetic OHLCV and explicitly mocked generation. They cover Friday→Monday→Tuesday ordering, holiday delays, signal cancellation, pause/resume idempotency, weekend adverse releases, LIMITED evidence acceptance in both actual C1/C2 graphs, independent critic observations, material/unknown risk rejection, bounded/unreadable coverage, false citations, fee-aware8% returns, opening gaps, ambiguous stop/target bars and portfolio accounting. Local neural RAG is rebuilt for the updated policy passages. No real model inference, new user simulation or automatic resume is performed during this change. Actual provider behavior and financial effectiveness remain separate demo/evaluation work.
