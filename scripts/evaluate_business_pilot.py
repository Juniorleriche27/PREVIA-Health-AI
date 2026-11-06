"""Audited, reproducible commercial-planning model for PREVIA Health AI.

This model separates deployed architecture facts from unverified planning cost
assumptions. It is not an audited account, supplier quote, signed contract,
clinical result, or achieved pilot performance report.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEPLOYMENT_FACTS = {
    "frontend": "Vercel deployment",
    "backend": "Netcup-hosted PREVIA API",
    "ai_service": "Knowlia accessed through a private API integration",
    "public_api_domain": "api.previa.koryxa.fr",
}

# No supporting invoice, supplier quote, payroll record, or signed service
# proposal is stored in this repository. These are planning assumptions.
COST_ASSUMPTIONS = {
    "vps_instance_monthly_eur": 25.0,
    "vercel_monthly_eur": 20.0,
    "domain_dns_annual_eur": 24.0,
    "backup_monitoring_per_instance_annual_eur": 180.0,
    "rag_query_eur": 0.0015,
    "rag_queries_per_profile": 0.30,
    "base_devops_annual_eur": 3200.0,
    "pilot_devops_eur": 1000.0,
    "campaign_devops_eur": 400.0,
    "license_devops_eur": 1500.0,
    "pilot_support_eur": 2200.0,
    "campaign_support_eur": 800.0,
    "license_support_eur": 1800.0,
    "pilot_audit_eur": 1500.0,
    "campaign_audit_eur": 300.0,
    "license_audit_eur": 800.0,
}

# Compatibility alias. Values are now correctly labelled as assumptions.
OBSERVED_COSTS = COST_ASSUMPTIONS

PRICING = {
    "pilot_package_eur": 12000.0,
    "campaign_package_eur": 2500.0,
    "annual_license_eur": 15000.0,
}

SCENARIOS = {
    "conservative": {"label": "Prudent (Conservative)", "years": {
        1: {"pilots": 1, "campaigns": 0, "annual_licenses": 0, "profiles": 1000},
        2: {"pilots": 1, "campaigns": 3, "annual_licenses": 0, "profiles": 8500},
        3: {"pilots": 0, "campaigns": 6, "annual_licenses": 1, "profiles": 20000},
    }},
    "base_case": {"label": "Central (Base Case)", "years": {
        1: {"pilots": 1, "campaigns": 2, "annual_licenses": 0, "profiles": 6000},
        2: {"pilots": 0, "campaigns": 6, "annual_licenses": 2, "profiles": 25000},
        3: {"pilots": 0, "campaigns": 15, "annual_licenses": 5, "profiles": 70000},
    }},
    "ambitious": {"label": "Ambitieux (Optimistic)", "years": {
        1: {"pilots": 2, "campaigns": 4, "annual_licenses": 0, "profiles": 12000},
        2: {"pilots": 0, "campaigns": 12, "annual_licenses": 4, "profiles": 55000},
        3: {"pilots": 0, "campaigns": 25, "annual_licenses": 10, "profiles": 150000},
    }},
}

_KPI_ROWS = [
    ("KPI-01", "Operational feasibility", "Complétude des dossiers", "Record completeness", "≥ 98%", "Proposed target — not measured", "Required-field audit"),
    ("KPI-02", "Operational feasibility", "Durée médiane par évaluation", "Median assessment duration", "≤ 90 s", "Proposed target — not measured", "Timestamp from intake start to validated result"),
    ("KPI-03", "Software fidelity", "Concordance avec les cellules OMS implémentées", "Concordance with implemented WHO cells", "100%", "Software baseline available; independent clinical review pending", "Automated 700-cell text-layer comparison plus expert review"),
    ("KPI-04", "Allocation integrity", "Respect de la capacité", "Capacity constraint compliance", "100%", "Software baseline available; field performance not measured", "Selected count must not exceed configured capacity"),
    ("KPI-05", "Equity monitoring", "Écarts de sélection et de suivi entre groupes", "Selection and follow-up gaps across groups", "Report estimates with uncertainty; no absolute guarantee", "Proposed evaluation criterion — not measured", "Prespecified subgroup rates, denominators and uncertainty intervals"),
    ("KPI-06", "Usability", "Score SUS des utilisateurs", "User SUS score", "Target to be agreed before pilot", "Proposed measure — not measured", "Standard 10-item System Usability Scale"),
    ("KPI-07", "Reliability", "Disponibilité de la plateforme", "Platform availability", "≥ 99.5% proposed", "Proposed service target — not measured over a pilot", "External uptime monitoring and incident log"),
    ("KPI-08", "Safety and privacy", "Incidents de confidentialité", "Privacy incidents", "0 serious incidents", "Safety target — not a guarantee", "Incident register, severity and corrective action"),
    ("KPI-09", "Economic feasibility", "Coût technique direct par profil", "Direct technical cost per profile", "≤ €0.50 proposed", "Model target — not observed", "Actual hosting, monitoring and inference invoices divided by evaluated profiles"),
    ("KPI-10", "Clinical workflow", "Orientations appropriées", "Appropriate referrals", "Target to be set with clinical governance", "Requires independent adjudication", "Agreement with prespecified local protocol and independent review"),
    ("KPI-11", "Documentary AI", "Validité des citations RAG", "RAG citation validity", "100% valid citations proposed", "Proposed safety target — not guaranteed", "Blinded sample review; invalid or unsupported citations counted as failures"),
    ("KPI-12", "Care pathway", "Suivi approprié complété", "Appropriate follow-up completed", "Target to be set from baseline data", "Real-world outcome — not measured", "Documented completion within a prespecified window"),
]
PILOT_KPIS = [
    {"id": r[0], "category": r[1], "name_fr": r[2], "name_en": r[3], "target": r[4], "status": r[5], "method": r[6]}
    for r in _KPI_ROWS
]


def calculate_revenue(pilots: int, campaigns: int, annual_licenses: int, profiles: int = 0) -> dict[str, float]:
    """Apply only declared prices; no profile-overage revenue is modelled."""
    del profiles
    pilot = pilots * PRICING["pilot_package_eur"]
    campaign = campaigns * PRICING["campaign_package_eur"]
    licence = annual_licenses * PRICING["annual_license_eur"]
    return {
        "revenue_pilots": pilot,
        "revenue_campaigns": campaign,
        "revenue_licenses": licence,
        "revenue_supplementary": 0.0,
        "total_revenue": pilot + campaign + licence,
    }


def _active_instances(pilots: int, campaigns: int, annual_licenses: int) -> int:
    """Planning heuristic; not measured server utilisation."""
    return max(1, pilots + campaigns // 4 + annual_licenses)


def calculate_costs(pilots: int, campaigns: int, annual_licenses: int, profiles: int) -> dict[str, float]:
    instances = _active_instances(pilots, campaigns, annual_licenses)
    infrastructure = (
        COST_ASSUMPTIONS["vps_instance_monthly_eur"] * 12 * instances
        + COST_ASSUMPTIONS["vercel_monthly_eur"] * 12
        + COST_ASSUMPTIONS["domain_dns_annual_eur"]
        + COST_ASSUMPTIONS["backup_monitoring_per_instance_annual_eur"] * instances
    )
    tokens = profiles * COST_ASSUMPTIONS["rag_queries_per_profile"] * COST_ASSUMPTIONS["rag_query_eur"]
    devops = COST_ASSUMPTIONS["base_devops_annual_eur"] + pilots * COST_ASSUMPTIONS["pilot_devops_eur"] + campaigns * COST_ASSUMPTIONS["campaign_devops_eur"] + annual_licenses * COST_ASSUMPTIONS["license_devops_eur"]
    support = pilots * COST_ASSUMPTIONS["pilot_support_eur"] + campaigns * COST_ASSUMPTIONS["campaign_support_eur"] + annual_licenses * COST_ASSUMPTIONS["license_support_eur"]
    audit = pilots * COST_ASSUMPTIONS["pilot_audit_eur"] + campaigns * COST_ASSUMPTIONS["campaign_audit_eur"] + annual_licenses * COST_ASSUMPTIONS["license_audit_eur"]
    total = infrastructure + tokens + devops + support + audit
    return {
        "active_instances_assumption": instances,
        "infrastructure": round(infrastructure, 2),
        "tokens_inference": round(tokens, 2),
        "devops_maintenance": round(devops, 2),
        "support_training": round(support, 2),
        "audit_documentation": round(audit, 2),
        "total_costs": round(total, 2),
    }


def calculate_scenario_table() -> list[dict]:
    rows = []
    for scenario, config in SCENARIOS.items():
        for year, values in config["years"].items():
            revenue = calculate_revenue(values["pilots"], values["campaigns"], values["annual_licenses"], values["profiles"])
            costs = calculate_costs(values["pilots"], values["campaigns"], values["annual_licenses"], values["profiles"])
            margin = revenue["total_revenue"] - costs["total_costs"]
            rows.append({
                "scenario": scenario, "scenario_label": config["label"], "year": year,
                "pilots_count": values["pilots"], "campaigns_count": values["campaigns"], "licenses_count": values["annual_licenses"],
                "profiles_evaluated_assumption": values["profiles"], "active_instances_assumption": costs["active_instances_assumption"],
                "total_revenue_eur": revenue["total_revenue"], "revenue_pilots_eur": revenue["revenue_pilots"],
                "revenue_campaigns_eur": revenue["revenue_campaigns"], "revenue_licenses_eur": revenue["revenue_licenses"],
                "revenue_supplementary_eur": 0.0, "total_modeled_costs_eur": costs["total_costs"],
                "infrastructure_cost_assumption_eur": costs["infrastructure"], "tokens_cost_assumption_eur": costs["tokens_inference"],
                "devops_cost_assumption_eur": costs["devops_maintenance"], "support_cost_assumption_eur": costs["support_training"],
                "audit_cost_assumption_eur": costs["audit_documentation"], "modeled_margin_eur": round(margin, 2),
                "modeled_margin_pct": round(100 * margin / revenue["total_revenue"], 2),
                "modeled_total_cost_per_profile_eur": round(costs["total_costs"] / values["profiles"], 2),
                "modeled_technical_cost_per_profile_eur": round((costs["infrastructure"] + costs["tokens_inference"]) / values["profiles"], 4),
            })
    return rows


def calculate_breakeven() -> dict[str, float | int]:
    baseline = calculate_costs(0, 0, 0, 0)["total_costs"]
    campaign_increment = calculate_costs(0, 1, 0, 0)["total_costs"] - baseline
    licence_increment = calculate_costs(0, 0, 1, 0)["total_costs"] - baseline
    campaign_contribution = PRICING["campaign_package_eur"] - campaign_increment
    licence_contribution = PRICING["annual_license_eur"] - licence_increment
    return {
        "fixed_annual_overhead_assumption_eur": baseline,
        "incremental_cost_per_campaign_assumption_eur": campaign_increment,
        "contribution_per_campaign_eur": campaign_contribution,
        "campaigns_to_breakeven_continuous": round(baseline / campaign_contribution, 3),
        "campaigns_to_breakeven_integer": math.ceil(baseline / campaign_contribution),
        "incremental_cost_per_license_assumption_eur": licence_increment,
        "contribution_per_license_eur": licence_contribution,
        "licenses_to_breakeven_continuous": round(baseline / licence_contribution, 3),
        "licenses_to_breakeven_integer": math.ceil(baseline / licence_contribution),
    }


def cost_input_rows() -> list[dict]:
    return [{
        "input": key, "value": value,
        "evidence_class": "planning_assumption_unverified",
        "source_status": "No invoice, supplier quote, payroll record or signed service proposal in repository",
    } for key, value in COST_ASSUMPTIONS.items()]


def cost_breakdown_rows() -> list[dict]:
    pilot = calculate_costs(1, 0, 0, 1000)
    central_y2 = calculate_costs(0, 6, 2, 25000)
    labels = {
        "infrastructure": "Infrastructure, backups and monitoring",
        "tokens_inference": "RAG inference",
        "devops_maintenance": "DevOps and maintenance",
        "support_training": "Support and training",
        "audit_documentation": "Audit and documentation",
    }
    return [{
        "cost_category": key, "label": label,
        "pilot_year1_amount_eur": pilot[key], "pilot_year1_share_pct": round(100 * pilot[key] / pilot["total_costs"], 2),
        "base_case_year2_amount_eur": central_y2[key], "base_case_year2_share_pct": round(100 * central_y2[key] / central_y2["total_costs"], 2),
        "evidence_class": "modeled_from_unverified_cost_assumptions",
    } for key, label in labels.items()]


def _svg_header(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" rx="14" fill="#fff" stroke="#d5e3ea"/>', f'<text x="36" y="38" font-family="Arial" font-size="19" font-weight="700" fill="#112d3d">{escape(title)}</text>', f'<text x="36" y="61" font-family="Arial" font-size="12" fill="#526f80">{escape(subtitle)}</text>']


def render_financial_scenarios_svg(path: Path, rows: list[dict]) -> None:
    width, height = 980, 510
    maximum = max(r["total_revenue_eur"] for r in rows) / 1000 * 1.15
    lines = _svg_header(width, height, "PREVIA — modeled financial scenarios", "Declared prices only; revenue and margin in kEUR; no signed contracts")
    top, chart_h = 100, 315
    for tick in range(0, int(maximum) + 1, 50):
        y = top + chart_h - tick / maximum * chart_h
        lines += [f'<line x1="60" y1="{y:.1f}" x2="940" y2="{y:.1f}" stroke="#e3edf2"/>', f'<text x="50" y="{y+4:.1f}" font-family="Arial" font-size="10" text-anchor="end" fill="#657f8d">{tick}</text>']
    for s_index, scenario in enumerate(SCENARIOS):
        group_x = 90 + s_index * 295
        subset = [r for r in rows if r["scenario"] == scenario]
        lines.append(f'<text x="{group_x+90}" y="88" font-family="Arial" font-size="12" font-weight="700" text-anchor="middle" fill="#173b4c">{escape(SCENARIOS[scenario]["label"])}</text>')
        for y_index, row in enumerate(subset):
            x = group_x + y_index * 72
            for offset, field, color in ((0, "total_revenue_eur", "#087584"), (22, "modeled_margin_eur", "#10b981")):
                value = row[field] / 1000
                bar_h = value / maximum * chart_h
                y = top + chart_h - bar_h
                lines += [f'<rect x="{x+offset}" y="{y:.1f}" width="18" height="{bar_h:.1f}" rx="3" fill="{color}"/>', f'<text x="{x+offset+9}" y="{y-5:.1f}" font-family="Arial" font-size="9" text-anchor="middle" fill="{color}">{value:.1f}</text>']
            lines.append(f'<text x="{x+20}" y="435" font-family="Arial" font-size="10" text-anchor="middle" fill="#657f8d">Y{row["year"]}</text>')
    lines += ['<rect x="350" y="468" width="14" height="5" fill="#087584"/><text x="370" y="474" font-family="Arial" font-size="11">Revenue</text>', '<rect x="510" y="468" width="14" height="5" fill="#10b981"/><text x="530" y="474" font-family="Arial" font-size="11">Modeled margin</text>', '</svg>']
    path.write_text("\n".join(lines), encoding="utf-8")


def render_cost_breakdown_svg(path: Path, rows: list[dict]) -> None:
    lines = _svg_header(940, 455, "PREVIA — modeled cost structure", "Base-case year 2; all monetary inputs are unverified planning assumptions")
    colors = ("#64748b", "#f59e0b", "#087584", "#0284c7", "#0d9488")
    for index, (row, color) in enumerate(zip(rows, colors)):
        y, pct = 105 + index * 62, row["base_case_year2_share_pct"]
        lines += [f'<text x="310" y="{y+20}" font-family="Arial" font-size="11" text-anchor="end">{escape(row["label"])}</text>', f'<rect x="330" y="{y}" width="480" height="30" rx="5" fill="#eef3f6"/>', f'<rect x="330" y="{y}" width="{pct/45*480:.1f}" height="30" rx="5" fill="{color}"/>', f'<text x="820" y="{y+20}" font-family="Arial" font-size="11">{pct:.2f}% · EUR {row["base_case_year2_amount_eur"]:,.2f}</text>']
    lines.append('</svg>')
    path.write_text("\n".join(lines), encoding="utf-8")


def render_pilot_timeline_svg(path: Path) -> None:
    lines = _svg_header(960, 300, "PREVIA — proposed pilot sequence", "All targets require approvals and prospective measurement; none is an achieved clinical result")
    phases = (("1", "Governance", "Approvals, protocol, data roles"), ("2", "Dry run", "Training and synthetic cases"), ("3", "Supervised pilot", "Human review and incident logging"), ("4", "Independent analysis", "Results and limitations"))
    for index, (number, title, description) in enumerate(phases):
        x = 40 + index * 230
        lines += [f'<rect x="{x}" y="100" width="205" height="125" rx="10" fill="#f8fafc" stroke="#087584"/>', f'<circle cx="{x+28}" cy="130" r="16" fill="#087584"/><text x="{x+28}" y="135" font-family="Arial" font-size="12" text-anchor="middle" fill="#fff">{number}</text>', f'<text x="{x+55}" y="135" font-family="Arial" font-size="13" font-weight="700">{escape(title)}</text>', f'<text x="{x+18}" y="175" font-family="Arial" font-size="11" fill="#526f80">{escape(description)}</text>']
    lines.append('</svg>')
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = output_dir / "figures"
    figures.mkdir(exist_ok=True)
    files = {
        "financial_scenarios_csv": output_dir / "financial_scenarios.csv", "cost_breakdown_csv": output_dir / "cost_breakdown.csv",
        "cost_inputs_csv": output_dir / "cost_inputs.csv", "pilot_kpis_csv": output_dir / "pilot_kpis.csv",
        "figure_financial_scenarios": figures / "financial_scenarios.svg", "figure_cost_breakdown": figures / "cost_breakdown.svg",
        "figure_pilot_timeline": figures / "pilot_timeline.svg",
    }
    scenarios, breakdown = calculate_scenario_table(), cost_breakdown_rows()
    _write_csv(files["financial_scenarios_csv"], scenarios)
    _write_csv(files["cost_breakdown_csv"], breakdown)
    _write_csv(files["cost_inputs_csv"], cost_input_rows())
    _write_csv(files["pilot_kpis_csv"], PILOT_KPIS)
    render_financial_scenarios_svg(files["figure_financial_scenarios"], scenarios)
    render_cost_breakdown_svg(files["figure_cost_breakdown"], breakdown)
    render_pilot_timeline_svg(files["figure_pilot_timeline"])
    manifest = {
        "analysis": "PREVIA commercial planning model — audited", "schema_version": "2.0.0",
        "deployment_facts_verified_from_repository_and_public_endpoints": DEPLOYMENT_FACTS,
        "cost_evidence_status": {"observed_expenses_with_invoice_in_repository": [], "supplier_quotes_in_repository": [], "planning_assumptions_unverified": COST_ASSUMPTIONS},
        "indicative_pricing_non_contractual": PRICING, "supplementary_revenue_modeled": False,
        "breakeven_analysis": calculate_breakeven(),
        "business_boundaries": [
            "Scenario volumes, prices, costs, margins and break-even points are planning assumptions, not actual sales or audited accounts.",
            "No invoice, supplier quote, payroll record, signed customer contract or signed pilot partnership is stored in the repository.",
            "Chantier 15 results are synthetic allocation simulations and are not clinical observations or causal health-impact evidence.",
            "Seeded random allocation is a simulation comparator and must not be described as opportunistic or first-come-first-served care.",
            "Pilot KPI thresholds are proposed targets; they have not been achieved in a real-world pilot.",
            "The public GitHub repository has no LICENSE file; public access does not grant general open-source reuse rights.",
        ],
        "files": {key: {"path": path.relative_to(output_dir).as_posix(), "sha256": _sha256(path)} for key, path in files.items()},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "business-pilot" / "results")
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
