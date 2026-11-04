# PREVIA Health AI v0.7 - regression and production-build verification.
# PowerShell-only installation workflow; does not modify .env.local,
# .venv, CDC files, local_public_data or any clinical data.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (!(Test-Path $python)) { throw "Missing Python environment: $python" }

Push-Location (Join-Path $root 'backend')
try {
    Write-Host 'STEP 1/4 - WHO 700-cell official PDF-text reference check' -ForegroundColor Cyan
    & $python -c "from app.source_verification import verify_all_chart_cells; x=verify_all_chart_cells(); print(str(x['cells_matching'])+'/'+str(x['cells_compared'])); assert x['text_cross_check_passed']"
    if ($LASTEXITCODE -ne 0) { throw 'WHO cross-check failed' }

    Write-Host 'STEP 2/4 - All Python regression tests' -ForegroundColor Cyan
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed' }

    Write-Host 'STEP 3/4 - New synthetic workflow smoke test' -ForegroundColor Cyan
    & $python -c "from app.pathways import PathwayInput,simulate_pathway; x=simulate_pathway(PathwayInput(confirm_synthetic_demo=True)); print('Pathway:', x.summary.selected, 'selected /', x.summary.attended, 'attended demo /', x.summary.reviewed, 'reviewed demo'); assert x.summary.selected==45 and x.summary.reviewed==6 and x.summary.attended==12"
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic workflow smoke test failed' }
} finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    Write-Host 'STEP 4/4 - Next.js production build' -ForegroundColor Cyan
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Next.js build failed. Check npm dependencies and terminal log.' }
} finally { Pop-Location }

Write-Host 'PREVIA v0.7 - Regression tests and production build PASSED.' -ForegroundColor Green
Write-Host 'No real patients, medical appointments or messages are processed by this module.' -ForegroundColor Yellow
