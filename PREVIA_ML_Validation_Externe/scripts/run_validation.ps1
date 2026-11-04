param([switch]$Quick)
$ErrorActionPreference = 'Stop'
$module = Split-Path -Parent $PSScriptRoot
$project = Split-Path -Parent $module
$oldModule = Join-Path $project 'PREVIA_ML_NHANES'
$python = Join-Path $oldModule '.venv_ml\Scripts\python.exe'
if (-not (Test-Path $python)) {
  throw "Original isolated ML Python environment not found: $python. First complete PREVIA_ML_NHANES training."
}
$requirements = Join-Path $module 'requirements-ml.txt'
Write-Host 'Checking ML packages in existing isolated environment...'
& $python -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
$downloadScript = Join-Path $PSScriptRoot 'download_cycles.ps1'
Write-Host 'Collecting both CDC NHANES cycles...'
& $downloadScript -ModuleRoot $module -DevelopmentRaw (Join-Path $oldModule 'data\raw')
if (-not $?) { throw 'CDC download script failed' }
Write-Host 'Running preprocessing and scientific protocol tests...'
& $python -m pytest -q (Join-Path $module 'tests')
if ($LASTEXITCODE -ne 0) { throw 'Protocol tests failed; stopping before training' }
$dev = Join-Path $oldModule 'data\raw'
$ext = Join-Path $module 'data\raw\2015_2016'
$out = Join-Path $module 'results\cross_cycle'
$entry = Join-Path $PSScriptRoot 'external_validation.py'
Write-Host 'Fitting and comparing models on 2017-2018; evaluating once on 2015-2016...'
$args = @($entry,'--development-raw',$dev,'--external-raw',$ext,'--out',$out)
if ($Quick) { $args += '--quick' }
& $python @args
if ($LASTEXITCODE -ne 0) { throw 'Cross-cycle training/validation failed' }
Write-Host "Finished. Report: $(Join-Path $out 'RAPPORT_VALIDATION_EXTERNE.md')" -ForegroundColor Green
Get-Content -LiteralPath (Join-Path $out 'RAPPORT_VALIDATION_EXTERNE.md') -Encoding UTF8
