"""Smoke-test a running local FastAPI service: python scripts/smoke_local.py."""
from __future__ import annotations
import json
import sys
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = os.getenv('AEGIS_API_URL','http://127.0.0.1:8000').rstrip('/')


def fetch(path: str, data: dict | None = None) -> dict:
    body = None if data is None else json.dumps(data).encode('utf-8')
    request = Request(ROOT+path, data=body,
                      headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=90) as r:
        return json.load(r)


def main() -> int:
    try:
        cases = [
            ('API health', '/health', None),
            ('Symbol universe', '/market/universe', None),
            ('Market history', '/market/history?symbol=RELIANCE&limit=20', None),
            ('Backtest comparison', '/backtest/compare', None),
            ('Knowledge retrieval', '/knowledge/search', {'query':'human approval exact order'}),
            ('Broker audit history', '/audit/events', None),
        ]
        for name, endpoint, body in cases:
            result = fetch(endpoint, body)
            if endpoint=='/health' and result.get('version')!='0.28.0':
                print('NOTE: Running API source version differs from this final-review source; restart the matching checkout.')
            print(f'PASS {name}: {str(list(result) if isinstance(result,dict) else len(result))[:80]}')
        print('Smoke test passed. No real trades were placed.')
        return 0
    except (URLError, HTTPError, ValueError) as exc:
        print(f'Smoke test failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
