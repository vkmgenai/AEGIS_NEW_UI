# AegisTrade update — configurable capital, date ranges and C0/C1/C2 web UI

## What's new

* `Strategy Backtests` has a form for initial capital (default ₹200,000), daily-bar start/end dates, 0.25–3% per-trade risk, fee/slippage basis points, and ALL/individual strategy choices. Historical simulations use the same starting capital across strategies.
* Results include equity and cash curves, open position counts, a trade ledger (BUY/SELL_SIGNAL/SELL_STOP), saved simulation IDs, and JSON/CSV exports. Run files persist under `data/simulation_runs/`.
* New `AI Agent Experiments` workspace runs C0 (0 LLM calls), C1 (up to 1/case), C2 (up to 3/case), or ALL (up to 4/case) on the same fixed research scenarios. Maximum 3 scenarios per UI run (up to 12 attempted external calls). Results persist under `data/research_runs/`.
* C1/C2 and ALL require a configured OpenRouter key, `AEGIS_ENABLE_LLM_EXPERIMENTS=true`, an authorized reviewer token, and explicit cost consent for each run. No key is entered in the browser UI.
* `Supervised Trading` now accepts a **reference equity** amount for one proposal; this is **not yet a persistent paper-trading portfolio**. Broker actions remain manually approved.
* New Prometheus metrics for simulations and research attempts; expanded Grafana dashboard panels.

## What this is NOT

* No automatic C2-powered portfolio backtesting. The historical `ROUTER` remains a code-approved fixed-rule router.
* No real broker connectivity, live NSE price stream, or trading with real currency.
* No proof of returns; synthetic data is default, and real-data adjustments/survivorship require validation.
* No complete faculty-ready evaluation until held-out cases, calibration, fair-budget repeated comparisons and security trials are independently completed.
* The per-run 12-call cap is NOT a monthly API spending limit. Set a monetary limit on your OpenRouter account.

## Patch update (existing Mac installation)

1. Stop the startup script with `Ctrl+C` and back up the repository (or commit its current state).
2. Download `AegisTrade_AI_Capital_C0C1C2_Patch.zip` to `~/Downloads`.
3. Run:
   ```bash
   cd /Users/karthikakrishnakumar/aegistrade-ai
   cp app/ui.py app/ui_backup_before_capital.py
   cp app/api.py app/api_backup_before_capital.py
   unzip -o ~/Downloads/AegisTrade_AI_Capital_C0C1C2_Patch.zip -d /Users/karthikakrishnakumar/aegistrade-ai
   ```
4. Restart `bash scripts/start_unix.sh`. Your `.env` and SQLite DBs remain unchanged.
5. Check: `.venv/bin/python -m pytest -q` and `.venv/bin/python -m scripts.smoke_portfolio_agents` (with API running).
6. Open http://127.0.0.1:8501; use `Strategy Backtests` and `AI Agent Experiments`.

## Key setup (when ready)

1. Create a key at https://openrouter.ai/settings/keys and set an account/key spending limit before enabling calls.
2. Open local `.env` with `nano .env`; set `OPENROUTER_API_KEY=...`, `OPENROUTER_MODEL=<approved model slug>`, and `AEGIS_ENABLE_LLM_EXPERIMENTS=true`.
3. Restart API/dashboard to reload `.env` and verify `/health` shows `llm_experiments_enabled: true`.
4. Enter `AEGIS_REVIEWER_TOKEN` into sidebar privately, select C1 with **1 case**, check cost-consent box, submit. Review errors/usage; then try C2 and ALL.
5. Never paste key into UI, commit `.env`, share screenshots of tokens, or assume 12 attempted calls is a cost ceiling across repeated runs.

## Docker

Docker is **optional for running the two local web services**; it is part of the capstone's full deployment/monitoring requirements. On Docker Desktop:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
docker compose up --build api dashboard
# Or with monitoring and MCP services:
docker compose up --build
```

Streamlit :8501; API docs :8000/docs; Prometheus :9090; Grafana :3000. Docker uses `.env` in the API service, but does **not** share a local script's in-memory Streamlit session history. Save runs are persisted in the Docker `aegis_data` named volume.

For detailed explanations and a guided viva sequence, see `docs/AegisTrade_AI_Capital_C0C1C2_End_to_End_Manual.docx`.
