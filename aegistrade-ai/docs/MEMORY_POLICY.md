# AegisTrade memory policy

- Short-term: LangGraph typed state + SQLite checkpoint: symbols, market snapshot,
  citations, proposed payload hash, action status, trace. Purpose: resume approvals.
- Long-term: SQLite `reviewed_lessons.sqlite`: proposed/accepted/rejected lessons,
  applicability, review reason and frozen playbook manifest. Purpose: avoid repeating
  operational reasoning mistakes. A lesson never changes hard risk code.
- Access: the local API limits write review endpoints using a demo reviewer token;
  this is NOT enterprise authentication. Only accepted lessons are returned by the
  read-only records MCP server.
- Storage: local project data volume; do not store passwords, broker credentials,
  personal account identifiers or real customer trade history.
- Expiration: there is no automatic retention scheduler in this prototype. Before a
  real pilot, implement retention windows, encryption, user access controls,
  deletion requests and independent security testing.
- Correction/deletion: use app-specific admin workflows or explicitly delete the
  local SQLite volumes while services are off. Document the change and re-evaluate.
- Experiment: compare frozen held-out results with memory disabled and with approved
  lessons retrieved. The repo does not include a completed, measured E3 LLM result.

Order provenance (9 November 2026): persisted workflow context retains the required C2 run/case IDs, result digest, evidence snapshot, critic acceptance, explanation and citations. Resume reloads and validates saved research. Deleting or changing that research blocks an outstanding approval; create a new researched proposal rather than restoring approval from an unsupported context.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.

Company snapshots: data/company_research/packs retains extracted text, source/publication/availability/retrieval metadata, coverage and hashes for reproducible research. Only bounded excerpts go to generation. Source changes/deletion invalidate linked research and approvals. Administrative retention/correction must preserve experiment provenance; the prototype has no automated archival/deletion scheduler.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.

C2 historical runs retain atomic portfolio phase/ledger state and per-decision source/tool/model traces under data/c2_portfolio_runs. Completed research is reused on same-case resume; unknown provider calls remain reserved rather than silently retried for free. Independent new runs do not import prior holdings automatically. Do not alter active checkpoint files; source/prompt/corpus changes require a fresh run. Administrative correction/deletion must document affected evidence and performance claims.


## Version 0.19: materiality and reviewed portfolio memory

The current company view preserves issuer impact sections that can occur after long cover letters. Each matched adverse disclosure has extractive windows for action, amount, impact, status and event context. Windows from overlapping positions in the same source are merged. Identical windows share a text reference; each document retains its own citation ID, date and field mapping. Full source text, metadata and pack snapshots remain local. A missing field is unknown, never an invented Nil. An issuer statement of Nil impact is attributed, not independently verified.

C2 assesses severity, operating restrictions, unresolved consequences, recency and resolution rather than treating every negative keyword as material downside. Missing unrelated coverage alone is not a finding of adverse risk. Genuinely incomplete scans, unreadable required attachments and unresolved material exposure still block ENTER/HOLD. The independent critic and code gates remain authoritative. This is an evidence-quality improvement, not an instruction to buy every strong signal.

### Portfolio lessons through the UI

1. Open **Learning & Lessons → Portfolio lesson memory**. Select a completed C2 portfolio and click **Draft portfolio lesson candidates**. The reviewer token is required. Drafting is deterministic and makes zero generation calls; it does not judge a blocked trade from its later return.
2. Select a candidate. Inspect **Dated source cases and original assessment**, including source links and available materiality windows from the original immutable pack. Check the facts before generalizing. Missing financial coverage, context overflow and citation errors have different remedies. A draft is a hypothesis; not every blocked case was wrong.
3. Edit the conditional lesson and **Applies when** as needed. Choose ACCEPT or REJECT, write a rationale and click **Save portfolio lesson review**. Pending and rejected candidates cannot enter C2 context.
4. Select accepted candidates and click **Freeze portfolio lesson version**. Each immutable version records ID, hash, source period, accepted text and review provenance. Further accepted lessons require a new version; old runs remain pinned.
5. Open **Strategy Backtests → C2 historical portfolio**. Choose **Frozen portfolio lesson version** before creating a run. Default is **No portfolio lessons**. Up to three relevant reminders and at most 2400 characters enter market/strategy/critic context, with fewer or none when source evidence needs the context space. Inspect each saved research trace's `portfolio_memory` manifest and `lesson_ids`.
6. For evaluation, choose dates strictly after the latest source run end (`trained_through`). To debug an overlapping period, explicitly tick **Mark as development replay if lesson training overlaps these dates**. It is labelled DEVELOPMENT_REPLAY and is not unseen-period evidence. LATER_PERIOD_EVALUATION denotes date separation, not a statistical proof of benefit.
7. Create a new run. Start with one short window and 48 inference units; normal C2 uses six units per researched case and reserves eight. Resume only after inspecting any pause. Draft/review/freeze/retrieval adds no model requests; ordinary C2 research still uses the selected inference backend and allowance.

Friday/pre-gap fresh review, the default 8% net take-profit, fixed-entry-ATR 2× trailing stop, code sizing/cost rules and no forced end-date sale remain unchanged. Memory cannot change those rules or force a trade. There is no weight fine-tuning, self-training or automatic profit optimization.

### Fair test after this update

Preserve earlier results. Use identical dates, data, capital, risk, fees/slippage, entry/exit rules and inference configuration for technical reference, current C2 without portfolio lessons and current C2 with one frozen version. Start later than all lesson source runs for the memory comparison. Prefer a short diagnostic run before a three-month run; ₹200,000, risk 1%, fees/slippage 10 bps each, target 8%, ATR trail 2× and holding review every five sessions are reproducible starting settings, not optimized profit settings. Confirm the chosen dates exist in the active dataset and dated company packs can be prepared. At run start, plan for enough inference allowance; 48 units are a checkpoint budget, not a promise that three months will finish.

Report realized/unrealized return, drawdown, time in cash, fees, blocked reasons and inference use. Higher returns alone do not establish better research; lower exposure can reduce both return and drawdown. A rising stock after a block does not prove that the original block was wrong. No new profitable result is claimed before actual testing.

### Storage, versions and startup

Portfolio candidates/versions use `data/portfolio_lessons.sqlite`, separate from the legacy AI Agent Experiments playbook in `data/reviewed_lessons.sqlite`. The existing research-failure reflection workflow is retained. New endpoints: GET `/portfolio-lessons`; authenticated POST `/portfolio-lessons/draft`, `/review`, `/freeze`. Source checksums protect draft/review/freeze; version hash and temporal binding are rechecked on portfolio execution/resume and completed-C2 validation. Existing saved runs and ledgers remain unchanged. Earlier prompt/corpus/engine versions cannot resume under the new configuration; read them as historical results and create a fresh run.

Run from the project root: `bash scripts/start_unix.sh`. Open `http://127.0.0.1:8501`; API health is `http://127.0.0.1:8000/health`. Restart the API and dashboard together after an update, stopping the previous launcher first if its ports are occupied. This update preserves the configured inference backend and private credentials. It starts no portfolio or external inference request automatically.
