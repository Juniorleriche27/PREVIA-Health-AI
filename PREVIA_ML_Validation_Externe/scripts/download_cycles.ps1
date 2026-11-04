param(
  [string]$ModuleRoot = (Split-Path -Parent $PSScriptRoot),
  [string]$DevelopmentRaw = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'PREVIA_ML_NHANES\data\raw')
)
$ErrorActionPreference = 'Stop'
$externalRaw = Join-Path $ModuleRoot 'data\raw\2015_2016'
New-Item -ItemType Directory -Path $externalRaw -Force | Out-Null
New-Item -ItemType Directory -Path $DevelopmentRaw -Force | Out-Null
$prefixes = @('DEMO','BMX','BPX','SMQ','DIQ','GHB','BPQ','PAQ')
$cycles = @(
  @{ Year=2017; Suffix='J'; Target=$DevelopmentRaw },
  @{ Year=2015; Suffix='I'; Target=$externalRaw }
)
foreach ($cycle in $cycles) {
  foreach ($prefix in $prefixes) {
    $name = "$($prefix)_$($cycle.Suffix)"
    $target = Join-Path $cycle.Target "$name.xpt"
    if (Test-Path -LiteralPath $target) {
      if ((Get-Item -LiteralPath $target).Length -gt 2000) {
        Write-Host "Already available: $name" -ForegroundColor DarkGreen
        continue
      }
      throw "Invalid or incomplete source file $target. Remove it after inspection."
    }
    $url = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/$($cycle.Year)/DataFiles/$name.xpt"
    $temp = "$target.partial"
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    Write-Host "Downloading CDC NHANES $name ..."
    try {
      Invoke-WebRequest -Uri $url -OutFile $temp -TimeoutSec 180 -MaximumRedirection 5
      if ((Get-Item -LiteralPath $temp).Length -lt 2000) { throw "Downloaded file too small" }
      # A SAS XPT file starts with the string HEADER RECORD.
      $f = [System.IO.File]::OpenRead($temp)
      try {
        $bytes = New-Object byte[] 80
        $null = $f.Read($bytes,0,$bytes.Length)
        if (-not ([Text.Encoding]::ASCII.GetString($bytes).Contains('HEADER RECORD'))) {
          throw "Not an SAS XPT file; server returned an unexpected response"
        }
      } finally { $f.Dispose() }
      Move-Item -LiteralPath $temp -Destination $target -Force
    } catch {
      Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
      throw "CDC download failed for $name : $($_.Exception.Message)"
    }
  }
}
Write-Host 'All 16 source files present (8 existing or downloaded from each cycle).' -ForegroundColor Green
