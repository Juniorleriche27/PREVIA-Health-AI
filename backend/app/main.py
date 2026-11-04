"""PREVIA Health AI research demonstration API.

Includes WHO chart-cell lookups, synthetic cohorts and non-clinical
scenario comparisons. Never a substitute for clinical judgment.
"""
from enum import Enum
import os
from typing import Literal

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(
    title="PREVIA Health AI API",
    summary="Preventive screening demonstration — not a diagnostic system",
    version="0.8.0",
    redoc_url=None,
)

@app.middleware("http")
async def safety_headers(request: Request, call_next):
    """Add traceability and conservative browser protections to every response."""
    request_id = request.headers.get("X-Request-ID", "").strip()[:64] or str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a stable, non-echoing validation contract for all endpoints."""
    errors = [
        {"field": ".".join(str(part) for part in item["loc"] if part != "body"),
         "message": item["msg"], "type": item["type"]}
        for item in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "message": "Submitted data is invalid.", "details": errors},
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("PREVIA_CORS_ORIGINS", "").split(",") if x.strip()] or [
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


class ChartSex(str, Enum):
    male = "male"
    female = "female"
    not_provided = "not_provided"


class EligibilityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    age: int = Field(ge=18, le=110)
    sex_used_by_chart: ChartSex
    current_smoker: bool
    systolic_bp: float | None = Field(default=None, ge=60, le=300)
    bmi: float | None = Field(default=None, ge=10, le=80)
    known_cvd: bool
    consent_for_demo_assessment: bool


class EligibilityOutput(BaseModel):
    status: Literal[
        "consent_required", "out_of_scope", "needs_measurements", "eligible_for_reference_assessment"
    ]
    message: str
    missing_fields: list[str]
    next_step: str
    risk_score_percent: None = None
    clinical_notice: str = "Demo only. This is neither a medical diagnosis nor a validated risk assessment."
    data_storage: str = "The demo does not persist submitted screening information."


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.8.0"}


@app.post("/api/v1/screenings/eligibility", response_model=EligibilityOutput)
def eligibility(payload: EligibilityInput) -> EligibilityOutput:
    """Validate eligibility to a future WHO chart lookup, without scoring."""
    if not payload.consent_for_demo_assessment:
        return EligibilityOutput(
            status="consent_required",
            message="Explicit consent is required before processing screening inputs.",
            missing_fields=[],
            next_step="Review the notice and choose whether to consent.",
        )

    if payload.known_cvd:
        return EligibilityOutput(
            status="out_of_scope",
            message="This primary-prevention pathway is not intended for people with known cardiovascular disease.",
            missing_fields=[],
            next_step="Discuss an appropriate individualized care pathway with a qualified clinician.",
        )

    if not 40 <= payload.age <= 74:
        return EligibilityOutput(
            status="out_of_scope",
            message="This demonstration is limited to adults aged 40–74, the age range selected for the intended WHO chart pathway.",
            missing_fields=[],
            next_step="Seek age-appropriate screening guidance from a healthcare professional.",
        )

    missing: list[str] = []
    if payload.sex_used_by_chart == ChartSex.not_provided:
        missing.append("sex_used_by_chart")
    if payload.systolic_bp is None:
        missing.append("systolic_bp")
    if payload.bmi is None:
        missing.append("bmi")
    if missing:
        return EligibilityOutput(
            status="needs_measurements",
            message="Additional measurements or chart-specific inputs are required.",
            missing_fields=missing,
            next_step="Provide the missing measurements or request professional assistance.",
        )

    return EligibilityOutput(
        status="eligible_for_reference_assessment",
        message="Required inputs are present. A WHO-chart lookup can be added after source verification and clinical reference testing.",
        missing_fields=[],
        next_step="Use an appropriately validated risk chart with qualified clinical oversight; no numerical risk has been calculated.",
    )

# --- WHO 2019 chart module (regional prototype) ---
from .who_chart import COUNTRIES, REGION, SOURCE, lookup


class WHOAssessmentInput(EligibilityInput):
    country: str = Field(min_length=1, max_length=80)


class WHOAssessmentOutput(BaseModel):
    status: Literal["scored", "consent_required", "out_of_scope", "needs_measurements", "unsupported_region"]
    message: str
    risk_score_percent: int | None = None
    risk_category: str | None = None
    risk_horizon: str | None = None
    age_band: str | None = None
    bp_band: str | None = None
    bmi_band: str | None = None
    region: str | None = None
    source_url: str | None = None
    next_step: str
    clinical_notice: str = (
        "Research demonstration of the WHO 2019 regional chart; a rounded chart-bin value "
        "is NOT a diagnosis or a precise individualized prediction. Not validated for clinical use."
    )
    data_storage: str = "The demo does not persist screening information."


@app.get("/api/v1/screenings/supported-countries")
def supported_countries() -> dict:
    return {"region": REGION, "countries": list(COUNTRIES), "source_url": SOURCE}


@app.post("/api/v1/screenings/who-cvd-risk", response_model=WHOAssessmentOutput)
def who_cvd_risk(payload: WHOAssessmentInput) -> WHOAssessmentOutput:
    """Look up a discrete WHO 2019 chart cell, with region and consent safeguards."""
    existing = eligibility(payload)
    if existing.status != "eligible_for_reference_assessment":
        return WHOAssessmentOutput(
            status=existing.status,
            message=existing.message,
            next_step=existing.next_step,
        )
    if payload.country not in COUNTRIES:
        return WHOAssessmentOutput(
            status="unsupported_region",
            message="The selected country is outside the currently implemented WHO chart region.",
            next_step="Use the correct WHO regional chart; do not apply this region's numbers elsewhere.",
        )
    assert payload.systolic_bp is not None and payload.bmi is not None
    result = lookup(
        age=payload.age,
        sex=payload.sex_used_by_chart.value,
        smoker=payload.current_smoker,
        sbp=payload.systolic_bp,
        bmi=payload.bmi,
    )
    if payload.systolic_bp >= 180:
        next_step = (
            "A systolic pressure of 180 mmHg or above warrants prompt clinical assessment; "
            "seek emergency care if concerning symptoms are present."
        )
    else:
        next_step = (
            "Discuss appropriate prevention and screening options with a qualified clinician. "
            "Do not use this prototype to initiate or change treatment."
        )
    return WHOAssessmentOutput(
        status="scored",
        message="WHO 2019 non-laboratory regional chart lookup completed.",
        risk_score_percent=result.value,
        risk_category=result.risk_band,
        risk_horizon="10 years (fatal/non-fatal myocardial infarction and stroke)",
        age_band=result.age_band,
        bp_band=result.bp_band,
        bmi_band=result.bmi_band,
        region=REGION,
        source_url=SOURCE,
        next_step=next_step,
    )

# Population demonstration: seeded synthetic cohort, no health record ingestion.
from .population import router as population_router
app.include_router(population_router)

# Module 04: reproducible comparison of non-clinical selection strategies.
from .prioritization import router as prioritization_router
app.include_router(prioritization_router)

# Module 05: scientific transparency, selection integrity and synthetic robustness audit.
from .evaluation import router as evaluation_router
app.include_router(evaluation_router)

# Module 06: full PDF-text reference check and public-data input compatibility.
from .evidence import router as evidence_router
app.include_router(evidence_router)

# Module 07: stateless, synthetic preventive screening-to-review pathway.
from .pathways import router as pathways_router
app.include_router(pathways_router)
