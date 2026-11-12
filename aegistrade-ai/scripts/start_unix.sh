#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -x .venv/bin/python ]]; then
  python=.venv/bin/python
else
  if command -v python3.11 >/dev/null 2>&1; then
    interpreter=python3.11
  elif command -v python3.12 >/dev/null 2>&1; then
    interpreter=python3.12
  else
    echo 'Install Python 3.11 or 3.12, then run this script again.' >&2
    exit 2
  fi
  "$interpreter" -m venv .venv
  python=.venv/bin/python
fi
"$python" -m pip install -r requirements.txt
"$python" scripts/bootstrap.py
"$python" scripts/launch_local.py
