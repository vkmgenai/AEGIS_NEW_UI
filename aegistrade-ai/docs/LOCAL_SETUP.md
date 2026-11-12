# Local installation and troubleshooting

**Recommended:** Python 3.11, 8 GB RAM, Docker Desktop optional. CPU only. No exchange connection.

## Windows — fastest setup

1. Extract the downloaded ZIP. Enter `aegistrade-ai` (contains `README.md` and `docker-compose.yml`).
2. Install Python 3.11, and ensure `py -3.11 --version` works in PowerShell.
3. From the folder, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_windows.ps1
```

The script creates `.venv`, installs dependencies, generates `.env`, and launches two local web services. After the startup messages, visit http://127.0.0.1:8501.

**Manual Windows route** (if the helper script fails):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\bootstrap.py
.venv\Scripts\python.exe scripts\launch_local.py
```

## macOS or Linux — fastest setup

```bash
cd /path/to/aegistrade-ai
bash scripts/start_unix.sh
```

**Manual macOS/Linux route:**

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/bootstrap.py
.venv/bin/python scripts/launch_local.py
```

If Python 3.11 is unavailable, Python 3.12 is a reasonable alternative; use the same version for `.venv` and `pip`. Check library compatibility if trying newer Python versions.

## Verify your installation

Open a second terminal with the active environment (or use `.venv/Scripts/python.exe` or `.venv/bin/python`):

```bash
python -m pytest -q
python scripts/smoke_local.py
```

A successful smoke check prints **PASS** for health, universe, history, comparison, knowledge, and audit endpoints. None of these operations calls a live broker.

## URLs / ports

| Service | URL | Needs Docker? |
|---|---|---|
| Trading dashboard | http://127.0.0.1:8501 | No |
| API schema | http://127.0.0.1:8000/docs | No |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json | No |
| Prometheus | http://127.0.0.1:9090 | Yes (unless manually installed) |
| Grafana | http://127.0.0.1:3000 | Yes (unless manually installed) |

## Docker alternative

1. Install and launch Docker Desktop.
2. From project root, run `python scripts/bootstrap.py` (or `py -3.11 scripts/bootstrap.py` on Windows).
3. Start the main app: `docker compose up --build api dashboard`.
4. For monitoring and MCP servers, use `docker compose up --build`.
5. Stop with `Ctrl+C` or `docker compose down`.

`docker compose down -v` **deletes runtime databases**, including simulated orders and reviewed lessons. Do not use it unless you intend to reset the demo.

## How to use the frontend

- **Dashboard:** choose a synthetic research symbol, examine daily close and EMA lines, and inspect RSI and regime.
- **Strategy Backtests:** run and compare fixed strategies vs rule-based router; plot equity and view event log. No profit is guaranteed.
- **Supervised Trading:** choose automatic signal, start a workflow, examine exact SHA-256 payload and approve/reject/edit using reviewer token from `.env`.
- **Policy Knowledge:** retrieve indexed internal policy passages and inspect dates and IDs.
- **Learning & Lessons:** propose a development lesson, approve or reject it, freeze the reviewed playbook.
- **Broker Audit:** view local simulated order acceptance/rejection events.

## Common errors

| Problem | Likely reason | Fix |
|---|---|---|
| `ModuleNotFoundError: streamlit` | Dependencies not installed in the Python you launched | Use the `.venv` Python executable to install `requirements.txt` |
| `ModuleNotFoundError: langgraph` | Full requirements not installed | Re-run `python -m pip install -r requirements.txt` |
| Dashboard says API unavailable | Backend stopped, port mismatch, or already occupied port | Run `python scripts/launch_local.py`; check http://127.0.0.1:8000/health |
| HTTP 403 on approval | Missing/incorrect reviewer token | Copy `AEGIS_REVIEWER_TOKEN` from `.env` to sidebar; restart API after changing `.env` |
| HTTP 422 no eligible BUY signal | Requested symbol has no eligible replay signal | Choose `(automatic)` for the demo |
| Stale quote rejected | Deliberate fail-closed safeguard | Uncheck the injection setting for a normal simulated acceptance |
| Docker cannot build | Offline or dependency resolution failed | Check internet, restart Docker, rebuild; capture logs |
| Grafana looks empty | Insufficient API traffic / missing datasource | Exercise dashboard, open Prometheus, verify targets and provisioning |
| Port 8000/8501 already used | Old process running | Stop other app instances or inspect port usage |
| OpenRouter cost / key errors | No key, wrong model, or token budget | Keep it off for initial runs; confirm approved model and limit |

## Safety

Every service is bound to loopback in this local setup. The reviewer token is a single-user *demo* check, not full user/role authentication. Do not expose Docker ports to the internet, do not replace the simulator with a live broker, and never commit `.env` or SQLite files.
