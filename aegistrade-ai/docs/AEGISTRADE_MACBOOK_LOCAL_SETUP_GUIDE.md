# AegisTrade AI — MacBook Local Setup Guide

**Purpose:** install and run the AegisTrade capstone project safely on another MacBook.  
**Main dashboard:** `http://127.0.0.1:8501`  
**FastAPI backend:** `http://127.0.0.1:8000`  
**Operating mode:** simulation and historical research only—no live broker connection.

## 1. What your friend needs

- A MacBook with macOS and at least 8 GB RAM.
- Administrator access for installing developer tools.
- Internet access for the first installation.
- Python **3.11 or 3.12**. Do not use a newer Python version unless its dependencies have been tested.
- Git.
- Optional: her own OpenRouter account, ChatGPT-supported Codex CLI login, or Claude CLI login. The application works in its free deterministic/synthetic mode without any of these.

Do **not** send your `.env`, OpenRouter key, reviewer token, Codex login files or Claude login files to another person. Each installation generates its own local reviewer credential.

## 2. Install Apple command-line tools

Open **Terminal** from Applications → Utilities and run:

```bash
xcode-select --install
```

If macOS reports that the tools are already installed, continue. Verify Git:

```bash
git --version
```

## 3. Install Python 3.11

### Recommended method: Homebrew

Check whether Homebrew is installed:

```bash
brew --version
```

If `brew` is not found, install it from the official Homebrew instructions at `https://brew.sh`. Then run:

```bash
brew install python@3.11
python3.11 --version
```

The final command should report Python 3.11.x. Python 3.12 is also supported:

```bash
brew install python@3.12
python3.12 --version
```

## 4. Download the project from GitHub

Choose a working folder such as `Documents`, then clone the repository:

```bash
cd "$HOME/Documents"
git clone https://github.com/vkmgenai/KarthikaKrishnakumar.git
cd KarthikaKrishnakumar/aegistrade-ai
```

Confirm that this is the correct folder:

```bash
pwd
ls README.md scripts/start_unix.sh app/ui.py
```

All three files should be listed. Commands in the remainder of this guide must be run from this `aegistrade-ai` folder.

If the repository is private, your friend must be granted GitHub access and authenticate using her own GitHub account. Do not share a personal access token in chat or email.

## 5. First start—the recommended one-command method

Run:

```bash
bash scripts/start_unix.sh
```

On the first run, the script:

1. Creates a private Python virtual environment in `.venv`.
2. Installs the packages from `requirements.txt`.
3. Creates a private `.env` with a random local reviewer token.
4. Starts FastAPI on port `8000`.
5. Waits for the API health check.
6. Starts Streamlit on port `8501`.

Package installation can take several minutes. Keep the Terminal window open. When startup succeeds, open:

- Dashboard: `http://127.0.0.1:8501`
- API landing page: `http://127.0.0.1:8000/`
- API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

The URL `127.0.0.1` means the services are available only on that MacBook.

## 6. What to check after startup

In the dashboard:

1. Confirm that the left panel says **SIMULATION ONLY—No live broker connection**.
2. Confirm that **Local reviewer authentication** says `configured`.
3. Open **Market Data** and verify that a universe/data source is shown.
4. Open **Overview** and select a symbol.
5. Open **Policy Knowledge** and perform a policy query.
6. Open **AI Agent Experiments**. C0 can run without external LLM inference; C1 and C2 require a configured provider and explicit consent.
7. Open **Strategy Backtests** for the C2 historical-portfolio workflow. This requires an enabled inference provider when research calls are needed.

Opening the application does not place live orders and does not automatically spend money on model calls.

## 7. Stop and restart the project

To stop both services, return to the launch Terminal and press:

```text
Control + C
```

To start it again later:

```bash
cd "$HOME/Documents/KarthikaKrishnakumar/aegistrade-ai"
bash scripts/start_unix.sh
```

The script reuses `.venv` and preserves the private `.env`.

## 8. Manual installation if the start script fails

From the project folder:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/bootstrap.py
.venv/bin/python scripts/launch_local.py
```

If Python 3.11 is unavailable, replace `python3.11` only in the first command with `python3.12`.

Never run the application using a different global Python after creating `.venv`; use `.venv/bin/python` or the supplied start script.

## 9. Verify the installation

Keep the application running and open a second Terminal window:

```bash
cd "$HOME/Documents/KarthikaKrishnakumar/aegistrade-ai"
.venv/bin/python scripts/smoke_local.py
```

For the full automated test suite, stop the application first if the tests need exclusive local state, then run:

```bash
.venv/bin/python -m pytest -q
```

The current validated project has **377 passing tests**. A different count can occur after later project updates, but there should be no failed tests.

## 10. Initial free configuration

The bootstrap process creates `.env` with these safe defaults:

```text
AEGIS_DATA_SOURCE=synthetic
AEGIS_RETRIEVAL_MODE=offline
AEGIS_ENABLE_LLM_EXPERIMENTS=false
```

This is the best first test because it requires no API key and cannot make external inference calls. The `.env` file is private and ignored by Git.

To inspect it locally without sharing its contents:

```bash
grep -E '^(AEGIS_DATA_SOURCE|AEGIS_RETRIEVAL_MODE|AEGIS_ENABLE_LLM_EXPERIMENTS|AEGIS_LLM_BACKEND)=' .env
```

## 11. Optional: enable an inference provider

AegisTrade retains three adapters. Configure only one initially. Restart the application after editing `.env` or authenticating a CLI.

### Option A—OpenRouter API

Your friend must use her own key. Edit `.env` locally:

```text
AEGIS_LLM_BACKEND=openrouter
OPENROUTER_API_KEY=her_private_key
OPENROUTER_MODEL=openai/gpt-4.1-mini
AEGIS_ENABLE_LLM_EXPERIMENTS=true
```

Start with one research case and a small displayed inference allowance. OpenRouter usage may incur charges. Never commit or screenshot the key.

### Option B—ChatGPT/Codex CLI

Install the supported Codex CLI, authenticate using her own account, and verify it in Terminal:

```bash
codex login
codex --version
```

Set:

```text
AEGIS_LLM_BACKEND=codex_cli
AEGIS_ENABLE_LLM_EXPERIMENTS=true
```

If `codex` is not on the Terminal path, set `AEGIS_CODEX_BIN` in `.env` to its exact executable path. ChatGPT subscription limits still apply.

### Option C—Claude CLI

Install Claude Code, authenticate using her own account and verify it:

```bash
claude auth login
claude --version
```

Set:

```text
AEGIS_LLM_BACKEND=claude_cli
AEGIS_ENABLE_LLM_EXPERIMENTS=true
```

If necessary, set `AEGIS_CLAUDE_BIN` to the exact executable path. Claude account limits still apply.

The dashboard's **Run AI agents using** selector shows whether each adapter is ready. There is no automatic fallback between providers.

## 12. Optional: prepare NSE historical data

The Git repository does not include private runtime databases or a large downloaded market cache. A fresh clone therefore starts safely with synthetic/offline data.

To prepare market data through the UI:

1. Open **Market Data**.
2. Choose one of the configured universes.
3. Select the historical period.
4. Start **Prepare selected universe**.
5. Wait for the download/progress status to complete.
6. Review the provenance and coverage warnings before activating the dataset.

This step requires internet access. NSE source availability can vary. The project uses historical daily OHLCV for research; it does not connect to a broker. Current-constituent survivorship bias and unadjusted corporate actions must remain disclosed.

## 13. Use a different dashboard port

The standard launcher uses dashboard port `8501` and API port `8000`. To change only the Streamlit port, start the services manually in two Terminal windows.

Terminal 1:

```bash
cd "$HOME/Documents/KarthikaKrishnakumar/aegistrade-ai"
set -a
source .env
set +a
PYTHONPATH="$PWD" .venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

Terminal 2—for example, dashboard port `8510`:

```bash
cd "$HOME/Documents/KarthikaKrishnakumar/aegistrade-ai"
set -a
source .env
set +a
AEGIS_API_URL=http://127.0.0.1:8000 PYTHONPATH="$PWD" \
  .venv/bin/python -m streamlit run app/ui.py \
  --server.address 127.0.0.1 --server.port 8510 --server.headless true
```

Then open `http://127.0.0.1:8510`.

## 14. Port-conflict troubleshooting

Check whether another process is using a required port:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:8501 -sTCP:LISTEN
```

First return to any earlier project Terminal and press `Control+C`. If the old Terminal is unavailable, note the process ID shown by `lsof`, verify that it belongs to the old AegisTrade process, and stop that exact process:

```bash
kill PROCESS_ID
```

Do not use broad process-killing commands.

## 15. Common problems

| Problem | Cause | Resolution |
|---|---|---|
| `python3.11: command not found` | Python 3.11 is not installed or not on PATH | Install `python@3.11` with Homebrew, or use supported Python 3.12. |
| `ModuleNotFoundError: streamlit` | The wrong Python was used or installation did not finish | Run `.venv/bin/python -m pip install -r requirements.txt`. |
| Dashboard says the API is unavailable | API failed to start or port 8000 is occupied | Open `/health`, inspect the launch Terminal, and check the ports with `lsof`. |
| `http://127.0.0.1:8000/` previously showed `Not Found` | An older backend or different application was running | Stop old processes, update the repository and restart with `scripts/start_unix.sh`. The current API has a landing page. |
| Reviewer actions are disabled | The API/UI did not load the generated reviewer token | Confirm `.env` exists, contains `AEGIS_REVIEWER_TOKEN`, and restart both services. Do not type the token into the UI. |
| C1/C2 provider is not ready | Provider is disabled, unauthenticated, or the executable/key is missing | Configure exactly one provider, enable LLM experiments and restart. |
| OpenRouter returns 401/402/429 | Invalid key, insufficient credit, or rate limit | Check the account and model on OpenRouter; reduce the case/call allowance. |
| Codex or Claude times out | CLI login, account limit, or local timeout | Verify the CLI directly, wait for limits to reset, then resume the saved run where supported. |
| NSE preparation fails | Source/network limitation | Retry later or continue with the synthetic dataset for the software demo. |
| macOS blocks a command | Terminal/developer-tool permission issue | Install command-line tools and approve only the required local executable in macOS settings. |

## 16. Update an existing installation

Stop the running application. From the outer cloned repository:

```bash
cd "$HOME/Documents/KarthikaKrishnakumar"
git pull --ff-only
cd aegistrade-ai
bash scripts/start_unix.sh
```

`git pull --ff-only` avoids silently creating an unexpected merge. Do not run destructive Git cleanup commands if your friend has local work.

## 17. Safety and hand-off checklist

Before considering the setup complete, verify:

- [ ] Dashboard opens on `127.0.0.1:8501` or the deliberately selected local port.
- [ ] `/health` returns a healthy API response.
- [ ] UI states **simulation only**.
- [ ] Reviewer authentication says `configured`.
- [ ] No `.env`, API key or CLI login file was copied from another person.
- [ ] External inference remains disabled until the user explicitly enables and consents to it.
- [ ] No service is bound to `0.0.0.0` or exposed through router port forwarding.
- [ ] The user knows that results are historical research outputs, not investment advice or guaranteed profitability.

## 18. Recommended first demonstration

1. Start with synthetic/offline data and no external inference.
2. Show **Market Data**, **Overview** and **Policy Knowledge**.
3. Run a small C0 deterministic reference case in **AI Agent Experiments**.
4. Configure one inference adapter only if needed.
5. Run one C1/C2 case with explicit consent and a small allowance.
6. Use **Strategy Backtests** only after confirming the provider is ready; choose a short date range for the first C2 portfolio test.
7. Stop the services with `Control+C` when finished.

This sequence proves that the local installation works before spending time or provider allowance on a longer experiment.
