"""Create a private local .env without overwriting existing configuration.

Run from the repository root or anywhere: python scripts/bootstrap.py
"""
from __future__ import annotations

from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / '.env'
TEMPLATE = ROOT / '.env.example'


def main() -> int:
    if TARGET.exists():
        print(f'Configuration already exists: {TARGET}. Leaving it unchanged.')
        return 0
    if not TEMPLATE.exists():
        print('Missing .env.example in project root', file=sys.stderr)
        return 1
    content = TEMPLATE.read_text(encoding='utf-8')
    content = content.replace('AEGIS_REVIEWER_TOKEN=SET_ME', f'AEGIS_REVIEWER_TOKEN={secrets.token_urlsafe(24)}')
    content = content.replace('AEGIS_GRAFANA_PASSWORD=SET_ME', f'AEGIS_GRAFANA_PASSWORD={secrets.token_urlsafe(20)}')
    TARGET.write_text(content, encoding='utf-8')
    try:
        TARGET.chmod(0o600)
    except OSError:
        pass
    print(f'Created private configuration: {TARGET}')
    print('Your reviewer token and Grafana password are in .env. Never commit that file.')
    print('OpenRouter remains disabled until you explicitly add OPENROUTER_API_KEY.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
