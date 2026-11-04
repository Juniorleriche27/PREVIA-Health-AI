# PREVIA Health AI — Production readiness and jury guide

## Operational scope

PREVIA runs as three independently monitored services: the FastAPI prevention API on 8765, the Next.js interface on 3001 and the isolated ML/XAI/RAG sidecar on 8766. This repository is technically prepared for deployment; no public production deployment has been performed.

The scientific components remain distinct:

- WHO output is a discrete 2019 regional chart cell, not an ML prediction.
- Random Forest output is an exploratory association with contemporaneously measured HbA1c ≥5.7% in US NHANES data, not future diabetes or cardiovascular risk. External intercycle results are ROC-AUC 0.668 and PR-AUC 0.583.
- SHAP explains fitted-model arithmetic, not biological causality.
- RAG uses curated WHO, CDC and NIDDK summaries. Extractive mode is always available; LLM output is accepted only when it cites retrieved source IDs.

## Multi-provider architecture

No provider is configured or selected by default. The browser receives only public provider metadata and readiness state; keys remain server-side. Supported protocols are OpenAI-compatible, Anthropic Messages, Gemini generateContent and Cohere Chat v2. Registered providers have bounded timeouts (2–60 seconds), bounded output (64–1200 tokens), explicit model selection, HTTPS enforcement outside localhost and deterministic fallback to extractive retrieval.

Use `scripts/configure_previa_llm.ps1` on Windows or mount a server-only provider JSON and inject key variables through the deployment secret manager. Never expose a key through a `NEXT_PUBLIC_*` variable.

## Windows commands

```powershell
.\scripts\previa_full.ps1 start
.\scripts\previa_full.ps1 start -Production
.\scripts\previa_full.ps1 status
.\scripts\previa_full.ps1 restart
.\scripts\previa_full.ps1 diagnose
.\scripts\previa_full.ps1 verify
.\scripts\previa_full.ps1 stop
```

The verification gate runs backend regressions, AI/provider/RAG/SHAP tests, ML protocol and external-validation tests, the Next.js production build and npm security audit.

## Container deployment preparation

`compose.yaml` and three Dockerfiles provide a Linux-oriented baseline. By default, Compose binds all ports to loopback and leaves the provider registry empty. Before external deployment:

1. Terminate TLS at a hardened reverse proxy and expose only required HTTPS routes.
2. Set exact `PREVIA_CORS_ORIGINS`; never use wildcard origins.
3. Inject provider configuration and keys through platform secrets.
4. Add authentication, authorization, rate limiting, body-size limits and centralized sanitized logging.
5. Pin and scan images, produce an SBOM, test backup and rollback.
6. Complete clinical, regulatory, ethics, privacy and penetration reviews before processing non-synthetic data.

The Compose file is a reproducible technical preview, not a clinically authorized production stack.

## Jury demonstration (8–10 minutes)

1. Show both health endpoints and explain the three-service separation.
2. Run a fictional individual WHO screening; distinguish chart binning from diagnosis.
3. Explore the seeded synthetic population and capacity constraint.
4. Compare the three allocation strategies and subgroup selection gaps.
5. Show the 700-cell WHO source check and aggregate NHANES limitations.
6. Replay one fictional pathway transition; emphasize that no message or appointment is created.
7. Open `/ai`, explain a fictional profile and read the SHAP legend: contributions are model mechanics, not causes.
8. Ask “Que signifie une HbA1c de 5,7 % ?” in extractive mode and open an official citation.
9. Show the empty provider state. Explain that invalid citations or provider failure trigger extractive fallback.
10. Close with external performance, privacy-by-design and validation required before real-world use.

## Known open limits

- No clinical validation, prospective study or target-region calibration.
- No authentication, tenant isolation or durable clinical audit trail.
- Curated summaries are not a live evidence-synthesis pipeline.
- Citation enforcement reduces but cannot eliminate LLM hallucination risk.
- HTTPS, observability backend and disaster recovery are prepared conceptually but not deployed.
