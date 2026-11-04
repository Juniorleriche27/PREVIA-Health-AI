param([switch]$SkipBuild, [switch]$NoStart)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$module=Join-Path $root 'PREVIA_AI_XAI_RAG'
$python=Join-Path $root 'PREVIA_ML_NHANES\.venv_ml\Scripts\python.exe'
if (!(Test-Path $python)) { throw 'PREVIA_ML_NHANES isolated Python missing. Complete NHANES ML training first.' }
if (!(Test-Path (Join-Path $root 'scripts\previa.ps1'))) { throw 'PREVIA v0.8 scripts/previa.ps1 is required; this patch does not overwrite it.' }
if (!(Test-Path (Join-Path $root 'PREVIA_ML_Validation_Externe\results\cross_cycle\PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib'))) {
    Write-Host 'NHANES v2 model not found: RAG works, SHAP will show a clear unavailable message.' -ForegroundColor Yellow
}
Write-Host 'Installing isolated SHAP, FastAPI and retrieval dependencies...' -ForegroundColor Cyan
& $python -m pip install -r (Join-Path $module 'requirements-ai.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
$previousPath=$env:PYTHONPATH
$env:PYTHONPATH=$module + [IO.Path]::PathSeparator + $previousPath
try { & $python -m pytest -q (Join-Path $module 'tests') }
finally { $env:PYTHONPATH=$previousPath }
if ($LASTEXITCODE -ne 0) { throw 'AI module tests failed.' }

# Preserve all existing v0.8 config keys; replace only PREVIA AI URL.
$envFile=Join-Path $root 'frontend\.env.local'
$config=if (Test-Path $envFile) { [System.IO.File]::ReadAllText($envFile) } else { '' }
$config=[regex]::Replace($config, '(?m)^NEXT_PUBLIC_AI_API_URL=.*(?:\r?\n)?', '')
$config=$config.TrimEnd() + "`nNEXT_PUBLIC_AI_API_URL=http://127.0.0.1:8766`n"
[System.IO.File]::WriteAllText($envFile,$config,[System.Text.UTF8Encoding]::new($false))

# Add a single navigation entry to previous seven pages without replacing Codex fixes.
$front=Join-Path $root 'frontend\app'
$pages=Get-ChildItem -LiteralPath $front -Filter 'page.tsx' -File -Recurse |
    Where-Object { $_.FullName -notlike '*\app\ai\*' }
foreach ($page in $pages) {
    $content=[System.IO.File]::ReadAllText($page.FullName)
    if ($content.Contains('className="topnav"') -and !$content.Contains('href="/ai"')) {
        $point=$content.IndexOf('</nav>')
        if ($point -ge 0) {
            $content=$content.Insert($point,'<a className="navlink" href="/ai">ML + XAI + RAG</a>')
            [System.IO.File]::WriteAllText($page.FullName,$content,[System.Text.UTF8Encoding]::new($false))
        }
    }
}

if (-not $SkipBuild) {
    Push-Location (Join-Path $root 'frontend')
    try {
        Write-Host 'Building Next.js including /ai page...' -ForegroundColor Cyan
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed; servers not restarted.' }
    } finally { Pop-Location }
}
if (-not $NoStart) {
    Set-Location $root
    & (Join-Path $root 'scripts\previa_full.ps1') start
    Write-Host 'Open http://localhost:3001/ai for AI modules.' -ForegroundColor Green
} else {
    Write-Host 'Installation passed. Start with .\scripts\previa_full.ps1 start' -ForegroundColor Green
}
