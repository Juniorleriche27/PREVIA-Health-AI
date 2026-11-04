"""API and methodological guardrails for synthetic population scenarios."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ENDPOINT = '/api/v1/population/scenario'


def test_synthetic_scenario_integrity():
    r = client.post(ENDPOINT, json={'country':'Togo','cohort_size':120,'outreach_capacity':20,'seed':42})
    assert r.status_code == 200
    j = r.json()
    assert j['data_type'] == 'synthetic_simulation'
    assert j['cohort_size'] == 120
    assert j['outreach_capacity'] == j['selected_for_demo'] == 20
    assert j['unselected_for_demo'] == 100
    assert sum(row['count'] for row in j['risk_distribution']) == 120
    assert sum(row['count'] for row in j['age_distribution']) == 120
    assert sum(row['count'] for row in j['area_distribution']) == 120
    assert sum(row['count'] for row in j['sex_reference_distribution']) == 120
    assert j['higher_chart_category_count'] == sum(row['count'] for row in j['risk_distribution'][2:])
    assert len(j['demonstration_queue']) == 8
    assert all(p['synthetic_id'].startswith('SYN-') for p in j['demonstration_queue'])
    assert j['source_url'].startswith('https://www.who.int/')


def test_reproducible_synthetic_cohort():
    payload={'country':'Ghana','cohort_size':150,'outreach_capacity':30,'seed':81}
    a=client.post(ENDPOINT,json=payload).json()
    b=client.post(ENDPOINT,json=payload).json()
    assert a == b
    c=client.post(ENDPOINT,json={**payload,'seed':82}).json()
    assert a['risk_distribution'] != c['risk_distribution'] or a['demonstration_queue'] != c['demonstration_queue']


def test_capacity_does_not_change_generated_cohort():
    p={'country':'Togo','cohort_size':100,'outreach_capacity':10,'seed':2026}
    a=client.post(ENDPOINT,json=p).json()
    b=client.post(ENDPOINT,json={**p,'outreach_capacity':70}).json()
    assert a['risk_distribution'] == b['risk_distribution']
    assert a['age_distribution'] == b['age_distribution']
    assert a['selected_for_demo'] == 10
    assert b['selected_for_demo'] == 70


def test_country_validation():
    assert client.post(ENDPOINT,json={'country':'United States'}).status_code == 422
    assert client.post(ENDPOINT,json={'country':'Togo'}).status_code == 200


def test_capacity_validation():
    assert client.post(ENDPOINT,json={'cohort_size':40,'outreach_capacity':41}).status_code == 422
    assert client.post(ENDPOINT,json={'cohort_size':501,'outreach_capacity':30}).status_code == 422
    assert client.post(ENDPOINT,json={'cohort_size':40,'outreach_capacity':0}).status_code == 422


def test_api_does_not_expose_real_patient_data():
    j=client.post(ENDPOINT,json={'cohort_size':40,'outreach_capacity':5}).json()
    assert all(set(row)=={'synthetic_id','area','age_band','sex_reference','current_smoker','systolic_bp','bmi','who_chart_value_percent','risk_category'} for row in j['demonstration_queue'])
    assert all(row['area'].startswith('Demo sector') for row in j['demonstration_queue'])
    assert 'Not for clinical' in j['clinical_use']
