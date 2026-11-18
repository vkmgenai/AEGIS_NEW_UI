#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export AEGIS_API_URL="${AEGIS_API_URL:-http://127.0.0.1:8002}"
preview_api_pid=""
if ! curl -fsS --max-time 2 "$AEGIS_API_URL/health" >/dev/null 2>&1; then
  .venv/bin/uvicorn app.api:app --host 127.0.0.1 --port 8002 > /tmp/aegistrade-preview-api.log 2>&1 &
  preview_api_pid="$!"
fi

cleanup() {
  if [[ -n "$preview_api_pid" ]]; then
    kill "$preview_api_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

.venv/bin/streamlit run app/ui_redesign_preview.py --server.address 127.0.0.1 --server.port 8504 --browser.gatherUsageStats false
