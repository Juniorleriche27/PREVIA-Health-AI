# PREVIA v0.4 — Terminal-only upgrade for an existing Windows installation

1. Stop the previous PREVIA servers with `Ctrl+C` in their two terminals. Do not stop unrelated projects using other ports.
2. Download `PREVIA_v0.4_patch.zip` into your Windows Downloads folder.
3. In PowerShell (any working directory), paste:

```powershell
$root = 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
$archive = Join-Path $env:USERPROFILE 'Downloads\PREVIA_v0.4_patch.zip'
if (-not (Test-Path $archive)) { throw "Missing patch ZIP: $archive" }
if (-not (Test-Path (Join-Path $root '.venv\Scripts\python.exe'))) { throw "Missing project virtual environment" }
Expand-Archive -Path $archive -DestinationPath $root -Force
Set-Location (Join-Path $root 'backend')
& (Join-Path $root '.venv\Scripts\python.exe') -m pytest -q
```

Expected: **39 passed** in the Linux reference environment; on Windows a harmless Starlette test-client deprecation warning can appear.

4. Start the backend in PowerShell terminal A:

```powershell
cd 'C:\Users\DELL WORKSTATION\previa-health-ai-starter\backend'
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

5. In PowerShell terminal B:

```powershell
cd 'C:\Users\DELL WORKSTATION\previa-health-ai-starter\frontend'
# Preserve existing local config and ensure it points at the running FastAPI service.
$envFile = '.env.local'
$contents = if (Test-Path $envFile) { Get-Content $envFile -Raw } else { '' }
$contents = [regex]::Replace($contents, '(?m)^NEXT_PUBLIC_API_URL=.*(?:\r?\n)?', '')
$contents = $contents.TrimEnd() + "`nNEXT_PUBLIC_API_URL=http://127.0.0.1:8765`n"
[System.IO.File]::WriteAllText((Join-Path (Get-Location).Path $envFile), $contents, (New-Object System.Text.UTF8Encoding($false)))
npm run dev -- --port 3001
```

6. Open: **http://localhost:3001/prioritization**. Use defaults Togo, 240 synthetic profiles, 45 slots and seed 2026; click `Compare three strategies`, then select each comparison card. 

For a pure API smoke test (backend must be running):

```powershell
$payload = @{country='Togo'; cohort_size=240; outreach_capacity=45; seed=2026} | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8765/api/v1/prioritization/compare -Method POST -Body $payload -ContentType 'application/json' | Select-Object cohort_size, outreach_capacity, higher_reference_in_cohort
```

Note: frontend `npm run build` should be run locally to verify full Next.js compilation: this environment did not successfully install npm dependencies. No files outside the local PREVIA project need to be edited.
