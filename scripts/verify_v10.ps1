$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$MainPython = Join-Path $Root '.venv\Scripts\python.exe'
$AiPython = Join-Path $Root 'PREVIA_ML_NHANES\.venv_ml\Scripts\python.exe'
if (!(Test-Path $MainPython)) { throw "Missing backend Python: $MainPython" }
if (!(Test-Path $AiPython)) { throw "Missing AI Python: $AiPython" }

Write-Host 'STEP 1/5 - Backend regressions' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'backend')
try { & $MainPython -m pytest -q; if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' } }
finally { Pop-Location }

Write-Host 'STEP 2/5 - AI, provider, RAG and SHAP tests' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'PREVIA_AI_XAI_RAG')
try { & $AiPython -m pytest -q tests; if ($LASTEXITCODE -ne 0) { throw 'AI tests failed.' } }
finally { Pop-Location }

Write-Host 'STEP 3/5 - ML protocol and external-validation tests' -ForegroundColor Cyan
foreach ($suite in @('PREVIA_ML_NHANES','PREVIA_ML_Optimisation_Seuil','PREVIA_ML_Validation_Externe')) {
    Push-Location (Join-Path $Root $suite)
    try { & $AiPython -m pytest -q tests; if ($LASTEXITCODE -ne 0) { throw "$suite tests failed." } }
    finally { Pop-Location }
}

Write-Host 'STEP 4/5 - Frontend production build' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'frontend')
try { & npm run build; if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' } }
finally { Pop-Location }

Write-Host 'STEP 5/5 - Dependency audit' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'frontend')
try { & npm audit --audit-level=high; if ($LASTEXITCODE -ne 0) { throw 'npm dependency audit failed.' } }
finally { Pop-Location }

Write-Host 'PREVIA v1.0 production-readiness gate PASSED.' -ForegroundColor Green
