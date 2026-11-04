param([string]$Root = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
# ML virtual environment is isolated: does not alter PREVIA v0.8 Python dependencies.
$venv = Join-Path $Root '.venv_ml'
$python = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $python)) {
  Write-Host 'Creating isolated ML Python environment...'
  if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv $venv }
  else { & python -m venv $venv }
  if ($LASTEXITCODE -ne 0) { throw 'Could not create ML environment' }
}
Write-Host 'Installing ML dependencies in isolated environment...'
& $python -m pip install -r (Join-Path $Root 'requirements-ml.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency install failed' }
Write-Host 'Downloading six official CDC files if missing...'
& (Join-Path $PSScriptRoot 'download_nhanes.ps1') -Root $Root
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw 'CDC download failed' }
Write-Host 'Training and evaluating models...'
& $python (Join-Path $PSScriptRoot 'train_nhanes.py') --raw (Join-Path $Root 'data\raw') --out (Join-Path $Root 'results\nhanes')
if ($LASTEXITCODE -ne 0) { throw 'ML pipeline failed' }
Write-Host 'ML completed. See results\nhanes\RAPPORT_ML.md' -ForegroundColor Green
