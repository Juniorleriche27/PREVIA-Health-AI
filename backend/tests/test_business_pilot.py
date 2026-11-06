"""Non-regression tests for the commercial viability, financial model and pilot plan."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.evaluate_business_pilot import (  # noqa: E402
    OBSERVED_COSTS,
    PILOT_KPIS,
    PRICING,
    calculate_breakeven,
    calculate_costs,
    calculate_revenue,
    calculate_scenario_table,
    run,
)


def test_observed_costs_are_positive_and_realistic():
    assert OBSERVED_COSTS["vps_netcup_monthly"] == 25.0
    assert OBSERVED_COSTS["vercel_frontend_monthly"] == 20.0
    assert OBSERVED_COSTS["domain_dns_annual"] > 0
    assert 0 <= OBSERVED_COSTS["token_rag_query_eur"] < 0.05
    assert OBSERVED_COSTS["extractive_query_eur"] == 0.0


def test_revenue_and_cost_calculations():
    # Test a single pilot
    rev_pilot = calculate_revenue(pilots=1, campaigns=0, annual_licenses=0, profiles=1000)
    assert rev_pilot["total_revenue"] == PRICING["pilot_package_eur"]

    costs_pilot = calculate_costs(pilots=1, campaigns=0, annual_licenses=0, profiles=1000)
    assert costs_pilot["total_costs"] > 0
    assert costs_pilot["infrastructure"] > 0
    assert costs_pilot["devops_maintenance"] > 0
    assert costs_pilot["support_training"] > 0

    margin = rev_pilot["total_revenue"] - costs_pilot["total_costs"]
    assert margin > 0, "A standard pilot must generate positive contribution margin"


def test_scenario_financials_logical_ordering():
    rows = calculate_scenario_table()
    assert len(rows) == 9  # 3 scenarios × 3 years

    by_scenario_year = {(r["scenario"], r["year"]): r for r in rows}

    for year in (1, 2, 3):
        cons = by_scenario_year[("conservative", year)]
        base = by_scenario_year[("base_case", year)]
        ambi = by_scenario_year[("ambitious", year)]

        # Revenue ordering
        assert cons["total_revenue_eur"] <= base["total_revenue_eur"] <= ambi["total_revenue_eur"]
        # Volume ordering
        assert cons["profiles_evaluated"] <= base["profiles_evaluated"] <= ambi["profiles_evaluated"]

        # Margins are strictly positive and bounded
        for r in (cons, base, ambi):
            assert r["gross_margin_eur"] > 0
            assert 0.0 < r["gross_margin_pct"] < 90.0
            assert 0.0 < r["cost_per_profile_eur"] < 15.0


def test_breakeven_thresholds():
    breakeven = calculate_breakeven()
    assert 1.0 <= breakeven["campaigns_to_breakeven"] <= 12.0
    assert 0.1 <= breakeven["licenses_to_breakeven"] <= 2.0


def test_pilot_kpis_structure_and_coverage():
    assert len(PILOT_KPIS) == 12
    categories = {kpi["category"] for kpi in PILOT_KPIS}
    assert "Operational Feasibility" in categories
    assert "Clinical Reliability" in categories
    assert "Equity & Access" in categories
    assert "Economic Viability" in categories

    for kpi in PILOT_KPIS:
        assert kpi["id"].startswith("KPI-")
        assert len(kpi["name_fr"]) > 5
        assert len(kpi["name_en"]) > 5
        assert kpi["target_value"] >= 0.0
        assert "evidence_level" in kpi


def test_business_pilot_is_bitwise_reproducible(tmp_path: Path):
    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"

    manifest_a = run(out_a)
    manifest_b = run(out_b)

    assert manifest_a["analysis"] == manifest_b["analysis"]
    assert manifest_a["breakeven_analysis"] == manifest_b["breakeven_analysis"]

    for key, item in manifest_a["files"].items():
        rel_path = item["path"]
        assert (out_a / rel_path).read_bytes() == (out_b / rel_path).read_bytes()
        assert item["sha256"] == manifest_b["files"][key]["sha256"]


def test_manifest_contains_required_boundaries(tmp_path: Path):
    manifest = run(tmp_path)
    boundaries = " ".join(manifest["business_boundaries"]).lower()
    for term in ("contracts", "indicative", "negotiated", "boundaries", "diagnostic"):
        assert term in boundaries
