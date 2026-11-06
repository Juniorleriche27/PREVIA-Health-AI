# PREVIA Health AI — production-readiness release

PREVIA is a research demonstration for the **Future Health Digital Innovation Challenge 2026**, track *Population Health — Precision Prevention and Screening*. It combines an educational WHO 2019 cardiovascular chart lookup with deterministic synthetic population, prioritization, scientific-audit and prevention-pathway simulations.

> PREVIA is not a medical device, diagnosis, clinical triage tool, referral system or treatment recommendation. The web application accepts no direct identifiers, stores no submitted screening data and uses synthetic profiles plus aggregate public research data only.

## Quick start (Windows 11 / PowerShell)

```powershell
.\scripts\previa_full.ps1 start       # backend 8765 + frontend 3001 + AI 8766
.\scripts\previa_full.ps1 status
.\scripts\previa_full.ps1 restart
.\scripts\previa_full.ps1 stop
.\scripts\previa_full.ps1 diagnose
.\scripts\previa_full.ps1 verify
```

The launchers refuse to terminate unrelated processes occupying ports 8765, 8766 or 3001. For a production-style local run, verify first and use `.\scripts\previa_full.ps1 start -Production`.

The unified launcher intentionally runs FastAPI without the auto-reloader because Windows can orphan reload workers. After code changes, use `.\scripts\previa.ps1 restart`.

Open the application at http://localhost:3001, including `/ai`. Health endpoints are http://127.0.0.1:8765/health and http://127.0.0.1:8766/api/v1/ai/health.

## Product modules

1. `/` — screening readiness and discrete WHO chart-cell lookup.
2. `/population` — deterministic synthetic cohort and capacity scenario.
3. `/prioritization` — comparison of three illustrative allocation rules.
4. `/evaluation` — source checks, integrity checks and sensitivity analysis.
5. `/evidence` — WHO transcription provenance and optional NHANES input completeness.
6. `/pathways` — stateless, fictional screening-to-review workflow replay.
7. `/ai` — frozen NHANES Random Forest explanations with SHAP and source-grounded documentary RAG.

## Architecture and quality

- Backend: FastAPI, Pydantic v2, deterministic Python calculation modules.
- Frontend: Next.js 15, React 19 and TypeScript.
- Scientific source: WHO 2019 non-laboratory chart for Western Sub-Saharan Africa; 700 cells cross-checked against the official PDF text layer.
- Data policy: no database, authentication, cookies, analytics or persistence in this prototype.
- Release gate: backend unit/integration/API regressions, WHO reference cross-check, TypeScript validation and optimized Next.js build.

See [docs/PRODUCTION_READINESS_V10.md](docs/PRODUCTION_READINESS_V10.md) for architecture, security, deployment, limitations and the jury demonstration script.

The challenge-ready, bilingual quantitative evidence package is available in [docs/health-impact/README.md](docs/health-impact/README.md). It includes reproducible synthetic experiments, CSV tables, SVG charts, scientific limitations, jury briefs and a future-pilot measurement protocol. Regenerate it with:

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_health_impact.py
```

## Fresh dependency installation

```powershell
py -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Push-Location .\frontend
npm ci
Pop-Location
.\scripts\previa.ps1 verify
```

Optional NHANES aggregate preparation is documented in `docs/EXTERNAL_EVIDENCE_V06.md`; it is not required to run PREVIA.
