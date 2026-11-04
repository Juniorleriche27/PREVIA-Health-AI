# PREVIA Health AI — Technical release v0.8

## Purpose and boundary

PREVIA demonstrates a transparent prevention journey from screening inputs to population planning and a fictional follow-up workflow. Numerical WHO outputs are discrete values printed in a regional reference chart. They are not diagnoses or continuously estimated individual probabilities. Synthetic funnel conversion ratios are invented interface fixtures, not observed outcomes.

No real-world clinical use is authorized. Moving beyond a hackathon research demo requires clinical governance, ethics and privacy review, an independently verified chart transcription, prospective validation, security testing, regulated-device assessment where applicable and country-specific operational design.

## Architecture

```text
Browser :3001 (Next.js, static/client UI)
       │ JSON over local HTTP
       ▼
FastAPI :8765
  ├─ eligibility + WHO discrete lookup
  ├─ deterministic synthetic cohort
  ├─ allocation strategy comparison
  ├─ scientific/source audit
  ├─ aggregate public-data evidence status
  └─ stateless fictional pathway replay
```

There is deliberately no database. Inputs and workflow events live only for the duration of a request or in browser component state. The optional NHANES pipeline writes aggregate completeness output locally and is not called by the web application.

## Reliability and security controls

- Pydantic bounds, strict enumerations and forbidden extra request fields reject unexpected or unbounded input.
- Cross-field capacity validation prevents selecting more profiles than the cohort contains.
- CORS is restricted to documented local origins and GET/POST methods.
- Every response uses `Cache-Control: no-store`, clickjacking/MIME/referrer protections and an `X-Request-ID` correlation value.
- Validation errors use a stable envelope and do not echo submitted values.
- Workflow events are capped at 200 and validated against allowed transitions.
- The launcher only stops a port owner whose command line belongs to this project.

This is defense in depth for a local demo, not an Internet production security certification. There is no authentication or rate limiting because no multi-user deployment is supplied.

## Scientific traceability

- Primary chart: WHO 2019 non-laboratory CVD risk chart, Western Sub-Saharan Africa.
- Implemented scope: ages 40–74 and the 19 countries assigned to that chart region.
- Verification: 700/700 digitized cells compared with the official PDF text layer plus 28 separate anchor fixtures.
- Limitation: text-layer agreement is not an independent visual or clinician-certified audit and does not validate calibration, discrimination, outcomes or benefit.
- NHANES: public US survey data is used only for aggregate input-availability analysis, never as evidence of performance in the target region.

## Release verification

Run `.\scripts\previa.ps1 verify` from the repository root. It runs all backend tests, the complete WHO text-layer comparison and the optimized Next.js build. Manual smoke checks should cover all six pages, narrow-screen navigation, invalid values, API-unavailable messages and JSON exports.

## Deployment conditions

The supplied configuration is local-only. For an external demonstration, place both services behind HTTPS, restrict origins to the exact hostname, add authentication if access is non-public, apply edge rate and request-size limits, protect API documentation, centralize sanitized logs and complete a data-protection threat model. Never add patient data to this prototype.

## Recommended jury demonstration (6–8 minutes)

1. Start with `.\scripts\previa.ps1 start`, show `/health` version `0.8.0`, then open the application.
2. On **Individual screening**, explain consent and scope gates. Run a fictional Togo profile and emphasize that the result is a WHO reference cell, not a diagnosis.
3. On **Population intelligence**, keep seed 2026. Show reproducibility and change capacity without claiming prevalence.
4. On **Strategy comparison**, contrast the three rules and explain capture/yield and subgroup-gap trade-offs without recommending clinical use.
5. On **Scientific audit** and **External evidence**, show the 700-cell check, sensitivity runs and explicit validation gaps.
6. On **Prevention pathway**, replay one fictional transition and export JSON. State that PREVIA sends no message and books no appointment.
7. Close with the stateless privacy architecture and work required before clinical deployment.

## Known limitations

- One WHO region and one non-laboratory chart only; English-only interface.
- No real cohort, outcomes, external validation or health-economic evaluation.
- No persistent workflow, interoperability, identity, authorization or audit-log service.
- No end-to-end browser automation suite; validation combines API integration tests, production compilation and manual browser smoke checks.
