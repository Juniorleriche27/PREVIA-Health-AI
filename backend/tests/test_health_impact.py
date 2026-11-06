"""Non-regression tests for the synthetic health-impact demonstration."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.evaluate_health_impact import calculate_run, run  # noqa: E402


def test_baseline_capacity_45_matches_existing_scientific_audit():
    rows = {row["strategy"]: row for row in calculate_run(240, 45, 2026)}
    assert rows["chart_descending"]["priority_total"] == 121
    assert rows["chart_descending"]["priority_selected"] == 45
    assert rows["chart_descending"]["priority_capture_pct"] == 37.19
    assert rows["sector_balanced"]["priority_selected"] == 45
    assert rows["sector_balanced"]["sector_selection_gap_pp"] == 1.67
    assert rows["seeded_random"]["priority_selected"] == 22
    assert rows["seeded_random"]["priority_capture_pct"] == 18.18


def test_capacity_results_are_bounded_and_complete():
    for capacity in (24, 45, 72, 120):
        rows = calculate_run(240, capacity, 2026)
        assert [row["strategy"] for row in rows] == [
            "chart_descending", "sector_balanced", "seeded_random"
        ]
        for row in rows:
            assert 0 <= row["priority_selected"] <= min(capacity, row["priority_total"])
            assert 0 <= row["priority_capture_pct"] <= 100
            assert 0 <= row["priority_yield_pct"] <= 100
            assert 0 <= row["sector_selection_gap_pp"] <= 100
            assert 0 <= row["sex_selection_gap_pp"] <= 100


def test_chart_based_metric_is_explicitly_circular_not_clinical_accuracy():
    for capacity in (24, 45, 72, 120):
        rows = {row["strategy"]: row for row in calculate_run(240, capacity, 2026)}
        chart = rows["chart_descending"]
        assert chart["priority_selected"] >= rows["seeded_random"]["priority_selected"]
        assert chart["mean_chart_value_pct"] >= rows["seeded_random"]["mean_chart_value_pct"]


def test_full_analysis_is_bitwise_reproducible(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    manifest_a = run(first, 240, (24, 45), (2026, 2027, 2028))
    manifest_b = run(second, 240, (24, 45), (2026, 2027, 2028))
    assert manifest_a == manifest_b
    assert manifest_a["cohort_sha256"] == manifest_b["cohort_sha256"]
    for filename in ("risk_distribution.csv", "baseline_capacity_results.csv", "all_seed_runs.csv", "stability_summary.csv", "manifest.json"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()


def test_generated_tables_reconcile(tmp_path: Path):
    run(tmp_path, 240, (45,), (2026, 2027, 2028))
    with (tmp_path / "risk_distribution.csv").open(encoding="utf-8") as handle:
        risk_rows = list(csv.DictReader(handle))
    assert sum(int(row["count"]) for row in risk_rows) == 240
    assert round(sum(float(row["percentage"]) for row in risk_rows), 2) == 100.0
    assert risk_rows[-1]["risk_category"] == "≥30%"

    with (tmp_path / "all_seed_runs.csv").open(encoding="utf-8") as handle:
        run_rows = list(csv.DictReader(handle))
    assert len(run_rows) == 3 * 3  # three seeds × three strategies × one capacity
    assert {row["seed"] for row in run_rows} == {"2026", "2027", "2028"}


def test_manifest_states_required_scientific_boundaries(tmp_path: Path):
    run(tmp_path, 240, (45,), (2026,))
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    limits = " ".join(manifest["scientific_boundaries"]).lower()
    for required in ("synthetic", "circular", "clinical validation", "health outcome", "shap", "hba1c"):
        assert required in limits
