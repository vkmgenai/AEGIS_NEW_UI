# Karthika: questionnaire for packet 20261117 (LLM DRAFT, not signed)

**Status of this draft.** Prepared 2026-11-17 for Karthika from `observed_results/` only. Do not finalize until the blinded labels are frozen and E1/E2/E3 have run. Per the team plan, Karthika explains traces (calls, citations, routing, critic, failures, budgets) and does not certify the expected labels of her own subsystem. Items needing Vineet's or Mathangi's independent acceptance are marked. No blinded file was filled in, and nothing here is signed on anyone's behalf.

**Runs inspected:** AI experiment `026512e1f9054db09011c4e9e611ef8d` (3 cases, C0/C1/C2, development); C2 portfolio `dc354841097240e0bc88d8430953fa22`; E4 `20261117T105811-138ef587`; deterministic neural `20261117T110205-1c7df087`; RAG report `rag_development_20261117.json`.

## Q1. Prompt, corpus, backend/model and run versions

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Versions are recorded, but the runs used different corpus and prompt versions, so they cannot be treated as one configuration.

**Evidence:**
- AI experiment: prompt `2026-11-13-dated-issuer-library-ocr-v15`; backend `codex_cli`, model `codex-default`, adapter `codex-intent-v1`, Codex CLI 0.164.0-alpha.11.1; corpus 86 passages, sha256 `b018426d...20d2a`; `use_memory` false, `memory_manifest` null (FULL_TRACE.json: prompt_version, inference, knowledge_corpus).
- RAG report: corpus 87 passages, sha256 `f4bc6994...3dcb`.
- C2 portfolio: backend `claude_cli`, model `haiku`, adapter `claude-intent-v1`, `portfolio_playbook_id` null, `memory_allow_development_replay` false.
- Repository `config/agents.json` now carries prompt `2026-11-15-relative-materiality-v16`.

**Method:** Read the fields and compared them across files.

**Exceptions:** Corpus 86 vs 87 and prompt v15 vs v16 mean the 3-case experiment ran on an older configuration than the current repository. Two different providers appear (Codex and Claude CLI). No E1/E3 run exists yet; record versions again for each.

**Reviewer/date:** Karthika, ________

## Q2. Budgets and read-tool permissions

**Status:** PARTIALLY SUPPORTED

**Conclusion:** All six C1/C2 rows stayed inside the declared ceilings and used only read tools.

**Evidence:** FULL_TRACE.json `outputs[*].budget` = 8 model calls, 16 tool calls, 3,600 output tokens, 36,000 context characters. Observed: C1 2-3 calls and 4-5 tool calls; C2 3-7 calls and 3-7 tool calls (TCS C2: 7 calls, 7 tool calls). Tools used: `market_snapshot`, `company_evidence`, `check_strategy`, `search_policy`, `search_dated_web`; none is a write tool.

**Method:** Compared `llm_calls`, `tool_calls` and `tool_trace` names with `budget` and `available_tools` for each row.

**Exceptions:** Context-character use per row was not recomputed (only `context_usage` events exist). Provider cost is null (`cost_reporting_complete` false). Three cases only.

**Reviewer/date:** Karthika, ________. Independent acceptance: Vineet or Mathangi.

## Q3. Citations vs evidence observed before the cutoff

**Status:** PARTIALLY SUPPORTED

**Conclusion:** Citation IDs follow the expected format and the critic cites observed company and scan IDs, but I did not check each quote against source text or dates.

**Evidence:** TCS C2: strategy cites `POL-21`, `POL-25`, `POL-72`; critic cites `CMP-fa039da623f2b6d7`, `SCAN-45f8c881505324db`, `WEBSCAN-a3c04c2881353199`. C1 BHARTIARTL cites none (blocked).

**Method:** Read citations from `handoffs` and `critic_reason`.

**Exceptions:** Not done: mapping each ID to the exact observed passage, its publication time and the case cutoff (2026-11-08). The data is `research30`, a curated snapshot as of 2026-11-12, so point-in-time claims need human checking. Needs independent acceptance from Vineet or Mathangi.

**Reviewer/date:** Karthika, ________

## Q4. Typed hand-offs vs locked route and purpose

**Status:** PARTIALLY SUPPORTED

**Conclusion:** In the two completed C2 cases the market, strategy and critic hand-offs all name EMA_TREND/ENTRY, matching the code route.

**Evidence:** LT and TCS C2 `handoffs` (schemas `MarketJudgement`, `StrategyJudgement`, `CriticJudgement`): regime TREND, strategy EMA_TREND, action ENTER, critic `accept: true`; `expected_strategy` and `expected_regime` match.

**Method:** Compared `handoffs[*].payload` with `expected_*` per row.

**Exceptions:** BHARTIARTL C2 stopped after the market hand-off, so strategy and critic hand-offs do not exist for it. Three cases only.

**Reviewer/date:** Karthika, ________

## Q5. Did the critic inspect evidence independently?

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The critic made its own tool calls, so it did not only repeat earlier answers, but whether its reading was truly independent is a semantic judgement for a human.

**Evidence:** TCS C2 `tool_trace`: critic called `company_evidence`, `check_strategy`, `search_policy` after the strategy hand-off (role field `critic`).

**Method:** Read tool-trace roles and the critic reason.

**Exceptions:** The critic reason largely agrees with the strategy text; no case shows the critic disagreeing. Needs independent acceptance from Vineet or Mathangi.

**Reviewer/date:** Karthika, ________

## Q6. One validation failure and replan

**Status:** SUPPORTED

**Conclusion:** TCS C2 retains a validation failure and a replan that led to an accepted typed output.

**Evidence:** FULL_TRACE.json, TCS-2026-11-08 / C2 `trajectory`: `validation_failed` (turn 2, code `COMPANY_CITATION_UNSUPPORTED`, category EVIDENCE, agent market, "Company citation not observed/readable"), then `replan` (same agent and code, "Correct the specific field or evidence issue within the existing budget"), then a `typed_handoff` for the market agent with company status SUFFICIENT and adverse_risk NO_MATERIAL_ADVERSE_FOUND.

**Method:** Read the trajectory events in order.

**Exceptions:** I did not diff the failed first output against the corrected one; the first payload is not in the extract. Ask the owner to confirm the corrected citations were observed.

**Reviewer/date:** Karthika, ________

## Q7. Classifying blocks

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The two blocks in the 3-case run have different causes: one is a policy conflict by the single agent, the other is an evidence block that may be a legitimate adverse finding.

**Evidence:**
- BHARTIARTL C1: `STRATEGY_ROUTE_CONFLICT`, category POLICY, agent single. It returned NONE while code route was EMA_TREND (`validation_failed` then `blocked`, turn 3).
- BHARTIARTL C2: `COMPANY_ASSESSMENT_BLOCKED`, category EVIDENCE, agent market. `company_assessment` = REVIEW_REQUIRED, ADVERSE_EVENT_FOUND (continuing spectrum-charge litigation); the dated web search returned `SEARCHED_BUT_INSUFFICIENT`.
- Portfolio `dc354841...`: 104 decisions: 43 BLOCKED, 26 HOLD, 13 ENTER, 12 DEFERRED_REVIEW, 4 ENTRY_CANCELLED, 4 PROVIDER_FAILURE, 2 QUALIFIED_NOT_SELECTED. Status `COMPLETED_WITH_GAPS`.

**Method:** Read failure objects and counted decision actions.

**Exceptions:** The experiment summary counts both as "model errors" and as unsuccessful. For C2 the block may be correct behaviour, so reported success (66.67%) understates it while C1's route conflict is a genuine miss. The 43 blocks were not individually split by cause. The 4 provider failures need a timeout vs schema breakdown.

**Reviewer/date:** Karthika, ________

## Q8. Dated-web fallback

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The fallback ran in three rows, but it never added an accepted source, so its date and hash handling is untested here.

**Evidence:** `dated_web_search` for BHARTIARTL C1, BHARTIARTL C2 and TCS C1: status `SEARCHED_BUT_INSUFFICIENT`, `queries_recorded` 2, `accepted_sources` 0, `cached` true. TCS C1 trajectory shows a `dated_web_fallback` event.

**Method:** Read the fields.

**Exceptions:** No accepted source means source dates and persisted hashes could not be checked. Unit tests for this exist in the repository but they are not run evidence.

**Reviewer/date:** Karthika, ________

## Q9. Lessons retrieved and any that worsened an outcome

**Status:** PENDING

**Conclusion:** No lessons were used.

**Evidence:** AI experiment `use_memory` false and `memory_manifest` null; portfolio `portfolio_playbook_id` null. No E3 off/on run exists.

**Exceptions:** Needs E3 on a frozen playbook.

**Reviewer/date:** Karthika, ________

## Q10. Lessons were development-only, human reviewed and frozen first

**Status:** PENDING

**Conclusion:** No frozen playbook or lesson review record is in the packet.

**Evidence:** None. README_FIRST lists a human-reviewed frozen playbook as still required.

**Reviewer/date:** Karthika, ________. Independent acceptance: Vineet or Mathangi.

## Q11. Measured benefit of C2 over C1, and cost without benefit

**Status:** PARTIALLY SUPPORTED

**Conclusion:** On three development cases C2 showed no measured benefit over C1 and cost about twice as much; this is far too small a sample to conclude anything.

**Evidence:** SUMMARY.json `summary`: C1 and C2 each succeeded on 2 of 3 (66.67%); model calls 8 vs 16; total tokens 111,152 vs 182,760; median latency 35.44 s vs 63.82 s; p95 40.58 s vs 70.95 s; policy violations 0 for both; C0 3 of 3 with 0 calls.

**Method:** Read the summary table.

**Exceptions:** C0 agreement is self-agreement by construction. Cost in USD is not reported. Cases were curated event cases, not a held-out set. In the portfolio extract, the only metrics block is `reference` (the technical baseline: +3.35% return, 18 completed trades, 44.44% win rate), set beside buy-and-hold at +6.78%; no C2 return metrics are included, and 20 of the 42 C2 ledger events carry the `HUMAN_EVIDENCE_OVERRIDE` marker, so it would not measure the agents alone anyway. E1 is required.

**Reviewer/date:** Karthika, ________

## Q12. Implementation, measured and unmeasured claims

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The system is implemented and tested; only small development runs are measured; most course-bar measurements are still unmeasured.

**Implemented and tested in code (not run evidence):** LangGraph C2 graph with typed hand-offs, read-only MCP tools, evidence gates, dated-web fallback, checkpoint and resume, memory workflow.

**Measured in runs:** 3-case C0/C1/C2 development comparison; 104-decision C2 portfolio (with human overrides, completed with gaps); deterministic dev check (20 of 20, labels seeded); neural RAG on 101 authored queries (hit@5 0.9604 after rewrite, up from 0.9406 before); synthetic E4 ablation.

**Unmeasured:** E1 three held-out repetitions, E2 model-level attack off/on, E3 memory off/on, E4 agent-level ablation, different-family judge and Cohen's kappa, independent labels, hosted failed-CI, fired alert. The local intentional-CI file (accuracy 0.85) is not hosted evidence.

**Reviewer/date:** Karthika, ________

## To do before signing

1. Wait for the frozen blinded labels, then run E1/E2/E3 and redo Q1-Q11 against those runs.
2. Resolve the corpus (86 vs 87) and prompt (v15 vs v16) mismatch before any final run.
3. Map every citation to its observed passage and date (Q3).
4. Have Vineet or Mathangi independently accept Q2, Q3, Q5, Q10 and Q11.
