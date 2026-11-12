"""Launch the AegisTrade API and dashboard from one terminal.

Python 3.11/3.12 with `pip install -r requirements.txt` is recommended.
The services bind to the local computer only, never to a public interface.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def read_env(path: Path) -> dict[str, str]:
    """Very small .env parser; keep demo values simple (KEY=value, no shell expansion)."""
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=', 1)
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def check_modules() -> list[str]:
    import importlib.util
    return [name for name in ('uvicorn', 'streamlit', 'langgraph', 'fastapi')
            if importlib.util.find_spec(name) is None]


def main() -> int:
    missing = check_modules()
    if missing:
        print('Missing dependencies: '+', '.join(missing), file=sys.stderr)
        print('Run: python -m pip install -r requirements.txt', file=sys.stderr)
        return 2
    values = read_env(ROOT / '.env')
    if not values:
        print('No .env found. Run: python scripts/bootstrap.py', file=sys.stderr)
        return 2
    token = values.get('AEGIS_REVIEWER_TOKEN', '')
    if len(token) < 12 or token == 'SET_ME':
        print('Configure a private reviewer token in .env (at least 12 characters).', file=sys.stderr)
        return 2
    env = os.environ.copy()
    env.update(values)
    env.setdefault('AEGIS_API_URL', 'http://127.0.0.1:8000')
    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
    print('Selected inference backend: '+env.get('AEGIS_LLM_BACKEND','openrouter'))
    print('Starting AegisTrade in simulation-only mode.')
    print('Dashboard: http://127.0.0.1:8501')
    print('API docs:  http://127.0.0.1:8000/docs')
    print('For approvals, copy AEGIS_REVIEWER_TOKEN from your private .env file.')
    procs = []
    try:
        procs.append(subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.api:app',
                       '--host', '127.0.0.1', '--port', '8000'], cwd=ROOT, env=env))
        ready = False
        for _ in range(300):
            if procs[0].poll() is not None:
                print('API process exited. See messages above.', file=sys.stderr)
                return 1
            try:
                with urlopen('http://127.0.0.1:8000/health', timeout=1) as response:
                    ready = response.status == 200
                if ready:
                    break
            except (URLError, OSError, TimeoutError):
                time.sleep(0.2)
        if not ready:
            print('API health check did not become ready after 60 seconds; check the backend logs and port 8000.', file=sys.stderr)
            return 1
        procs.append(subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app/ui.py',
                       '--server.address', '127.0.0.1', '--server.port', '8501',
                       '--server.headless', 'true'], cwd=ROOT, env=env))
        print('Open http://127.0.0.1:8501 in your browser. Press Ctrl+C to stop both services.')
        while all(p.poll() is None for p in procs):
            time.sleep(0.4)
        print('One service exited; shutting down the other.')
        return 1
    except KeyboardInterrupt:
        print('\nStopping AegisTrade...')
        return 0
    finally:
        for p in reversed(procs):
            if p.poll() is None:
                p.terminate()
        for p in reversed(procs):
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=5)


if __name__ == '__main__':
    raise SystemExit(main())
