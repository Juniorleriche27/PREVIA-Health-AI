# PREVIA Health AI — Upgrade from v0.2 to v0.3

## Installation (PowerShell, Windows)

Stop your two development servers with Ctrl+C before applying the patch. Leave your existing `.venv` and `.env.local` in place.

```powershell
cd "C:\Users\DELL WORKSTATION\previa-health-ai-starter"
Expand-Archive -Path "$env:USERPROFILE\Downloads\PREVIA_v0.3_patch.zip" -DestinationPath . -Force
cd backend
& ..\.venv\Scripts\python.exe -m pytest -q
```

Expected test total: **22 passed** (one known non-blocking deprecation warning may appear).

Then in backend terminal:

```powershell
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then use a separate terminal:

```powershell
cd "C:\Users\DELL WORKSTATION\previa-health-ai-starter\frontend"
npm run dev
```

Open `http://localhost:3000/population`.

## Smoke test

1. Keep Togo, synthetic cohort 240, screening slots 45, seed 2026.
2. Click **Run population simulation**.
3. Verify four KPIs, WHO risk distribution, age distribution, synthetic area distribution and sample illustrative queue appear.
4. Change screening slots to 20: risk and age distributions must remain exactly the same, with the selected count updating to 20.
5. Visit `/` to confirm individual screening still works.

## Scientific limitations

This dashboard is an **entirely synthetic demonstration**, not real population health intelligence, a model trained on medical observations or a clinically validated prioritization system. No personal data are accepted or persisted in this module.
