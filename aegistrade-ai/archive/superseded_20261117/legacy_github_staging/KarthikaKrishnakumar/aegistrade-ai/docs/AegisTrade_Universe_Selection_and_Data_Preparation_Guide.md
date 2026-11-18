# AegisTrade — Universe Selection and Data Preparation

Version 0.20.0 • 12 November 2026

## 1. Three separate choices

Market Data now contains a Universe dataset selector. The existing data remains available; choosing another item to inspect does not activate it or change a running portfolio.

| Choice | Membership | Local data directory |
|---|---|---|
| Existing Nifty 50 — frozen top 20 | Original pre-period-liquidity-selected research subset | data/nse_nifty20 |
| Nifty 100 — frozen constituent snapshot | All 100 members in the official snapshot frozen on 12 November 2026 | data/nse_nifty100 |
| Diversified research — frozen 30 | The agreed 21 established-company, 6 cyclical and 3 event-research cases | data/nse_research30 |

These are research universes, not expected winning-stock ratios. The 70/20/10 mix describes counts in the 30-name list, not capital allocation, a promise of profit, or the composition of every four-position portfolio. The custom set includes names outside the official index snapshot and is not described as an exact Nifty 100 subset.

Current constituent and curated selections applied to older dates have survivorship/selection bias. The deliberately included event cases support controlled research evaluation; a combined result is not a random representative market sample. Historical constituent reconstruction and corporate-action-adjusted accounting remain separate improvements.

## 2. Frozen 30 members

| Group | Sector | Symbols |
|---|---|---|
| Established | Banking/lending | HDFCBANK, ICICIBANK, SBIN, BAJFINANCE |
| Established | IT | TCS, INFY, HCLTECH |
| Established | Consumer | HINDUNILVR, ITC, DABUR, TITAN |
| Established | Pharmaceuticals | SUNPHARMA, CIPLA, DRREDDY |
| Established | Industrials, telecom, diversified | LT, BHARTIARTL, RELIANCE |
| Established | Automobiles | MARUTI, M&M |
| Established | Utilities | NTPC, POWERGRID |
| Cyclical | Metals | TATASTEEL, HINDALCO, JSWSTEEL |
| Cyclical | Energy/mining, aviation | ONGC, COALINDIA, INDIGO |
| Event research | Banking, telecom, media | YESBANK, IDEA, ZEEL |

The definition is retained in config/universes/research30.csv and checked for 30 distinct symbols and exact 21/6/3 counts. Research-group labels are UI/evaluation metadata; they are not passed to the LLM as company judgments. C2 must assess the dated evidence rather than assume an event-case company is always bad.

## 3. How to use the selector

1. Open Market Data. The top status cards describe the active dataset; the Universe dataset selector chooses the dataset you want to inspect or prepare.
2. Select the desired universe. Review its membership, requested period, history coverage, bias and raw-price caveats. The Nifty 100 and custom 30 memberships can be inspected before prices finish downloading.
3. If history is not ready, enter the reviewer token, expand Prepare or resume this universe, confirm Dataset evaluation start/end and click Prepare selected universe. Defaults use the existing dataset's requested window where available, supporting comparable experiments.
4. Public-data preparation runs asynchronously. Its status/message refreshes every five seconds while queued/preparing; Refresh download status remains available. A single data worker prepares one universe at a time. This worker is separate from the C2 inference worker.
5. If preparation fails, inspect the error. Resolve source/connectivity problems and resume with the same frozen dates; cached chunks are retained. No synthetic/Yahoo fallback is used and failed preparation does not switch the active dataset.
6. When the selected dataset is complete, tick Use this provisional research dataset with the displayed limitations understood. Click Use downloaded NSE data. Activation requires the reviewer token and validates the dataset checksum and frozen membership.
7. Open Overview or Strategy Backtests and confirm the active instrument count/name before creating a new run. Existing result panels refer to their saved data, not necessarily the currently active universe.
8. To return to the original dataset, select Existing Nifty 50 — frozen top 20 and activate it with the same acknowledgement. No redownload is needed while its validated cache is retained.

A selection alone is not activation. Preparation alone is not activation. Neither starts C2 research or a portfolio. Newly prepared histories are deliberately not activated automatically.

## 4. Historical data preparation

Downloads use NSEPython and public official NSE sources. Compatible complete history from another retained universe is reused by symbol and validated source checksum before new requests are made. Reuse does not edit the source files. New requests are bounded to under forty calendar days and cached; data CSV and manifest publication are atomic.

The official Nifty 100 definition is retained in config/universes/nifty100_snapshot.csv with a source/date/checksum JSON record. Official security-master and symbol-change snapshots are also retained with checksums. Verified symbol intervals allow requests under historical names and normalization to one current identifier; examples include LTI → LTIM → LTM and ADANITRANS → ADANIENSOL. Identifier normalization does not reconstruct merger/demerger distributions or adjust prices.

Not every current constituent existed as a listed security throughout the five years. New datasets retain shorter observed histories with explicit coverage metadata; the code still requires historical indicator warm-up before a stock can be eligible. Missing prices are never invented. Official listing metadata limits requests before a security's listing where appropriate. Coverage is checked over each observed span; an early ending still requires investigation and is not automatically proof of a delisting. Existing legacy top-20 validation remains unchanged.

Prices remain raw/unadjusted. New stock histories and more companies do not by themselves fix dividends, splits, bonuses, demergers, exchange-calendar reconciliation or stale holding marks when observations disappear. Inspect these limits before making financial claims.

## 5. Saved-run consistency

New C2 portfolios capture their market frame and save universe/dataset provenance with the existing data fingerprint. An active worker retains its captured frame when another universe is activated; it does not begin trading the new universe midway through the run.

On resume, an NSE portfolio resolves its original retained dataset by checksum instead of using whichever universe is active today. Missing or changed original data fails closed. Existing prompt, corpus, engine, backend and memory compatibility guards still apply; resolving the old dataset does not permit mixing incompatible old policies. Old runs without a universe ID can still be resolved by their original data checksum. All eight retained NSE run fingerprints matched their original data during implementation verification.

Technical simulations and new research experiments also capture active dataset/provenance at submission. Switching clears transient stock-shortlist and linked-case selections in the browser, while saved results, broker records, lessons, configuration credentials and original data remain retained. Outstanding supervised proposals are still subject to current provenance/freshness checks and may require a fresh researched proposal if their supporting context changes.

## 6. RAG and inference behaviour

More stocks broaden the screening pool. They do not cause an LLM call for every stock every day: code still screens and ranks before C2 entry research and scheduled holding reviews. Actual case counts can nevertheless increase or change, so do not assume a larger universe has the same inference cost.

The same policy RAG, read-only market/strategy/knowledge MCP tools, materiality rubric, critic, initial/trailing stop, target, sizing and consent rules apply. Dated company packs are prepared for selected symbol/session cases as before. Official symbol continuity also applies to dated company announcement requests for renamed securities. Incomplete financial/adverse evidence can still block a candidate; a larger price universe does not guarantee sufficient company evidence.

The downloader and universe activation make zero generation calls. C2 runs and explicitly authorized resumes continue to consume the selected model backend's allowance. No application change silently resumes a paused provider job.

## 7. Comparing universes fairly

For a universe comparison, keep dates, capital, code strategy/risk settings, costs, stop/target/trailing settings, model/backend and memory version fixed. Change only the universe, record each run ID and manifest hash, and compare coverage, exposure, drawdown, returns, research errors and inference usage. Report the event-case subgroup separately when discussing adverse-event research quality.

The active cache retains the original requested five-year window for initial preparation. A current-member snapshot is not a historically unbiased starting universe, even when data and RAG cutoffs are causal. Date-separated model evaluation also does not eliminate historical facts already present in pretrained model weights. Describe measured evidence and limitations rather than promising profitability.

## 8. CLI and API

The UI is the recommended workflow. A local resumable downloader is also available:

```bash
.venv/bin/python -m scripts.download_universe --universe research30
.venv/bin/python -m scripts.download_universe --universe nifty100
```

Optional --start and --end accept ISO dates; --data-root selects the local dataset root. Do not launch a second downloader for the same universe while its preparation is active. Completed universes are preserved rather than overwritten. CLI completion still requires explicit activation in the UI.

Read endpoints: GET /market/datasets and GET /market/dataset?universe_id=research30 (or nifty100/nifty20). Protected writes: POST /market/dataset/prepare with universe_id/start_date/end_date and POST /market/dataset/activate with universe_id/acknowledge_provisional_data. Unknown universe IDs and incomplete or mismatched datasets are rejected. The health capability universe_switching_supported identifies the updated API.

## 9. Verification and operational status

215 automated tests passed, including authenticated switching and switch-back, preservation of original files, rejected incomplete/mislabelled universes, original-data resume resolution, cached history reuse, preparation failures, shorter listing spans, official identifier intervals and the UI controls. Research generation is mocked in the applicable tests.

The universe definitions and official snapshots are ready. The custom 30-stock public-history dataset completed and passed checksum/membership validation during this update. The official Nifty 100 history preparation is continuing next; it may take time or stop on source errors. Inspect the current Market Data preparation status rather than treating this document as a completion receipt. The existing top-20 dataset remains active until you explicitly activate another complete dataset. No portfolio simulation or model call was started for this change.


## 10. Policy RAG update and company-archive coverage

POL-37 (capacity) and POL-58 (universe provenance/bias) now describe the three selectable universes. The 81-passage neural policy index was rebuilt and its fingerprint verified; 27 targeted RAG/agent/universe checks passed with no generation calls. Use a new C2 run for the corrected corpus; old saved results remain retained and prior corpus-fingerprint guards still apply.

At this check, 14/30 custom-universe symbols and 20/100 official-universe symbols had at least one cached company pack. These are any-pack counts, not full five-year coverage or a guarantee of readable/sufficient evidence. The portfolio prepares the selected stock's exact-date company pack before generation. It does not preload all historical news for every stock/session, and unavailable archives can still cause a block. Price-universe preparation and company-evidence preparation are different operations.
