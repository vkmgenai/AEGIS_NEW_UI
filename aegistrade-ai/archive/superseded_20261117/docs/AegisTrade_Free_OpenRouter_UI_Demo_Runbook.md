# AegisTrade AI
UI demo runbook for a free OpenRouter account

**Practice edition • 10 November 2026 • Project baseline 0.15.1**

Use this guide before your funded exam rehearsal. It provides one practical route: rehearse the local screens without generation, attempt one genuine free-model C2 case, then optionally try a tiny C2 portfolio. It does not promise that a free provider will complete the agents reliably.

This document was prepared without making model requests, changing your private .env or freezing lessons. You must apply the configuration steps below yourself before trying cloud research. Keep the existing data, evidence and risk checks in place.

## 1. What you can demonstrate with this account

| Demo part | What you show | Generation allowance |
|---|---|---|
| Local foundation | Data, charts, technical portfolio, policy search and shortlist | Zero OpenRouter requests |
| One real C2 case | Three specialists, dated company evidence, tool observations, citations and critic | Normally 6 requests; maximum 8 |
| Supervised action after that C2 | Valid researched proposal, edit, new hash, approval and broker audit | No additional generation calls |
| Optional tiny C2 portfolio | Researched entries, next-open fills, cash/holdings and terminal valuation | Set a total allowance of 16; may pause or finish with gaps |

The planned cloud allowance is at most 24 attempted requests:8 for one C2 case plus16 for the optional portfolio. Other activity, failed attempts and earlier runs still matter. Do not assume this many requests remain in your account.

OpenRouter's published free-tier figures at review time are 20 requests/minute and50 requests/day for the lower free-model tier; provider-specific restrictions and capacity can still intervene. Consult the current account counter and official limits before each rehearsal. A new key does not create a fresh account-wide allowance. [OpenRouter pricing](https://openrouter.ai/pricing), [limits documentation](https://openrouter.ai/docs/api_reference/limits)

The application allowance and OpenRouter quota are different. The app limits attempted calls in a run; it cannot guarantee remaining provider quota or availability. Wait at least 60 seconds between cloud demo stages, and stop after a rate-limit error instead of rapidly retrying. This is a cautious rehearsal practice, not a guarantee that every provider will accept the next request.

## 2. One-time preparation: select a genuinely free route

### 2.1 The important model setting

The project's default openai/gpt-4.1-mini is a paid model. [Official model pricing](https://openrouter.ai/openai/gpt-4.1-mini) Having a free account or an API key does not waive that price. For this practice guide use the single route below:

```text
OPENROUTER_MODEL=openrouter/free
AEGIS_ENABLE_LLM_EXPERIMENTS=true
```

Privately edit only those settings in the existing .env. Preserve your OPENROUTER_API_KEY, AEGIS_REVIEWER_TOKEN and all other settings. Do not replace the whole file with this two-line example, put a real key in this document or show .env during screen sharing.

OpenRouter documents openrouter/free as a zero-cost router that selects from available free models and filters for requested capabilities such as tool calling. The underlying model can vary between requests. This is suitable for a practice attempt; it does not guarantee AegisTrade-compatible responses, available capacity or repeatability. Keep a record of the actual returned models. [Free Models Router](https://openrouter.ai/docs/guides/routing/routers/free-router)

AegisTrade needs tool calling, valid tool-result handling and typed JSON responses. Some free models may fail these requirements or exceed the application's response/context bounds. A failure must remain blocked; do not remove required tools, citations or critic checks to produce a success. [OpenRouter tool calling](https://openrouter.ai/docs/guides/features/tool-calling)

### 2.2 Restart and verify

1. Stop your existing launcher with Ctrl+C in its Terminal. Do not start a second copy over occupied ports.
2. From the project root, restart the already installed application:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
.venv/bin/python scripts/launch_local.py
```

3. Open http://127.0.0.1:8501. Confirm http://127.0.0.1:8000/health reports version0.15.1 and agent_model=openrouter/free. If a later compatible source version is installed, use its actual version; the model value must still match the intended free route.
4. In the sidebar enter your private AEGIS_REVIEWER_TOKEN. This is not the OpenRouter key.
5. In AI Agent Experiments expand Plan and permissions before running. Verify its model is openrouter/free before allowing any cloud request. “Key configured: Yes” does not prove either quota or model availability.

The UI and API still use labels such as “paid OpenRouter requests” and “Paid experiments enabled”. These are the app's generic cloud-call authorization gates. You must explicitly authorize the request, even for a free route. Selecting the checkbox does not itself change a model's price; verify the route first.

For the local-only part below you can leave AEGIS_ENABLE_LLM_EXPERIMENTS=false. Enable it only when you are ready for the genuine free-model attempt. No code change is required for this configuration.

## 3. Start here: a dependable zero-generation rehearsal

### Step A — Market Data

Select Market Data. Confirm NSEPython is active, inspect the20-stock universe, date coverage and provisional-data notice. If already active, do not redownload or reactivate unnecessarily.

Say: “This is historical daily data. We selected a manageable20-stock research universe and disclose current-membership bias and unresolved corporate actions.”

Expected evidence: source, symbols and available dates. No cloud model call.

### Step B — Overview

Choose Overview, select HINDUNILVR and a convenient history window such as180 or360 sessions. Inspect the price chart and indicator/regime summary.

Say: “Code computes the indicators and permitted route. A candidate on this screen is not yet a researched or approved order.”

The overview reflects its available market window; it is not automatically a chart locked to the historical research date used later.

### Step C — Technical-only historical portfolio

In Strategy Backtests explicitly select **Technical-only baseline**. The default engine is C2 historical portfolio, so this selection is important for a zero-generation rehearsal.

Use these settings:

| Control | Value |
|---|---|
| Initial capital | ₹200,000 |
| Simulation start / end | 2022-11-01 / 2023-03-31 |
| Strategies to run | ROUTER |
| Automatically screen and rank stocks | On |
| Maximum risk per trade | 1% |
| Fees / slippage | 10bps each |

Approve the displayed historical assumptions and click Run historical portfolio simulation. The technical baseline needs at least 45 sessions; this period is long enough. Inspect equity, drawdown, cash, ledger and stock-selection audit. Download JSON if useful.

Say: “These are the technical-only reference results. No LLM selected these trades, and I am not presenting them as C2 performance.”

### Step D — Policy Knowledge

Open Policy Knowledge. Search “What happens if completed C2 research changes before approval?” Inspect the returned passage IDs and source text. You can also try a strategy/risk query.

Say: “Retrieval supplies project-policy evidence. The generator must cite observed passages; code still enforces the rules.”

Neural embedding/reranking runs locally once models are cached. Searching here makes no paid generation call.

### Step E — Shortlist and source evidence

Go to AI Agent Experiments. Set C2, one research case, Earliest case date=2023-03-31 and Latest case date=2023-03-31. Leave automatic ranking on and frozen human-reviewed lessons off. The lesson option is disabled when no accepted frozen playbook exists; normal C2 needs no lesson memory.

Click **Preview selected-date stock shortlist (no model calls)**. With the current cache and ₹200,000 screening capital, HINDUNILVR ranks first; MARUTI is also selected in the shortlist. The one-case research setting targets the highest eligible candidate. Verify the displayed date and ranking rather than assuming they cannot change.

Expand Historical company research — prepare before paid calls. Select HINDUNILVR and2023-03-31, then Inspect cached company evidence. This case was prepared during the previous fix; its readable financial filing was available before the decision cutoff. Inspect its status, CMP ID, original filing URL and availability time. If the pack is missing, use Prepare historical company evidence with the reviewer token; public archive downloads/extraction use no generation calls, but can take time or fail.

Say: “The company evidence must have been available by 15:30 IST on the decision date. An accounting period-end alone is not its publication date.”

You have now rehearsed data, market analysis, a portfolio baseline, selection and RAG without any OpenRouter generation request.

## 4. Attempt one genuine C2 run using the free route

Proceed only after verifying openrouter/free in the running API/plan, sufficient remaining account allowance and a SUFFICIENT company pack.

| Control | Value |
|---|---|
| Experiment configuration | C2 |
| Research cases to test | 1 |
| Earliest / latest case date | 2023-03-31 / 2023-03-31 |
| Reference capital for screening | ₹200,000 |
| Output-token cap per case | 4,800 |
| Research automatically ranked eligible stocks | On |
| Use frozen human-reviewed lessons | Off |

1. Read Plan and permissions before running. Confirm maximum attempted requests=8 and the intended free route.
2. Select the explicit cloud-call authorization checkbox and click Run AI experiment once.
3. Wait for the response. Do not repeatedly click Run; another run can consume more quota.
4. Inspect the actual usage and errors. A successful C2 needs all three specialist hand-offs, accepted critic, passing code guard, observed policy/financial citations, sufficient company assessment and no model errors.
5. Open the full hand-off/tool trace. Identify a tool request, observed evidence and final typed response. Normal execution uses six generation requests; correction can consume the remaining ceiling.
6. Save the genuine result JSON and a sanitized screenshot. Record the actual returned model IDs and run/case ID. Free-router requests can use different models, so this practice is not a fair final fixed-model C1/C2 comparison.

Suggested explanation: “The market specialist interprets technical/company evidence; strategy returns the constrained decision with policy citations; the critic checks it. Code validates before an action becomes eligible.”

If it fails, keep the error and stop this stage. Do not substitute C0, a mock or a partial response for successful C2. The failed-closed result is valid safety evidence, but not a successful GenAI demo.

## 5. Reuse successful C2 for human approval — no extra generation

This stage is available only if Step4 produced an eligible ENTRY case. If C2 is blocked, demonstrate that the hand-off is unavailable and continue with the local foundation; do not bypass it.

1. Select the successful case and click **Use this C2 case in Supervised Trading**.
2. Set Reference capital to ₹200,000. Keep both failure-injection checkboxes off for the first attempt.
3. Click Prepare researched order for human review. Read the exact symbol, quantity, reference/stop prices, company assessment, sources and payload hash.
4. For the edit demonstration select edit. Enter a lower positive quantity, such as original quantity minus1, if the original exceeds1. The suggested increase may exceed risk limits; do not accept it blindly. Submit the decision.
5. Confirm a new payload/hash and another WAITING_HUMAN state. Select approve and submit the fresh decision within the ten-minute expiry.
6. Open Broker Audit, refresh and match the accepted simulated action to its request identity and quantity. Export the audit if required.

Say: “Completed C2 came before approval. Editing invalidated the old consent. Final code checks still decide whether the exact reviewed action can execute.”

Preparing, editing and approving reuse the completed research rather than making a new generation request. A stale/expired approval or changed source evidence can still block the action. A fresh proposal may be enough for expiry, while changed research/corpus/company evidence requires fresh C2 and additional quota. Broker Audit is for this supervised simulator; portfolio fills belong to Strategy Backtests.

One additional fresh proposal can demonstrate reject or stale-quote injection without a new C2 call, provided the saved research remains valid. You do not need to demonstrate every failure on the same day.

## 6. Optional: a tiny genuine C2 historical portfolio

Attempt this only after the single-case run works and quota remains. Wait at least 60 seconds after the previous cloud stage. Skip it if the free service is unstable; never label a technical-only run as a substitute C2 portfolio.

In Strategy Backtests choose **C2 historical portfolio** and use:

| Control | Value |
|---|---|
| Initial capital / risk | ₹200,000 / 1% |
| Simulation start / end | 2023-03-31 / 2023-04-03 |
| Strategy / automatic ranking | ROUTER / On |
| Fees / slippage | 10bps each |
| Total OpenRouter request allowance | 16 |
| Holding review interval | 5 market sessions |

This is a two-session smoke demonstration, not a meaningful trading-performance study. The C2 engine permits such a short period; the separate technical-only engine requires at least 45 sessions. The first session has HINDUNILVR and MARUTI candidates in the current cache. Missing company evidence is prepared/checked on demand; it can block a candidate without a model call.

1. Enter the reviewer token. Approve cloud calls and the historical entry/exit rules. The historical rules authorize automatic simulated fills; there is no human pause at every historical order.
2. Start the job. In C2 portfolio progress, resume and saved jobs click Refresh C2 progress. Track completed sessions, OPEN/CLOSE phase, decisions and usage.
3. If research passes, an entry can queue on 31 March and fill at the next available open on 3 April, subject to fill-time risk/gap checks. Inspect the ledger and linked research trace.
4. Inspect cash, ending equity, realized/unrealized P&L and open holdings. A surviving holding is valued at the last close; ending the period does not force a sale.
5. If PAUSED_BUDGET, inspect usage and remaining daily quota. Do not add more allowance in this free-day plan. Save the run ID and continue another day only after deliberately checking quota and consenting to resume.
6. If PAUSED_PROVIDER, stop. Resolve the provider error before a consented resume. If COMPLETED_WITH_GAPS, inspect blocked cases; it is not proof of complete company coverage.

This short window is designed to show researched entry, later fill and final valuation. It normally cannot demonstrate a scheduled five-session holding review, and a sale is not guaranteed. Stops/strategy exits occur only when their actual conditions occur; C2 EXIT also requires a genuine accepted review. Do not force an exit or alter evidence merely to make the screen look complete. Use the longer funded exam rehearsal to demonstrate those paths.

No single-case C2 result is automatically reused across a newly created portfolio job: the job carries its own portfolio context, research and accounting. Budget this stage as additional calls. The16-request allowance is below the default 48 and leaves room within the planned free-day budget; a run can still pause when fewer than eight requests remain for another bounded case.

## 7. What to do if the free run fails

| What you see | What it means / next action |
|---|---|
| API shows the paid default model | Stop before cloud consent. Correct OPENROUTER_MODEL, restart and recheck. |
| HTTP402 | Check the route and account credit/restriction details. A paid model needs funding; account problems can also affect free routes. Do not repeatedly retry. |
| HTTP429 | Rate/quota/capacity limitation. Stop cloud attempts; inspect provider guidance and resume only when allowed. Local screens remain usable. |
| HTTP400/404 or no tool-compatible endpoint | A suitable free endpoint/parameter combination may be unavailable. Keep tools and validation intact; use the local demo and retry later. |
| Timeout / provider unavailable | Save the error. Free capacity is not guaranteed; avoid a rapid retry loop. |
| JSON, missing-tool, citation or critic rejection | A real model response failed the research contract. Keep the trace; do not approve an order from it. |
| Frozen lessons unavailable | Leave lesson memory off. It is optional and does not disable C2 or RAG. Do not freeze an empty playbook to clear the message. |
| Insufficient company evidence | Inspect the exact symbol/date pack. Resolve the source issue or stop that case; it cannot be waived by human order approval. |
| No eligible stocks | Read shortlist reasons and the selected date. Do not weaken risk/entry rules to manufacture a trade. |

The limits documentation notes that a negative account balance can interfere even with free-model requests. Check the actual account state rather than assuming every 402 means the project selected a paid route. [OpenRouter limits](https://openrouter.ai/docs/api_reference/limits)

If genuine generation does not complete, present what you actually observed: working data/retrieval/baseline, the dated company pack, the attempted agent trace/error and the blocked action gate. Existing mocked integration reports demonstrate implementation tests only; do not call them real free-model output.

## 8. Your rehearsal checklist and later exam transition

Before practice:

- Source0.15.1 or later compatible patch is running; data/index are ready.
- Intended free route is visible in API health and the pre-run plan.
- Reviewer token is private; lesson memory is off; company evidence is inspected.
- You know the day's prior usage and will stop within the chosen allowance.

Save during practice:

- Data provenance, technical baseline and policy-search screenshots.
- A genuine C2 JSON/trace if successful, with actual model IDs and call count.
- Edited hash/new approval and broker record if the researched proposal succeeds.
- Optional portfolio status, decisions, holdings and explicit incomplete/gap labels.

For the funded exam rehearsal, use a deliberately selected fixed tool-capable model, fund/configure its OpenRouter access, set a spending limit and verify a genuine one-case run first. The existing default can be restored only after you intend to use that paid route. Restart after changes and begin a new portfolio run: model/prompt/data changes should not be mixed into an old checkpoint. Rehearse a longer portfolio window, actual holding reviews/exits, provider-failure recovery and a labelled backup recording. A funded endpoint still needs capacity, schema validation and testing; funding alone does not establish reliable reasoning or profitable returns.

Do not use random free routing for final claims that C1 and C2 used the same fixed model. Do not treat this tiny practice portfolio as the final five-year evaluation. The complete design guide and viva handbook describe the broader project and evidence requirements.

Official provider references were checked on 10 November 2026. Limits, model availability and provider terms may change; recheck before the exam. This runbook makes no claim that a real free-model C2 request has already succeeded on your account.
