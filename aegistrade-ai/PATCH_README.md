# Applying the AegisTrade Capital + C0/C1/C2 UI Patch

This ZIP is a **root-relative overlay** for the existing `aegistrade-ai` folder. Do not extract it into a nested subfolder. It intentionally does not contain `.env`, virtual environments or local SQLite databases.

## On the target Mac

1. Stop AegisTrade with `Ctrl+C` and stop Docker with `docker compose down` if you were using containers (do NOT add `-v`).
2. In Terminal:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
cp app/api.py app/api_before_capital_update.py
cp app/ui.py app/ui_before_capital_update.py
unzip -o ~/Downloads/AegisTrade_AI_Capital_C0C1C2_Patch.zip -d /Users/karthikakrishnakumar/aegistrade-ai
bash scripts/start_unix.sh
```

3. Open http://127.0.0.1:8501. Use **Strategy Backtests** to configure capital/date/risk and **AI Agent Experiments** to test C0 without a key.
4. In another Terminal, run:

```bash
cd /Users/karthikakrishnakumar/aegistrade-ai
.venv/bin/python -m pytest -q
.venv/bin/python -m scripts.smoke_portfolio_agents
```

5. Before enabling paid C1/C2, create an OpenRouter key, set its provider-side spending limit, and then add your key and `AEGIS_ENABLE_LLM_EXPERIMENTS=true` to the private `.env`. Restart the API. Enter the private `AEGIS_REVIEWER_TOKEN` only into the UI sidebar approval field.

## Need to undo the patch?

You can restore just the two backed-up entry points:

```bash
cp app/api_before_capital_update.py app/api.py
cp app/ui_before_capital_update.py app/ui.py
```

However, other new files may remain. The cleanest full rollback is a Git commit checkout or a complete directory backup made before applying the patch.

See `docs/AegisTrade_AI_Capital_C0C1C2_End_to_End_Manual.docx` for the complete Mac setup, OpenRouter guidance, workflow demonstration, Docker monitoring and final capstone evidence checklist.
