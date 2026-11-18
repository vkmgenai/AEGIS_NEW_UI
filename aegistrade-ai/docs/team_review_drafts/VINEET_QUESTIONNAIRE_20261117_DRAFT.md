# Vineet: questionnaire for packet 20261117 (LLM DRAFT, not signed)

**Status of this draft.** Prepared 2026-11-17 for Vineet to accept, correct or reject. Reviewer and date lines are blank: Vineet must verify each answer and sign. The drafter had seen the seeded labels and `observed_results/` before drafting, so Q3 and Q8 cannot count as blinded or independent. Final answers belong after the labels are frozen and E1/E2/E3 have run.

## Q1. Run IDs and artifact hashes

**Status:** SUPPORTED (for the supplied files)

**Conclusion:** Every supplied file matches its recorded hash, and both capstone runs completed.

**Evidence:** `SHA256SUMS.txt` check: 0 mismatches. `20261117T105811-138ef587` (E4, COMPLETED, report sha256 `7e43ced6...c9451`) and `20261117T110205-1c7df087` (deterministic neural, COMPLETED, `c93f0fb4...ed7a11`); manifest `report_sha256` equals `shasum` of `report.json` for both. AI experiment `026512e1...d`, C2 portfolio `dc354841...a`, `rag_development_20261117.json` (`919fb37b...5dd065c`).

**Method:** Re-ran `shasum -a 256` and compared with the manifests and the packet checksum file.

**Exceptions:** `inputs_sha256` is empty in both manifests (no case file was passed), so no case-file hash is tied to either run. Vineet should re-run the check on his own copy.

**Reviewer/date:** ________

## Q2. Development/held-out family separation

**Status:** PARTIALLY SUPPORTED

**Conclusion:** No family name appears in both splits, but the split is weaker than it looks.

**Evidence:** Development families (4): DEV_APPROVAL_MISMATCH, DEV_ROUTE_RANGE, DEV_ROUTE_TREND, DEV_STOP_ABOVE. Held-out families (8): TEST_BROKER_DUPLICATE, TEST_BROKER_PRICE, TEST_BROKER_STALE, TEST_BROKER_VALID, TEST_RISK_CASH, TEST_RISK_POSITION_COUNT, TEST_ROUTE_BREAKOUT, TEST_ROUTE_HIGH_VOL (blinded files, `family`).

**Method:** Compared family sets; checked the `input` fields.

**Exceptions:** Each family is five variants of the same fault (only `variant` 0-4 changes), so the 60 cases are 12 distinct checks. Development approval-mismatch and held-out broker families test the same mechanism type. All cases are deterministic code checks, not agentic research cases with symbols, dates and evidence. Held-out cases were exposed to the drafter and to Karthika's reports.

**Reviewer/date:** ________. Independent acceptance: Mathangi.

## Q3. Independently label the assigned golden cases

**Status:** PENDING

**Conclusion:** No human label exists. An LLM-assist draft is at `blinded_llm_drafts/golden_*_LLM_DRAFT.jsonl` (route: TREND to EMA_TREND, RANGE to RSI_REVERSION, BREAKOUT to BREAKOUT, HIGH_VOL to NONE; risk faults and stale/price-deviation broker faults to BLOCK/REJECT; duplicate to no second fill; valid to FILL).

**Exceptions:** The draft was not blind. Vineet should label on his own before opening it.

**Reviewer/date:** ________

## Q4. Dates, point-in-time boundaries, constituent bias, unadjusted prices

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The limits are disclosed in the data provenance, and two of them are serious.

**Evidence:** AI experiment `data_provenance`: provider nsepython, universe `research30`, `membership_mode` curated_research_snapshot, `membership_asof` 2026-11-12, `survivorship_bias` true, `price_adjustment` unadjusted, `selection_bias` "deliberately selected event cases". Period 2021-11-08 to 2026-11-08. E4 run is synthetic data (2022-01-03 to 2024-05-17, 620 sessions).

**Method:** Read the provenance fields.

**Exceptions:** The case date 2026-11-08 is a Sunday, so these cases rely on the weekend-gap review rule rather than a normal session close. Membership was fixed on 2026-11-12, after the case date, which is look-back selection. The portfolio run covers 2023-09-01 to 2023-11-30 on a different capital (300,000). Corporate-action handling is by exclusion, not adjustment.

**Reviewer/date:** ________

## Q5. Did C0/C1/C2 get identical cases and fair settings?

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The three configs ran the same three cases with the same model and ceilings, but tools and budget use differ by design.

**Evidence:** FULL_TRACE `outputs`: same `case_id`s (BHARTIARTL, LT, TCS, all 2026-11-08); C1 and C2 both `codex_cli`/`codex-default`, same prompt v15, and the same `budget` (8 model calls, 16 tool calls, 3,600 output tokens, 36,000 context chars). C0 uses 0 model calls.

**Method:** Compared the fields row by row.

**Exceptions:** C1 is one agent with all tools; C2 splits tools by role (so C2 consumed 17 tool calls vs 14 for C1). The portfolio run used a different provider (`claude_cli`, `haiku`), so it is not comparable with the 3-case run. Only 3 cases, development only.

**Reviewer/date:** ________

## Q6. Three frozen repetitions without picking the best

**Status:** PENDING

**Conclusion:** None exist. The E4 and deterministic runs have `repeats` 1 and the AI experiment is a single run.

**Evidence:** Manifests `configuration.repeats` = 1.

**Reviewer/date:** ________

## Q7. Recompute success, violations, calls/cost, latency, timeouts, errors

**Status:** SUPPORTED (for the 3-case run only)

**Conclusion:** The summary recomputes exactly from the row data.

**Evidence:** C1: 2 of 3 guard-pass (66.67%), 8 model calls, mean latency 34.585 s, median 35.44 s, tokens 111,152, 1 model error. C2: 2 of 3, 16 calls, mean 54.912 s, median 63.819 s, tokens 182,760, 1 model error. C0: 3 of 3, 0 calls. Policy violations 0 for all. Dollar cost is null (`cost_reporting_complete` false); no timeouts are recorded.

**Method:** Recomputed sums, means, medians and token totals from `outputs`.

**Exceptions:** The neural deterministic run's `stderr.log` shows repeated failed network requests to huggingface.co (5 retries) before finishing, so confirm the cross-encoder came from a local cache. The "model error" counts include a legitimate evidence block (see Q10).

**Reviewer/date:** ________

## Q8. Retrieval queries and relevant passage IDs

**Status:** PARTIALLY SUPPORTED

**Conclusion:** The 36 queries are 12 families of 3 paraphrases, each mapped to one passage, and the author-assigned mappings look plausible, but no human has reviewed them.

**Evidence:** `retrieval_queries_36_BLINDED.jsonl` (all `label_origin` author_mapped_pending_independent_review). Draft review: all 36 accepted, each passage states the rule the query asks about (POL-01 to POL-12). RAG report: 36 queries, neural hit@5 0.9167; the 101 authored development queries reach 0.9406 before and 0.9604 after the rewrite.

**Method:** Read each query against the passage text.

**Exceptions:** One relevant ID per query hides other relevant passages. The queries paraphrase the passage text, so they are easy. The rewrite was made after seeing failures on those 101 development queries, so 0.9604 is a tuned development number, not held-out. The same 36 queries score 0.9444 in the report's `legacy_16_offline` block but 0.75 in its `expanded_offline` block; the packet does not say what differs between them (likely the corpus), so ask Karthika before relying on either.

**Reviewer/date:** ________

## Q9. Profitability statements, fees, marks, benchmark, limitations

**Status:** PARTIALLY SUPPORTED

**Conclusion:** No run supports a claim that the agents or the router make money.

**Evidence:** E4 (synthetic): ROUTER +3.28% (133 trades, win 36.09%, max drawdown -7.08%) vs equal-weight buy-and-hold +76.66%; single strategies: EMA_TREND +10.64%, EMA_PULLBACK -0.91%, RSI_REVERSION +3.14%, BREAKOUT +3.80%. Fees 11.874 bps buy / 10.374 bps sell, slippage 10 bps. Portfolio extract: technical reference +3.35% (18 trades) vs buy-and-hold +6.78% over 2023-09 to 2023-11; no C2 return metrics are included.

**Method:** Read the metrics and settings.

**Exceptions:** Synthetic data; short sample; current-member and unadjusted-price bias; status `COMPLETED_WITH_GAPS`; 20 of 42 C2 ledger events carry a human-override marker. Open-position marks were not recomputed.

**Reviewer/date:** ________

## Q10. Negative results that must stay in the report

**Status:** SUPPORTED

**Conclusion:** These must remain visible.
- ROUTER +3.28% vs +76.66% buy-and-hold (synthetic E4).
- EMA_PULLBACK -0.91% in E4.
- C1 route conflict on BHARTIARTL (`STRATEGY_ROUTE_CONFLICT`) and C2 evidence block on the same case; C2 matched C1 on success (2/3) at twice the model calls and latency.
- 4 provider failures and 43 blocked decisions of 104 in the portfolio run.
- Offline retrieval on the same 36 queries is 0.9444 in one report block and 0.75 in another; the cause is unexplained.
- The local CI demo is not hosted evidence.

**Evidence:** The files cited in Q7 to Q9.

**Reviewer/date:** ________

## Q11. Final decision and reruns

**Status:** PENDING

**Conclusion (provisional):** REJECT/RE-RUN. Required: independent labels frozen; a fixed corpus and prompt version; E1 with three held-out repetitions on agentic cases that have symbols, dates and evidence; a different-family judge calibrated on 20 or more human labels; replace the duplicate attacks; hosted CI and alert evidence.

**Reviewer/date:** ________
