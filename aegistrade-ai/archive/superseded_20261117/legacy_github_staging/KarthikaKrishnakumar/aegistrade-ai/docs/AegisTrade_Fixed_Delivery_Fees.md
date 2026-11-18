# Fixed NSE delivery fees — version 0.25.2

The editable fee control has been removed. New C1, C2 and technical simulations use the supplied screenshot as a fixed cost assumption, with zero delivery brokerage. These are screenshot rates, not a claim that a current broker tariff or every historical tariff is identical.

| Component | Buy | Sell |
|---|---:|---:|
| Brokerage | ₹0 | ₹0 |
| STT | 0.1% | 0.1% |
| Stamp duty | 0.015% | 0 |
| NSE transaction charge | 0.00307% | 0.00307% |
| SEBI fee | 0.0001% | 0.0001% |
| GST | 18% of brokerage + NSE + SEBI | Same |
| Total turnover rate | 0.1187406% | 0.1037406% |
| Basis points | 11.87406 | 10.37406 |

For ₹100,000 turnover, modeled buy charges are ₹118.7406 and sell charges ₹103.7406. Each fill uses its actual modeled execution value after slippage. Internal arithmetic keeps precision; displayed totals may be rounded. This is not exchange/broker contract-note rounding.

Buy affordability and risk checks include buy fees. Exit proceeds and realized P&L deduct sell fees and the original entry fee. Profit targets solve for the selected net return after both sides and modeled slippage. The buy-and-hold reference pays the same buy charges and retains unsold holdings at the end.

Slippage is separate and remains configurable. The screenshot does not specify DP/depository charges, so those are excluded; personal capital-gains taxes are also outside transaction costs. Brokerage is the zero-delivery-brokerage option in the screenshot, not its possible 0.5% maximum. BSE rates are not used because the project uses NSE stocks.

Start a fresh simulation after this update. Previous ledgers remain unchanged. Older paused portfolios cannot resume under the revised engine policy. No LLM calls are required to calculate fees.
