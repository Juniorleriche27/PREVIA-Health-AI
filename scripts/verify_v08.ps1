$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (!(Test-Path $Python)) { throw "Missing Python environment: $Python" }

Push-Location (Join-Path $Root 'backend')
try {
    & $Python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
    & $Python -c "from app.source_verification import verify_all_chart_cells; x=verify_all_chart_cells(); assert x['text_cross_check_passed']; print('WHO reference:', x['cells_matching'], '/', x['cells_compared'])"
    if ($LASTEXITCODE -ne 0) { throw 'WHO reference verification failed.' }
} finally { Pop-Location }

Push-Location (Join-Path $Root 'frontend')
try {
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend production build failed.' }
} finally { Pop-Location }

Write-Host 'PREVIA v0.8 verification PASSED.' -ForegroundColor Green
