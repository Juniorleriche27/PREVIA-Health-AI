"""PREVIA AI sidecar: isolated XAI + retrieval-augmented documentary assistant."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from .ml_xai import ModelNotAvailable, explain, load_model
from .rag import answer, sources
from .providers import ProviderError, providers_public

MODULE_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.getenv("PREVIA_PROJECT_ROOT", str(MODULE_ROOT.parent))).resolve()
CORPUS = MODULE_ROOT / "knowledge" / "curated_sources.json"

DEFAULT_ORIGINS = [
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:3001", "http://127.0.0.1:3001",
]
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("PREVIA_CORS_ORIGINS", "").split(",") if x.strip()] or DEFAULT_ORIGINS

app = FastAPI(title="PREVIA AI Research Sidecar", version="1.1.0", redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_credentials=False, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type", "X-Request-ID"])


@app.middleware("http")
async def privacy_headers(req: Request, next_handler):
    request_id = req.headers.get("X-Request-ID", "").strip()[:64] or str(uuid4())
    response = await next_handler(req)
    response.headers["X-Request-ID"] = request_id
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(req: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"field": ".".join(str(x) for x in e["loc"] if x != "body"),
                "message": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={
        "error": "validation_error", "message": "Submitted data is invalid.", "details": details,
    })


class XAIInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    confirm_fictitious_demo: Literal[True]
    age: int = Field(ge=40, le=74)
    sex: Literal["male", "female"]
    bmi: float | None = Field(default=None, ge=12, le=75)
    sbp: float | None = Field(default=None, ge=70, le=260)
    smoking: Literal["never", "former", "current", "unknown"] = "never"
    waist_cm: float | None = Field(default=None, ge=40, le=220)
    hypertension_history: Literal["yes", "no", "unknown"] = "unknown"
    high_cholesterol_history: Literal["yes", "no", "unknown"] = "unknown"
    leisure_activity: Literal["yes", "no", "unknown"] = "unknown"
    work_activity: Literal["yes", "no", "unknown"] = "unknown"


class ConversationTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=700)


class RAGInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=5, max_length=450)
    provider_id: str = Field(default="extractive", min_length=2, max_length=42)
    model_id: str | None = Field(default=None, max_length=160)
    history: list[ConversationTurn] = Field(default_factory=list, max_length=6)
    language: Literal["fr", "en"] = "fr"


@app.get("/api/v1/ai/health")
def health() -> dict:
    try:
        _, _, frozen, _, _ = load_model(ROOT)
        model_status = "available"
        winner = frozen.get("winner")
    except (ModelNotAvailable, ValueError, OSError, ImportError):
        model_status = "unavailable"
        winner = None
    return {"status": "ok", "version": "1.1.0", "model_status": model_status,
            "model_name": winner, "rag_mode_requested": "provider_selection_or_extractive",
            "sources": len(sources(CORPUS)), "clinical_validation": "not_performed"}


@app.get("/api/v1/ai/live")
def live() -> dict[str, str]:
    """Cheap process liveness probe; readiness details remain on /health."""
    return {"status": "ok"}


@app.get("/api/v1/ai/providers")
def llm_providers() -> dict:
    try:
        return {"providers": providers_public(), "default": "extractive", "message": "Aucun fournisseur LLM n’est utilisé automatiquement."}
    except ProviderError:
        raise HTTPException(status_code=503, detail="Configuration des fournisseurs invalide.") from None


@app.get("/api/v1/ai/sources")
def indexed_sources() -> dict:
    return {"sources": sources(CORPUS), "method": "Curated WHO/CDC/NIDDK summaries; local TF-IDF retrieval."}


@app.post("/api/v1/ai/explain")
def xai(payload: XAIInput) -> dict:
    try:
        return explain(ROOT, payload.model_dump(exclude={"confirm_fictitious_demo"}))
    except ModelNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="Incompatible model or inputs for XAI; check local research artifact and schema.") from exc


@app.post("/api/v1/ai/ask")
def rag_ask(payload: RAGInput) -> dict:
    try:
        return answer(CORPUS, payload.question, payload.provider_id, payload.model_id, [turn.model_dump() for turn in payload.history], payload.language)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
