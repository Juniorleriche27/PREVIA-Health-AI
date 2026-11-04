# Download five official CDC NHANES public files locally; aggregate only.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (!(Test-Path $python)) { throw "Missing virtual environment $python" }
& $python -m pip install 'pandas>=2.2,<4'
if ($LASTEXITCODE -ne 0) { throw 'Cannot install pandas for XPT reading.' }
& $python (Join-Path $PSScriptRoot 'prepare_nhanes_v06.py')
if ($LASTEXITCODE -ne 0) { throw 'CDC NHANES input QA failed. Inspect download/connectivity error above.' }
Write-Host 'NHANES public-data aggregate prepared: refresh /evidence in the browser.' -ForegroundColor Green
