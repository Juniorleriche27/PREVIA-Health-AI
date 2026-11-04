"""Module 04: strategy comparison is deterministic, bounded and non-clinical."""

from fastapi.testclient import TestClient
from app.main import app
from app.population import make_synthetic_cohort
from app.prioritization import choose_by_chart, choose_by_sector, choose_random

client = TestClient(app)
URL = '/api/v1/prioritization/compare'
BASE = {'country': 'Togo', 'cohort_size': 240, 'outreach_capacity': 45, 'seed': 2026}


def get(payload=BASE):
    response = client.post(URL, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_compare_returns_all_three_expected_strategies():
    x = get()
    assert x['data_type'] == 'synthetic_strategy_comparison'
    assert [s['key'] for s in x['strategies']] == [
        'chart_descending', 'sector_balanced', 'seeded_random'
    ]
    assert x['cohort_size'] == 240
    assert x['outreach_capacity'] == 45


def test_capacity_and_selection_integrity():
    x = get()
    for s in x['strategies']:
        assert s['selected_count'] == 45
        assert s['unselected_count'] == 195
        ids = s['selected_synthetic_ids']
        assert len(ids) == 45 == len(set(ids))
        assert all(i.startswith('SYN-') for i in ids)
        assert len(s['example_profiles']) == 8
        assert set(p['synthetic_id'] for p in s['example_profiles']).issubset(ids)


def test_all_rates_and_math_are_coherent():
    x = get()
    high = x['higher_reference_in_cohort']
    for s in x['strategies']:
        selected_high = s['higher_reference_selected']
        assert 0 <= selected_high <= min(high, 45)
        assert abs(s['higher_reference_capture_pct'] - (round(100 * selected_high / high, 2) if high else 0)) < 0.001
        assert abs(s['higher_reference_yield_pct'] - round(100 * selected_high / 45, 2)) < 0.001
        assert 0 <= s['average_chart_value_pct'] <= 100
        for group, gap_key in (('sector_selection', 'sector_selection_gap_pp'), ('sex_reference_selection', 'sex_reference_selection_gap_pp')):
            rates = [r['selection_rate_pct'] for r in s[group] if r['population_count']]
            assert 0 <= s[gap_key] <= 100
            assert s[gap_key] == round(max(rates) - min(rates), 2)
            assert sum(row['selected_count'] for row in s[group]) == 45
            assert sum(row['population_count'] for row in s[group]) == 240


def test_exact_same_cohort_across_comparisons():
    # No per-strategy re-generation or differences in synthetic population.
    cohort = make_synthetic_cohort(240, 2026)
    all_ids = {p['synthetic_id'] for p in cohort}
    for s in get()['strategies']:
        assert set(s['selected_synthetic_ids']).issubset(all_ids)


def test_chart_strategy_is_a_reference_based_upper_bound():
    x = get()
    chart, balanced, random = x['strategies']
    assert chart['higher_reference_selected'] >= balanced['higher_reference_selected']
    assert chart['higher_reference_selected'] >= random['higher_reference_selected']
    assert chart['average_chart_value_pct'] >= balanced['average_chart_value_pct']
    assert chart['average_chart_value_pct'] >= random['average_chart_value_pct']


def test_sector_balanced_rates_are_nearly_equal():
    x = get()
    assert x['strategies'][1]['sector_selection_gap_pp'] <= 2.0


def test_reproducible_payload():
    assert get() == get()


def test_change_seed_changes_profiles():
    a = get()
    b = get({**BASE, 'seed': 2027})
    assert a['strategies'][0]['selected_synthetic_ids'] != b['strategies'][0]['selected_synthetic_ids']


def test_capacity_change_preserves_risk_population_reference_count():
    a = get()
    b = get({**BASE, 'outreach_capacity': 65})
    assert a['higher_reference_in_cohort'] == b['higher_reference_in_cohort']
    assert b['strategies'][0]['selected_count'] == 65


def test_country_same_who_region_changes_only_label():
    a = get()
    b = get({**BASE, 'country': 'Ghana'})
    assert a['country'] != b['country']
    assert a['strategies'] == b['strategies']


def test_unsupported_region_rejected():
    assert client.post(URL, json={**BASE, 'country': 'France'}).status_code == 422


def test_invalid_capacity_and_size_rejected():
    for payload in [
        {**BASE, 'outreach_capacity': 0},
        {**BASE, 'outreach_capacity': 241},
        {**BASE, 'cohort_size': 30},
        {**BASE, 'cohort_size': 501},
    ]:
        assert client.post(URL, json=payload).status_code == 422


def test_full_capacity_selects_all_proof():
    x = get({**BASE, 'cohort_size': 40, 'outreach_capacity': 40})
    ids = [set(s['selected_synthetic_ids']) for s in x['strategies']]
    assert ids[0] == ids[1] == ids[2]
    assert all(s['sector_selection_gap_pp'] == 0 for s in x['strategies'])


def test_small_capacity_no_duplicate_or_crash():
    x = get({**BASE, 'cohort_size': 40, 'outreach_capacity': 1})
    assert all(len(s['selected_synthetic_ids']) == 1 for s in x['strategies'])


def test_no_patient_records_or_outcome_claims():
    x = get()
    assert 'Not a clinical' in x['clinical_use']
    assert len(x['limitations']) >= 5
    assert x['source_url'].startswith('https://www.who.int/')
    for s in x['strategies']:
        for p in s['example_profiles']:
            assert p['area'].startswith('Demo sector')
            assert set(p) == {
                'synthetic_id', 'area', 'age_band', 'sex_reference', 'current_smoker',
                'systolic_bp', 'bmi', 'who_chart_value_percent', 'risk_category',
            }


def test_selectors_never_mutate_cohort():
    c = make_synthetic_cohort(40, 33)
    before = [dict(p) for p in c]
    choose_by_chart(c, 10)
    choose_by_sector(c, 10)
    choose_random(c, 10, 33)
    assert c == before


def test_prior_population_endpoint_unaffected():
    r = client.post('/api/v1/population/scenario', json=BASE)
    assert r.status_code == 200
    j = r.json()
    assert j['selected_for_demo'] == 45
    assert j['higher_chart_category_count'] == get()['higher_reference_in_cohort']
