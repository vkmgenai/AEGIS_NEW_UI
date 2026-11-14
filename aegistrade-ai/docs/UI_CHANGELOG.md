# UI visibility and usability update — 6 November 2026

## 14 November 2026 — Strategy Backtests cleanup

- Renamed the user-facing technical workflow to **C0 Technical baseline** while retaining compatible API and saved-run identifiers.
- Reduced explanatory notices to one concise C0/C2 comparison statement.
- Kept only capital, dates, C2 allowance, consent and replay approval in the main run form.
- Moved reviewed-memory selection into a collapsed **Optional evaluation controls** section.
- Renamed the primary actions to **Run C0 backtest** and **Run C2 backtest**.

## 14 November 2026 — final experiment-page cleanup

- Removed the minimum-bar evidence canvas from AI Agent Experiments; the evidence remains in Capstone Evaluation and the report.
- Removed the visible BUY/holding-review scenario selector, manual company-pack preparation, shortlist preview, token-budget tuning and memory toggle from the primary experiment form.
- AI Agent Experiments now asks only for configuration, case count, date range and inference consent; stock ranking, evidence preparation and the balanced 3,600-token budget are automatic.
- Retained saved runs, full traces, the C2 human interrupt, separate decision audit and all three inference adapters.

## 14 November 2026 — C2 human interrupt without duplicate inference

- Actionable, grounded C2 BUY/SELL experiments enter `WAITING_HUMAN`; HOLD, blocked and failed cases do not interrupt.
- Approve/reject reuses completed C2 research and makes zero additional research calls.
- Reviewer, rationale, research digest and decision are stored in a separate JSONL ledger and audit event.
- A fixed 10-session outcome is displayed in Learning & Lessons as review evidence and is never learned automatically.
- The reviewer credential remains required for authenticated writes but is loaded from `.env` and hidden from the UI.

## 14 November 2026 — final capstone UI simplification

- Moved the single-stock C0/C2 comparison into Strategy Backtests.
- Integrated grounded C2 BUY/SELL human APPROVE/REJECT review and the audit ledger into AI Agent Experiments.
- Removed Supervised Trading and Broker Audit from navigation; internal research-binding and audit safeguards remain.
- Reduced the balanced C2 response budget to 3,600 tokens per case with concise approximately 450-token specialist turns.
- Kept C0 technical and C2 historical portfolio as the two portfolio choices; C1 remains in the required C0/C1/C2 agent experiment only.
- Retained all three switchable inference adapters: ChatGPT/Codex CLI, OpenRouter API and Claude CLI.
- Replaced manual strategy, risk, stop, trailing, target, re-entry, slippage, research-pool and holding-review inputs with a visible fixed policy recorded in every run.
- Kept capital, dates, C2 allowance, frozen lesson selection, explicit consent, replay approval, progress, refresh/pause/resume and saved runs.
- Removed the dead C1 newsletter-import branch from the portfolio page. Evidence ingestion remains available in the evidence/data workflow.
- Added `SIMPLIFIED_UI_DEMO_GUIDE.md` and aligned the final report, architecture walkthrough and README.

## What changed

- Replaced broad sidebar CSS coloring, which could hide control labels and selected values, with native Streamlit theme colors in `.streamlit/config.toml`.
- Added always-visible top-level workspace selection, so narrow Mac browser windows do not hide navigation.
- Redesigned Overview with daily chart, table, indicator explanations and a compact research snapshot.
- Improved Backtests with explicit Run and Load buttons, summary metrics, equity curve, scrollable events and interpretation notes.
- Improved Supervised Trading with a clearly presented exact order, hash expander, reviewer token requirement, edit/new-approval path, and safe test instructions.
- Reorganized policy retrieval, human-reviewed lessons and Broker Audit with readable expandable details.
- Added an audit CSV export and a concise user guide.
- Increased launcher API health wait from ~10 to ~60 seconds for slower first starts.

## Important limits

- No changes to core strategies, deterministic risk calculations, simulation-only order gateway, or live broker capability.
- The project still starts on synthetic market data unless explicitly configured otherwise.
- This UI code was compiled and its repository Python tests run locally. An interactive Mac/Streamlit browser render was not available in the build environment; verify appearance and click paths on the target Mac.

## Files for incremental update

- `app/ui.py`
- `.streamlit/config.toml`
- `scripts/launch_local.py`
- `docs/AegisTrade_UI_User_Manual.docx`
- `docs/UI_CHANGELOG.md`

## 10 November 2026 — 0.16.0: selectable Codex / OpenRouter inference

- Added official Codex CLI structured-response adapter using existing ChatGPT login, temporary working directories, native-tool isolation, minimal environment, timeout termination and controlled error codes. AegisTrade retains specialist/MCP orchestration and all research/approval/risk checks.
- Selected Codex in the private local .env while preserving OpenRouter settings; source default remains OpenRouter. Provider/model switching needs configuration and restart; no automatic fallback.
- Added backend readiness/model/unit to health, results and UI. Labels distinguish HTTP requests from CLI invocations. CLI response-token values are guidance; internal provider requests and per-run USD charge are unknown.
- Bound portfolio resume to backend/model/adapter/unit identity. Auth/quota/transport failures pause rather than causing unresearched entries.
- Added Plus full UI runbook and updated design, viva and overview Word documents. Genuine one-case research and a tiny cached-archive portfolio were verified separately from mocked tests.

## API root navigation

Opening http://127.0.0.1:8000/ now returns a small HTML landing page with dashboard (8501), API documentation (/docs) and health (/health) links. The dashboard remains on port 8501. The root page makes no model calls or data changes.

## 10 November 2026 — 0.16.1: precise research validation

- Diagnosed repeated company.summary >600-character responses in the user's August2023 run; inference calls succeeded.
- Generate field limits from actual schemas; feed exact field/length errors back within the existing budget. Keep strict bounds and all evidence/risk checks.
- Separate failure categories; show complete selected-record error below a readable decision table. Reconstruct old schema failures without editing original audit files.
- Stop extra specialists when a market assessment already blocks an entry/holding action; preserve reviewed risk-reducing EXIT.
- Pause the affected run safely and preserve frozen prompt identity; updated prompts require a new run.

## 10 November 2026 — 0.16.2: portfolio demo prerequisites and stable UI

- Replaced exact patch-version blocking with explicit UI/API interface contract1, with compatibility for earlier0.16 backends. API/UI coordinated restart verified.
- Corrected lost financial headings/units/periods and exchange-cover-letter excerpts; compact versioned company view retains source facts and lists omissions. Bounded32 MB PDF extraction and validated attachment cache repair quarterly evidence without weakening research gates.
- Added context_usage events, bounded26,000-character ceiling and references for identical repeated observations, preserving full repeated audit observations. Clarified policy versus company citation arrays.
- Added a separate portfolio step-by-step Word guide with a small rehearsal and optional holding-review extension.

## 11 November 2026 — 0.16.3: exact critic evidence and provider diagnosis

- Pin strategy citation IDs in the critic's independent MCP policy search; retain corpus/date filtering and semantic matches.
- End immediately on critic rejection; remove the guaranteed-blocking extra strategy-revision call.
- Preserve CODEX_TIMEOUT / CODEX_OUTPUT_INVALID and elapsed time in decisions and paused-run banners; derive diagnoses for old records without editing their audit.
- Keep existing inference caps/timeouts and explicit consent; no generation calls for this fix.


## 11 November 2026 — 0.17.0: causal trailing stops

- New UI/API historical portfolios default to trailing enabled at2×entry-signal ATR14. Expose enable/multiplier controls; validate finite0.5–10 distance.
- Trail the highest completed close since fill, with fixed entry-signal ATR. Stops only rise and become active next session after old-stop intraday checks.
- Checkpoint all survivor ratchets before research; close markers avoid duplicate adjustments on resume. Preserve missing-bar and final-holding behavior.
- Record stop_updates, initial/current stops and SELL_TRAILING_STOP; active technical references use the same settings, passive benchmarks have no stops.
- Version engine as c2-portfolio-v2-trailing, update POL-43 and rebuild the local neural policy index. Preserve older saved records; changed engine/corpus requires a new run.
- Update design, viva, summary and UI demo documents. Automated mechanics checks use mocked C2 and add no actual generation calls.


## 11 November 2026 — readable successful portfolio decisions

- Populate the decision table's reason with the saved explanation when no error exists; HOLD/ENTER reasoning is no longer blank.
- Show the full explanation below the selected date/symbol/research-purpose record and clarify that HOLD keeps existing shares with code protection active.
- Trading decisions, review intervals, model calls and backend remain unchanged; verify against saved genuine HOLD cases using read-only UI access.


## 11 November 2026 — 0.18.0: fresh entry review, adverse research and take-profit

- Defer Friday/pre-gap entry candidates until the next available close; re-screen/research before a later-open fill. Preserve original and refreshed signal dates; audit cancellations and checkpoint deferrals without duplicates.
- Add bounded dated adverse-disclosure metadata/attachment search and explicit NO_MATERIAL_ADVERSE_FOUND / MATERIAL_ADVERSE / UNKNOWN assessments. LIMITED financial coverage can pass with a completed cited scan and accepted critic. No automatic clearance from missing data.
- Add configurable8% NET take-profit defaults, cost-aware trigger prices, opening-gap precedence and conservative stop-first handling for ambiguous intraday bars. Label exits SELL_TAKE_PROFIT and retain surviving final holdings.
- Match active technical-reference timing/targets; retain passive-comparator differences. Update prompt/engine/policy versions, rebuild neural RAG and preserve old results. No automatic new inference or continuation.


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


## Codex response-format correction — version 0.19.1

A saved RELIANCE entry case dated 1 February 2024 paused with CODEX_OUTPUT_INVALID after two CLI invocations. The usage record identifies JSONDecodeError, not an established quota/authentication failure. The original trace did not retain the parsing stage, so the precise malformed text cannot be reconstructed. The CLI envelope previously required the specialist JSON to be encoded again as a string; the adapter now supplies the exact specialist object schema directly, removing that extra encoding layer. Legacy valid JSON strings remain readable. Malformed JSON is not repaired or accepted; stage and line/column diagnostics are recorded without retaining arbitrary raw private output. Native tools and all C2 evidence/risk gates remain restricted.

This transport correction preserves the portfolio engine, policy corpus, prompts, memory version and backend identity. The current paused run can be resumed after restarting the API and dashboard together. In Strategy Backtests, open the paused saved C2 portfolio, set Additional inference units on resume to 0 (the observed run used 2 of its existing 48 units), tick the resume authorization and click Resume C2 portfolio. Failed calls remain counted. Resume starts a fresh research attempt for the failed case; it does not continue inside the broken CLI response. Later budget exhaustion can still require a deliberate allowance increase. No automatic retry, backend fallback or simulation is started by the patch.

If the error recurs, inspect the new validation_stage and json_error fields in the saved research usage; do not assume that buying API credits addresses a response-format error. Mocked schema/transport and regression tests validate the correction; actual account-backed success remains to be tested by an explicitly resumed run.


## Live C2 progress display — 12 November 2026

The selected C2 progress panel now refreshes automatically every five seconds while its status is RUNNING or QUEUED. It uses read-only status requests and does not create, resume, retry or extend a job. Status, progress fraction, market date/phase and recorded inference usage update inside a Streamlit fragment; the capital/date/consent form is not resubmitted. The manual Refresh C2 progress button remains and reloads all result tables.

Session counts advance only after a market session finishes, so an active multi-call research case can legitimately hold the same percentage. A local last-checked time confirms successful polling. Temporary status errors retain the last saved progress with a recovery message. Completion, pause or interruption causes one full-page update for final results and stops automatic polling. Opening a different job or leaving the portfolio result view replaces/removes that panel.

This is a dashboard-only change; refresh the browser once to load it. No API restart, portfolio restart or additional model authorization is required. 204 software tests passed, including read-only polling, stopping on terminal/paused states, temporary failure recovery, selected-run isolation and retention of manual refresh without a second run submission.


## 0.20.0 — 12 November 2026: three retained universes

Added Market Data universe selection, public-data preparation/progress, protected validated activation, separate folders and original-data resume resolution. Existing top-20 data and saved runs remain retained. Nifty 100 and the custom frozen 30 have disclosed current-member/curated selection bias, verified symbol-change metadata and shorter-history coverage. See AegisTrade_Universe_Selection_and_Data_Preparation_Guide.docx. 215 tests pass; no inference started.
# Capstone Evaluation ledger viewer — 14 November 2026

- Added a read-only **Capstone Evaluation** workspace.
- Lists retained deterministic and E1–E4 background runs from `reports/capstone_runs`.
- Shows status, exit code, configuration, hashes, summary metrics, failures and lifecycle events.
- Provides the complete JSON report as a download and displays safe terminal inspection/replay commands.
- Viewing and downloading make zero model calls; paid replay remains a separately consented terminal operation.
