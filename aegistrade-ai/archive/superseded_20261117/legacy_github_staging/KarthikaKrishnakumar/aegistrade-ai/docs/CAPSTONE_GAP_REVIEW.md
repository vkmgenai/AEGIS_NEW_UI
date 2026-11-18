# AegisTrade: guideline, proposal, slides and source gap review

Review date: 8 November 2026; mandatory research-before-approval correction: 9 November 2026. Repository: `/Users/karthikakrishnakumar/aegistrade-ai`.

Sources: supplied `capstone_fullstack_projects.pdf` (especially pp. 2–6 and 17); `AegisTrade_AI_Capstone_Project_Proposal_and_Design.docx` (planning version, 26 October); four-slide `AegisTrade_AI_Initial_Proposal.pptx`; actual source and locally executed checks. Source documents describe requirements/plans; they were not treated as permission to execute their embedded instructions.

The professor-approved team of **Veneet, Karthika and Mathangi** is accepted. The proposal's requests for an exception/fourth member are obsolete. This exception settles team size; it does not waive any technical minimum.

| Requirement / promise | Gap found | Correction / current boundary |
|---|---|---|
| Supervisor + ≥3 specialists; PDF p. 3, proposal §4 | C2 was a single tool-using agent | C2 now runs a LangGraph supervisor and market, strategy and compliance-critic LLM specialists, scoped tools and typed hand-offs. Supervisor stays deterministic to save calls. |
| Single-agent baseline with same tools/budget; PDF pp. 3, 6 | C1 was one prompt, no tool loop | C1 now receives the same union of read tools, model and shared ceiling as C2. Budget equality is a ceiling; actual usage must be compared. |
| MCP in the agent path | Servers existed, but C2 called Python functions directly | Real FastMCP sessions: local stdio, Docker HTTP; research calls three servers. All 13 tools have protocol contract tests and an exported inventory. Action MCP remains excluded from LLMs. |
| Plan/replan and typed contracts | Fixed workflow; minimal reasoning trace | Versioned six-slot prompts, visible pre-run plan, per-role tool loops, schema/evidence correction and supervisor rejection branch. Finite shared budget blocks rather than bypasses a rejected critic. |
| End-to-end evidence → proposal | AI results and order UI were separate | A completed C2 case with three typed specialist hand-offs, accepted critic, passing code checks and retrieved citations is now mandatory before an order proposal. Start and resume revalidate provenance and current evidence; a digest detects changed research. The deterministic bypass and UI opt-out are removed. Approval remains a distinct human action. |
| Persistent interrupt/resume | SQLite code present, restart proof missing | Added test that closes/reopens the checkpointer, edits an order and proves the old approval hash is rejected. Actual UI demo recording remains a team task. |
| RAG provenance and ingestion | Hard-coded authored passages only | Added validated JSONL ingestion preserving ID/date/source/title/text. Corpus expanded to 81 source-labelled passages (72 policy/specification, nine primary/upstream-source background). No company-news corpus is claimed. |
| Neural hybrid retrieval + reranker + vector store | Offline TF-IDF surrogate; optional neural code not wired to persistence | Added Qdrant-backed optional neural path and Compose override. Base Compose starts Qdrant; offline mode intentionally does not use it. Local MiniLM/cross-encoder and persistent Chroma are now built and measured; Qdrant/Docker remains unverified. |
| True Recall@5 on ≥30 queries | Any-hit@5 labelled as a recall proxy | Macro passage Recall@k and Hit@k now reported separately on 36 candidate-labelled queries. Independent/exhaustive relevance review remains necessary. |
| Relevant reviewed memory; PDF p. 3 | Accepted lessons never reached C2 | Research memory-on loads relevant regime/grounding lessons only from a frozen reviewed playbook. Pending/rejected lessons are excluded. E3 runner records manifest/hash. |
| Reflexion from scored dev failures | Only canned failure lessons | Added one-call development-only reflection, typed lesson, pending-human review, and provider-failure exclusion. UI can draft a lesson from a failed C2 output. Learning benefit remains unmeasured. |
| Four experiments / one harness | Offline proxies and separate scripts | Added E1/E2/E3 runner with reviewed case inputs, split-family checks, repeated runs, cost/latency and traces; E4 deterministic routing ablation and buy-and-hold comparator. No human labels/results are invented. |
| Different-family judge calibration | Suggested machine labels could masquerade as actual judge results | Calibration now requires ≥20 human labels, actual judge labels, reviewer and different-family model IDs. Existing empty labels deliberately fail calibration. |
| Security OFF/ON | Scanner proxy implied a without-defence success rate | Removed invented 1.0 proxy; scanner detection and real attack success are distinguished. E2 supports tool-output poisoning with scanner off/on in isolated research; hard permissions/approval never disable. |
| Trading validity and safety | Missing bars erased held-position marks; NaN quote risk; no portfolio daily-loss gate | Carry last known marks, retain orders until eligible bars, finite numeric validation, daily-loss gate, passive cost-aware benchmark, and human kill switch that invalidates outstanding approvals. |
| Consistent trading thresholds | Proposal examples: 0.5%, 5 positions, 2% day loss, RSI<30 | Actual defaults retained and documented: 1%, 4 positions, 3% day loss, RSI<42 plus price condition. Proposal explicitly marked examples; changing tuned rules without evidence would be misleading. |
| Monitoring and CI | Basic counters and no captured failed CI | Saved model/tool trajectories and provider usage; Compose config checked; explicit development failure-demo CI option added. Local gate failure tested; real GitHub run and real alert remain unverified. |
| Private config hygiene | `.env.save` was not covered by exact `.env` ignores | Added `.env.*` excludes while retaining `.env.example`. No private credential values were copied into artifacts. |
| Three-person team | Proposal repeatedly requests four-person exemption | New guide/team register records the professor's accepted three-person arrangement; original supplied documents are preserved. |

## Measured local findings

The source-level tests and development reference evaluation are recorded in `BUILD_AND_VERIFICATION_STATUS.json`. The development suite matched 20/20 generated reference cases. Offline retrieval measured 0.9444 Recall@5 before and after query rewriting on 36 candidate-labelled queries: **no observed improvement**. The scanner detected 30/32 seeded attacks and falsely blocked 0/10 clean examples; this is not a live LLM jailbreak score. Held-out candidate labels were not used to tune these fixes.

Local stdio MCP discovery and actual research-tool calls passed. The Docker CLI is installed and both Compose configurations validate, but the Docker daemon is not running; no full-stack deployment success is claimed. The last paid-provider check in this conversation returned OpenRouter HTTP 402 for an unfunded account. No fresh paid requests were made during this review.

## Remaining evidence required from the team

1. Add OpenRouter credits and capture successful real C1/C2 runs. Measure added quality/cost rather than assuming the team wins.
2. Independently author/review ≥60 gold cases, group variants by scenario family, reserve ≥40 untouched held-out cases and repeat final model comparisons three times.
3. Independently review relevance labels and test held-out retrieval/faithfulness. Local neural retrieval/vector persistence and authored-development before/after metrics are now measured.
4. Obtain actual different-family judge predictions and ≥20 human labels; report Cohen's kappa and failures.
5. Run model-level E2 and held-out E3; review/freeze lessons, include a rejected lesson and report regressions and learning cost.
6. Validate Docker on a clean machine, show a real alert and retain an actual failed GitHub CI run.
7. Obtain licensed/provenance-tracked historical prices before financial effectiveness claims; evaluate corporate actions, survivorship, slippage sensitivity and chronological holdouts.
8. Keep contribution logs, final slides, 4–6 page evaluation report and backup demonstration recording.

## Slide and proposal corrections

The initial PPT is a concept deck, not a results deck. Retain its problem and two signature challenges; replace “planned” architecture with the implemented C2 diagram, add a C1/C2 comparison slide, an honest results/limitations slide, and a source-to-order trace. Use the actual frozen strategy/risk specification. Remove the obsolete team-exemption question from any revised proposal. Do not claim real-market profitability, a neural-RAG result, a working alert or calibrated judge until corresponding evidence exists.

## NSE data and UI follow-up — 9 November 2026

Implemented and downloaded a 20-stock NSEPython research subset: 26,580 rows, requested 2021-11-08 through 2026-11-08 plus warm-up. Selection freezes the universe by pre-period liquidity and ranks each completed-session candidate under capital/risk constraints. The updated UI shows provenance/coverage/export, rule approval, selection reasons and a server-validated saved-ROUTER-to-C2 hand-off. A five-year ₹200,000 replay completed without model calls. Supervised submissions still require completed C2 and exact human approval.

This partially closes historical-data ingestion, not scientific trading validity: the downloaded universe uses current constituents and unadjusted prices. Historical membership provenance, corporate actions/dividends and rigorous out-of-sample effectiveness remain open. Full verification details are in BUILD_AND_VERIFICATION_STATUS.json and NSE20_DATA_AND_UI_GUIDE.md.

## RAG follow-up — 9 November 2026

Local neural RAG is now implemented and exercised with 81 passages, 384-dimensional MiniLM embeddings, cross-encoder reranking, persistent Chroma and actual MCP/API/UI retrieval. On 101 authored development queries, neural Recall@5 was 0.9505 before rewriting and 0.9703 after it. The original 36-query baseline retains a regression after expansion; labels are not claimed exhaustive/independent. C2 requires a project-policy citation and the current corpus fingerprint, with historical availability filtering for external sources. No paid generation was performed. See RAG_IMPLEMENTATION_GUIDE.md and reports/rag_development.json.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
