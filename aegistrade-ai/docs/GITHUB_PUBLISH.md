# Publish the folder to your GitHub repository

## 1. Confirm the repository is safe to publish

Use a **private GitHub repository** while your capstone is under development. The code is educational and the candidate evaluation data are not independently validated. Do not upload faculty course PDFs or files for which you lack redistribution permission.

Check files first:

```bash
git status --short
# .env, .venv/, *.sqlite*, generated data and API secrets must not be staged.
```

The starter `.gitignore` excludes those items. Verify independently before every commit.

## 2. Create a GitHub repository

In GitHub, click **New repository** and call it `aegistrade-ai`. Choose **Private**, and for the simplest workflow create it **empty** (do not initialize a README, since this folder already has one).

## 3. Initialize Git and upload from the project root

```bash
git init
git branch -M main
git add .
git status --short             # inspect exactly what is being uploaded
git commit -m "Initial AegisTrade AI local capstone application"
git remote add origin https://github.com/YOUR_USERNAME/aegistrade-ai.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. GitHub may request authentication through the browser or Git Credential Manager. Do not paste your OpenRouter API key into a Git credential prompt.

Alternative using the GitHub CLI (if installed, `gh auth login` first):

```bash
git init && git add . && git commit -m "Initial local AegisTrade application"
gh repo create aegistrade-ai --private --source . --remote origin --push
```

## 4. Each team member clones the repository

```bash
git clone https://github.com/YOUR_USERNAME/aegistrade-ai.git
cd aegistrade-ai
python scripts/bootstrap.py
# follow docs/LOCAL_SETUP.md to install dependencies
```

Avoid sharing `.env` between team members; each should generate a private reviewer token. Each member uses their own OpenRouter credentials or an approved shared team secret store. Never commit keys.

## 5. Suggested collaborative workflow

| Branch | Owner / intent |
|---|---|
| `main` | Stable runnable integration only |
| `feature/quant-backtests` | Veneet: real data, strategies and quantified evaluation |
| `feature/agents-rag` | Karthika: RAG, MCP, LangGraph and Reflexion |
| `feature/risk-dashboard` | Mathangi: approvals, UI, simulated broker, CI/Docker |

Open pull requests to `main`, request review, and merge only after `python -m pytest -q` and development evaluation pass. Use GitHub Issues for integration milestones and a project-level contribution log.

## 6. Continuous integration

`.github/workflows/ci.yml` runs Python 3.11, unit tests, a synthetic development evaluation check, and a basic credential-pattern scan on pushes and pull requests. It does not prove the full capstone research requirements or validate real-market returns. If an integration test is skipped due to missing package errors, investigate rather than treating the project as completely verified.

## 7. Important corrections to avoid

- Do not run `git add -f .env` or upload `.env` through the GitHub website.
- Do not publish internal student identifiers or private data in a public repository.
- Do not claim that C1/C2 fixed-router proxy backtest rows prove an AI agent advantage.
- Do not paste sample synthetic returns into slides without labelling them **synthetic**.
- Do not enable live broker APIs; all existing gateway actions are simulated.
