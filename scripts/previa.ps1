param(
    [ValidateSet('start','stop','restart','status','diagnose','verify')]
    [string]$Action = 'start',
    [switch]$Production
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root '.previa-runtime'
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$Frontend = Join-Path $Root 'frontend'
$Backend = Join-Path $Root 'backend'
$BackendPort = 8765
$FrontendPort = 3001

function Get-PortOwner([int]$Port) {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) { return $connection.OwningProcess }
    $line = netstat -ano -p tcp | Select-String -Pattern (":$Port\s+.*LISTENING\s+(\d+)\s*$") | Select-Object -First 1
    if ($line -and $line.Matches.Count) { return [int]$line.Matches[0].Groups[1].Value }
}

function Test-PreviaProcess([int]$ProcessId) {
    if (-not $ProcessId) { return $false }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
    return $process -and $process.CommandLine -and $process.CommandLine.Contains($Root)
}

function Stop-Previa {
    $candidates = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -and $_.CommandLine.Contains($Root) -and
        ($_.CommandLine -match 'uvicorn.*8765|next.*3001|npm-cli\.js.*run (dev|start)')
    }
    foreach ($process in ($candidates | Sort-Object ProcessId -Descending)) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped PREVIA $($process.Name) (PID $($process.ProcessId))." -ForegroundColor Yellow
    }
}

function Wait-Url([string]$Url, [int]$Seconds = 40) {
    $deadline = (Get-Date).AddSeconds($Seconds)
    do {
        try { Invoke-RestMethod -Uri $Url -TimeoutSec 2 | Out-Null; return $true } catch { Start-Sleep -Milliseconds 500 }
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Start-Previa {
    if (!(Test-Path $Python)) { throw "Missing Python environment: $Python" }
    if (!(Test-Path (Join-Path $Frontend 'node_modules'))) { throw 'Missing frontend dependencies. Run npm ci in frontend.' }
    New-Item -ItemType Directory -Path $Runtime -Force | Out-Null
    $envFile = Join-Path $Frontend '.env.local'
    Set-Content -LiteralPath $envFile -Value @(
        'NEXT_PUBLIC_API_URL=http://127.0.0.1:8765',
        'NEXT_PUBLIC_AI_API_URL=http://127.0.0.1:8766'
    ) -Encoding utf8

    # Always replace this project's stale processes so code and cache versions cannot drift.
    Stop-Previa
    Start-Sleep -Milliseconds 800
    foreach ($port in @($BackendPort, $FrontendPort)) {
        $owner = Get-PortOwner $port
        if ($owner -and -not (Test-PreviaProcess $owner)) {
            throw "Port $port is occupied by another application (PID $owner). Run: .\scripts\previa.ps1 diagnose"
        }
    }
    $args = @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port',"$BackendPort")
    Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Backend -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $Runtime 'backend.out.log') -RedirectStandardError (Join-Path $Runtime 'backend.err.log') | Out-Null
    if (-not (Wait-Url "http://127.0.0.1:$BackendPort/health")) { throw 'Backend startup failed. Inspect .previa-runtime/backend.err.log.' }

    $npmArgs = if ($Production) { @('run','start','--','-p',"$FrontendPort") } else { @('run','dev','--','-p',"$FrontendPort") }
    $oldCacheSetting = $env:PREVIA_DEV_CACHE
    if (-not $Production) { $env:PREVIA_DEV_CACHE = '1' }
    Start-Process -FilePath 'npm.cmd' -ArgumentList $npmArgs -WorkingDirectory $Frontend -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $Runtime 'frontend.out.log') -RedirectStandardError (Join-Path $Runtime 'frontend.err.log') | Out-Null
    $env:PREVIA_DEV_CACHE = $oldCacheSetting
    if (-not (Wait-Url "http://localhost:$FrontendPort" 60)) { throw 'Frontend startup failed. Inspect .previa-runtime/frontend.err.log.' }
    Write-Host "PREVIA is ready: http://localhost:$FrontendPort" -ForegroundColor Green
}

function Show-Status {
    foreach ($item in @(@('Backend',$BackendPort), @('Frontend',$FrontendPort))) {
        $owner = Get-PortOwner $item[1]
        $url = if ($item[0] -eq 'Backend') { "http://127.0.0.1:$($item[1])/health" } else { "http://localhost:$($item[1])" }
        try { $null = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2; $reachable = $true } catch { $reachable = $false }
        $state = if ($reachable) { if ($owner) { "READY (PID $owner)" } else { 'READY' } } else { 'STOPPED' }
        Write-Host ("{0,-10} {1,-8} {2}" -f $item[0], $item[1], $state)
    }
}

switch ($Action) {
    'start' { Start-Previa }
    'stop' { Stop-Previa }
    'restart' { Stop-Previa; Start-Sleep -Milliseconds 800; Start-Previa }
    'status' { Show-Status }
    'diagnose' {
        Write-Host "Root: $Root"; Write-Host "Python: $Python ($(Test-Path $Python))"; Write-Host "Node: $(& node --version)"; Write-Host "npm: $(& npm --version)"
        Show-Status
        if (Test-Path $Runtime) { Get-ChildItem $Runtime -Filter '*.log' | Select-Object Name,Length,LastWriteTime }
    }
    'verify' { & (Join-Path $PSScriptRoot 'verify_v08.ps1'); if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
}
