# Run from any folder: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
  py -3.11 -m venv .venv
}
$python = '.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python scripts\bootstrap.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python scripts\launch_local.py
