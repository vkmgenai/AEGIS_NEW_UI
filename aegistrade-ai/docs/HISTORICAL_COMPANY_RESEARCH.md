**Current rules — v0.18.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.

# Historical company research in C2 — version 0.16.2

Implemented 9 November 2026. This extends the existing three specialists; no fourth agent or new generation provider is added. Generation uses the selected Codex CLI or OpenRouter transport. This implementation does not establish profitability.

## What changed

C1/C2 now require historical company financial filings and issuer news in addition to technical indicators and policy RAG. A new read-only company_evidence tool is exposed through the existing market MCP server. Market and critic both observe the same dated pack; C1 has the same additional tool. The market specialist returns a typed company assessment: status, summary, cited CMP IDs, event risks and limitations. Strategy receives that hand-off; critic independently reads the pack. SUFFICIENT means coverage sufficient for this bounded research task, not “financially healthy” or “buy”. REVIEW_REQUIRED and INSUFFICIENT_EVIDENCE cannot reach order approval.

Normal C2 still uses six model requests: each specialist requests its tools together, then interprets observations. Required tools are market_snapshot + company_evidence for market; search_policy + check_strategy for strategy; all three company/policy/strategy tools for critic. That is seven tool invocations and six normal generation requests, within the existing eight-request/16-tool ceiling. Corrections can consume remaining budget. There are no extra LLM calls for downloads, PDF extraction or order preparation.

## Sources and point-in-time rule

The public NSE corporate-announcement archive supplies results announcements, material disclosures and company press releases. Company press releases are issuer statements, not independent journalism. The downloader scans 180 calendar days in at most seven date windows and selects up to six archive PDFs: two results filings, one annual-report candidate, two issuer-news releases and one other announcement. Only approved NSE archive HTTPS PDF hosts are fetched; redirects, untrusted download hosts, files over32 MB and PDFs over 250 pages are rejected. Extraction uses the first 35 pages and up to100,000 characters per document. There is no OCR, paid news subscription or unrestricted model browser.

The selected daily decision cutoff is **15:30 Asia/Kolkata on the signal date**. Availability is the later of the exchange announcement and dissemination timestamps. A result for a September quarter published in November is unavailable to an October case. A filing disseminated at 15:40 is unavailable to that day's15:30 decision. Future/incorrect-company documents are excluded. Missing/invalid timestamps make exchange coverage unverified; they are never assumed earlier.

A coverage pass requires a completed bounded announcement scan and at least one readable recent financial filing containing financial-statement labels and numeric content. An annual-report link notice or generic cover letter cannot alone qualify. This is a content-availability check, not audited accounting validation. Extracted table windows can mix periods and consolidated/standalone sections; the prompt forbids quoting/comparing figures without explicit units, periods and basis. Full valuation, reliable ratio extraction, exhaustive news coverage and causal return predictions are not claimed.

Public archive records are retrieved now. Their exchange timestamps support disclosure timing; the system does not possess a certified historical revision chain for every attachment. Text snapshots and available PDF/text hashes are retained locally. An archive download may fail; the system records insufficient evidence and never treats an unreadable filing as clean fundamentals.

## Cache, tool and approval integrity

Data lives in data/company_research/packs/SYMBOL_YYYY-MM-DD.json, separate from the 81-passage policy Chroma corpus. Full extracted text remains in the local pack; the LLM receives bounded extractive windows, original URLs, publication/availability/retrieval timestamps, status and stable CMP IDs. No hidden labels or future outcomes are included. A SHA-256 binds the complete pack. Old/new versions are retained under data/company_research/snapshots/HASH.json when refreshing/importing, while the current pack is replaced atomically; historical research can be audited without restoring old approval eligibility. Market and critic observations must match the stored current pack and exact symbol/cutoff.

The order gate checks a financial-content citation, observed company citations and SUFFICIENT typed assessment, in addition to the existing technical/policy/critic checks. Start/resume compare the current pack hash and result linkage. Refreshing/importing/changing evidence invalidates older research and pending approvals. Old0.13 research without company hand-offs is intentionally ineligible. A human cannot bypass missing company evidence by approving the technical signal.

## UI guide

1. Restart API and dashboard on 0.15.0. Use the existing reviewer token; no new API key is needed for public archive downloads.
2. In Strategy Backtests, inspect a selected ROUTER date and hand it to AI Agent Experiments. Verify the case date and capital in the research form, especially if the browser already had older date fields.
3. Expand **Historical company research — prepare before paid calls**. Select the company and decision date. The saved TCS example is2026-10-23.
4. Click **Prepare historical company evidence**. This requires the reviewer token, downloads bounded public evidence and makes zero OpenRouter calls. Or choose **Inspect cached company evidence** to read the prepared pack without network work.
5. Inspect coverage status, source URLs, CMP IDs, availability timestamps and excerpts. SUFFICIENT is a coverage result, not an investment rating. Use the original filing to verify financial-table interpretation.
6. Run one C2 case with explicit paid consent. The service also prepares/checks packs automatically before any generation if needed. Missing coverage fails before paid calls. Every selected case must pass preflight.
7. Inspect the **Company research** result expander: assessment, risks, limitations, citations and pack hash. Only a completed passing C2 with sufficient company evidence can be handed to Supervised Trading.
8. Review the company assessment beside the exact proposal. Approve/edit/reject remains a separate human decision after research. Evidence refresh requires new C2/proposal/approval.

The technical-only replay remains deterministic. The new C2 historical portfolio invokes this tool before prospective entries and scheduled holding reviews, and implements explicit code/model exits plus unsold terminal holdings. Actual financial improvement remains unmeasured. See C2_HISTORICAL_PORTFOLIO.md. A holding EXIT may use a cited REVIEW_REQUIRED assessment; new entries/HOLD still require SUFFICIENT.

## Command-line preparation

From the project root, with internet access for the public archive:

```bash
.venv/bin/python -m scripts.prepare_company_research --symbols TCS INFY --date 2026-10-23
```

Existing packs are reused. Use --refresh deliberately to redownload; it changes provenance and can invalidate saved approvals. The CLI reads private environment settings without printing credentials. Its report is reports/company_research_preparation.json. A nonzero exit indicates at least one requested pack is insufficient or failed; a partial success is preserved.

## Independent press and archived newsletters

These are supported through a source/date-reviewed excerpt import, not automatic general web search. Public search results can be retrospective or carry unreliable timestamps. Obtain licensed excerpts with verified original publication metadata and use one or two per pack. They cannot replace the required official financial filing or an incomplete exchange scan.

Prepare a private JSONL file with fields: symbol, kind (news or newsletter), title, publisher, source_url (original HTTPS article), text (100–4000 character licensed excerpt), published_at (timezone-aware original timestamp or YYYY-MM-DD) and original_publication_verified=true. Optionally provide a later available_at. A named reviewer must verify the source and date; this is an attestation, not an automatic authenticity guarantee. Date-only material becomes available at the following IST midnight, so it cannot influence its own publication day's close. No arbitrary article URL is fetched by the importer.

```bash
.venv/bin/python -m scripts.prepare_company_research --symbols TCS --date 2026-10-23 --import-news /path/to/reviewed_excerpts.jsonl --reviewer "Actual reviewer name"
```

Do not substitute an event's occurrence date for its original publication date. Do not invent excerpts or backdate present-day articles. Refresh replaces the official pack; reimport supplementary material deliberately afterwards.

## Verification and known limits

The real TCS 2026-10-23 pack contains readable quarterly results and issuer releases. The downloaded INFY pack for that date currently lacks a readable qualifying financial attachment and stays INSUFFICIENT_EVIDENCE. This negative outcome is intentional. Some archive PDFs cannot be extracted within bounds or may be unavailable; no silent OCR/host/source fallback occurs.

The full local suite records 134 passing tests. Automated tests cover dissemination after the cutoff, future documents, unsafe URLs, unverified timestamps, unreadable financials, reviewed/date-only newsletter import, fabricated CMP citations, no paid call on missing evidence and invalidation of pending approval when the pack changes. Mocked generation verifies control flow; it is not a successful real paid C2 run. Full-stack Docker HTTP and genuine model quality remain separate verification tasks.

For Docker, the market MCP server now shares the API's data volume so both read the same company packs. Seed/cache data as described in the design guide. requirements-full.txt now includes pypdf. Run the normal test suite and verify actual HTTP tool observations before claiming deployment success.

The C0 baseline exposes the same cached company pack/coverage without semantic interpretation; its guard agreement remains the deterministic route reference, not company-quality success. Evaluation runs require prepared company packs before paid comparisons. Historical symbol changes are not inferred into another company history: unsupported/missing alias coverage remains insufficient.

## 0.16.2 evidence/context improvements

Evidence view company-view-v3 preserves results narratives/table headings, units, periods and reporting basis, and announcement bodies after exchange cover letters. It prioritizes one substantive recent financial source, gives shorter secondary excerpts, compacts repeated metadata and lists unreadable/non-financial attachments separately. Full text and complete metadata remain in hashed source packs; new views version the pack and preserve earlier snapshots. Preparing an older cached pack upgrades its view; changed evidence requires fresh C2.

Two December2023 quarterly PDFs exceeded the previous8 MB bound. The bounded limit is now32 MB; the250-page, first35-page extraction and100,000-character text limits remain. No OCR or normalized financial-ratio engine is claimed. Source text/PDF hashes and actual retrieval time are cached per approved attachment URL; ordinary preparation reuses unchanged cache. Explicit refresh bypasses the attachment cache.

The context ceiling is26,000 characters, recorded in prompts/config and context_usage events. Identical repeated observations are referenced to an earlier complete observation within the same specialist conversation; full repeated observations remain in the audit. New evidence is not silently dropped. Policy citations must match search_policy IDs; CMP citations stay in the company assessment/explanation.

Use AegisTrade_Portfolio_Simulation_Demo_Step_by_Step.docx for tested short-window settings and prerequisite steps. A coverage pass is still not a guaranteed positive assessment or profitable trade.
