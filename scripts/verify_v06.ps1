# PREVIA v0.6: validates WHO transcription, Python regressions, and Next.js build.
# Uses existing .venv, frontend dependencies and .env.local; no file editing.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (!(Test-Path $python)) { throw "Cannot locate Python virtual environment at $python" }

Push-Location (Join-Path $root 'backend')
try {
    Write-Host '1/3 - Checking all 700 WHO text-layer reference cells...' -ForegroundColor Cyan
    & $python -c "from app.source_verification import verify_all_chart_cells; r=verify_all_chart_cells(); print(str(r['cells_matching'])+'/'+str(r['cells_compared'])); assert r['text_cross_check_passed']"
    if ($LASTEXITCODE -ne 0) { throw 'WHO text-layer reference integrity mismatch.' }
    Write-Host '2/3 - Running backend tests...' -ForegroundColor Cyan
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend regression tests failed.' }
} finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    Write-Host '3/3 - Checking Next.js production build...' -ForegroundColor Cyan
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Next.js build failed. Run npm install once, then retry.' }
} finally { Pop-Location }

Write-Host 'PREVIA v0.6 regression tests and frontend build passed.' -ForegroundColor Green
Write-Host 'CDC dataset remains optional and NOT loaded automatically.' -ForegroundColor Yellow
