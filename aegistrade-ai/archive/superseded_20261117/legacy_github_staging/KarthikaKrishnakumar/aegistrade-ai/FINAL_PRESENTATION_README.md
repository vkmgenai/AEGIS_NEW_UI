# AegisTrade AI — final presentation and demo guide

Use this file for the final presentation. The main repository setup remains in [README.md](README.md); the detailed diagram is [docs/FINAL_ARCHITECTURE.md](docs/FINAL_ARCHITECTURE.md); completion evidence is tracked in [docs/FINAL_CAPSTONE_COMPLETION_CHECKLIST.md](docs/FINAL_CAPSTONE_COMPLETION_CHECKLIST.md).

## One-line pitch

AegisTrade is a simulation-only, evidence-grounded agentic equity-research platform in which code detects and sizes opportunities, a specialist team researches dated evidence, a critic checks claims, and a human controls exact supervised actions.

## What to say first

1. It never places a live exchange order.
2. C0 is the zero-LLM four-strategy technical baseline.
3. C1 is retained only as the guideline-required same-tool/budget single-agent evaluation baseline.
4. C2 adds market, strategy and critic specialists, dated RAG/web evidence, SMC, typed validation and holding reviews.
5. Python owns arithmetic, risk, costs and fills; models research and explain.
6. The claim is improved auditability and research quality—not guaranteed profit.

## Start everything

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
bash scripts/start_unix.sh
```

Open Streamlit at `http://127.0.0.1:8501`, API documentation at `http://127.0.0.1:8000/docs`, and Grafana at `http://127.0.0.1:3000` when using the full Docker stack. Copy the private reviewer token from `.env`; never show it on slides or in a recording.

## Recommended 12-minute demo

### 1. Architecture and data — 2 minutes

- Show `docs/FINAL_ARCHITECTURE.md`.
- In **Market Data**, show the active frozen universe, requested dates, source manifest and limitations.
- State that current constituents applied backward create survivorship bias and prices are not fully corporate-action adjusted.

### 2. C0 technical control — 2 minutes

- Open **Strategy Backtests → Technical-only baseline**.
- Use ROUTER, ₹200,000, an available three-month window, 1% risk, default fixed fees and 10 bps slippage.
- Show the selection audit, later-open ledger, equity curve and four strategies. Explain that this makes zero LLM calls.

### 3. C2 agentic research — 3 minutes

- Open **Strategy Backtests → C2 historical portfolio**.
- Prefer a previously completed short run for reliability. Show one ENTRY or HOLDING_REVIEW record.
- Open its trace: plan, market hand-off, strategy hand-off, critic, MCP observations, citations, usage and final code gate.
- Point out the fifth SMC route. If the run is paused, demonstrate checkpoint resume only after identifying the pause category.

### 4. Fair AI experiment — 2 minutes

- Open **AI Agent Experiments** and select a saved ALL result.
- Compare C0, evaluation-only C1 and C2 on the same case, model, tools and budget.
- Discuss success, grounding, tool trajectory, calls, latency and failures before mentioning portfolio return.

### 5. Human control and security — 2 minutes

- In **AI Agent Experiments**, open a grounded C2 BUY/SELL recommendation and its cited evidence.
- Edit it and show that the old approval hash becomes invalid; then reject or approve a fresh exact payload.
- Show stale-price or injected-text defence and the audit entry. Remind the panel that submission is simulated locally.

### 6. Memory and evaluation — 1 minute

- In **Learning & Lessons**, show accepted/rejected lessons and a frozen version.
- Show the 20/40 split, 32 attacks, retrieval queries, Grafana dashboard and the final checklist.
- Clearly identify independent evidence still outstanding if it has not been completed.

## Safe demo parameters

- Capital: ₹200,000
- Window: a verified three-month period present in the selected dataset
- Risk: 1% per trade; breakout 0.5%
- Stop: enabled, 5% or the displayed ATR default
- Take profit: 8% net target
- Slippage: 10 bps; fixed NSE delivery fees are code-defined
- Holding review: every five sessions
- Initial C2 allowance: 48 for a short diagnostic; longer runs need a planned larger allowance

Do not start a long external-inference run during the live exam. Use saved completed traces and keep one tiny consented case as the live call.

## Questions to expect

- Why is this GenAI? C1/C2 make real model calls for evidence interpretation, tool choice, typed hand-offs, critique and correction.
- Why not let the model choose quantity? Money and permissions are deterministic, testable code responsibilities.
- Why retain C1? It is the fair single-agent baseline required to measure whether the specialist team justifies its cost.
- Does C2 guarantee higher return? No. It targets grounded, auditable decisions; return depends on data, exposure and market conditions.
- What is the key limitation? Frozen current constituents and raw prices limit financial conclusions; independent held-out evaluation must also be completed.

## Before entering the exam room

- Run `PYTHONPATH=. .venv/bin/pytest -q`.
- Start services and confirm `/health`.
- Open saved C0, C2 and AI Experiment results.
- Confirm reviewer token privately.
- Keep architecture, report, threat model, memory policy and experiment results open.
- Test screen sharing and prepare a local backup recording.
- Never expose `.env`, API keys, tokens, private data or unlicensed source documents.

