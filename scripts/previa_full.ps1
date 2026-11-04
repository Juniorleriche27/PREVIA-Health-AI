param(
    [Parameter(Position=0)][ValidateSet('start','stop','restart','status','verify','diagnose')]
    [string]$Action='start',
    [switch]$Production
)
$ErrorActionPreference='Stop'
$main=Join-Path $PSScriptRoot 'previa.ps1'
$ai=Join-Path $PSScriptRoot 'previa_ai.ps1'
if (!(Test-Path $main)) { throw 'PREVIA v0.8 lifecycle script scripts/previa.ps1 is missing.' }
if (!(Test-Path $ai)) { throw 'AI lifecycle script missing.' }
if ($Action -eq 'stop') {
    & $ai stop
    & $main stop
} elseif ($Action -eq 'restart') {
    & $main restart -Production:$Production
    & $ai restart
} elseif ($Action -eq 'start') {
    & $main start -Production:$Production
    & $ai start
} elseif ($Action -eq 'verify') {
    & (Join-Path $PSScriptRoot 'verify_v10.ps1')
} else {
    & $main $Action
    & $ai $Action
}
