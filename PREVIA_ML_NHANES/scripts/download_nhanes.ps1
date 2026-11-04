param([string]$Root = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$target = Join-Path $Root 'data\raw'
New-Item -ItemType Directory -Path $target -Force | Out-Null
$files = @('DEMO_J', 'BMX_J', 'BPX_J', 'SMQ_J', 'DIQ_J', 'GHB_J')
foreach ($file in $files) {
  $path = Join-Path $target "$file.xpt"
  if ((Test-Path $path) -and ((Get-Item $path).Length -gt 2000)) {
    Write-Host "Already present: $file" -ForegroundColor DarkGreen
    continue
  }
  $url = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/$file.xpt"
  Write-Host "CDC download: $file"
  $temporary = "$path.download"
  try {
    Invoke-WebRequest -Uri $url -OutFile $temporary -MaximumRedirection 5 -TimeoutSec 90
    if ((Get-Item $temporary).Length -lt 2000) { throw "Unexpectedly small CDC file" }
    Move-Item $temporary $path -Force
  } catch {
    Remove-Item $temporary -Force -ErrorAction SilentlyContinue
    throw "CDC file $file could not be obtained. $_"
  }
}
Write-Host 'Official NHANES files downloaded. Source XPT retained locally.' -ForegroundColor Green
