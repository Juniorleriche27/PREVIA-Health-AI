# PREVIA v0.5: verification only. Does not delete files or modify personal settings.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Python virtual environment missing: $python" }

Push-Location (Join-Path $root 'backend')
try {
    Write-Host 'Running backend regression and evaluation tests...' -ForegroundColor Cyan
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    Write-Host 'Compiling Next.js...' -ForegroundColor Cyan
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Next.js build failed.' }
} finally { Pop-Location }
Write-Host 'PREVIA v0.5: backend tests and Next.js build completed.' -ForegroundColor Green
