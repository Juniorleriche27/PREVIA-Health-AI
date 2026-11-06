"""Regression and audit tests for PREVIA's commercial planning model."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.evaluate_business_pilot import (  # noqa: E402
    COST_ASSUMPTIONS,
    PILOT_KPIS,
    PRICING,
    calculate_breakeven,
    calculate_costs,
    calculate_revenue,
    calculate_scenario_table,
    run,
)


EXPECTED_REVENUE = {
    ("conservative", 1): 12000.0,
    ("conservative", 2): 19500.0,
    ("conservative", 3): 30000.0,
    ("base_case", 1): 17000.0,
    ("base_case", 2): 45000.0,
    ("base_case", 3): 112500.0,
    ("ambitious", 1): 34000.0,
    ("ambitious", 2): 90000.0,
    ("ambitious", 3): 212500.0,
}


def test_cost_values_are_explicitly_assumptions_not_observations():
    assert COST_ASSUMPTIONS["vps_instance_monthly_eur"] == 25.0
    assert COST_ASSUMPTIONS["vercel_monthly_eur"] == 20.0
    assert all(value >= 0 for value in COST_ASSUMPTIONS.values())


def test_declared_prices_are_the_only_revenue_sources():
    revenue = calculate_revenue(1, 3, 2, profiles=999999)
    expected = 12000 + 3 * 2500 + 2 * 15000
    assert revenue["total_revenue"] == expected
    assert revenue["revenue_supplementary"] == 0
    assert PRICING == {
        "pilot_package_eur": 12000.0,
        "campaign_package_eur": 2500.0,
        "annual_license_eur": 15000.0,
    }


def test_every_scenario_revenue_reconciles_to_declared_quantities():
    rows = calculate_scenario_table()
    assert len(rows) == 9
    for row in rows:
        key = (row["scenario"], row["year"])
        assert row["total_revenue_eur"] == EXPECTED_REVENUE[key]
        assert row["total_revenue_eur"] == (
            row["revenue_pilots_eur"]
            + row["revenue_campaigns_eur"]
            + row["revenue_licenses_eur"]
            + row["revenue_supplementary_eur"]
        )
        assert row["revenue_supplementary_eur"] == 0
        assert row["modeled_margin_eur"] == round(row["total_revenue_eur"] - row["total_modeled_costs_eur"], 2)


def test_cost_categories_reconcile_without_double_counting():
    for row in calculate_scenario_table():
        category_sum = sum(row[key] for key in (
            "infrastructure_cost_assumption_eur", "tokens_cost_assumption_eur",
            "devops_cost_assumption_eur", "support_cost_assumption_eur",
            "audit_cost_assumption_eur",
        ))
        assert round(category_sum, 2) == row["total_modeled_costs_eur"]
        assert row["modeled_total_cost_per_profile_eur"] > 0
        assert row["modeled_technical_cost_per_profile_eur"] >= 0


def test_breakeven_uses_incremental_costs_and_whole_saleable_units():
    result = calculate_breakeven()
    baseline = calculate_costs(0, 0, 0, 0)["total_costs"]
    assert result["fixed_annual_overhead_assumption_eur"] == baseline == 3944.0
    assert result["incremental_cost_per_campaign_assumption_eur"] == 1500.0
    assert result["contribution_per_campaign_eur"] == 1000.0
    assert result["campaigns_to_breakeven_integer"] == 4
    assert result["incremental_cost_per_license_assumption_eur"] == 4100.0
    assert result["contribution_per_license_eur"] == 10900.0
    assert result["licenses_to_breakeven_integer"] == 1


def test_pilot_kpis_are_targets_not_achieved_results():
    assert len(PILOT_KPIS) == 12
    for kpi in PILOT_KPIS:
        assert kpi["id"].startswith("KPI-")
        assert "status" in kpi
        assert "achieved" not in kpi["status"].lower()
        assert kpi["method"]


def test_output_is_bitwise_reproducible_and_hashes_verify(tmp_path: Path):
    first, second = tmp_path / "first", tmp_path / "second"
    manifest_a, manifest_b = run(first), run(second)
    assert manifest_a == manifest_b
    assert manifest_a["supplementary_revenue_modeled"] is False
    assert manifest_a["cost_evidence_status"]["observed_expenses_with_invoice_in_repository"] == []
    for key, item in manifest_a["files"].items():
        a, b = first / item["path"], second / item["path"]
        assert a.read_bytes() == b.read_bytes()
        assert hashlib.sha256(a.read_bytes()).hexdigest() == item["sha256"]
        if a.suffix == ".svg":
            ET.parse(a)


def test_generated_csv_has_expected_grain_and_unique_keys(tmp_path: Path):
    run(tmp_path)
    with (tmp_path / "financial_scenarios.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    keys = [(row["scenario"], row["year"]) for row in rows]
    assert len(rows) == len(keys) == len(set(keys)) == 9
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    boundaries = " ".join(manifest["business_boundaries"]).lower()
    for term in ("synthetic", "random", "targets", "license file", "audited accounts"):
        assert term in boundaries
