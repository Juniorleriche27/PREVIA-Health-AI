param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot | Split-Path -Parent))
$ErrorActionPreference = 'Stop'
$module = Join-Path $ProjectRoot 'PREVIA_ML_NHANES'
$python = Join-Path $module '.venv_ml\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Environnement ML introuvable : $python. Lance d'abord run_training.ps1" }
$script = Join-Path $PSScriptRoot 'optimize_decisions.py'
& $python $script
if ($LASTEXITCODE -ne 0) { throw 'Optimisation des seuils echouee' }
Write-Host "Rapport cree : $module\results\threshold_study\RAPPORT_SEUILS.md" -ForegroundColor Green
