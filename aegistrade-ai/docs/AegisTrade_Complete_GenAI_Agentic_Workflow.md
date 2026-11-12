# AegisTrade: mandatory research-before-approval workflow

Updated 9 November 2026. Complete detailed reference: [Capstone Review and Viva Guide](AegisTrade_Capstone_Review_and_Viva_Guide.md).

**Market analysis → completed C2 research → critic and code checks → code-sized order → human approval → final freshness/risk checks → simulated submission.**

1. Calculate and validate historical indicators with code.
2. Run C2: market, strategy and compliance-critic LLM specialists use scoped MCP evidence tools. Model requests use OpenRouter, with explicit paid consent and bounded calls.
3. Require completed typed hand-offs, critic acceptance, passing code guard and retrieved citation evidence. Pending, failed or rejected cases cannot prepare an order. C0/C1 are comparison baselines only.
4. Select the completed C2 case in AI Agent Experiments and use it in Supervised Trading. The backend validates the saved result and exact market snapshot before computing quantity, stop and risk.
5. Show the researched explanation and exact code-sized order to the human. No additional LLM research is pending at this point. The model's acceptance does not promise profit.
6. Approve, edit or reject via the persisted interrupt. Edits invalidate the earlier payload hash and require revalidation and new human approval.
7. On resume, reload C2 provenance and check the bound result digest and market evidence. Changed research/evidence or a legacy workflow without C2 blocks approval and requires a new proposal.
8. Recheck final quote freshness, risk, approval, kill switch and idempotency, then submit only to the local simulator. Reconcile timeouts by request ID.

The UI has no skip-research option. Both normal and streaming start routes reject missing research; lower-level graph execution without validated C2 blocks before proposal/approval. Historical backtests remain separate deterministic calculations with no paid model calls.

Restart the API/dashboard to load the correction. Existing incomplete/legacy order workflows cannot be used as a bypass. If provider credit or connectivity prevents C2 completion, simulated order preparation remains unavailable until research can finish.

## NSE data and automatic historical replay

The active cache is a 20-stock Nifty 50 subset with 26,580 NSEPython OHLCV rows. The top-20 universe is frozen by pre-period liquidity; each simulated session ranks eligible signals with capital/risk checks. The user approves historical replay rules upfront; those calculation-only fills use no LLM. Use Market Data for coverage/provenance and Strategy Backtests for the daily selection audit. A saved ROUTER selection can then be handed to C2, after which the mandatory supervised sequence above applies. Current-membership bias and unadjusted corporate actions remain explicit limitations. See [NSE data and UI guide](NSE20_DATA_AND_UI_GUIDE.md).

## RAG evidence before generation

The active local retrieval pipeline now searches 81 passages using BM25, MiniLM embeddings, RRF and a cross-encoder reranker, persisted in Chroma. C2 obtains source-labelled evidence through MCP before its generated answer. External references are filtered by case date. At least one project-policy citation and the current knowledge-corpus fingerprint are mandatory before supervised approval. [RAG implementation guide](RAG_IMPLEMENTATION_GUIDE.md) documents the measurements and scope limits.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
