# AegisTrade AI
Viva questions and answers

**Source baseline 0.19.0 • Reviewed 11 November 2026**

**Current rules — v0.19.0 (11 November 2026):** Friday/pre-gap entry candidates wait for the next actual trading close, are freshly screened and researched, and can fill only at a subsequent open. Financial incompleteness alone is not a rejection: a LIMITED assessment can support a code-qualified entry after a completed cited bounded adverse-disclosure scan finds no material adverse event in its observed scope. Material/unknown adverse risk still blocks entries; absence of evidence is not proof of safety. New historical portfolios also default to an 8% take-profit NET of modeled entry/exit fees, with slippage in execution. This supplements daily code/trailing exits; no end-date liquidation is forced. Older numerical examples and archived run IDs retain their original policies. A NEW run is required. See ENTRY_ADVERSE_AND_PROFIT_POLICY.md for exact timing, scope, costs and validation.
**Current memory update — v0.19:** Company materiality windows and bounded evidence packing are implemented. Completed portfolios can draft pending process lessons for human review, freeze and version-pinned retrieval into a NEW C2 run. See the final “Version 0.19” section for the exact UI sequence and development-replay/date rules. No improved profit result is claimed before testing.


**Demo history reset — 11 November 2026:** Existing portfolio/research/backtest history and simulated broker ledgers/approvals were cleared at the user's request. Earlier run IDs and numerical examples below describe archived rehearsals; they are not available in the active saved-run lists. Start a new run for your demo. Recoverable originals are under data/history_archives/20261111_105802/. Market data, company evidence, policy/model caches, reviewed lessons and private configuration were preserved.

For the approved three-member team: Veneet, Karthika and Mathangi. This handbook is separate from the Detailed Design and Demo Guide. Answers describe current implementation and evidence, not promises of completed experiments. This edition includes separately recorded genuine Codex runtime checks; writing the handbook did not trigger additional inference.

Read the eight required guideline questions first, then rehearse the technical questions. Replace “not yet measured” with numbers only after collecting authentic results. Every member should be able to draw the architecture and trace a request, even when another member led that component.

## 1. The eight questions explicitly listed on PDF page 17

### Q1. Trace one request through your architecture. What does each box decide?

A user chooses period and capital in Streamlit. FastAPI validates the request; deterministic code screens the 20-stock universe and records ranking reasons. A selected historical case enters C2 after paid-run consent. The LangGraph supervisor delegates market interpretation, grounded strategy explanation and compliance criticism to three scoped LLM specialists. Each specialist requests permitted MCP evidence, interprets it and returns a typed hand-off. Code validates the permitted route, citations, critic and provenance, then saves research. Only that passing result can create a code-sized proposal. LangGraph persists a human interrupt. The reviewer approves the exact hash; final research, quote, risk and emergency checks precede one idempotent simulated broker action and audit record.

Show: selection audit → C2 tool trace and citations → waiting order/hash → changed hash after edit → broker event. The C2 historical path researches entries and scheduled holding reviews, then fills under upfront rules; the technical-only reference makes no generation calls.

### Q2. Which decisions belong to the model, code and person?

Models choose permitted read tools, interpret observations, explain the constrained route with citations and critique the evidence. Code calculates indicators, regimes, the allowed route, screening/ranking, quantity, risk, budgets, validation and execution eligibility. The person approves paid runs, accepts/rejects lessons, freezes the playbook and approves/edits/rejects the exact simulated order. The LLM critic accepts research; it does not provide human order authorization.

Show: config/agents.json for roles, strategies.py for the router, safety.py for sizing and app/ui.py for explicit decisions.

### Q3. Show the single-agent baseline. What benefit did the team provide, and at what cost?

C1 is one tool-using agent with the same union of market, strategy and policy tools, model and budget ceilings as C2. C2 uses three role-specific conversations with typed hand-offs under a deterministic supervisor. Normal C2 uses six generation requests and can attempt at most eight per case. Specialist separation may improve traceability and critique, but also adds latency, tokens and failure points. We cannot claim a measured improvement yet: authentic independently reviewed held-out comparisons remain unfinished. E1 is designed to answer that question fairly, including failures and actual cost.

Do not answer “three agents are always better.” A defensible result may be that C1 is sufficient for easy cases and C2 adds value only for difficult grounding/error cases.

### Q4. Which experiment or finding changed the design?

The retrieval development measurement found that query rewriting changed neural Recall@5 from 0.9505 to 0.9703 on the same 101 authored queries. The older 36-query subset still regressed against its original smaller-corpus baseline, so the expanded design needs further independent relevance review. Integration checks also established the need to bind proposals to completed research and the corpus fingerprint; an explanation shown beside an unrelated order was insufficient. These are development/source findings, not held-out proof of multi-agent benefit.

Show reports/rag_development.json and the mandatory-research gate tests. Distinguish “a requirement review prompted a fix” from “a measured experiment proved an improvement.”

### Q5. Show traces for missing evidence, a failed tool and an injected instruction.

Missing/unobserved citations fail the code guard and cannot create a proposal. A structured tool error enters the trace; the specialist may correct within budget, otherwise research fails closed. Tool-output poisoning in E2 tests untrusted instructions arriving through the project's own evidence path. Tool allowlists and the absence of a model broker-write capability remain in force even with the scanner off.

Our saved integration tests use mocked generation for controlled faults. Real model-level poisoned-tool and failure traces still need to be captured. The scanner's 30/32 detections are not a model jailbreak-success measurement. Show the actual tested trace with its label; do not improvise a live attack into production tools.

### Q6. What does memory retain, why, and how can it be deleted?

Action checkpoints retain workflow state for safe resume; research JSON retains evidence/usage for audit; the reviewed lesson store retains conditional development lessons with review state and applicability. Only accepted, relevant lessons from a frozen playbook enter memory-on research. Pending/rejected lessons are audit records rather than instructions. The memory policy specifies correction/deletion through administrative handling; there is no complete retention/deletion UI. Deleting an active SQLite database is not a safe substitute for a retention process.

Short context uses a 26,000-character bound with deterministic extractive company views, merged overlapping windows and duplicate text references. Remaining overflow fails closed. Reviewed portfolio lessons are optional, version-pinned and lower priority than dated evidence. Show docs/MEMORY_POLICY.md and the playbook freeze metadata.

### Q7. Which lessons helped unseen cases, and how do you know?

The implementation can draft a conditional lesson from an actual scored development failure, require human review and freeze it before held-out use. E3 compares the same untouched cases with relevant lessons off/on and must include lesson-generation cost and regressions. We have not yet established that a particular lesson improves unseen cases. A plausible lesson or an accepted review state is not evidence of generalization.

Show a genuine accepted and rejected lesson, reason, applicability and frozen hash when available; then show the actual E3 report. Do not invent successful lessons or before/after numbers.

### Q8. What is needed before a supervised pilot with real users?

First establish independent held-out quality/security evidence, calibrated judging, operational recovery, clean deployment, appropriate identity/authorization and a usable retention/audit process. Financial data needs adjustments, membership/calendar provenance and licensed use. A forward simulator needs a persistent cash/holdings ledger, reliable data and reconciled lifecycle handling. Any real broker integration would be a separate project with current legal, exchange, broker and security review. This repository contains no live broker path; our present scope is local academic simulation.

This is a design-readiness answer, not current legal guidance or a claim that simulation tests authorize real trading.

## 2. Project framing and genuine GenAI/agentic behavior

### Q9. Give a 45-second project introduction.

“AegisTrade is a human-governed trading research prototype. It screens a frozen 20-stock NSE research universe under capital and risk rules. Three tool-using LLM specialists interpret market evidence, explain the permitted strategy with retrieved policy citations and critique it. Code validates and sizes the proposal; a person approves the exact payload before a local simulated action. We evaluate grounded explanations and safety separately from deterministic replay returns. We do not claim profitable trading, live execution or complete final evaluation.”

### Q10. How is it GenAI if synthetic data and no-model modes exist?

Data source and generation are independent choices. Synthetic data supports reproducible tests; real NSE data is now cached and active locally. C0 and the technical-only historical baseline use no generator; the C2 historical portfolio invokes the generator for entries and scheduled holding reviews. C1/C2 call OpenRouter to produce tool requests, explanations, citations and judgments. An executed C2 with authentic responses is GenAI; an available button or a mocked test alone does not prove a real generation run. The last saved provider check returned 402, so live successful evidence remains a preparation task.

### Q11. What makes it agentic rather than just a prompt?

Each C2 specialist operates an observation/action loop: inspect its context, select a scoped MCP tool, receive evidence, then return a typed result or correct an invalid response within budget. A supervisor coordinates roles and conditional validation. The specialist's tool choices and interpretation are model-driven, while permissions and final eligibility are code-driven. This is bounded agentic behavior; it is not unrestricted autonomous trading.

### Q12. Is the supervisor itself an LLM agent?

No. It is deterministic LangGraph orchestration. It delegates in a visible plan, validates typed hand-offs and follows bounded correction/blocking branches. Keeping planning control in code avoids another paid planner request. The three specialists are the LLM components required for the multi-agent design.

### Q13. Is the LLM discovering profitable strategies?

No. The catalogue contains EMA_TREND, RSI_REVERSION and BREAKOUT, plus NONE for abstention. Code defines the allowed mapping. The LLM gathers evidence and explains/checks the allowed decision. It now also interprets dated company filings and issuer news, reporting financial/event context and evidence limitations; it still does not invent a strategy or calculate a guaranteed fair value. To claim strategy discovery or return optimization would require a different design and leakage-controlled experiments. Current research asks whether constrained agents improve evidence quality and robustness at acceptable cost.

### Q14. Why use an LLM when code already knows the correct route?

The defensible use is translating technical evidence, dated company financial filings, issuer news and policy into a cited explanation, interpreting event risks, checking consistency and making failures interpretable. This extends the earlier policy-only research scope. Arithmetic and deterministic eligibility stay in code because a model adds unnecessary uncertainty there. C2 can now also block a prospective entry on company evidence and recommend a cited HOLD/EXIT for an existing position, so its decisions can change the historical portfolio. E1 and portfolio comparisons must establish whether those benefits justify added calls/cost rather than assuming improvement.

### Q15. Why separate historical replay from supervised research?

There are now three scopes. The technical-only baseline makes no generation calls. The C2 historical portfolio completes research before every prospective entry and periodically reviews holdings; code carries cash/positions through the period, fills exits and marks unsold positions at the end. It uses upfront rule approval and a total model-call allowance. The supervised single-action workflow separately demonstrates exact per-order human review. C2 portfolio returns now belong to that researched portfolio, not to the technical reference. A genuine benefit still requires measured comparisons.

### Q16. Can a person approve while research is still running?

The current proposal path should reject that. Backend validation requires completed C2, all specialist evidence, accepted critic, guard pass, no errors and matching provenance before a proposal is created. Human approval occurs after that research. A front-end “research passed” flag is not trusted. C0/C1, pending or failed C2 cannot unlock the supervised proposal.

## 3. Data, stock selection and quantitative design

### Q17. How were the top 20 chosen, and why not all 50?

The downloader starts from a current official Nifty 50 membership snapshot and freezes a top-20 subset by mean Close × Volume over up to 60 pre-evaluation sessions, requiring at least 20. Twenty liquid stocks keep the capstone tractable and still allow portfolio selection. This is an authored research choice, not the index's official ranking. Current membership creates survivorship bias even though the liquidity window is pre-period.

### Q18. What data is actually available?

The local NSEPython cache has 26,580 daily OHLCV rows for 20 symbols. It includes warm-up from 1 July2021 and requested evaluation from 8 November2021 through 8 November2026, with 1,242 evaluation sessions per symbol. The endpoint date can be a non-trading day; effective bars stop at available sessions. Market Data shows actual coverage. Do not describe this as adjusted, intraday or live data.

### Q19. What does OHLCV mean?

Open, high, low, close and volume for each session. Code uses it to compute indicators, screening evidence and historical fills. Structured OHLCV is obtained through market tools; it is not replaced by an LLM's numerical estimates or treated as a pile of text documents for RAG.

### Q20. How does automatic daily stock picking work?

Code filters for sufficient history, indicators, liquidity, acceptable volatility, current entry eligibility, no held duplicate, capacity/cash and risk. It rejects large-jump-affected new entries for 20 sessions. Survivors receive a score:70% strategy strength,20% liquidity percentile and 10% lower ATR fraction. Symbol tie-breaking is deterministic. Capital constrains affordability and final size. The score is a ranking heuristic, not a probability of profit or a model forecast.

### Q21. What is a market regime, and which rule wins when several match?

A regime is a code-defined description used to constrain routing. Precedence is WARMUP, HIGH_VOL, BREAKOUT, TREND, RANGE, then UNCERTAIN. HIGH_VOL therefore blocks a breakout when volatility exceeds the limit. BREAKOUT requires a close above prior20-session high and ADX≥18; TREND requires ADX≥22 and EMA20>EMA50; RANGE is ADX<22 after earlier rules. A route does not itself guarantee an entry signal.

### Q22. Why are the RSI threshold and risk numbers different from the initial proposal?

The proposal marked its values as examples. The code currently enters RSI reversion below 42 with Close>0.88×EMA50 and exits above 58; default risk is 1%, four positions and 3% daily loss. We document actual implemented values consistently instead of silently claiming the proposal's 0.5%/five/2% defaults. Parameter effectiveness still requires independent testing rather than hindsight tuning.

### Q23. How do you avoid look-ahead bias in replay?

Signals and ranking use completed-session evidence; the prior breakout high excludes the current bar. Orders fill at the next eligible open, with quantity recalculated from that fill and costs. Warm-up is not an evaluation period. The research tool locks its historical case, and external sources are date-filtered. These controls do not eliminate current-membership survivorship bias or raw-price distortions.

### Q24. Explain ATR sizing with an example.

For equity ₹200,000, entry ₹500 and ATR₹10, a 2ATR stop is ₹480. At1% risk,₹2,000 divided by ₹20 stop distance permits 100 shares. A20% position cap permits 80 shares, so the minimum is 80 before fee/cash/other checks. Modeled initial stop-distance exposure is ₹1,600. Code rounds to whole shares, validates finite positive values and rejects zero-size orders. Gaps may create larger losses than the initial risk estimate.

### Q25. Why are current results provisional even with real NSE data?

The universe uses current constituents and raw prices have not been adjusted for splits, bonuses, demergers or dividends. These can create artificial returns and signals. Alias mapping fixes identifiers, not economic continuity. The large-jump filter only rejects some new entries; it does not repair marked holdings. Download integrity and correct code execution are different from financially valid inference.

### Q26. How do fees, missing bars and the benchmark work?

Replay defaults to10 bps fees and 10 bps adverse slippage. Missing bars keep the last known holding mark with staleness disclosure and delay orders until a valid bar. The passive equal-weight comparator uses the same universe/cost assumptions, but no active stops or position-cap behavior, so it is not risk-identical. Show costs and drawdown alongside any return rather than presenting an unqualified winner.

## 4. LLM calls, tools and orchestration

### Q27. Exactly where does external inference happen?

External inference occurs in C1/C2 single-case research, each C2 historical prospective-entry case and each scheduled C2 holding-review case. Normal C2 has two inference units per specialist, six total, bounded by eight per case. OpenRouter units are HTTP requests; Codex units are CLI invocations whose internal request count is unknown. MCP/archive retrieval and PDF extraction are not additional generation calls. Code sizing, actual fill accounting, protective/strategy exits and final valuation make no model call. Development reflection can add one separately consented request. The technical-only baseline remains zero generation.

### Q28. What do the paid-run gates check?

Reviewer authentication, selected-backend readiness (OpenRouter key or ChatGPT CLI sign-in), explicit enable flag, per-run consent and requested case/inference bounds. They prevent accidental cloud use. They do not verify the account balance or guarantee a dollar maximum. Status “key configured” cannot establish that a paid request will succeed.

### Q29. What are the budgets and why do they matter?

C1 and C2 share an eight-inference-unit ceiling and16 MCP tool calls. Normally4,800 aggregate allocated response tokens are available per case; the UI offers6,400. OpenRouter sends per-request max_tokens. Codex uses guidance and local size checks, not a hard provider output/reasoning-token cap. Context is bounded at 26,000 characters. Three cases in AI Agent Experiments can attempt24 C2 calls; ALL includes C1 and C2 and can attempt48. A ceiling bounds behavior and makes comparisons fairer, but actual calls/input tokens/cost differ. Record measured consumption, not just the ceiling.

### Q30. Can this project use the existing ChatGPT Plus account?

Yes. Version 0.16 adds codex_cli using the official CLI and supported ChatGPT login; this is the current local configuration. OpenRouter remains an explicit configuration alternative, with separate API access/credits. Plus does not fund OpenRouter. Codex consumes account allowance, not unlimited free inference. Never paste ChatGPT credentials, OAuth tokens or provider keys into the reviewer-token field.

### Q31. Which model is used, and can it change?

OpenRouter defaults to OPENROUTER_MODEL/openai/gpt-4.1-mini at temperature0. Codex uses AEGIS_LLM_MODEL or codex-default, which delegates model selection to the CLI and is not a pinned model. CLI sampling settings are not claimed equivalent to OpenRouter temperature0. Record effective model ID, prompt/config version, retrieval mode and budget in run metadata. Temperature0 improves consistency but does not guarantee identical provider responses; final held-out comparisons still require repeats.

### Q32. What does MCP add compared with a Python function call?

It gives a protocol boundary for tool discovery, schemas and invocation, allowing evidence services to run as stdio subprocesses locally or HTTP services in deployment. The research loop actually opens FastMCP sessions and receives tool observations. Merely wrapping a Python function in a server file would not prove it was on the agent path. Contract tests and real stdio traces supply that evidence; Docker HTTP still needs full deployment proof.

### Q33. What are the specialist permissions?

Market requests market_snapshot and company_evidence. Strategy requests search_policy and check_strategy. Critic requests search_policy, check_strategy and company_evidence independently. C1 receives the union for fair comparison. None receives simulated broker submission. Six server modules exist overall, but only three participate in research. Broker writes occur in deterministic code after authenticated human approval; the action MCP server is omitted from Compose.

### Q34. What are typed hand-offs, and why not pass arbitrary prose?

Market returns a constrained regime, explanation and typed company assessment (status, summary, CMP citations, risks and limitations); strategy returns a permitted strategy, citation IDs and explanation; critic returns acceptance and reason. Pydantic validates those payloads. Typed messages expose missing/invalid fields and allow code guards to compare evidence with the deterministic route. Prose can still be wrong, so type validation complements evidence checks rather than proving correctness.

### Q35. What happens after a contradictory response or critic rejection?

A bounded specialist loop can receive schema/evidence feedback and correct its response within the shared budget. A controlled test corrected a contradictory market result with seven total calls. Critic rejection blocks research. The supervisor ends the case immediately on rejection. The former extra strategy-revision call could not authorize a result without a fresh critic and has been removed. We cannot describe this as unlimited self-repair or proven successful critic-driven reacceptance.

### Q36. What can resume after a crash?

The supervised action graph resumes a SQLite interrupt. The C2 historical portfolio separately checkpoints OPEN/CLOSE phases, queue, cash, positions, completed days and per-decision research files. Resuming a close must not repeat opening fills or successful paid research. Provider calls cannot resume halfway through a request: a crash without a durable response retains the full eight-call reservation as uncertain. Data/prompt/model/corpus/version changes prevent mixing configurations on resume. Saved C2 portfolio IDs restore history after browser restart; the single-action UI still has its own session-restoration limits.

## 5. Retrieval, provenance and learning

### Q37. Is RAG actually implemented? What is its corpus?

Yes:81 validated passages,72 project policy/code specifications and 9 external background summaries, with source/date/authority metadata. Neural retrieval uses local MiniLM embeddings, BM25, RRF, cross-encoder reranking and query rewriting, with a persistent Chroma index. C2 receives retrieved passages through MCP and cites their IDs. The81-passage index is policy/system knowledge. Dated company financial filings and issuer news now live in a separate point-in-time pack, exposed through company_evidence. This is not comprehensive independent press coverage.

### Q38. Why combine keyword and vector retrieval with RRF?

BM25 is effective for exact policy names and thresholds; vector retrieval captures paraphrases. Their numerical scores have different scales. RRF combines rank contributions, conventionally1/(60+rank), rather than adding incomparable raw scores. A cross-encoder then scores query/passage pairs in the shortlist to improve final ordering. This adds local compute cost that should be measured.

### Q39. What do the embedding model and reranker do?

all-MiniLM-L6-v2 encodes a passage/query into 384 dimensions for candidate similarity search. ms-marco-MiniLM-L6-v2 jointly scores each shortlisted query/passage pair. Neither generates the strategy explanation. These public models run locally on CPU; the selected-backend LLM generates/criticizes the explanation after retrieval. Offline TF-IDF mode is a separate labelled baseline, not the same embedding model.

### Q40. How is a citation validated, and what remains unchecked?

Code requires cited IDs to occur in successful search_policy observations, at least one with project-policy authority. It checks current corpus provenance and route consistency. That rejects fabricated IDs and irrelevant authority claims, but an existing passage can still be misinterpreted. Semantic support and faithfulness require reviewed answer labels and a calibrated judge or human assessment.

### Q41. How do you prevent future documents leaking into a historical case?

The policy case locks its search as_of date. External policy references published later are excluded; unknown publication uses retrieval date conservatively. Company research uses exact publication/dissemination timestamps at or before 15:30 IST on the case date; an accounting quarter-end is not an availability timestamp. Imported date-only news is delayed to the following IST midnight. Indexed/authored dates are displayed separately. Current project policies define the experiment rather than impersonating historical news. This source filter does not imply historical index membership or adjusted data is correct.

### Q42. What retrieval results can you honestly quote?

On the same101 authored development queries, neural Recall@5 is 0.9505 without rewriting and 0.9703 with rewriting, an absolute1.98-percentage-point increase. On the older36-query subset, expanded neural retrieval is 0.9167 versus 0.9444 for the original smaller offline corpus, so a regression remains. Labels are not independently held-out/exhaustive. These results do not establish generated-answer quality or trading performance.

### Q43. How is Recall@5 different from hit rate?

For one query, Recall@5 is the number of relevant passage IDs in the top five divided by the total labelled relevant IDs. Macro recall averages across queries. Hit rate asks only whether at least one relevant passage appears. If a query has four relevant passages and retrieves one, recall is 0.25 while hit is 1. Confusing them overstates retrieval quality. Label completeness affects recall interpretation.

### Q44. How does Reflexion differ from a canned lesson?

Actual Reflexion consumes a scored development failure with a real model response and uses a separate paid generation request to draft a conditional lesson. A UI template is deterministic teaching material. Provider-credit failures have no model reasoning to reflect on and are excluded. Every generated lesson remains pending until a person reviews it; an accepted lesson still requires unseen-case evaluation.

### Q45. How do you stop bad lessons contaminating later runs?

Require applicability, human acceptance/rejection with reasons, relevance filtering and a frozen playbook before held-out use. Pending/rejected lessons are excluded. Store the frozen manifest/hash so E3 can reproduce its memory condition. Relevance matching is currently simple, so review overbroad lessons carefully. Do not allow a lesson to change risk limits, grant permission or memorize held-out answers.

### Q46. What is the current memory weakness against the guideline?

Version 0.19 implements extractive evidence packing and duplicate-window references with a 26,000-character cap. Source windows preserve selected impact, amount, status and event context; full observations remain audited. Seven previously overflowing saved cases were checked with mocked generation and fit below the limit. This is not unrestricted summarization: essential missing context still requires abstention, and a larger unseen evidence shape can still hit the cap.

## 6. Approval, execution and security

### Q47. What exactly binds research to an order?

Backend validation reloads a completed passing C2 result and verifies its typed hand-offs, observed evidence tools, critic, route and citations. It checks the current corpus SHA-256, observed financial-content CMP citations for SUFFICIENT assessments, or a completed cited adverse SCAN with explicit LIMITED coverage; material/unknown adverse risk does not authorize a new position, and stores the company-pack digest plus research-result and locked-snapshot linkage. Market and critic must observe the current matching pack. Start/resume revalidate current market/entry evidence. The order then has its own exact-payload hash and request identity. Research validity and human payload approval are separate required gates.

### Q48. What if research or the knowledge corpus changes after approval?

The current digest/corpus/evidence checks should block use of the old linkage. A person approved a decision supported by a specific research version, not any future replacement text. Run current C2, create a new proposal and obtain fresh approval. Browser fields cannot waive that check. Historical saved results lacking provenance also require fresh research.

### Q49. Why does editing quantity invalidate approval?

Quantity changes money at risk and the exact action. Edit creates a new payload/hash/request identity and reruns risk/critic checks; it returns for a new human approval. The old hash is rejected. This implements the guideline's “approve that exact change” rule and protects against a time-of-check/time-of-use substitution.

### Q50. What is checked immediately before submission?

Approval identity/hash and expiry, current research/evidence, kill switch, valid finite price/quantity/stop values, quote freshness/deviation and risk policy. Standard quote age is 90 seconds; the replay UI uses 600 seconds. Approval expires after ten minutes; deviation tolerance is 2%. These are simulator quote rules, not proof of a live feed. Approval cannot override failed final checks.

### Q51. How do idempotency and timeout recovery work?

The local broker records request identity and payload hash durably. A repeated identity with the same payload resolves to the existing action; a mismatched payload is rejected. If a simulated timeout occurs after commit, reconciliation queries the durable result instead of assuming failure and placing another order. The safety claim is scoped to the local simulator and tested scenarios, not universal exactly-once delivery across real exchanges.

### Q52. What does the kill switch do and not do?

It blocks new proposals/submissions and invalidates outstanding approval tokens. Turning it off requires fresh order approval; it does not resurrect old consent. It does not liquidate a real position or cancel exchange orders because no such integration exists. Show the control state and blocked attempt, then restore it deliberately for further demo work.

### Q53. What is prompt injection in this project?

Untrusted retrieved policy-like text, imported logs or tool observations could tell a specialist to ignore constraints, leak secrets or call an unauthorized action. Such content is evidence, not an instruction authority. Scoped tools, schema validation, input/output checks, route/citation guards and absence of model write access limit effects. Human approval is an additional control, not a reason to trust malicious text.

### Q54. What do your red-team numbers prove?

The lexical scanner detected 30 of 32 seeded attacks and falsely blocked 0 of 10 clean samples. These small authored tests measure scanner behavior only. They do not establish a successful attack rate against the actual LLM or real broker. E2 must compare actual model outcomes with scanner off/on using independent poisoned-tool/data cases and clean work. Hard permissions/approval remain on, and the current metric counts forbidden-tool attempts or forbidden final text.

### Q55. Is the reviewer token production-grade security?

No. It is a private local demo credential for reviewer actions. It is not a complete identity provider, role system, authorization audit or account recovery design. Internal HTTP MCP endpoints also lack production-grade authentication. Restricting exposure and binding actions is useful, but a real-user deployment needs stronger identity, isolation, secret management and operational controls.

### Q56. What is not yet a full paper-trading portfolio?

The C2 historical simulator now has a complete within-run cash/holdings ledger, entry research, scheduled holding reviews, code/model exits and realized/unrealized accounting. At the end it reports open holdings rather than selling them artificially. It remains historical, not an ongoing live forward portfolio. The separate Supervised Trading reference capital still sizes one proposal and does not share a reconciled forward ledger with these simulations. A new independent historical run starts from its own specified capital; extending the date window requires a new run.

## 7. Evaluation, monitoring and deployment

### Q57. What are E1, E2, E3 and E4?

E1 compares C0 fixed reference, C1 single agent and C2 specialists with fair cases/model/tools/ceilings. E2 compares defenses off/on on independent attacks and clean tasks. E3 compares a frozen reviewed playbook off/on, including generation cost and harmful lessons. E4 is the signature ablation: routing versus fixed strategies under consistent assumptions, with safe-execution failure evidence for the second signature. The original E4 CLI remains a synthetic deterministic reference. The new C2 historical portfolio adds a separate same-window ROUTER/passive comparison including entry filters and holding-review exits; actual independent performance evidence is still required. Agree the custom-topic ablation with faculty if required.

### Q58. What makes a fair golden set and held-out evaluation?

At least60 independently reviewed cases, roughly 20 development and at least 40 untouched held-out, with variants grouped by scenario family. Tuning uses development only; solver prompts/tools must never receive expected answers. Protect held-out files from the solver process, not merely its tool list. Repeat final held-out comparisons three times and report spread. If a viewed held-out failure drives a change, disclose and reclassify those cases as development.

### Q59. Why do you need a different-family judge and Cohen's kappa?

Code checks exact outcomes and tool/risk invariants; nuanced explanation faithfulness may need a judge. A genuinely different model family reduces shared biases, but does not eliminate them. Compare actual judge labels with at least 20 human labels and report agreement/confusion and kappa, which adjusts observed agreement for expected chance agreement. The script's provider-prefix check is only a proxy; the team must verify actual family difference. Real predictions/labels are still missing.

### Q60. Which metrics should the report include?

Success counts/rate, policy violations, attack success, legitimate false blocks, actual calls/tokens/cost per case, median and 95th-percentile latency, errors/timeouts and repeated-run spread. Include failed runs. Report unknown provider cost as unknown, not zero. For learning, add reflection/review overhead and regressions; for replay, show drawdown/cost/benchmark and data limitations. Keep retrieval, agent-quality and portfolio metrics separate.

### Q61. What is actually measured so far?

Version 0.16 records 141 passing local tests, including chronological C2 portfolio entry/exit accounting, no terminal liquidation, phase resume without duplicate fills, conservative uncertain-call budgeting, provider failure pauses and authenticated UI consent. The earlier five-year technical replay had1,242 sessions,24,840 audit rows and 326 ledger events with zero model calls; it is not C2 performance. Real company/MCP/neural integration has been checked with explicitly mocked generation. Independent repeated actual-provider E1/E2/E3, calibrated judge and clean Docker/alert/hosted-CI proof remain separate evidence requirements.

### Q62. What can Grafana show, and what remains in local traces?

Panels show request volume, blocked trade events, API health, approved proposals, completed simulations and attempted inference units by configuration. Specialist tools, hand-offs and provider usage are saved in research JSON. Dedicated token/cost/tool-latency Grafana panels and external LangSmith/Langfuse integration are not implemented. Metrics count attempts where labelled; a call counter does not prove model success or correct answers.

### Q63. How would you prove deployment, an alert and failed CI?

On a clean machine start the full Compose stack, seed/activate the dataset and neural cache in Docker volumes, verify HTTP MCP and current UI, then capture health and one genuine research case. With Prometheus still running, stop only API until AegisAPIDown fires, then restore it. For CI, run the deliberate failure-demo workflow in a sanitized hosted repository; retain logs showing 85% below 90%. YAML validation, alert definitions and a local exit1 do not replace those live evidence items.

### Q64. What are the biggest limitations and next priorities?

For the demo: current service restart, genuine funded one-case C2 success, an eligible selection date, edit/approval/audit and failure rehearsal. For remaining technical work: broader context-packing evaluation, tighter output/error contracts, independent protected evaluation, real judge/held-out/security/learning evidence, clean Docker/alert/CI proof. For financial validity: corporate actions, historical membership, calendars, licensing and chronological out-of-sample research. We prioritize accurate evidence over adding more strategy/provider variants.

## 8. Historical company research extension

### Q65. Does the LLM now research fundamentals and historical news?

Yes, within a bounded scope. The market specialist reads historical financial filings and issuer releases through company_evidence, interprets them with citations and states event risks/limitations. The critic independently observes the same pack. Policy RAG remains a separate index. We do not claim a complete valuation model, standardized ratio database or comprehensive independent-news search. The default source is the official NSE corporate-announcement archive; reviewed licensed news/newsletter excerpts can be imported.

### Q66. Which exact time determines whether a source is allowed?

15:30 Asia/Kolkata on the selected daily signal date. Availability is the later of exchange announcement/dissemination times. A September-quarter result released in November cannot influence an October case; a15:40 release cannot influence the 15:30 decision that day. Imported news with only a publication date is conservatively delayed until next local midnight. The LLM cannot change the locked symbol/date through its tool arguments.

### Q67. What does SUFFICIENT mean? Is it a buy recommendation?

It means the bounded exchange scan completed and a readable recent financial filing with financial-content markers is available, and the typed company assessment cites observed evidence. It does not mean good fundamentals, audited extraction or profitability. The model can return REVIEW_REQUIRED for unresolved material events or INSUFFICIENT_EVIDENCE for inadequate evidence. Both block order eligibility even when technical indicators show a valid entry.

### Q68. Why not search Google or trust the model's historical knowledge?

Search pages and retrospective articles can leak information unavailable at the simulated decision time. A model's training memory has no dependable publication cutoff for each claim. The project supplies dated source-backed evidence and original URLs rather than asking it to remember old news. The bounded archive is imperfect but inspectable. Independent press/newsletters require verified original publication metadata and a named reviewer; that is explicit attestation, not automatic proof.

### Q69. Do more fundamental tools mean more paid calls?

Not necessarily. Market requests its two tools together, strategy its two, and critic its three, then each interprets observations. Normal C2 therefore uses seven tool invocations within six generation requests, retaining the eight-request shared ceiling. Downloads, extraction and cache inspection make zero paid model calls. Service preflight blocks missing coverage before generation. Corrections still consume extra requests within the same budget.

### Q70. What happens if a financial PDF is scanned, too large or just a notice?

There is no OCR or unlimited download fallback. Extraction is bounded and unreadable/invalid attachments are reported. A generic annual-report-link notice cannot alone qualify as financial content. If no qualifying readable recent financial filing remains, coverage is insufficient and order preparation is blocked. The actual INFY demo-date pack currently illustrates this outcome; TCS has readable results. Missing data does not mean no company risk.

### Q71. How are financial numbers interpreted safely?

The tool provides extractive table windows and the original filing. A filing can contain consolidated and standalone statements and several period columns. The prompt forbids quoting or comparing numbers without explicit unit/period/basis. Code detects financial content but does not independently normalize or audit every accounting figure. A qualitative summary with disclosed limitations is preferable to an invented ratio. Human/judge faithfulness evaluation remains necessary.

### Q72. What if a source is refreshed after the person approves?

The full company pack is hashed and linked to the saved research result. Both specialists' observations must match current storage. Refresh/import changes the digest; start/resume block old research or an outstanding approval. New evidence requires new C2, proposal and human approval. This extends exact-payload control to the evidence supporting the action, rather than treating all future revisions as already approved.

## 9. Complete C2 historical portfolio: entry, exits and valuation

### Q73. Is the historical simulator now really C2 in the loop?

Yes. A new portfolio entry cannot queue without dated company evidence, all three C2 specialist hand-offs, accepted critic, valid citations and passing code checks. The next eligible open revalidates that research and recalculates size under actual cash/gap/risk conditions. Holdings are reviewed by C2 every configured N market sessions. The portfolio's own resulting ledger/equity measures this flow; the technical-only reference is separately labelled. Mocked integration tests prove wiring, not actual model profitability.

### Q74. Which exit paths exist, and can the model block a stop?

Code executes protective2ATR stops with gap-aware prices. Code also queues strategy exits at the completed close: EMA20<EMA50 for trend, RSI>58 for reversion, Close<EMA20 for breakout. These rules operate under upfront replay approval and do not wait for C2. Scheduled C2 holding reviews can additionally produce a cited critic-accepted EXIT for the next eligible open. HOLD never disables a stop or vetoes a strategy exit. All sale fills and costs enter realized P&L.

### Q75. Why can positions remain after the end date?

The end date stops observation; it is not an economic reason to sell. If no valid exit filled within the window, the position remains open and is marked at its last available close with date/staleness disclosed. No exit fee or hypothetical sale is invented. An exit signal occurring only at the final close remains a pending intention because the next open lies outside the replay. A genuine exit queued earlier can still fill on the final session.

### Q76. How do realized and unrealized P&L reconcile?

Realized P&L comes from completed sells after entry/exit costs. Unrealized P&L is marked value less entry cost basis of unsold holdings, including their entry fee once. Ending equity equals cash plus marked holdings, and also initial capital plus realized plus unrealized P&L. No terminal sale is needed for a total-equity return. Model charges remain separately reported USD; INR trading returns do not silently assume an exchange-rate conversion. Unknown provider cost is not zero.

### Q77. Does this call the model for all 20 stocks every day?

No. Code cheaply screens the universe and keeps portfolio/risk arithmetic. C2 researches selected prospective entries and scheduled holding reviews, default every five market sessions, rather than every bar or every fill. A valid code stop/strategy exit needs no paid call. The global allowance defaults to48 attempted requests, and each research case reserves up to eight even though six is normal. Exhaustion pauses before another case; an explicit consented resume can extend the allowance.

### Q78. How do you avoid duplicate trades or hidden retry costs after a crash?

Persist separate OPEN/CLOSE phases and each decision's durable research result. A resumed close does not repeat opening fills. The same completed decision reuses its saved result. Reserve the eight-call ceiling before making requests; settle to known actual usage afterwards. If a crash leaves no durable response, keep the reservation as uncertain rather than refunding or claiming zero. Provider errors pause promptly; retry requires explicit resume consent and retains the failed trace.

### Q79. What happens when fundamental evidence is missing during replay?

A prospective entry is blocked before paid generation and cannot fill. A holding-review gap does not automatically sell a position or pretend the company is healthy; existing stops/strategy exits remain active and the gap is logged. A completed window with such failures is labelled COMPLETED_WITH_GAPS. Returns then reflect availability-driven abstention as well as model decisions, so compare coverage, failures, costs and risk before attributing any return difference to useful AI.

### Q80. Who approves trades in the historical C2 portfolio?

Before starting, a reviewer explicitly approves the historical entry/exit rules and paid-call allowance. Within that evaluation scope, validated historical fills proceed automatically, including risk-reducing exits. This makes a multi-year replay feasible. The separate supervised-order demonstration still interrupts for approve/edit/reject of each exact payload. Neither approval scope authorizes real brokerage activity. Paused/incomplete C2 runs are not full-period performance reports; full-period reference metrics are withheld until completion.

## 10. Team rehearsal and answer discipline

Veneet should lead data/quant/evaluation demonstrations, Karthika the RAG/MCP/LLM trace and reflection design, and Mathangi risk/approval/recovery/deployment. These are suggested responsibility boundaries, not proof of actual contributions; keep dated contribution logs. Independent case/attack authorship must remain separate from agent/defense tuning. All three should answer Q1–Q8 and explain where the other components fit.

Practice a whiteboard drawing with eight boxes: UI/API, data/screening, deterministic replay, C2 supervisor/specialists, MCP/RAG, completed research gate, persistent approval graph, simulated broker/audit. Mark the selected inference transport as the cloud boundary and the exact human approval as the action boundary. Explain normal six-call behavior without claiming the supervisor makes another call.

Before the viva, prepare a private evidence card containing one genuine research run/case, corpus version, a selection date, a waiting order/thread/hash, the edited hash, broker event, actual E1–E4 report paths and the known remaining gaps. Keep keys/tokens off that card and off the screen.

Answer using: current behavior → reason → evidence → limitation when material. If a result is not measured, say so and explain the experiment that would measure it. Never call mocked generation a real provider response, scanner detections a live attack-success result, a config parse a deployment proof, or deterministic replay a C2 investment return.

## 11. Quick evidence map

| Topic | Where to inspect |
|---|---|
| Overall design and exact UI instructions | AegisTrade_Detailed_Design_and_Demo_Guide.docx, Sections2–10 |
| Roles, prompts, effective-model baseline and budgets | config/agents.json; aegistrade/llm_research.py |
| Regimes, entry/exit and sizing | aegistrade/strategies.py; selection.py; safety.py |
| Real MCP runtime and tool schemas | aegistrade/mcp_runtime.py; docs/MCP_TOOL_INVENTORY.json |
| Corpus and hybrid retrieval | knowledge/corpus.jsonl; aegistrade/corpus.py; knowledge.py |
| Neural development metrics | reports/rag_development.json |
| Research provenance and action binding | aegistrade/research_gate.py; app/api.py; workflow.py |
| C2 historical portfolio | aegistrade/c2_portfolio.py; docs/C2_HISTORICAL_PORTFOLIO.md |
| Historical company research | aegistrade/company_research.py; docs/HISTORICAL_COMPANY_RESEARCH.md |
| Lessons and reflection | aegistrade/lessons.py; reflection.py; docs/MEMORY_POLICY.md |
| Experiment protocols and judge calibration | evaluation/run_capstone.py; judge_agreement.py |
| Security scope | docs/THREAT_MODEL.md; evaluation/; tests/ |
| Actual verification boundaries | docs/BUILD_AND_VERIFICATION_STATUS.json; reports/ |
| Alerts, panels and CI | monitoring/alerts.yml; monitoring/grafana/dashboards/aegistrade.json; .github/workflows/ci.yml |

Guideline references: minimum bar p.3; experiment/submission requirements pp.5–6; eight required team questions p.17. The professor-approved three-person arrangement is settled. Any separate custom-topic or signature-ablation approval should be confirmed through the course process, without reopening team size.

## 12. Codex CLI, Plus and provider configuration

### Q81. Where does GenAI happen when using Codex instead of OpenRouter?

Each specialist invokes Codex with its role conversation and a structured-response schema. It first asks for declared evidence tools, then interprets their observations and returns typed JSON. The application runs actual MCP tools and validates the output. The GenAI work is real model inference; the CLI is its transport. LangGraph still coordinates market, strategy and critic.

### Q82. Does Codex get shell access or the five-year dataset?

The adapter runs in a temporary directory, disables native shell/apps/web/MCP/memory tools, ignores user rules/config and passes no project API/reviewer secrets. It receives only the current conversation and selected observations. AegisTrade executes virtual tools under role permissions and historical cutoffs. Unexpected native-tool events or malformed responses block the case. Pretrained later knowledge remains a limitation, so require cited supplied evidence.

### Q83. Are eight CLI invocations the same as eight model requests?

No. The application bounds eight CLI invocations per case. Internal provider requests are not counted by the CLI adapter. The response-token setting is conciseness guidance and local response-size validation, not a hard cap on provider reasoning/output tokens or cost. Record actual CLI token usage and unknown per-run USD charge. Plus allowance can be exhausted even with a small final JSON.

### Q84. Can switching configuration return to OpenRouter?

Yes. Stop the launcher, set AEGIS_LLM_BACKEND=openrouter, clear AEGIS_LLM_MODEL so OPENROUTER_MODEL applies, retain the private provider key and restart. Codex uses codex_cli plus supported login. No automatic fallback occurs. Paused historical jobs freeze backend/model/adapter/unit and reject a changed identity; restore it or start a new job. Completed research retains provenance.

### Q85. What proves that the Plus route actually works?

reports/codex_c2_demo.json records genuine HINDUNILVR-2023-03-31 research, saved run 290874d24eeb498b868949c2796b3424. It passed the guard and completed-research gate using 7 CLI invocations and 7 actual MCP tool calls with neural RAG. It reported 59,069 tokens and about66 seconds latency; USD cost was not available. This is one verified case, not proof of profitability or final E1–E4 results. Earlier mocked reports remain separately labelled.

### Q86. What happens when Plus reaches its limit mid-replay?

Provider failure records the attempt and pauses as PAUSED_PROVIDER. The engine makes no unresearched entry and does not switch billing providers. Completed research and phases stay on disk. Resolve allowance/login/network, then explicitly consent to resume. An unresolved crash retains a conservative uncertain reservation. Protective code exits remain independent in sessions the simulator actually processes; a paused historical job is not a live monitoring service.

### Q87. Why is codex-default suitable for a demo but insufficient for a formal comparison?

It selects the CLI's current available default, which can change. The JSON events in the verified run did not identify a resolved model. Formal comparisons need a supported explicit AEGIS_LLM_MODEL, recorded CLI/version, fixed evidence, repeats and comparable measured budgets. The capstone runner refuses codex-default for CLI comparative runs. Identical invocation ceilings alone do not establish equal tokens or cost.

### Q88. Does a working Plus demo satisfy every capstone requirement?

It demonstrates real GenAI, specialist coordination, MCP, RAG, dated company evidence and guarded simulated actions. Independently reviewed held-out cases, calibrated different-family judging, repeats, measured attack/defence results and required experiment reports remain separate evidence tasks. The professor-approved three-person team is accepted; a transport switch neither changes team approval nor supplies missing evaluations.

### Q89. Why did three successful model calls still produce BLOCKED?

The August 2023 traces returned company.summary exceeding600 characters. Calls succeeded, but the JSON did not satisfy the application schema; generic correction feedback did not identify the field. Version0.16.2 supplies the real field limits and exact feedback, records schema errors separately and displays a derived diagnosis for older records. A corrected schema still needs adequate company evidence, valid citations and accepted critic/code checks before any entry.

### Q90. Would increasing the call allowance fix these blocks?

A larger portfolio allowance does not fix an oversized field or an unreadable financial filing. Field-specific rewriting must preserve the substantive assessment. Missing evidence remains blocking; an insufficient market assessment now stops before additional specialists consume allowance. The old replay was paused with its audit preserved. A new prompt version requires a new run rather than silently mixing research configurations or refunding old calls.

For the November11 timeout example, explain that seven calls succeeded, the critic had rejected a citation it could not retrieve semantically, and an unproductive eighth revision timed out. The current critic reads exact cited IDs independently through MCP and rejection ends the case. CODEX_TIMEOUT, invalid output, quota and login are distinct diagnoses; a larger portfolio allowance does not fix all of them. No new model calls were used to test this update.


### Q91. How does the new trailing stop work?

New historical runs enable a2×entry-signal ATR14 distance. After each completed close, code sets the stop to max(previous stop, highest completed close since entry minus that fixed distance). It only rises. With ATR₹10 and highest close₹530, the candidate is₹510; a later close₹525 does not lower it. The initial2ATR stop, strategy exits and accepted C2 EXIT remain active. Raised-stop fills are SELL_TRAILING_STOP. All arithmetic is deterministic and adds no LLM calls. The multiplier is a configurable research assumption, not a proven optimum or profit guarantee.

### Q92. How do you avoid hindsight and preserve trailing stops across a pause?

Test today's open/low against the previously active stop first, then raise surviving positions' stops at the completed close for the next session. Use entry-signal ATR from saved validated research, never the later fill-day ATR or an intraday high. Checkpoint all stop adjustments before C2 research can pause that close; trailing_last_close makes reprocessing idempotent. Missing bars do not advance the peak. A final-close update does not force a sale. Gap-down fills use the opening price with costs, which can be below the stop. Tests cover these mechanics with mocked C2 and synthetic prices; old fixed-stop runs remain unchanged and require a new run for the changed engine/corpus. The technical reference uses matching trailing settings; passive buy-and-hold does not.


### Q93. How can a run with only30% winning closed trades still be profitable?

In the reviewed quarter, three winning trades made₹24,541.58 and seven losses totaled₹19,231.32, producing₹5,310.26 realized profit. Average winners were about₹8,181 against average losses of₹2,747. Four unsold holdings contributed another₹16,003.80 after entry fees, giving₹21,314.06 total marked profit. Win rate alone ignores payoff size and unrealized outcomes. These ten trades do not establish a stable future distribution; forcing small profit targets could remove the larger gains.

### Q94. Did the actual C2 quarter beat the technical reference, and why?

No. C2 returned4.26% versus4.41% for the matched technical reference, approximately₹727 less on₹500,000; C2 drawdown was also larger in this window. C2 required readable dated company evidence and critic acceptance. It missed some HCLTECH/HINDALCO/HDFCBANK contributions because financial excerpts/filings were incomplete, while TMPV timing and some avoided losses favored C2. Positions, cash and capacity interacted, so individual stock differences are observed attribution rather than causal proof that adding one stock would improve the full portfolio. The result proves the audited workflow ran; it does not establish an AI financial edge. Improve evidence and evaluate separate periods before changing rules.

### Q95. Can the portfolio automatically learn a loss-reducing rule from this ledger?

The current code does not automatically turn portfolio P&L into trusted memory or inject the reviewed playbook into C2 historical portfolios. The post-run review saved hypothesis-only candidate observations separately, without accepting/freezing/indexing them. A possible opening-gap filter, aggregate-risk constraint or renewed-entry condition needs predeclared testing and human review. Do not train a lesson on future outcomes and apply it to earlier historical decisions. Keep the completed baseline unchanged, bind future lesson versions to their data period and compare risk, net return and costs on separate windows. A0.5% technical-only risk experiment reduced drawdown but also reduced the reviewed quarter's return; it is not a demonstrated C2 profit optimizer.


### Q96. Why is the Friday candidate reviewed Monday but filled no earlier than Tuesday?

Monday's full daily indicators and closing evidence are not available at Monday open. The historical engine defers the Friday entry candidate without paid entry research, re-screens and researches it at the next actual trading close, then queues a passing decision for a subsequent open. A Monday reversal cancels the stale entry. Holiday gaps use the next real session rather than assuming Monday traded. The original and refreshed signal dates remain in the audit. A pre-open Monday strategy would require a separately timestamped intraday feed and cutoff.

### Q97. Does LIMITED company research mean the stock is safe?

No. Financial completeness and adverse-event review are separate. A technically eligible entry can pass with LIMITED financial coverage only after a completed cited bounded official adverse-disclosure scan returns no material adverse evidence in that observed scope and the critic accepts the disclosed limitations. Material/unknown adverse risk, unreadable matched risk attachments, incomplete metadata or fabricated citations cannot authorize an entry. It is not exhaustive independent news, a valuation or proof of clean fundamentals.

### Q98. Why use an8% profit target, and what happens if the stop and target both trigger?

Eight percent is an explicit configurable research default requested for the demonstration, not a proven optimum. It applies per holding after modeled entry/exit fees; the trigger also accounts for adverse execution slippage. It sells the entire position as SELL_TAKE_PROFIT without a model call. Opening gaps are handled before intraday movement. If a daily bar later touches both stop and target with no known intraday ordering, use the stop first. Fixed targets can cut off larger trends, increase turnover and consume more re-entry research. Remaining positions are still marked rather than forcibly sold at the end date. Historical0.17 returns did not use this target and do not validate its profitability.


## 99. Can portfolio results teach C2 automatically?

No. Completed runs can produce deterministic pending process lessons, reviewed against dated source cases. Human acceptance and immutable freezing precede retrieval into a new portfolio. Later profit is not a correctness label and does not authorize a trade. This is reviewed retrieval memory, not model-weight training.

## 100. How do you prevent memory look-ahead bias?

Pin a version ID/hash at creation and record the latest source run end as trained_through. Evaluation starts strictly later; overlapping dates require an explicit DEVELOPMENT_REPLAY label. Pending/rejected lessons never enter context. Replay performance cannot be presented as unseen-period evidence, even if all underlying company filings were dated correctly.

## 101. How do you handle a small penalty disclosure?

Read its amount and unit, issuer-stated impact, restrictions, recency, resolution and continuing consequences. A negative keyword alone is not material downside; issuer Nil is not independent verification. Do not infer Nil from missing information or use an arbitrary absolute threshold. Keep UNKNOWN for genuinely unresolved material exposure, and cite the exact document. The independent critic and code checks still apply.


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
