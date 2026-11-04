param([switch]$NoRestart, [switch]$SkipBuild)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$module=Join-Path $root 'PREVIA_AI_XAI_RAG'
$python=Join-Path $root 'PREVIA_ML_NHANES\.venv_ml\Scripts\python.exe'
if(!(Test-Path $python)){throw 'Environnement ML manquant.'}
if(!(Test-Path (Join-Path $root 'scripts\previa_full.ps1'))){throw 'Script de demarrage PREVIA manquant.'}
$oldPath=$env:PYTHONPATH
$env:PYTHONPATH=$module + [IO.Path]::PathSeparator + $oldPath
try {
  & $python -m pytest -q (Join-Path $module 'tests')
  if($LASTEXITCODE -ne 0){throw 'Tests IA echoues.'}
} finally { $env:PYTHONPATH=$oldPath }
if(-not $SkipBuild){
  Push-Location (Join-Path $root 'frontend')
  try { & npm run build; if($LASTEXITCODE -ne 0){throw 'Build Next.js echoue.'} }
  finally { Pop-Location }
}
if(-not $NoRestart){
  & (Join-Path $root 'scripts\previa_full.ps1') restart
  if($LASTEXITCODE -ne 0){throw 'Redemarrage PREVIA echoue.'}
}
Write-Host 'PREVIA multi-provider : tests et procedure termines.' -ForegroundColor Green
