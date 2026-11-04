"""Module 05 tests: QA is reproducible; it does NOT imply medical validity."""

from copy import deepcopy
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from app.evaluation import OFFICIAL_ANCHOR_CELLS, selections_for, source_qa
from app.main import app
from app.population import make_synthetic_cohort
from app.who_chart import CHART, lookup

client = TestClient(app)
URL = "/api/v1/evaluation/audit"
BASE = {"country": "Togo", "cohort_size": 240, "outreach_capacity": 45, "seed": 2026, "sensitivity_runs": 12}


def result(params=None):
    response = client.post(URL, json=params or BASE)
    assert response.status_code == 200, response.text
    return response.json()


def test_route_registered_and_versioned():
    response = client.get("/health")
    assert response.json()["version"] == "0.8.0"
    assert URL in client.get("/openapi.json").text


def test_default_research_qa():
    x = result()
    assert x["data_type"] == "synthetic_software_audit"
    assert x["software_checks_passed"] is True
    assert all(check["passed"] for check in x["checks"])
    assert len(x["checks"]) == 10
    assert x["simulated_high_reference_count"] == 121
    assert x["sensitivity_runs"] == 12
    assert "CLINICAL VALIDATION NOT PERFORMED" in x["validation_status"]


def test_anchors_and_entire_chart_structure():
    qa = source_qa()
    assert qa.chart_cells == 700
    assert qa.anchor_cells_compared == qa.anchor_cells_matched == 28
    assert qa.nondecreasing_bmi_rows
    assert qa.nonincreasing_risk_as_bp_drops
    for age, quadrants in OFFICIAL_ANCHOR_CELLS.items():
        for quadrant, expected in quadrants.items():
            assert CHART[age][quadrant][0][0] == expected


def test_oracle_fixtures_do_not_claim_complete_source_validation():
    qa = result()["source_qa"]
    assert "700" in qa["coverage_notice"]
    assert "28" in qa["coverage_notice"]
    assert qa["status"] == "pass_with_limited_source_checks"
    assert result()["limitations"][0].startswith("All 700")


def test_who_bin_boundaries_reconciled():
    assert lookup(52, "female", False, 128, 26.1).value == 3
    assert lookup(52, "female", False, 139.9, 29.9).value == 3
    assert lookup(52, "female", False, 140, 30).value == 4
    assert lookup(74, "male", True, 180, 35).value == 38


def test_same_hash_and_selections_are_reproducible():
    a, b = result(), result()
    assert a == b
    assert len(a["cohort_sha256"]) == 64
    for s in a["strategies"]:
        assert len(s["selected_ids_sha256"]) == 64


def test_independent_cohort_hash_differs_by_seed():
    a = result()
    b = result({**BASE, "seed": 2027})
    assert a["cohort_sha256"] != b["cohort_sha256"]


def test_all_strategies_same_cohort_and_counts():
    a = result()
    assert len(a["strategies"]) == 3
    assert [s["key"] for s in a["strategies"]] == ["chart_descending", "sector_balanced", "seeded_random"]
    for s in a["strategies"]:
        assert s["selected_count"] == 45
        assert 0 <= s["high_reference_selected"] <= 45
        assert 0 <= s["high_reference_capture_pct"] <= 100
        assert s["high_reference_selected"] <= a["simulated_high_reference_count"]


def test_qa_matches_prior_strategy_compare_exactly():
    x = result()
    response = client.post("/api/v1/prioritization/compare", json={k:v for k,v in BASE.items() if k != "sensitivity_runs"})
    assert response.status_code == 200
    old = {s["key"]: s for s in response.json()["strategies"]}
    for s in x["strategies"]:
        prev = old[s["key"]]
        assert s["high_reference_selected"] == prev["higher_reference_selected"]
        assert s["high_reference_capture_pct"] == prev["higher_reference_capture_pct"]
        assert s["high_reference_yield_pct"] == prev["higher_reference_yield_pct"]
        assert s["sector_selection_gap_pp"] == prev["sector_selection_gap_pp"]
        assert s["sex_reference_selection_gap_pp"] == prev["sex_reference_selection_gap_pp"]
        ids = sorted(prev["selected_synthetic_ids"])
        assert s["selected_ids_sha256"] == sha256("\n".join(ids).encode()).hexdigest()


def test_group_denominators_and_group_high_counts():
    x = result()
    for strategy in x["strategies"]:
        for group_name in ["sector_high_coverage", "sex_reference_high_coverage"]:
            groups = strategy[group_name]
            assert sum(p["population_count"] for p in groups) == 240
            assert sum(p["selected_count"] for p in groups) == 45
            assert sum(p["high_reference_count"] for p in groups) == 121
            assert sum(p["high_reference_selected"] for p in groups) == strategy["high_reference_selected"]
            for p in groups:
                assert 0 <= p["selected_count"] <= p["population_count"]
                assert 0 <= p["high_reference_selected"] <= p["high_reference_count"]
                if p["high_reference_count"]:
                    assert p["high_reference_capture_pct"] == round(100 * p["high_reference_selected"] / p["high_reference_count"], 2)
                else:
                    assert p["high_reference_capture_pct"] is None


def test_selectors_have_no_duplicate_ids_and_do_not_mutate_cohort():
    cohort = make_synthetic_cohort(40, 15)
    snapshot = deepcopy(cohort)
    selections = selections_for(cohort, 10, 15)
    assert cohort == snapshot
    ids = {p["synthetic_id"] for p in cohort}
    for chosen in selections.values():
        selected = [p["synthetic_id"] for p in chosen]
        assert len(selected) == len(set(selected)) == 10
        assert set(selected) <= ids


def test_whole_capacity_has_perfect_selection_rates():
    x = result({**BASE, "cohort_size": 40, "outreach_capacity": 40, "sensitivity_runs": 3})
    for s in x["strategies"]:
        assert s["high_reference_capture_pct"] == 100
        assert s["sector_selection_gap_pp"] == 0
        assert s["sex_reference_selection_gap_pp"] == 0
    assert x["software_checks_passed"]


def test_small_capacity_is_valid():
    x = result({**BASE, "cohort_size": 40, "outreach_capacity": 1, "sensitivity_runs": 3})
    assert all(s["selected_count"] == 1 for s in x["strategies"])
    assert x["software_checks_passed"]


def test_capacity_variants_nondecreasing_and_bounded():
    x = result()
    points = x["capacity_sensitivity"]
    assert [p["slots"] for p in points] == [22,45,90]
    for key in ["chart_first_high_selected", "sector_balanced_high_selected", "random_high_selected"]:
        counts = [p[key] for p in points]
        assert counts == sorted(counts)
        for p in points:
            assert p[key] <= min(p["slots"], p["higher_reference_total"])
    assert all(p["higher_reference_total"] == 121 for p in points)


def test_capacity_edge_with_full_population_is_unique():
    x = result({**BASE, "cohort_size": 40, "outreach_capacity": 40, "sensitivity_runs": 3})
    assert [p["slots"] for p in x["capacity_sensitivity"]] == [20, 40]


def test_ranges_report_min_median_max_ordering():
    x = result()
    for strategy in x["sensitivity"]:
        for metric in ["capture_pct", "sector_gap_pp", "reference_sex_gap_pp", "high_reference_selected"]:
            s = strategy[metric]
            assert 0 <= s["minimum"] <= s["median"] <= s["maximum"]
            assert s["maximum"] <= (500 if metric == "high_reference_selected" else 100)


def test_sensitivity_runs_change_range_not_baseline_cohort():
    x = result({**BASE, "sensitivity_runs": 3})
    y = result({**BASE, "sensitivity_runs": 20})
    assert x["cohort_sha256"] == y["cohort_sha256"]
    assert x["strategies"] == y["strategies"]
    assert len(x["sensitivity"]) == len(y["sensitivity"]) == 3


@pytest.mark.parametrize("value", [0, 1, 2, 26, 100, -1])
def test_sensitivity_runs_bounded(value):
    assert client.post(URL, json={**BASE, "sensitivity_runs": value}).status_code == 422


def test_unsupported_country_is_rejected():
    assert client.post(URL, json={**BASE, "country": "France"}).status_code == 422


def test_region_country_label_does_not_fake_epidemiology():
    a = result()
    b = result({**BASE, "country": "Ghana"})
    assert a["region"] == b["region"]
    assert a["cohort_sha256"] == b["cohort_sha256"]
    assert a["strategies"] == b["strategies"]


def test_bad_scenario_inputs_are_rejected():
    for fields in [{"outreach_capacity": 0}, {"outreach_capacity": 300}, {"cohort_size": 39},
                   {"cohort_size": 501}, {"seed": -1}, {"unexpected": "oops"}]:
        assert client.post(URL, json={**BASE, **fields}).status_code == 422


def test_does_not_invent_model_accuracy_or_events_prevented():
    x = result()
    assert "NOT been clinically validated" in x["conclusion"]
    limits = " ".join(x["limitations"]).lower()
    for concept in ["calibration", "discrimination", "confidence", "circular", "patient", "outcomes"]:
        assert concept in limits
    assert "source_url" in x
    assert x["source_url"].startswith("https://www.who.int/")
