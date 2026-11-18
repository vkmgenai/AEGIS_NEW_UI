# NSEPython data, automatic stock selection and UI guide

Updated 9 November 2026. This is a 20-stock research subset of the Nifty 50, not an official “Nifty 20” index.

## Recommended capstone design

Use automatic historical replay for repeatable portfolio experiments after the user approves the selection/risk/cost assumptions. Demonstrate GenAI separately through the supervised path: deterministic shortlist → completed C2 market/strategy/critic research → code checks and sizing → exact human approval → final freshness/risk checks → simulated submission. The backtest does not ask an LLM to approve every historical fill and does not claim LLM-generated returns. C2 remains mandatory before every supervised proposal.

The ideal scientific universe is a genuine dated Nifty 50 membership snapshot from before the evaluation starts, or point-in-time membership if reconstituting throughout the study. Historical membership is different from historical prices. NSE Indices offers constituent-data products; do not pretend a current CSV is a historical constituent archive.

The implemented initial dataset uses the current official constituent CSV, explicitly marked `survivorship_bias: true`. The top 20 are then frozen using pre-period liquidity only. This avoids choosing five-year winners, but does not remove membership survivorship bias. For a rigorous rerun, supply a reviewed official constituent snapshot and its date using the downloader's `--constituents` and `--membership-asof` options.

## Downloaded dataset and provenance

- Library: nsepython 2.101, using its date-ranged equity-history interface, EQ series.
- Official universe CSV: https://archives.nseindia.com/content/indices/ind_nifty50list.csv . The other official host timed out; the NSE archive host succeeded.
- Evaluation window: 8 November 2021 through 8 November 2026, inclusive.
- Extra history for warm-up and pre-period ranking starts 1 July 2021.
- Downloaded rows: 26,580 across 20 stocks. Each stock has 1,242 rows inside the evaluation window and 1,329 rows including warm-up.
- Local OHLCV CSV: `data/nse_nifty20/ohlcv.csv`.
- Provenance, selected universe, ranking and checksums: `data/nse_nifty20/manifest.json`.
- Resumable request chunks: `data/nse_nifty20/chunks/`.
- Active source configuration: `data/market_config.json`, set to nsepython. This does not contain any API key.

The selected stocks, in frozen liquidity-rank order, are TMPV, RELIANCE, TATASTEEL, BHARTIARTL, INFY, TCS, SBIN, HDFCBANK, BAJFINANCE, ICICIBANK, KOTAKBANK, AXISBANK, HCLTECH, ITC, BAJAJFINSV, MARUTI, TECHM, HINDALCO, ADANIENT and HINDUNILVR.

A short warm-up sample was downloaded for the candidate list to screen it; full five-year histories were downloaded only for the selected 20. Full-history downloads for all 50 were not needed. The candidate list contains current members; the historical ranking is not proof that all those members belonged to the index in 2021.

Verified NSE symbol-name circulars support ZOMATO→ETERNAL, SRTRANSFIN→SHRIRAMFIN and TATAMOTORS→TMPV identifier normalization. Their official sources are recorded in `config/nse_symbol_aliases.json` and the manifest. This mapping does not adjust merger/demerger, split, bonus or distributed-share economics. Unexpected aliases stop the downloader instead of silently joining unrelated securities.

## Reproducible stock-picking criteria

There are two selection stages.

**Stage 1, freeze a 20-stock research universe:** before the evaluation start date, take up to 60 sessions per candidate and rank average daily Close × Volume, with at least 20 prior sessions. Pick the top 20. Only dates earlier than the evaluation start are allowed into this calculation. The ranking is not market capitalization, index weight, or return over the evaluation period.

**Stage 2, select trade candidates at each completed close:** screen the fixed universe using the following frozen research rules.

| Criterion | Rule |
|---|---|
| Data readiness | At least 60 historical sessions and ready indicators |
| Liquidity | At least ₹1 crore mean daily traded value over 20 sessions |
| Market risk | Abstain for HIGH_VOL, UNCERTAIN or WARMUP |
| ATR | Positive ATR; ATR/Close no greater than 6.5% |
| Price discontinuity | Exclude new candidates for 20 sessions after a raw close-to-close jump over 30%; this is a quarantine, not an adjustment |
| Entry | A valid existing EMA, RSI or breakout entry signal |
| Affordability | At least one whole share fits cash, planned-risk and position-value caps |
| Capacity | Exclude already-held symbols; at most four concurrent positions |
| Circuit breaker | No new entries when the daily-loss gate is active |

Eligible stocks receive a deterministic score: 70% strategy-specific signal strength, 20% same-session liquidity percentile and 10% lower ATR-fraction preference. Trend strength uses ADX plus 20-session momentum; RSI strength measures depth below the entry threshold; breakout strength uses breakout distance and relative volume. Exact formulas live in `aegistrade/selection.py` and are identified by `nifty20-selection-v1`.

Scores sort descending, with symbol as a stable tie-breaker. Selection uses only information available at that completed session. It does not read the remainder of the backtest period. Actual fill price and quantity are recomputed at a later eligible open, including fees/slippage. A ranked candidate can still be unfilled because of the next opening gap, cash constraints or risk checks.

Twenty stocks is the research universe, not the number of simultaneous positions. With limited money, fewer than four stocks may be affordable and cash may remain uninvested. The system should not force a trade simply to deploy all the capital.

These are explicit research hypotheses/settings, not promised profitable stock recommendations. Freeze them before held-out testing and report negative findings.

## Updated UI journey

### Market Data

This new workspace shows the download status, selected-stock count, cached chunk count, requested period, membership date/mode, top-20 ranking and per-stock coverage. It shows survivorship and unadjusted-price limitations. When the dataset is complete and not active, the authenticated reviewer can acknowledge its provisional nature and activate it. Activation persists the data-source setting and resets the API's data cache.

The downloaded NSE dataset is already configured as active in this workspace. Restart the running API/dashboard so the older process loads the new code and configuration. Use “Prepare OHLCV CSV download” and then “Download active OHLCV CSV” to export the active series.

### Overview

Charts now support five-year-sized history windows. The page displays the actual source and universe size. NSE raw-data and membership limitations appear at the top. The displayed workflow includes automatic selection, completed C2 research and mandatory approval.

### Strategy Backtests

Choose the date interval, starting money, risk, fees and slippage. Automatic screening/ranking is enabled by default. Approve the displayed assumptions before starting automatic historical replay. ROUTER and the three fixed strategies remain comparable configurations.

Results include the portfolio curve, cash/positions, passive benchmark and simulated ledger. Expand “Automatic stock-selection audit,” choose a date, and inspect ranked stocks, estimated shares and human-readable rejection reasons. “Research automatically selected stocks with C2” transfers the server-saved ROUTER run ID, date and capital into the research workspace; it makes no paid call by itself. It is disabled for fixed-strategy baselines or dates with no selected candidates. The research service reads the saved audit and restricts the hand-off to stocks that run actually selected.

### AI Agent Experiments

The no-spend shortlist preview shows code-generated candidates and rejection reasons. “Research automatically ranked eligible stocks” is enabled by default. The final selected date is used for the shortlist; early data outside the evaluation interval can supply indicator warm-up. Up to three of the highest-ranked eligible candidates are passed into the existing C0/C1/C2 comparison interface. If fewer qualify, fewer are run. If none qualify, no model call is made.

C2 is the main supervised research configuration. Its market evidence includes the code-produced selection score, rank and traded-value metric. Model tools do not get hidden future returns. C2 may fail or abstain; only completed, critic-accepted, code-validated C2 results unlock the next step. Reviewer authentication and explicit paid consent are still required.

The standalone research screen uses reference capital and the default supervised risk policy. A historical portfolio may have different cash/positions or a user-selected backtest risk percentage. The preview is therefore not an instruction to submit a trade from the historical portfolio ledger.

### Supervised Trading

A linked passing C2 case is mandatory. No unresearched manual stock picker or bypass exists. Starting the proposal revalidates the saved research and exact market data, computes quantity/stop/risk with code, then displays the full proposal for human approve/edit/reject. Resume rechecks the research digest and current evidence. Final quote, risk, kill-switch and idempotency checks remain unchanged. The broker remains a local simulator.

## Commands and caching

Install the market dependency if using a fresh environment:

```bash
.venv/bin/python -m pip install -r requirements-market.txt
```

Download/resume the current-constituent prototype:

```bash
.venv/bin/python -m scripts.download_nifty20
```

Use a genuine pre-period constituent snapshot for a new scientific run:

```bash
.venv/bin/python -m scripts.download_nifty20 --constituents path/to/official_dated_snapshot.csv --membership-asof 2021-10-29 --start 2021-11-08 --end 2026-11-08 --output data/nse_nifty20_historical
```

The example date is a user-supplied provenance declaration, not a claim that the repository includes that historical membership file. Do not relabel today's file with an older date. The tool does not purchase or fabricate membership history.

The warm-up rows cannot be used to evaluate an earlier trading window: that would evaluate dates preceding the frozen-universe selection. UI and backend enforce the evaluation start boundary while retaining earlier rows for indicators.

Requests are made in sub-40-day intervals through nsepython and cached. A provider error aborts rather than silently omitting a stock or falling back to synthetic/Yahoo prices. Re-running resumes cached intervals. SHA-256 and universe checks protect the completed cache from accidental modification; a minimum session-coverage check detects major truncation but is not a full exchange-calendar audit.

## Verification and limits

The NSE sample and full download succeeded. A ₹200,000 ROUTER replay across the evaluation window completed with 1,242 sessions, 24,840 selection-audit rows and 326 ledger events; it made zero paid LLM calls. Its run ID is recorded in `reports/nse20_simulation_smoke.json` and the complete saved result is in `data/simulation_runs/`. These are provisional raw-price replay outputs, not a return-performance claim.

All 64 tests pass. The UI was also exercised against the actual downloaded cache, including Market Data rendering, CSV export, the research screen and no-spend stock screening.

Tests check schema normalization, vetted aliases, bounded/resumable cache requests, future-data exclusion, selection feature causality, affordability and discontinuity filters, no model spend for an empty shortlist, dataset integrity and the interactive UI hand-off. The pre-existing mandatory-C2 and human-approval tests remain in force.

Two limitations are especially material: current constituent membership introduces survivorship bias; raw prices do not reconstruct splits, bonuses, mergers/demergers, distributed holdings or cash dividends. The new-entry discontinuity filter cannot repair an already-held position affected by a corporate action. Resolve those issues before interpreting returns as valid real-market strategy evidence. The data pipeline and the engineering workflow can still be demonstrated and evaluated honestly.

Official references: NSEPython source https://github.com/aeron7/nsepython ; documentation https://unofficed.com/nse-python/documentation/nsepy/ ; Nifty 50 constituents https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50 ; constituent-data products https://niftyindices.com/offerings/data-subscription .


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
