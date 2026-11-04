from fastapi.testclient import TestClient
from app.main import app
from app.who_chart import CHART, COUNTRIES, lookup

client = TestClient(app)
BASE = {
    "age": 52, "sex_used_by_chart": "female", "current_smoker": False,
    "systolic_bp": 128, "bmi": 26.1, "known_cvd": False,
    "consent_for_demo_assessment": True, "country": "Togo",
}


def test_chart_shape():
    # 7 age groups x 4 sex/smoking groups x 5 BP x 5 BMI = 700 chart cells
    assert sum(len(row) for quadrants in CHART.values() for grid in quadrants.values() for row in grid) == 700


def test_example_female_reference_cell():
    r = client.post('/api/v1/screenings/who-cvd-risk', json=BASE)
    assert r.status_code == 200
    j = r.json()
    assert j['status'] == 'scored'
    assert j['risk_score_percent'] == 3
    assert j['age_band'] == '50–54'
    assert j['bp_band'] == '120–139'
    assert j['bmi_band'] == '25–<30'
    assert j['risk_category'] == '<5%'
    assert j['region'] == 'Western Sub-Saharan Africa'


def test_reference_extremes_from_original_who_chart():
    assert lookup(74, 'male', True, 185, 39).value == 38
    assert lookup(40, 'female', False, 110, 19).value == 1
    assert lookup(55, 'male', False, 145, 32).value == 8


def test_eligibility_and_consent_gates():
    for changed, expected in [
        ({'consent_for_demo_assessment': False}, 'consent_required'),
        ({'known_cvd': True}, 'out_of_scope'),
        ({'age': 24}, 'out_of_scope'),
        ({'bmi': None}, 'needs_measurements'),
    ]:
        r = client.post('/api/v1/screenings/who-cvd-risk', json={**BASE, **changed})
        assert r.status_code == 200
        assert r.json()['status'] == expected
        assert r.json()['risk_score_percent'] is None


def test_region_check_and_no_wrong_regional_scoring():
    r = client.post('/api/v1/screenings/who-cvd-risk', json={**BASE, 'country': 'United States'})
    assert r.status_code == 200
    assert r.json()['status'] == 'unsupported_region'
    assert r.json()['risk_score_percent'] is None


def test_supported_countries_and_togo():
    r = client.get('/api/v1/screenings/supported-countries')
    assert r.status_code == 200
    assert 'Togo' in r.json()['countries']
    assert 'United States' not in r.json()['countries']
    assert len(r.json()['countries']) == len(COUNTRIES)


def test_grid_boundaries():
    assert lookup(54, 'female', False, 139, 29.9).value == 3
    assert lookup(54, 'female', False, 140, 30).value == 4
    assert lookup(54, 'female', False, 120, 35).value == 3
    assert lookup(55, 'female', False, 119, 25).value == 3
