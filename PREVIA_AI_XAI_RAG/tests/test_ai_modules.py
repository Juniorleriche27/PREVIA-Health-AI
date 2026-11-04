"""Executable contract tests; synthetic data only, never NHANES participant records."""
from __future__ import annotations

import json
import httpx
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ai_service import ml_xai, rag, providers
from ai_service.app import app, CORPUS


@pytest.fixture
def synthetic_local_model(tmp_path):
    rng = np.random.default_rng(2026)
    n = 150
    records = pd.DataFrame({
        "age": rng.integers(40, 75, n),
        "sex": rng.choice(["female", "male"], n),
        "bmi": rng.uniform(19, 42, n),
        "sbp": rng.uniform(95, 180, n),
        "smoking": rng.choice(["never", "current", "former"], n),
        "waist_cm": rng.uniform(75, 130, n),
        "hypertension_history": rng.choice(["yes", "no"], n),
        "high_cholesterol_history": rng.choice(["yes", "no"], n),
        "leisure_activity": rng.choice(["yes", "no"], n),
        "work_activity": rng.choice(["yes", "no"], n),
    })
    records.loc[[2,5,10], "bmi"] = np.nan
    records.loc[[4,7], "hypertension_history"] = np.nan
    y = (records.age + records.bmi.fillna(27) * 2 + rng.normal(0, 20, n) > 117).astype(int)
    numeric = ["age", "bmi", "sbp", "waist_cm"]
    cat = [c for c in records.columns if c not in numeric]
    prep = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True))]), numeric),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                           ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cat),
    ])
    pipeline = Pipeline([("prep", prep), ("model", RandomForestClassifier(n_estimators=40, max_depth=6, random_state=2026))])
    pipeline.fit(records[ml_xai.FEATURES], y)
    out = tmp_path / "PREVIA_ML_Validation_Externe" / "results" / "cross_cycle"
    out.mkdir(parents=True)
    joblib.dump(pipeline, out / "PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib")
    (out / "DEVELOPMENT_FROZEN.json").write_text(json.dumps({
        "winner": "extended_random_forest", "candidate_decisions": {
            "extended_random_forest": {"features": ml_xai.FEATURES, "oof_screening_threshold": .4147}},
        "selection_sha256": "synthetic-unit-test",
    }))
    (out / "SCORES_VALIDATION_EXTERNE.json").write_text(json.dumps({"external": {
        "winner_scores": {"roc_auc": 0.67, "pr_auc_ap": 0.59}}}))
    yield tmp_path
    ml_xai._load_cached.cache_clear()


FAKE = {"age": 53, "sex": "female", "bmi": 27.5, "sbp": 134, "smoking": "never", "waist_cm": 91,
        "hypertension_history": "yes", "high_cholesterol_history": "unknown",
        "leisure_activity": "no", "work_activity": "yes"}


def test_shap_sums_back_to_model_output(synthetic_local_model):
    report = ml_xai.explain(synthetic_local_model, FAKE)
    impacts = sum(item["impact_percentage_points"] for item in report["contributions"])
    assert abs(impacts + report["shap_baseline_percent"] - report["probability_unvalidated_percent"]) < 0.02
    assert report["shap_additivity_error"] < 1e-5
    assert len(report["contributions"]) == 10
    assert report["external_reference_metrics"]["roc_auc"] == .67


def test_unknown_category_and_missing_numerical(synthetic_local_model):
    report = ml_xai.explain(synthetic_local_model, {**FAKE, "bmi": None, "high_cholesterol_history": "unknown"})
    assert 0 <= report["probability_unvalidated_percent"] <= 100
    assert report["shap_additivity_error"] < 1e-5


def test_model_unavailable_must_not_invent_scores(tmp_path):
    with pytest.raises(ml_xai.ModelNotAvailable):
        ml_xai.explain(tmp_path, FAKE)


def test_form_schema_rejects_real_unverified_input_or_out_of_range():
    client = TestClient(app)
    out = client.post("/api/v1/ai/explain", json={**FAKE, "confirm_fictitious_demo": True, "age": 35})
    assert out.status_code == 422
    out = client.post("/api/v1/ai/explain", json={**FAKE, "confirm_fictitious_demo": False})
    assert out.status_code == 422
    out = client.post("/api/v1/ai/explain", json={**FAKE, "confirm_fictitious_demo": True, "secret":"hello"})
    assert out.status_code == 422


def test_rag_sources_are_official_and_retrievable():
    s = rag.sources(CORPUS)
    assert len(s) >= 8
    matches = rag.retrieve(CORPUS, "Que signifie une HbA1c de 5,7 % ?")
    assert matches and any(x["id"].startswith("CDC") for x in matches)
    assert all(x["url"].startswith("https://") for x in matches)


def test_rag_fallback_has_real_citations(monkeypatch):
    monkeypatch.setenv("PREVIA_RAG_MODE", "extractive")
    out = rag.answer(CORPUS, "Quelle est la plage de l'HbA1c pour le prédiabète ?")
    assert out["mode"] == "retrieval_extractif"
    assert out["sources"]
    assert any("[" + x["id"] + "]" in out["answer"] for x in out["sources"])


def test_rag_is_bilingual_and_keeps_official_citations():
    english = rag.answer(CORPUS, "What does an A1C of 5.7% mean?", language="en")
    french = rag.answer(CORPUS, "Que signifie une HbA1c de 5,7 % ?", language="fr")
    assert english["language"] == "en" and "Documentary synthesis" in english["answer"]
    assert french["language"] == "fr" and "Synthèse documentaire" in french["answer"]
    assert english["sources"] and french["sources"]
    assert all(source["title"] for source in english["sources"])


def test_ui_language_controls_answer_not_question_language():
    result = rag.answer(CORPUS, "Que signifie une HbA1c de 5,7 % ?", language="en")
    assert result["language"] == "en"
    assert "Documentary synthesis" in result["answer"]


def test_api_validates_language_and_returns_requested_locale():
    client = TestClient(app)
    good = client.post("/api/v1/ai/ask", json={"question": "What is cardiovascular risk?", "language": "en"})
    assert good.status_code == 200 and good.json()["language"] == "en"
    assert client.post("/api/v1/ai/ask", json={"question": "What is cardiovascular risk?", "language": "de"}).status_code == 422


def test_unrelated_questions_abstain():
    out = rag.answer(CORPUS, "galactic neutron rocket teleportation quantum spaceship")
    assert out["mode"] == "abstention"
    assert out["sources"] == []


def test_rag_refuses_personalized_dosage():
    out = rag.answer(CORPUS, "Quelle dose d'insuline pour mon diabète ?")
    assert out["mode"] == "safety_boundary"


def test_provider_failure_falls_back_to_citations(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda *a, **kw: (_ for _ in ()).throw(providers.ProviderError("unavailable")))
    out = rag.answer(CORPUS, "HbA1c et dépistage du diabète", provider_id="provider_fictif")
    assert out["mode"] == "retrieval_extractif"
    assert out["sources"] and out["fallback_reason"]


def test_provider_no_implicit_choice(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda *a, **kw: pytest.fail("Provider called without consent"))
    out = rag.answer(CORPUS, "HbA1c et dépistage du diabète")
    assert out["mode"] == "retrieval_extractif" and out["provider"] is None


def test_api_source_access_and_privacy_headers():
    client = TestClient(app)
    response = client.get("/api/v1/ai/sources")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]
    assert len(response.json()["sources"]) >= 8
    bad = client.post("/api/v1/ai/ask", json={"question": "abc"})
    assert bad.status_code == 422
    assert bad.json()["error"] == "validation_error"
    assert "input" not in bad.json()["details"][0]
    good = client.post("/api/v1/ai/ask", json={"question": "Que signifie HbA1c ?"})
    assert good.status_code == 200
    assert good.json()["sources"]


def test_http_xai_with_synthetic_fitted_artifact(synthetic_local_model, monkeypatch):
    import importlib
    api_module = importlib.import_module("ai_service.app")
    monkeypatch.setattr(api_module, "ROOT", synthetic_local_model)
    client = TestClient(api_module.app)
    res = client.post("/api/v1/ai/explain", json={**FAKE, "confirm_fictitious_demo": True})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["shap_additivity_error"] < 1e-5
    assert body["external_reference_metrics"]["pr_auc_ap"] == .59


def test_http_xai_without_artifact_gives_503(tmp_path, monkeypatch):
    import importlib
    api_module = importlib.import_module("ai_service.app")
    monkeypatch.setattr(api_module, "ROOT", tmp_path)
    client = TestClient(api_module.app)
    res = client.post("/api/v1/ai/explain", json={**FAKE, "confirm_fictitious_demo": True})
    assert res.status_code == 503
    assert "absent" in res.json()["detail"].lower()


def test_llm_mode_only_when_generation_has_verified_citations(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda *a, **kw: ("Réponse documentée [CDC-A1C-2024]", "test-model"))
    result = rag.answer(CORPUS, "Quelle est la plage de l'HbA1c pour le prédiabète ?", provider_id="config_test")
    assert result["mode"] == "llm_grounded"
    assert result["provider"] == "config_test" and result["model"] == "test-model"


def test_unsupported_citation_rejected(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda *a, **kw: ("Mauvaise source [FAKE-ID]", "test-model"))
    result = rag.answer(CORPUS, "Quelle est la plage de l'HbA1c pour le prédiabète ?", provider_id="config_test")
    assert result["mode"] == "retrieval_extractif"
    assert result["fallback_reason"]


def test_provider_registry_is_empty_without_config(monkeypatch, tmp_path):
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(tmp_path / "nonexistent.json"))
    monkeypatch.delenv("PREVIA_RAG_MODE", raising=False)
    assert providers.providers_public() == []
    client = TestClient(app)
    result = client.get("/api/v1/ai/providers")
    assert result.status_code == 200 and result.json()["providers"] == []
    assert result.json()["default"] == "extractive"


def test_multi_provider_openai_compatible_mock(monkeypatch, tmp_path):
    file = tmp_path / "providers.local.json"
    file.write_text(json.dumps({"providers": [{"id":"example", "adapter":"openai_compatible", "base_url":"https://api.example.com/v1", "default_model":"model-1", "api_key_env":"EXAMPLE_PREVIA_KEY"}]}))
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(file))
    monkeypatch.setenv("EXAMPLE_PREVIA_KEY", "secret-one")
    calls = []
    def mock_post(self, url, **kw):
        calls.append((url, kw))
        request = httpx.Request("POST", url)
        return httpx.Response(200, request=request, json={"choices":[{"message":{"content":"Réponse [CDC-A1C-2024]"}}]})
    monkeypatch.setattr(httpx.Client, "post", mock_post)
    text, selected = providers.generate("example", "chosen-model", "system", "user")
    assert selected == "chosen-model" and "[CDC-A1C-2024]" in text
    assert calls[0][0] == "https://api.example.com/v1/chat/completions"
    assert calls[0][1]["json"]["model"] == "chosen-model"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer secret-one"
    exposed = providers.providers_public()
    assert exposed[0]["ready"] and "secret-one" not in str(exposed)


def test_native_provider_adapters_mock(monkeypatch, tmp_path):
    data = {"providers": []}
    for adapter in ("anthropic", "gemini", "cohere"):
        data["providers"].append({"id": adapter, "adapter": adapter, "default_model": "test-model", "api_key_env": adapter.upper() + "_SECRET"})
        monkeypatch.setenv(adapter.upper() + "_SECRET", "test-secret")
    file=tmp_path / "providers.json"
    file.write_text(json.dumps(data))
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(file))
    responses = {
        "anthropic": {"content": [{"type": "text", "text": "Claude [WHO-CVD-2019]"}]},
        "gemini": {"candidates": [{"content": {"parts": [{"text": "Gemini [WHO-CVD-2019]"}]}}]},
        "cohere": {"message": {"content": [{"type": "text", "text": "Cohere [WHO-CVD-2019]"}]}}
    }
    def mock_post(self, url, **kw):
        adapter = "anthropic" if "anthropic" in url else "gemini" if "googleapis" in url else "cohere"
        return httpx.Response(200, request=httpx.Request("POST", url), json=responses[adapter])
    monkeypatch.setattr(httpx.Client, "post", mock_post)
    for adapter in responses:
        result, model = providers.generate(adapter, None, "System", "User")
        assert "[WHO-CVD-2019]" in result and model == "test-model"


def test_knowlia_public_adapter_mock(monkeypatch, tmp_path):
    file = tmp_path / "providers.json"
    file.write_text(json.dumps({"providers": [{
        "id": "knowlia", "label": "Knowlia", "adapter": "knowlia",
        "base_url": "http://prod_knowlia:8080", "tenant_id": "previa-health-ai",
        "default_model": "command-a-03-2025", "api_key_env": "PREVIA_KNOWLIA_API_KEY",
    }]}))
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(file))
    monkeypatch.setenv("PREVIA_KNOWLIA_API_KEY", "server-side-secret")
    calls = []
    def mock_post(self, url, **kw):
        calls.append((url, kw))
        return httpx.Response(200, request=httpx.Request("POST", url), json={
            "ok": True, "request_id": "test", "data": {
                "content": "Grounded answer 【CDC-A1C-2024】", "provider": "groq",
                "model": "routed-model", "usage": {}, "sources": [],
            },
        })
    monkeypatch.setattr(httpx.Client, "post", mock_post)
    text, model = providers.generate("knowlia", None, "System", "Question")
    assert text == "Grounded answer [CDC-A1C-2024]" and model == "routed-model"
    assert calls[0][0] == "http://prod_knowlia:8080/public/v1/generate"
    assert calls[0][1]["headers"] == {"X-Knowlia-Api-Key": "server-side-secret"}
    assert calls[0][1]["json"]["tenant_id"] == "previa-health-ai"
    assert calls[0][1]["json"]["web_access"] == "off"


def test_reject_remote_http_endpoint_and_unregistered_provider(monkeypatch, tmp_path):
    file=tmp_path / "providers.json"
    file.write_text(json.dumps({"providers": [{"id":"bad", "adapter":"openai_compatible", "base_url":"http://insecure.example/v1", "default_model":"test-model"}]}))
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(file))
    with pytest.raises(providers.ProviderError):
        providers.providers_public()
    file.write_text(json.dumps({"providers": []}))
    with pytest.raises(providers.ProviderError):
        providers.generate("unregistered", "model", "system", "user")


def test_provider_operational_limits_are_validated(monkeypatch, tmp_path):
    file = tmp_path / "providers.json"
    monkeypatch.setenv("PREVIA_LLM_CONFIG_FILE", str(file))
    base = {"id":"local", "adapter":"openai_compatible", "base_url":"http://127.0.0.1:11434/v1", "default_model":"demo"}
    file.write_text(json.dumps({"providers": [{**base, "timeout_seconds": 1}]}))
    with pytest.raises(providers.ProviderError):
        providers.providers_public()
    file.write_text(json.dumps({"providers": [{**base, "max_tokens": 5000}]}))
    with pytest.raises(providers.ProviderError):
        providers.providers_public()


def test_public_api_history_is_bounded():
    client = TestClient(app)
    long_history = [{"role":"user","content":"hello"}]*7
    assert client.post("/api/v1/ai/ask", json={"question":"HbA1c et diabète", "history":long_history}).status_code == 422
    assert client.post("/api/v1/ai/ask", json={"question":"HbA1c et diabète", "history":[{"role":"admin","content":"hello"}]}).status_code == 422
