# AegisTrade AI — Fresh Viva Questions and Answers

Version 0.19.1 • Prepared 11 November 2026 • 72 questions across nine topics

This is a newly organized current-version bank. Answers describe the implemented system and its limits; they do not invent evaluation results. Practise the short answer first, then show the suggested evidence. The professor-approved team size is three.

## How to practise

Explain the project in this order: purpose → two execution paths → code screening → six-call C2 → dated evidence/RAG → code risk and exits → human control → reviewed memory → measured evidence and limits. Keep the design diagram open. Use the retained March 2024 example for a concrete trace and be clear that its rules differ from the standard demo defaults.

## Purpose and architecture

### Q1. What does AegisTrade do?

It screens historical daily equity data, performs dated C2 research and simulates portfolio entries, reviews and exits. It retains citations, traces and accounting. Supervised orders require exact human approval; historical portfolios use upfront replay-rule approval.

### Q2. Where is the generative AI?

The model generates company/adverse assessments, strategy explanations and critic judgments from observed evidence. Indicators, quantities, fees and execution permissions are code calculations. A technical-only run alone does not demonstrate GenAI.

### Q3. What makes it agentic?

Specialists select declared read-only tools, observe their results and return typed hand-offs. The application executes the tool intents and enforces bounded correction and stopping. This is constrained agentic research, not unrestricted autonomous trading.

### Q4. Is the supervisor another LLM?

No. The supervisor plan and research graph order are deterministic code. The normal six inference calls belong to market, strategy and critic conversations; an additional supervisor generation is not claimed.

### Q5. What are the two signature challenges?

Explainable market-regime-aware routing and safe, auditable execution. Show the code-permitted route with its supporting research, then show dated execution provenance or an exact human-approved simulated order.

### Q6. How do portfolio and supervised workflows differ?

Portfolio replay automatically fills historical actions under rules approved before the run. Supervised Trading first consumes completed passing C2 research and then interrupts for approval of each exact simulated order. Both remain simulation-only.

### Q7. Can an examiner-approved order reach an exchange?

No. The execution adapter is a local simulated broker and the portfolio fills are historical calculations. Live brokerage integration, credentials and exchange permissions are outside this implementation.

### Q8. What are the major components?

Streamlit UI, FastAPI, market/quant code, LangGraph research orchestration, a selectable inference adapter, MCP evidence tools, hybrid policy RAG, reviewed memory, historical portfolio accounting and the supervised broker/audit workflow. Explain their boundaries rather than listing them as independent AI agents.

## C2 orchestration and inference

### Q9. Describe one complete C2 case.

The code locks a symbol/date/purpose. Market requests market and company evidence, strategy requests policy and route evidence, and critic independently checks company/policy/route support. Typed and provenance checks determine whether the result is eligible.

### Q10. Why does normal C2 use six calls?

Each of three specialists normally makes one inference call to request tools and another after the application returns observations. This produces six calls and seven tool invocations. Early abstention can use fewer; corrections can use more within the shared ceiling.

### Q11. What are the case budgets?

Eight inference calls, sixteen tool calls and 4800 requested output tokens are shared ceilings. Each specialist has at most three turns and context is bounded at 26,000 characters. CLI response targets are not hard caps on internal provider reasoning tokens.

### Q12. What tools does the market specialist use?

market_snapshot and company_evidence, normally requested together. It returns the code-supported regime and typed company/adverse assessment. It does not size an order or choose an unrestricted strategy.

### Q13. What tools does the strategy specialist use?

check_strategy and search_policy. It must select the code-permitted route and valid purpose-specific action, supported by observed policy IDs. It cannot override stops, cash limits or the catalogue.

### Q14. How is the critic different?

It receives prior hand-offs but independently obtains company evidence, route and policies. The strategy policy IDs are pinned into its retrieval for exact verification. It is a separate review step using the configured model, not a claim of a different independent model family.

### Q15. Does an invalid response always trigger another call?

No. Corrections are bounded by remaining turns, calls and output allowance; provider failures pause the job. A genuine final critic rejection ends the case. No unlimited retry or debate loop is used.

### Q16. How do C0, C1 and C2 compare?

C0 is the deterministic research reference without generation; C1 uses one tool-using research agent; C2 uses the three specialist hand-offs. C1/C2 share configured model/tool access and budget ceilings in the experiment. Research decision evaluation is separate from portfolio return evaluation.

## Model transport and response contracts

### Q17. Why can this use a ChatGPT account?

The configured codex_cli backend uses the supported CLI ChatGPT authentication rather than an OpenRouter API key. It consumes plan allowance. The application records CLI invocations; it cannot infer per-run USD charges or internal request counts.

### Q18. Can I switch to OpenRouter?

The application supports openrouter or codex_cli configuration. Set the appropriate backend, model and private credentials, restart the services together when idle, and start a compatible new job. Existing jobs are bound to their recorded backend/model identity; no silent provider fallback occurs.

### Q19. What changed in version 0.19.1?

Known specialist responses are supplied as typed JSON objects in the CLI envelope schema instead of JSON encoded again inside a string. Valid legacy strings remain readable. New failures record the parse stage and JSON position rather than only a generic invalid-output message.

### Q20. Does CODEX_OUTPUT_INVALID mean insufficient credits?

No. It means output could not be parsed or validated by the transport. Investigate parsing stage, envelope/argument/content diagnostics and bounds. Quota, authentication and timeout have separate codes.

### Q21. What does CODEX_TIMEOUT mean?

The local invocation exceeded the configured wall-clock timeout and its process was stopped. It does not prove an account quota or login failure. Inspect the cause and explicitly resume if appropriate; failed usage remains counted.

### Q22. Can the CLI run its own tools?

The adapter requests isolated, ephemeral, read-only inference with native shell, browser, apps and MCP disabled. It emits virtual tool intents only. AegisTrade validates and executes those intents through its own declared MCP runtime.

### Q23. Do you repair malformed JSON until it passes?

No. The adapter can unwrap an enclosing Markdown JSON fence without changing content, but malformed JSON or unsupported output remains blocked. Typed schema, citation, evidence and action checks still apply after successful parsing.

### Q24. What are paid-run gates?

They are consent, local reviewer authentication, feature-enable and backend-readiness checks before external inference. FastAPI itself is not charging a fee. CLI runs still require consent because plan allowance is consumed.

## RAG, MCP and company evidence

### Q25. What is policy RAG here?

It retrieves project policy and background passages relevant to a specialist query, then the model generates a response grounded in those observations. The active neural path combines BM25, sentence embeddings, reciprocal rank fusion and a cross-encoder. Exact policy IDs can also be pinned.

### Q26. What is the current corpus?

It contains 81 passages: 72 project-policy and 9 external-reference passages. Source, date, authority and IDs are retained. Passage count is an implementation fact, not a measure of independent coverage or answer quality.

### Q27. Why combine lexical and vector search?

Lexical retrieval helps exact terminology while vector retrieval captures semantic similarity. RRF combines their rankings before reranking. Benefit must be measured with independently reviewed relevance labels rather than assumed.

### Q28. What does the cross-encoder do?

It jointly scores the query and each candidate passage after initial retrieval. The implementation reranks a bounded candidate set rather than every document on every query. This adds local computation but does not add a generation request.

### Q29. Why does the critic pin policy IDs?

A semantically relevant top-five set might omit a policy already cited by strategy. Exact lookup makes that cited policy visible for verification alongside other results. Pinning does not make the citation correct; the critic must still read its text.

### Q30. How is company research different from policy RAG?

Company evidence comes from a dated symbol-specific archive pack of official disclosures and selected readable attachments. Policy RAG supplies the experiment rules and references. Reviewed lessons are a third store of process reminders; neither is a substitute for company facts.

### Q31. How do you prevent future-news leakage?

Use the selected decision date and 15:30 IST cutoff with document availability timestamps. Do not treat a quarter-end as a publication date or use current news to justify an old decision. Timestamp and historical-version completeness remain disclosed limitations.

### Q32. What does materiality mean in this project?

Evaluate the cited amount/unit, impact, operating restrictions, severity, recency, resolution and continuing exposure. A negative keyword alone is insufficient. Issuer-reported Nil must be attributed, while genuinely missing critical facts remain unknown.

## Evidence quality, safety and abstention

### Q33. Can LIMITED financial coverage pass?

Yes, for a code-qualified technical action when a complete ready bounded adverse scan is cited, no material adverse is found in that scope, and financial/independent-news limitations are explicit. LIMITED does not establish financial health or safety. All other gates still apply.

### Q34. Why does UNKNOWN block a strong technical entry?

Technical strength cannot resolve a genuinely uncertain material exposure or incomplete required scan. The revised rubric avoids manufacturing uncertainty from unrelated missing coverage, but does not clear real unknown material risk. A later price rise alone does not invalidate the earlier evidence-based block.

### Q35. What does a complete bounded scan prove?

It establishes completion of the configured search scope and required attachment checks. It does not prove that every news source was searched or that no undisclosed adverse event exists. The model must keep that scope explicit.

### Q36. How did evidence packing improve?

The view now retains impact/action/amount/status/event windows, merges overlapping source intervals and references identical windows once. Full retained extracted observations remain audited. This addresses lost impact sections and repeated context without claiming exhaustive source coverage.

### Q37. Why retain a context limit after compaction?

It bounds the conversation payload and protects the research budget. The current 26,000-character bound is a practical measure, not exact tokenization. New evidence shapes can still overflow and should fail explicitly rather than hide material risks.

### Q38. How is prompt injection handled?

Tool content and lessons are untrusted data, with scanner checks, typed arguments/outputs, role allowlists and separation from write permissions. These defenses reduce risk but do not prove immunity. Independent model-level attacks must be measured separately from scanner detections.

### Q39. Why not let the model size positions?

Cash, quantity, stop distance and exposure are deterministic financial calculations and authorization constraints. Code makes these reproducible and testable. A fluent explanation is not authority to increase risk.

### Q40. Does a blocked case mean the whole project failed?

No. A correctly unsupported or unsafe action should block. Distinguish evidence abstention, schema/citation errors, provider failures and budget pauses; they have different causes. COMPLETED_WITH_GAPS means the replay finished with coverage/decision gaps, not that every candidate was researched successfully.

## Portfolio selection and exits

### Q41. How are stocks shortlisted?

Code filters history, liquidity, regime, ATR fraction, discontinuities, signal, capacity and cash/risk. Eligible names are ranked by 70% strategy strength, 20% relative liquidity and 10% lower ATR fraction. The LLM researches the selected candidates rather than ranking all market stocks without limits.

### Q42. What does 1% risk mean?

It is the planned stop-distance risk budget as a fraction of current equity. The share count is further limited by 20% per-position exposure and available fee-aware cash. Gaps, fees and execution assumptions mean realized loss is not guaranteed to stay at 1%.

### Q43. Why wait after Friday signals?

The next trading close supplies a fresh signal and dated C2 research before a later-open fill. Monday closing information cannot justify Monday opening execution. The same principle applies to non-trading gaps and delayed missing-bar fills.

### Q44. How does the trailing stop work?

The stop is the greater of its previous value and highest completed close since entry minus a fixed multiple of entry-signal ATR. It never falls, and updates apply next session. A fresh widening ATR cannot lower the protection.

### Q45. What is the profit-taking rule?

The configurable target defaults to 8% net modeled holding return, with fee/slippage handling in the target reference. It applies to an individual holding, not total portfolio return. It is a testable exit assumption, not an optimized or guaranteed best target.

### Q46. What other exits exist?

Code strategy exits include EMA20 crossing below EMA50 for trend, RSI above 58 for reversion and close below EMA20 for breakout. C2 can also issue a validated holding-review EXIT. Stops and profit protection do not wait for a new LLM response.

### Q47. What happens if stop and target are touched in one bar?

Opening events are handled first. For ambiguous later intraday touches the simulator takes the conservative stop first because daily OHLC does not reveal the path. This is an explicit modeling assumption.

### Q48. Are holdings sold on the final date?

No. Unsold holdings are marked and contribute unrealized P&L. A queued final-close action may remain unfilled without a later bar. End-of-window equity is not the same as cash after liquidating everything.

## Memory and improvement

### Q49. What are the three portfolio lessons?

They concern correct citations, treating context overflow as an engineering issue, and assessing adverse-event materiality. They are conditional process reminders, not predictions or instructions to buy. Current accepted wording and conditions are visible in Learning & Lessons.

### Q50. Does accepting a lesson train the model?

No. Acceptance records a human-reviewed candidate. A frozen selected version can then be retrieved into a future C2 prompt. Model weights are not updated and existing runs do not automatically receive the lesson.

### Q51. Why freeze a playbook version?

A fixed ID/hash records which reviewed texts were available to a run. New accepted lessons require a separate version. This prevents a running experiment from silently changing its memory conditions.

### Q52. How are relevant lessons selected?

The current retriever scores conditions against current regime/route/purpose and company evidence tags/titles. It selects up to three bounded reminders, with at most 2400 characters and less when evidence context needs space. This is simple matching, not a learned portfolio optimizer.

### Q53. Why exclude later profit from draft lessons?

A rising stock after a block does not prove that the original evidence or risk judgment was wrong. Learning buy/avoid labels from later returns would encourage hindsight overfitting. Review dated source facts and process failures instead.

### Q54. What is trained_through?

It is the latest source portfolio end date in the selected frozen version. A later-period evaluation must start strictly after it. The currently observed three-lesson book was trained through 29 December 2023.

### Q55. Can I replay an earlier date with later lessons?

Only with the explicit development-replay setting when dates overlap. The run is labelled DEVELOPMENT_REPLAY and cannot be presented as unseen-period performance. Chronological separation also does not prove the user never inspected those dates earlier.

### Q56. How would you demonstrate memory benefit?

Compare current C2 without lessons and with one fixed version on the same untouched later cases/settings. Include regressions, abstention, latency, calls and quality, not just return. The separate technical reference helps identify the cost and benefit of C2 filtering.

## Human control, persistence and operations

### Q57. What is Portfolio review rationale?

It records why the reviewer accepts or rejects a conditional lesson. It should reflect actual understanding or source review, not claim that every document was verified if that was not done. It is retained as review provenance.

### Q58. Why is Save disabled?

Saving a pending portfolio review requires a reviewer token in the sidebar and at least five non-whitespace rationale characters. Enter the private AEGIS_REVIEWER_TOKEN value, not an API key, and commit the field. The UI now displays the missing requirement.

### Q59. Why is Freeze disabled?

At least one lesson must first have a saved ACCEPT review. Select the accepted candidates for the new version and provide the reviewer token. Choosing ACCEPT in a radio button without saving is not acceptance in the database.

### Q60. Why must an edited order be approved again?

The approval authorizes the exact payload hash. A changed quantity or other field changes the payload and invalidates that authorization. Revalidation and a fresh approval preserve the human decision boundary.

### Q61. How is a broker timeout handled?

The simulated broker uses request IDs and audit state. If a commit may have occurred, the application reconciles the request ID before retrying. Blind resubmission could create a duplicate action.

### Q62. What is saved when a portfolio pauses?

Cash, positions, OPEN/CLOSE phase, dates, processed decisions, pending orders, research outputs, fingerprints and inference reservations. A failed response is not reused as successful evidence. Resume starts the failed case again when explicitly authorized.

### Q63. Do I need to add allowance when resuming?

Only if the remaining allowance cannot reserve another case. The adapter reserves eight units before a case and reconciles actual known usage. A transport pause with ample remaining budget can be resumed with zero added units; the consent still authorizes the next invocation.

### Q64. Why can the UI show NSE when .env says synthetic?

The persisted market_config.json activation overrides the environment fallback. Check Market Data and dataset provenance to identify the active source. Reading one environment variable is insufficient to describe the running dataset.

## Evaluation, demonstration and limitations

### Q65. What do the 185 passing tests establish?

They verify controlled contracts such as typed parsing, tool boundaries, research gating, chronology, accounting, exits and UI lesson workflow. Many generation responses are mocked. They do not establish expected investment profit or universal model reliability.

### Q66. What does the completed March 2024 example establish?

A retained real CLI run completed with gaps, 101 typed-specialist invocations, entries, a take-profit exit, a stop exit and unsold holdings. Its recorded return was about +0.526%, with a negative technical reference for that selected window. It does not prove a profitable general strategy or memory benefit, because it used no portfolio lessons.

### Q67. Why can C2 underperform the technical reference?

C2 can block entries, hold more cash, change timing or make review exits; model and evidence errors can also matter. Compare exposure, avoided losses, missed winners, costs and dates. Do not conclude that relaxing every block improves risk-adjusted performance.

### Q68. What are survivorship bias and corporate-action limits?

Applying current constituents to history omits some companies that left the index and can bias conclusions. Unadjusted splits, bonuses and demergers can distort returns and indicators. A discontinuity filter is a quarantine, not a complete correction.

### Q69. What would a fair profitability evaluation require?

Predetermined rules, multiple untouched periods/regimes, realistic costs, corporate-action/membership handling and risk/exposure-aware comparisons. Separate development and evaluation and retain unfavorable results. Repeated tuning on the same quarter does not establish generalization.

### Q70. What capstone evaluation evidence remains?

Use independently reviewed gold and protected held-out cases, genuine C0/C1/C2 comparisons, model-level defense tests, memory ablations, judge/human calibration and repeated results with cost/error/latency accounting. Consult the official current rubric for thresholds. Passing software tests is only one evidence category.

### Q71. How do you demonstrate the project within a short exam slot?

Prepare a genuine completed portfolio and its traces beforehand, then show a short live case and UI controls. Walk through policy retrieval, one researched entry, an exit, a remaining holding, memory and the separate human interrupt. Label saved and live evidence clearly.

### Q72. What should each team member understand?

All three should explain the full architecture, dated evidence, actual LLM calls, risk/approval boundaries, memory chronology and limitations. Divide implementation responsibilities but cross-review the important controls. Three-person approval does not waive the remaining technical or evaluation requirements.

## Evidence to keep ready for follow-up questions

- Project Design and Orchestration document: architecture, C2 and execution diagrams.
- app/api.py /health: current version, backend readiness and capabilities; do not expose private configuration.
- config/agents.json and agentic.py: role tasks, allowlists, budgets and LangGraph sequence.
- A passing research trace: real tool requests, observations, typed hand-offs and final guard.
- A blocked trace: exact evidence/schema/provider cause and correct stopping behavior.
- Portfolio results: ledger, realized/unrealized accounting, stop updates, target exit and unsold holdings.
- Learning & Lessons: accepted/rejected state, review rationale, frozen version and trained_through.
- Supervised Trading and Broker Audit: exact-payload interrupt, edit/reapproval and request reconciliation.
- reports and BUILD_AND_VERIFICATION_STATUS: actual test/evaluation evidence and clearly marked pending work.

Say “not measured yet” when evidence is missing. Do not call a mocked test a real model result, a selected profitable month a robust strategy, or a date-separated replay a statistically independent evaluation without further evidence.
