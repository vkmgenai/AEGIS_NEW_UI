# One-page threat model: simulation only

Assets: order approval tokens/hashes, local SQLite records, OpenRouter API key,
strategy policy, research data, agent traces and lesson playbook.

Trust boundaries: untrusted market/news input; retrieved knowledge; LLM output;
read-only MCP tools; authenticated reviewer; broker simulator; monitoring.

Threats and controls:
1. News prompt injection -> retrieved text is evidence not instructions; block known
   injection patterns; code enforces strategy/risk, independent of generated prose.
2. LLM hallucinated price/quantity -> compute using validated OHLCV and Python,
   never an LLM estimate. Missing or invalid inputs fail closed.
3. Approval tamper -> SHA-256 of canonical exact order payload; edit invalidates.
4. Replay/duplicate after timeout -> request ID idempotency and broker status query.
5. Stale data or fast price jump -> timestamp/price deviation check before write.
6. Credential leak -> environment/secrets only, scrub prompts/logs, no broker keys.
7. Overbroad agent tools -> only a restricted non-LLM action node can write.
8. Denial of service/tool loop -> per-run tool and LLM budgets; CI limits; timeout.
9. Insider approval abuse -> demo bearer token only; real deployment needs accounts,
   MFA, RBAC, two-person controls and tamper-resistant audit logs.
10. Dataset leakage -> held-out files must not be mounted in the agent context.

Known limitations: regex guard can miss attacks and block legitimate work; MCP
read-only HTTP services have no authentication in the Docker demonstration network;
Streamlit and Grafana demo credentials are not production hardened. This design is
not fit for internet deployment without an expert security review.

Mandatory research gate (9 November 2026): orders require completed three-specialist C2 provenance, accepted critic and code validation. Normal/streaming start and approval resume reject missing, failed or changed research. A digest binds the proposal to the exact saved result; current historical evidence is rechecked. Old workflows without C2 cannot resume to approval. This does not turn model acceptance into a profit guarantee.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.

Company-source controls: archive downloads allow only NSE HTTPS PDF hosts and refuse redirects, credentials-in-URL, oversized/non-PDF attachments and excessive page counts. The model cannot select a download URL, symbol or cutoff. Retrieved financial text and reviewed imported excerpts remain untrusted; prompt injection cannot grant tools or broker-write access. Reviewer-attested news publication dates are not independently certified. Full extracted text is local; generation sends bounded excerpts and metadata to OpenRouter after consent. A corporate-action alias does not automatically authorize a different company-symbol history.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
