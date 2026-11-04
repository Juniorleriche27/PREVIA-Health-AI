from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
BASE = {
    "age": 52,
    "sex_used_by_chart": "female",
    "current_smoker": False,
    "systolic_bp": 128,
    "bmi": 26.1,
    "known_cvd": False,
    "consent_for_demo_assessment": True,
}


def check(changes, status):
    r = client.post("/api/v1/screenings/eligibility", json={**BASE, **changes})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == status
    assert data["risk_score_percent"] is None
    return data


def test_health():
    response = client.get("/health", headers={"X-Request-ID": "test-trace"})
    assert response.json() == {"status": "ok", "version": "0.8.0"}
    assert response.headers["x-request-id"] == "test-trace"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"


def test_eligible_inputs_are_not_claimed_as_medical_score():
    check({}, "eligible_for_reference_assessment")


def test_consent_gate():
    check({"consent_for_demo_assessment": False}, "consent_required")


def test_age_exclusion():
    check({"age": 31}, "out_of_scope")
    check({"age": 80}, "out_of_scope")


def test_known_disease_exclusion():
    check({"known_cvd": True}, "out_of_scope")


def test_missing_measurements():
    data = check({"bmi": None, "systolic_bp": None}, "needs_measurements")
    assert set(data["missing_fields"]) == {"bmi", "systolic_bp"}


def test_missing_chart_input():
    check({"sex_used_by_chart": "not_provided"}, "needs_measurements")


def test_invalid_inputs_are_rejected():
    r = client.post("/api/v1/screenings/eligibility", json={**BASE, "systolic_bp": -8})
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"
    assert r.json()["details"][0]["field"] == "systolic_bp"
    assert "input" not in r.json()["details"][0]


def test_extra_fields_rejected():
    r = client.post("/api/v1/screenings/eligibility", json={**BASE, "name": "Person"})
    assert r.status_code == 422
