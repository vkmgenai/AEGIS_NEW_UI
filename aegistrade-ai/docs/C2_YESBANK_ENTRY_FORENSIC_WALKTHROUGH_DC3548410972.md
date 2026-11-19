# AegisTrade AI — Forensic C2 Portfolio Walkthrough

## YESBANK entry research on 20 November 2023

**Saved run:** `dc354841097240e0bc88d8430953fa22` (short form `dc3548410972`)  
**Research record:** `e99db3e8f98976bf24227f2add10cc34`  
**Research key:** `2023-11-20:YESBANK:ENTRY`  
**Purpose:** Explain one real, saved C2 decision from input through simulated execution.  
**Important:** This is a historical simulation trace, not investment advice and not a live order.

---

## 1. What actually happened

YESBANK did **not** execute at the 20 November closing price. The completed 20 November daily bar produced a technical candidate. C2 researched that candidate after the close, returned `ENTER`, and passed the independent critic and deterministic guard. The engine then queued a simulated order and filled it at the **next market session's open on 21 November 2023**, including modeled slippage and fees.

| Stage | Saved value |
|---|---:|
| Original technical signal date | 17 November 2023 |
| Monday refresh/research date | 20 November 2023 |
| Selected strategy | `EMA_TREND` |
| Selection rank | 2 |
| Selection score | 87.70783 |
| C2 portfolio action | `ENTER` |
| Critic verdict | `accept=true` |
| Deterministic guard | Passed |
| Simulated fill date | 21 November 2023 |
| Quantity | 1,997 shares |
| Fill price | ₹20.3203 |
| Entry fee | ₹48.1845 |
| Initial stop | ₹18.7619 |
| End-of-run state | Position still open on 30 November 2023 |

The original 17 November signal was deliberately refreshed on Monday. This prevents the system from blindly filling a Friday signal after a weekend gap. No same-close fill or look-ahead was allowed.

## 2. End-to-end flow

```text
Completed OHLCV bars
        |
        v
Deterministic screening and ranking
YESBANK / EMA_TREND / rank 2 / eligible
        |
        v
C2 supervisor creates typed plan
        |
        +--> Market Agent
        |      market_snapshot
        |      company_evidence (NSE archive pack)
        |      search_dated_web (two bounded queries)
        |      -> MarketJudgement
        |
        +--> Strategy Agent
        |      check_strategy
        |      search_policy (policy RAG query)
        |      -> StrategyJudgement: ENTER
        |
        +--> Critic Agent (independent re-check)
               company_evidence
               check_strategy
               search_policy (separate RAG query)
               -> CriticJudgement: accept=true
        |
        v
Typed validation + deterministic final guard
        |
        v
Code-controlled sizing, stop, fees and later-open fill
        |
        v
Simulated BUY on 21 November; immutable ledger entry
```

The LLM agents explained and checked a code-qualified candidate. They did not calculate indicators, choose arbitrary position size, alter risk rules, or place a live exchange order.

---

## 3. Run and model context

The saved record identifies this as C2 multi-agent research using the Claude CLI adapter:

| Field | Value |
|---|---|
| Configuration | `C2` |
| Backend | `claude_cli` |
| Requested model alias | `haiku` |
| Resolved model in usage records | `claude-haiku-5-5` |
| Adapter | `claude-intent-v1` |
| Prompt version | `2026-11-15-relative-materiality-v16` |
| Maximum model calls for this case | 8 |
| Actual model/CLI calls | 8 |
| Maximum tool calls | 16 |
| Actual tool calls | 8 |
| Context limit per agent turn | 36,000 characters |
| Policy corpus fingerprint | `f4bc69945315b225eabf2794c2ef41a9e7f8bcccdbbbb3f7894ed863e9573dcb` |

The supervisor's saved plan was:

1. Market specialist.
2. Strategy specialist.
3. Compliance critic.
4. Deterministic final guard.

Each specialist returned a typed hand-off: `MarketJudgement`, `StrategyJudgement`, or `CriticJudgement`.

---

## 4. Step 1 — deterministic shortlist before any agent decision

The portfolio engine evaluated the available historical rows and recorded this exact audit row:

| Field | YESBANK value |
|---|---:|
| Date | 2023-11-20 |
| Regime | `TREND` |
| Candidate strategy | `EMA_TREND` |
| Eligible | Yes |
| Score | 87.70783 |
| Rank | 2 |
| 20-day average turnover | ₹4,581,294,557.66 |
| ATR fraction | 0.03444457 |
| Estimated shares at signal close | 2,252 |
| Exclusion reasons | None |

This screening is deterministic code. The LLM did not invent the candidate or score. The estimated 2,252 shares was a signal-close estimate, not the final order quantity. Final quantity was recomputed using the later opening price and the code-owned risk distance.

## 5. Step 2 — locked market snapshot

The Market Agent called `market_snapshot`. The tool returned historical, locked values—not a live quote:

| Indicator | Value | Meaning in this case |
|---|---:|---|
| Close | ₹20.15 | Completed 20 November close |
| ADX14 | 39.0543 | Above the trend threshold of 22 |
| EMA20 | ₹18.3464 | Short EMA |
| EMA50 | ₹17.6505 | Long EMA |
| RSI14 | 72.1250 | Reported, but not used to route this trend case |
| ATR14 | ₹0.6941 | Used later by code for risk distance |
| PriorHigh | ₹21.15 | Not a breakout on this row |
| PullbackRecent | `false` | Not an EMA pullback case |
| Average 20-day turnover | ₹4.581 billion | Liquidity/ranking input |

The code-qualified relationship was:

```text
ADX14 39.05 >= 22
Close 20.15 > EMA20 18.35 > EMA50 17.65
```

That supports a `TREND` route and an `EMA_TREND` candidate. It does **not** by itself guarantee profit or execution.

---

## 6. Step 3 — company evidence retrieval

### 6.1 This is not the same thing as policy RAG

The system has two evidence mechanisms:

- **Company evidence retrieval:** a bounded, date-filtered archive of official NSE disclosures and readable attachments for YESBANK. It is selected by symbol and historical cutoff, not by a free-text vector query.
- **Policy RAG:** neural/exact-ID retrieval over code-derived project-policy passages. This is called with explicit natural-language queries by the Strategy and Critic agents.

The Market Agent called `company_evidence` with an empty argument object because the symbol and cutoff were already locked in the case context: YESBANK, 20 November 2023 at 15:30 IST.

### 6.2 Company evidence pack returned

| Coverage field | Saved value |
|---|---:|
| Exchange metadata rows | 86 |
| Eligible announcements at/before cutoff | 86 |
| Downloaded/readable selected documents | 8 |
| Exchange scan complete | Yes |
| Invalid timestamp rows | 0 |
| Selected-documents-only warning | Yes |
| Final pack SHA-256 | `75fa67dcecaab407c6230c05e67aadf80e4e2088d31aef6e52d60f63da7623eb` |

The eight documents exposed to the agents were:

| ID | Date | Kind | What the readable passage contained |
|---|---|---|---|
| `CMP-fb85c317d69f0417` | 21 Oct 2023 | Financial results | Auditor limited-review context for quarter/half-year ended 30 Sep 2023. The extracted view did not provide reliable profit/revenue figures for materiality comparison. |
| `CMP-02266b9e97fd1190` | 22 Jul 2023 | Financial results | Auditor limited-review context for quarter ended 30 Jun 2023. |
| `CMP-a9de2a8cebc8df1d` | 26 Oct 2023 | Company news | Q2 FY2023-24 earnings-call transcript notice and issuer link. |
| `CMP-11040e4a344409ac` | 17 Aug 2023 | Press release | Introduction of the “iris by YES BANK” mobile application. |
| `CMP-af511d88da60f6ce` | 20 Nov 2023 13:38 | Management change | Appointment of Tushar Patankar as Chief Risk Officer, effective 1 Dec 2023; joined as senior management on 20 Nov. |
| `CMP-90c6c5c1304e3e75` | 29 Sep 2023 | Management change | Resignation of Harsh Gupta, Country Head—Stressed Asset Management. |
| `CMP-ab73dbcfb3a16199` | 27 Sep 2023 | Management change | Resignation letter of Ravi Thota, Country Head—Large Corporates. |
| `CMP-9ef6e296d33812eb` | 27 Sep 2023 | Management change | Appointment/designation and resignation details for senior management personnel. |

The ready adverse scan was `SCAN-0e5ae9e7e348c7fc`. It covered 24 May through 20 November 2023 and matched the three September management-change documents:

- `CMP-90c6c5c1304e3e75`
- `CMP-ab73dbcfb3a16199`
- `CMP-9ef6e296d33812eb`

The scan's own scope warning says it is a bounded official NSE issuer-disclosure search, not exhaustive press coverage and not proof that no adverse information exists.

### 6.3 Dated web fallback

Because independent coverage was limited, the Market Agent called `search_dated_web`. The exact saved queries were:

```text
YESBANK financial results India after:2023-05-24 before:2023-11-21
YESBANK adverse regulatory default news India after:2023-05-24 before:2023-11-21
```

Each search returned eight raw results, but none passed the bounded date/source/content acceptance checks. Therefore the saved web citation `WEBSCAN-bef3d0310dd9dc36` has:

| Field | Value |
|---|---:|
| Status | `SEARCHED_BUT_INSUFFICIENT` |
| Queries recorded | 2 |
| Accepted sources | 0 |
| Cached | No |

This is important: the agents did not turn unsuccessful web retrieval into a “no bad news” claim. They explicitly retained residual coverage risk.

---

## 7. Step 4 — Market Agent response

After reading the market snapshot, official company pack and web-search audit, the Market Agent returned this typed `MarketJudgement`:

> **Regime:** TREND  
> **Explanation:** On 2023-11-20, ADX14 is 39.05 (>=22), Close 20.15 is above EMA20 18.35, and EMA20 is above EMA50 17.65. This meets the code-qualified strong TREND condition. RSI14 is 72.1 and is not used for routing. Not a breakout or pullback case.

Its typed company assessment was:

| Field | Response |
|---|---|
| Status | `LIMITED` |
| Adverse risk | `COVERAGE_LIMITED` |
| Event risks | Empty list |
| Breakout support | Not applicable |
| Main citations | `SCAN-0e5ae9e7e348c7fc`, `WEBSCAN-bef3d0310dd9dc36`, the three resignation documents, and Sep-2023 results |

The Market Agent did not label the company clean or safe. Its limitations said:

1. Independent web coverage was insufficient.
2. Reliable profit/revenue/net-worth figures were not extracted from the financial-results passage.
3. The resignation passages did not provide enough issuer-reported impact text; impact remained unknown rather than “Nil.”
4. The official-source selection was not comprehensive press coverage.

---

## 8. Step 5 — Strategy Agent and policy RAG

### 8.1 Code constraint check

The Strategy Agent first called `check_strategy`. The tool confirmed that the code-approved route was `EMA_TREND` and that the permitted portfolio action was `ENTER`. This stops the LLM from choosing an unrelated strategy.

### 8.2 Exact RAG query

The Strategy Agent then called `search_policy` with:

```text
EMA_TREND ENTRY strong trend coverage limited adverse scan materiality
```

The RAG service used neural retrieval against the locked corpus fingerprint. It returned all five of these passages:

| Rank | ID | Title | Score | Key rule |
|---:|---|---|---:|---|
| 1 | `POL-72` | Strategy-specific evidence, coverage gaps and adverse-news exits | 5.45531 | A code-qualified strong EMA trend may proceed with `COVERAGE_LIMITED` when no concrete unresolved adverse event is found, but this is not proof of safety or profit. |
| 2 | `POL-21` | Trend regime classification | 0.64199 | TREND requires ADX14 >= 22 and EMA20 > EMA50 after higher-priority checks. |
| 3 | `POL-25` | EMA trend entry | -0.08950 | Entry requires a ready row with EMA20 > EMA50 and Close > EMA20; fill must be later-session. |
| 4 | `POL-26` | EMA trend exit | -2.18061 | Exit is EMA20 < EMA50, queued for a later open; protective stops also apply. |
| 5 | `POL-MAT-01` | Materiality of routine penalties and regulatory notices | -3.80100 | Materiality must be established from cited issuer facts; unknown serious event risk blocks, while non-material notices become limitations. |

Negative retrieval scores do not mean “bad” passages; they are ranking values from this retrieval implementation. The typed output cited only the passages needed for the entry explanation.

### 8.3 Full meaning of the retrieved policy passages

`POL-21` and `POL-25` grounded the numerical route. `POL-72` allowed a strong trend case to proceed despite incomplete independent news coverage only because there was no identified concrete unresolved adverse event. `POL-MAT-01` governed event materiality. `POL-26` was retrieved as related strategy context but was not needed to justify this entry.

### 8.4 Validation correction inside the Strategy Agent

The Strategy Agent's first draft mixed company-document IDs into the policy `citations` field. Typed validation rejected it with:

```text
POLICY_CITATION_UNSUPPORTED: Unsupported citation
```

The orchestrator replanned within the same budget. The corrected typed hand-off kept only valid policy IDs in the policy-citation field. This is a useful agentic behavior: the system did not silently accept a schema/evidence mistake.

### 8.5 Final Strategy Agent response

The corrected `StrategyJudgement` was:

| Field | Response |
|---|---|
| Strategy | `EMA_TREND` |
| Portfolio action | `ENTER` |
| Policy citations | `POL-72`, `POL-21`, `POL-25`, `POL-MAT-01` |

Its saved explanation states that the strong trend is code-qualified; the official scan found management-change notices but no monetary, regulatory, fraud, or operating-restriction event; web coverage remained insufficient; no reliable financial scale comparison was possible; and sizing/stops remained code controlled.

---

## 9. Step 6 — independent Critic Agent

The Critic did not merely read the Strategy Agent's prose. It independently called:

1. `company_evidence` — re-read the current hashed YESBANK evidence pack.
2. `check_strategy` — independently confirmed `EMA_TREND` and `ENTER` were permitted.
3. `search_policy` — ran its own policy query.

The Critic's exact RAG query was:

```text
EMA_TREND strong trend entry coverage limited materiality adverse event POL-72 POL-21 POL-25
```

It retrieved the same five passages, with exact-ID matches promoted because the query named policy IDs:

| Rank | ID | Mode | Score |
|---:|---|---|---:|
| 1 | `POL-72` | exact ID | 4.48288 |
| 2 | `POL-21` | exact ID | -0.61406 |
| 3 | `POL-25` | exact ID | -1.78140 |
| 4 | `POL-MAT-01` | exact ID | -4.89085 |
| 5 | `POL-26` | neural | -4.25570 |

The Critic returned:

> **accept=true.** EMA_TREND ENTRY is code-qualified by ADX and EMA relationships. The route and `ENTER` action are permitted. The official scan matched the three management resignations, but none of the readable evidence established a monetary, regulatory, fraud, or operating-restriction event. Web search was insufficient, so the conclusion remains `COVERAGE_LIMITED`, not a clean-company finding. The September results excerpt lacked extracted profit/revenue figures. Residual coverage risk remains. No breakout was claimed.

This is deliberately narrower than “YESBANK is fundamentally good.” The Critic accepted consistency with the project policy, not future profitability.

---

## 10. Step 7 — deterministic final guard

After the typed hand-offs, code validated that:

- required agents and evidence tools were observed;
- the strategy matched the deterministic route;
- the action was permitted;
- policy citations came from the observed retrieval result;
- company claims were tied to observed document/scan IDs;
- the independent Critic accepted the result;
- no model error remained.

The saved decision therefore recorded:

```text
action = ENTER
guard_pass = true
errors = []
llm_calls = 8
```

There was no human override for this case because it was not an eligible evidence-blocked decision. The historical replay used its approved assumptions and automatically queued the code-permitted simulated entry.

---

## 11. Step 8 — sizing, stop and next-open simulated execution

Execution remained deterministic:

- Risk per trade: 1%.
- Initial stop: 2 × ATR14 below the signal close.
- Trailing stop: enabled at 2 × entry-signal ATR.
- Take-profit target: 8% net return.
- Slippage: 10 basis points.
- Fees: code-modeled equity-delivery charges.

Initial stop calculation:

```text
20.15 - (2 × 0.69405808) = 18.76188384
```

The next session's raw opening price was modeled with slippage, producing a fill of ₹20.3203. The engine recomputed quantity against the actual fill-to-stop risk, resulting in 1,997 shares rather than the earlier 2,252-share close estimate.

The immutable ledger entry was:

| Field | Value |
|---|---:|
| Date | 2023-11-21 |
| Event | `BUY` |
| Symbol | YESBANK |
| Quantity | 1,997 |
| Price | ₹20.3203 |
| Fee | ₹48.1845 |
| Initial stop | ₹18.7619 |
| Strategy | `EMA_TREND` |
| Research ID | `e99db3e8f98976bf24227f2add10cc34` |
| Signal date | 2023-11-20 |
| Original signal date | 2023-11-17 |

No live broker was connected and no exchange order was submitted.

## 12. What happened by the end of this run

The run ended on 30 November while the YESBANK position was still open:

| Field | Value |
|---|---:|
| Entry price | ₹20.3203 |
| Last saved mark | ₹19.35 |
| Quantity | 1,997 |
| Position status | Open |
| Realized P&L | Not available; no sale occurred |
| Approximate mark-to-market before hypothetical exit costs | `(19.35 - 20.3203) × 1,997 - entry fee ≈ -₹1,985.87` |

That mark-to-market value is not a closed-trade conclusion. The engine intentionally did not force every holding to be sold at the end of the selected window.

---

## 13. Why C2 entered despite incomplete evidence

This was an `EMA_TREND` case, not a breakout. Under `POL-72`, missing independent coverage alone is not an automatic veto for a code-qualified strong trend if:

- the official adverse scan was actually performed;
- no concrete unresolved material adverse event was identified;
- event risks remain empty;
- the system explicitly records `COVERAGE_LIMITED` and its limitations;
- the Critic independently rechecks the evidence;
- code retains control of execution and risk.

A breakout would have faced a stricter evidence rule and could not use `COVERAGE_LIMITED` as sufficient corroboration.

## 14. What the agents did and did not decide

| Component | Did | Did not do |
|---|---|---|
| Screening code | Calculated indicators, eligibility, score and rank | Interpret company filings |
| Market Agent | Classified the observed regime and summarized dated company risk | Choose quantity or execute |
| Strategy Agent | Mapped the locked case to policy and proposed `ENTER` | Change EMA/ADX rules |
| Critic Agent | Independently re-read evidence and accepted/rejected the proposal | Guarantee profitability |
| Final guard | Enforced tool, citation, schema and route consistency | Generate prose judgment |
| Execution engine | Computed stop, sizing, fees, slippage and later-open fill | Place a live order |

---

## 15. Exact evidence lineage

The following saved artifacts make this walkthrough reproducible:

- Run state: `data/c2_portfolio_runs/dc354841097240e0bc88d8430953fa22/state.json`
- Activity log: `data/c2_portfolio_runs/dc354841097240e0bc88d8430953fa22/activity.json`
- Exact research trace: `data/c2_portfolio_runs/dc354841097240e0bc88d8430953fa22/research/e99db3e8f98976bf24227f2add10cc34.json`
- C2 portfolio engine: `aegistrade/c2_portfolio.py`
- Agent orchestration: `aegistrade/agentic.py`
- Typed research schemas: `aegistrade/llm_research.py`
- MCP/tool dispatcher: `aegistrade/mcp_runtime.py`
- Company archive preparation: `aegistrade/company_research.py`
- C2 completion gate: `aegistrade/research_gate.py`
- Strategy and indicator rules: `aegistrade/strategies.py`

## 16. Audit qualifications

1. This explanation reports the saved trace; it does not recreate or improve the decision with later knowledge.
2. The run used today's curated research universe against history and unadjusted NSE prices, so survivorship/selection bias and corporate-action distortions remain.
3. The company archive was retrieved later using historical publication timestamps; it is not a certified point-in-time content-version archive.
4. The dated web search was bounded and insufficient. That is a recorded limitation, not evidence of no adverse news.
5. The position remained open. Its result cannot be labelled a realized win or loss in this run.
6. Policy passages are code-derived project specifications authored in 2026 and applied to the historical replay; they are not historical market news.

---

## 17. Viva-ready summary

For this YESBANK example, deterministic code found a strong EMA trend and ranked it second. The C2 supervisor sent the locked case to three specialists. The Market Agent read the technical snapshot, an eight-document NSE evidence pack and a failed bounded web fallback, then returned `TREND` with `COVERAGE_LIMITED`. The Strategy Agent checked the permitted route, retrieved five policy passages with the query “EMA_TREND ENTRY strong trend coverage limited adverse scan materiality,” corrected one citation-schema error, and proposed `ENTER`. The independent Critic re-read the company evidence, reran the strategy check, issued a separate RAG query and accepted the proposal while preserving the coverage warning. Code then validated the trace, calculated risk and fees, and filled 1,997 simulated shares at the next session's open. The LLM did not calculate the indicators, size the trade, override the rules, or place a live order.
