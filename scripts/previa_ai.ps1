param(
    [Parameter(Position=0)][ValidateSet('start','stop','restart','status','verify','diagnose')]
    [string]$Action='status'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$module=Join-Path $root 'PREVIA_AI_XAI_RAG'
$python=Join-Path $root 'PREVIA_ML_NHANES\.venv_ml\Scripts\python.exe'
$runtime=Join-Path $module '.run'
$pidFile=Join-Path $runtime 'ai.pid'
$port=8766

function Get-ManagedProcess {
    if (!(Test-Path $pidFile)) { return $null }
    $idText=(Get-Content -LiteralPath $pidFile -Raw).Trim()
    if ($idText -notmatch '^\d+$') { return $null }
    $p=Get-CimInstance Win32_Process -Filter "ProcessId = $idText" -ErrorAction SilentlyContinue
    if ($null -ne $p -and $p.CommandLine -like '*ai_service.app:app*' -and $p.CommandLine -like '*8766*') { return $p }
    return $null
}
function Is-Healthy {
    try {
        $h=Invoke-RestMethod -Uri 'http://127.0.0.1:8766/api/v1/ai/health' -TimeoutSec 2
        return $h.status -eq 'ok'
    } catch { return $false }
}
function Stop-AI {
    $proc=Get-ManagedProcess
    if ($null -ne $proc) {
        Write-Host "Stopping managed PREVIA AI process PID $($proc.ProcessId)..."
        Stop-Process -Id $proc.ProcessId -Force
        Start-Sleep -Milliseconds 600
    } else {
        $conn=Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($conn) { Write-Host 'AI port 8766 has a listener not owned by this script: leaving it untouched.' -ForegroundColor Yellow }
    }
    if (Test-Path $pidFile) { Remove-Item -LiteralPath $pidFile -Force }
}
function Start-AI {
    if (!(Test-Path $python)) { throw "Isolated Python missing: $python" }
    $managed=Get-ManagedProcess
    if ($managed -and (Is-Healthy)) {
        Write-Host "PREVIA AI already active on 8766 (PID $($managed.ProcessId))." -ForegroundColor Green
        return
    }
    $existing=Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($existing) { throw 'Port 8766 is already occupied. Unrecognized processes will not be stopped.' }
    if ($managed) { Stop-AI }
    New-Item -ItemType Directory -Path $runtime -Force | Out-Null
    # Inject optional DPAPI-protected secrets into this child process only.
    # No API key is written into provider configuration or sent to the browser.
    $secretsPath=Join-Path $module 'config\secrets.dpapi.json'
    $restore=@{}
    if (Test-Path $secretsPath) {
        $vault=Get-Content -LiteralPath $secretsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($item in $vault.PSObject.Properties) {
            $key='PREVIA_LLM_KEY_' + (($item.Name.ToUpperInvariant()) -replace '[^A-Z0-9]', '_')
            $restore[$key]=[Environment]::GetEnvironmentVariable($key,'Process')
            $secure=ConvertTo-SecureString $item.Value
            $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
            try { [Environment]::SetEnvironmentVariable($key,[Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr),'Process') }
            finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
        }
    }
    $commandArgs=@('-m','uvicorn','ai_service.app:app','--host','127.0.0.1','--port','8766','--no-access-log')
    try {
        $proc=Start-Process -FilePath $python -ArgumentList $commandArgs -WorkingDirectory $module -PassThru -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $runtime 'stdout.log') -RedirectStandardError (Join-Path $runtime 'stderr.log')
    } finally {
        foreach ($key in $restore.Keys) { [Environment]::SetEnvironmentVariable($key,$restore[$key],'Process') }
    }
    Set-Content -LiteralPath $pidFile -Value $proc.Id -Encoding Ascii
    foreach ($attempt in 1..25) {
        if (Is-Healthy) {
            Write-Host "PREVIA AI ready at http://127.0.0.1:8766 (PID $($proc.Id))" -ForegroundColor Green
            return
        }
        if ($proc.HasExited) { break }
        Start-Sleep -Milliseconds 450
    }
    Write-Host "PREVIA AI startup failed. Log: $(Join-Path $runtime 'stderr.log')" -ForegroundColor Red
    if (Test-Path (Join-Path $runtime 'stderr.log')) { Get-Content (Join-Path $runtime 'stderr.log') -Tail 25 }
    throw 'Unable to start AI sidecar.'
}

switch ($Action) {
    'start' { Start-AI }
    'stop' { Stop-AI }
    'restart' { Stop-AI; Start-AI }
    'status' {
        if (Is-Healthy) {
            $status=Invoke-RestMethod 'http://127.0.0.1:8766/api/v1/ai/health'
            Write-Host "PREVIA AI: UP; model=$($status.model_status); RAG=$($status.rag_mode_requested); sources=$($status.sources)" -ForegroundColor Green
        } else { Write-Host 'PREVIA AI: OFF' -ForegroundColor Yellow }
    }
    'verify' {
        if (!(Test-Path $python)) { throw "Missing isolated Python: $python" }
        Push-Location $module
        try {
            & $python -m pytest -q 'tests'
            if ($LASTEXITCODE -ne 0) { throw 'AI service tests failed.' }
        } finally { Pop-Location }
    }
    'diagnose' {
        Write-Host "Root: $root"
        Write-Host "Python: $python"
        Write-Host "Model artifact: $(Test-Path (Join-Path $root 'PREVIA_ML_Validation_Externe\results\cross_cycle\PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib'))"
        Write-Host "Managed AI PID: $((Get-ManagedProcess).ProcessId)"
        Write-Host "Port 8766 listener: $((Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique) -join ', ')"
        & $PSCommandPath status
    }
}
