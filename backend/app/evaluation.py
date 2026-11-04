"""Module 05: reproducible *software* audit of an educational synthetic scenario.

No medical validation, fairness certification, discrimination estimate, or clinical
benefit estimate is possible without appropriate independent clinical outcomes.
All metrics below are about *simulation selection*, not patient care.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from json import dumps
from statistics import median
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .population import SIMULATED_AREAS, ScenarioInput, make_synthetic_cohort
from .prioritization import (
    REFERENCE_THRESHOLD, STRATEGY_KEYS, choose_by_chart, choose_by_sector,
    choose_random,
)
from .who_chart import CHART, COUNTRIES, REGION, SOURCE
from .source_verification import verify_all_chart_cells

router = APIRouter(prefix="/api/v1/evaluation", tags=["Evaluation — research QA only"])

# Independent manual reference fixtures transcribed from the WHO source's
# non-laboratory chart. Only these 28 corner cells are externally cross-checked:
# each (age group, reference sex and smoking status), top BP and lowest BMI.
# Does NOT constitute a full independent verification of all 700 cells.
OFFICIAL_ANCHOR_CELLS = {
    70: {"MN": 23, "MS": 29, "FN": 20, "FS": 29},
    65: {"MN": 17, "MS": 24, "FN": 15, "FS": 24},
    60: {"MN": 13, "MS": 20, "FN": 12, "FS": 20},
    55: {"MN": 10, "MS": 16, "FN": 9, "FS": 17},
    50: {"MN": 8, "MS": 13, "FN": 7, "FS": 14},
    45: {"MN": 6, "MS": 11, "FN": 5, "FS": 12},
    40: {"MN": 5, "MS": 9, "FN": 4, "FS": 10},
}


class AuditInput(ScenarioInput):
    sensitivity_runs: int = Field(default=12, ge=3, le=25)

    # Avoid an integer overflow or more than a million for derived seed values.
    # Base model validates seed <=1_000_000; evaluation uses modular seeds.


class SourceQA(BaseModel):
    chart_cells: int
    anchor_cells_compared: int
    anchor_cells_matched: int
    pdf_text_cells_compared: int
    pdf_text_cells_matched: int
    pdf_text_layer_matches: bool
    visual_full_chart_check_completed: bool = False
    nondecreasing_bmi_rows: bool
    nonincreasing_risk_as_bp_drops: bool
    source_url: str
    coverage_notice: str
    status: Literal["pass_with_limited_source_checks", "needs_revision"]


class AuditCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class SensitivityRange(BaseModel):
    minimum: float
    median: float
    maximum: float


class StrategySensitivity(BaseModel):
    key: str
    capture_pct: SensitivityRange
    reference_sex_gap_pp: SensitivityRange
    sector_gap_pp: SensitivityRange
    high_reference_selected: SensitivityRange


class GroupHighCoverage(BaseModel):
    label: str
    population_count: int
    high_reference_count: int
    selected_count: int
    high_reference_selected: int
    high_reference_capture_pct: float | None
    selection_rate_pct: float | None


class StrategyExplanation(BaseModel):
    key: str
    selected_count: int
    high_reference_selected: int
    high_reference_capture_pct: float
    high_reference_yield_pct: float
    sector_selection_gap_pp: float
    sex_reference_selection_gap_pp: float
    sector_high_coverage: list[GroupHighCoverage]
    sex_reference_high_coverage: list[GroupHighCoverage]
    decision_rule: str
    note: str
    selected_ids_sha256: str


class CapacityPoint(BaseModel):
    slots: int
    share_of_cohort_pct: float
    higher_reference_total: int
    chart_first_high_selected: int
    sector_balanced_high_selected: int
    random_high_selected: int


class AuditOutput(BaseModel):
    data_type: Literal["synthetic_software_audit"] = "synthetic_software_audit"
    version: str = "0.6.0"
    country: str
    region: str = REGION
    source_url: str = SOURCE
    cohort_size: int
    outreach_capacity: int
    seed: int
    sensitivity_runs: int
    reference_high_threshold_pct: int = REFERENCE_THRESHOLD
    simulated_high_reference_count: int
    cohort_sha256: str
    source_qa: SourceQA
    checks: list[AuditCheck]
    software_checks_passed: bool
    strategies: list[StrategyExplanation]
    sensitivity: list[StrategySensitivity]
    capacity_sensitivity: list[CapacityPoint]
    conclusion: str
    validation_status: str = "SOFTWARE QA ONLY — CLINICAL VALIDATION NOT PERFORMED"
    limitations: list[str]


def source_qa() -> SourceQA:
    errors = 0
    bmi_ok, bp_ok = True, True
    for age, by_group in CHART.items():
        for group, rows in by_group.items():
            if rows[0][0] != OFFICIAL_ANCHOR_CELLS[age][group]:
                errors += 1
            # For each SBP row, chart values should be non-decreasing with BMI.
            for row in rows:
                if list(row) != sorted(row):
                    bmi_ok = False
            # For each BMI column, risk cannot rise as BP decreases.
            for c in range(5):
                if [row[c] for row in rows] != sorted((row[c] for row in rows), reverse=True):
                    bp_ok = False
    count = sum(len(r) for by_group in CHART.values() for rows in by_group.values() for r in rows)
    text_audit = verify_all_chart_cells()
    good = (count == 700 and errors == 0 and bmi_ok and bp_ok and text_audit["text_cross_check_passed"])
    return SourceQA(
        chart_cells=count,
        anchor_cells_compared=28,
        anchor_cells_matched=28-errors,
        pdf_text_cells_compared=text_audit["cells_compared"],
        pdf_text_cells_matched=text_audit["cells_matching"],
        pdf_text_layer_matches=text_audit["text_cross_check_passed"],
        nondecreasing_bmi_rows=bmi_ok,
        nonincreasing_risk_as_bp_drops=bp_ok,
        source_url=SOURCE,
        coverage_notice="All 700 cells compared against the official WHO PDF text layer; 28 pre-existing anchor spot checks. A full independent visual glyph-by-glyph review remains pending.",
        status="pass_with_limited_source_checks" if good else "needs_revision",
    )


def _sha256_rows(rows: list[dict]) -> str:
    return sha256(dumps(rows, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def selections_for(cohort: list[dict], capacity: int, seed: int) -> dict[str, list[dict]]:
    return {
        "chart_descending": choose_by_chart(cohort, capacity),
        "sector_balanced": choose_by_sector(cohort, capacity),
        "seeded_random": choose_random(cohort, capacity, seed),
    }


def _group_coverage(cohort: list[dict], chosen: list[dict], column: str, labels: tuple[str, ...]) -> list[GroupHighCoverage]:
    total = Counter(p[column] for p in cohort)
    high = Counter(p[column] for p in cohort if p["who_chart_value_percent"] >= REFERENCE_THRESHOLD)
    selected = Counter(p[column] for p in chosen)
    selected_high = Counter(p[column] for p in chosen if p["who_chart_value_percent"] >= REFERENCE_THRESHOLD)
    return [GroupHighCoverage(
        label=label, population_count=total[label], high_reference_count=high[label],
        selected_count=selected[label], high_reference_selected=selected_high[label],
        high_reference_capture_pct=round(100 * selected_high[label] / high[label], 2) if high[label] else None,
        selection_rate_pct=round(100 * selected[label] / total[label], 2) if total[label] else None,
    ) for label in labels]


def _selection_gap(rows: list[GroupHighCoverage]) -> float:
    rates = [round(100 * p.selected_count / p.population_count, 2) for p in rows if p.population_count > 0]
    return round(max(rates) - min(rates), 2) if rates else 0.0


def _range(values: list[float]) -> SensitivityRange:
    return SensitivityRange(minimum=round(min(values), 2), median=round(median(values), 2), maximum=round(max(values), 2))


def _describe(key: str) -> tuple[str, str]:
    return {
        "chart_descending": (
            "Rank by descending WHO chart-cell value; break ties using fabricated ID.",
            "This necessarily favors the same chart-based metric used for evaluation; it is circular, not a clinical-performance win.",
        ),
        "sector_balanced": (
            "Allocate turns to the sector with the lowest fraction selected, then choose higher WHO chart cells within that sector.",
            "Equal simulated sector selection rates do NOT prove equitable access, clinical appropriateness, or benefit.",
        ),
        "seeded_random": (
            "Draw an equal number of synthetic profiles from a deterministic pseudorandom sample, independent of chart value.",
            "A control scenario for comparing allocation arithmetic, not a recommended clinical strategy.",
        ),
    }[key]


def audit(payload: AuditInput) -> AuditOutput:
    if payload.country not in COUNTRIES:
        raise HTTPException(422, "Country not supported by this WHO regional chart")
    cohort = make_synthetic_cohort(payload.cohort_size, payload.seed)
    selections = selections_for(cohort, payload.outreach_capacity, payload.seed)
    all_ids = {p["synthetic_id"] for p in cohort}
    high_total = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in cohort)
    source = source_qa()

    checks = [
        AuditCheck(name="WHO chart structure, 700 PDF-text cells and 28 reference anchors",
                   passed=source.status == "pass_with_limited_source_checks",
                   detail=f"{source.chart_cells} chart cells; {source.pdf_text_cells_matched}/{source.pdf_text_cells_compared} PDF text matches; {source.anchor_cells_matched}/{source.anchor_cells_compared} anchors."),
        AuditCheck(name="Unique synthetic IDs", passed=len(all_ids) == len(cohort),
                   detail=f"{len(all_ids)} unique IDs for {len(cohort)} fabricated records."),
        AuditCheck(name="All three strategies use identical cohort", passed=True,
                   detail="Each selector receives the same generated records and capacity."),
    ]
    for key, chosen in selections.items():
        ids = [p["synthetic_id"] for p in chosen]
        valid = len(chosen) == payload.outreach_capacity and len(set(ids)) == len(ids) and set(ids) <= all_ids
        checks.append(AuditCheck(name=f"Selection invariants · {key}", passed=valid,
                                 detail=f"{len(chosen)} selected; target {payload.outreach_capacity}; all IDs must be unique and in cohort."))
        # Ensure no mutation of cohort was necessary for selection audit.
    checks.append(AuditCheck(name="Seed determinism", passed=cohort == make_synthetic_cohort(payload.cohort_size, payload.seed),
                             detail="Re-generating the same cohort from the same seed yields identical records."))

    details = []
    for key in STRATEGY_KEYS:
        chosen = selections[key]
        sector = _group_coverage(cohort, chosen, "area", SIMULATED_AREAS)
        sex = _group_coverage(cohort, chosen, "sex_reference", ("female", "male"))
        high_selected = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in chosen)
        rule, note = _describe(key)
        details.append(StrategyExplanation(
            key=key,
            selected_count=len(chosen), high_reference_selected=high_selected,
            high_reference_capture_pct=round(100*high_selected/high_total, 2) if high_total else 0.0,
            high_reference_yield_pct=round(100*high_selected/len(chosen), 2) if chosen else 0.0,
            sector_selection_gap_pp=_selection_gap(sector),
            sex_reference_selection_gap_pp=_selection_gap(sex),
            sector_high_coverage=sector, sex_reference_high_coverage=sex,
            decision_rule=rule, note=note,
            selected_ids_sha256=sha256("\n".join(sorted(p["synthetic_id"] for p in chosen)).encode()).hexdigest(),
        ))
        checks.append(AuditCheck(name=f"Subgroup denominators · {key}",
                   passed=sum(x.population_count for x in sector) == len(cohort)
                   and sum(x.selected_count for x in sector) == len(chosen)
                   and sum(x.high_reference_count for x in sector) == high_total
                   and sum(x.high_reference_selected for x in sector) == high_selected
                   and sum(x.population_count for x in sex) == len(cohort)
                   and sum(x.selected_count for x in sex) == len(chosen)
                   and sum(x.high_reference_selected for x in sex) == high_selected,
                   detail="Sector and reference-sex totals reconcile with overall cohort, selection, and high chart-category counts."))

    series: dict[str, dict[str, list[float]]] = {
        key: {metric: [] for metric in ("capture", "sex_gap", "sector_gap", "selected_high")}
        for key in STRATEGY_KEYS
    }
    for i in range(payload.sensitivity_runs):
        shifted_seed = (payload.seed + i) % 1_000_001
        sample = make_synthetic_cohort(payload.cohort_size, shifted_seed)
        sample_high = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in sample)
        for key, selected in selections_for(sample, payload.outreach_capacity, shifted_seed).items():
            selected_high = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in selected)
            sector = _group_coverage(sample, selected, "area", SIMULATED_AREAS)
            sex = _group_coverage(sample, selected, "sex_reference", ("female", "male"))
            values = series[key]
            values["capture"].append(100 * selected_high / sample_high if sample_high else 0.0)
            values["sex_gap"].append(_selection_gap(sex))
            values["sector_gap"].append(_selection_gap(sector))
            values["selected_high"].append(float(selected_high))
    sensitivity = [StrategySensitivity(
        key=key,
        capture_pct=_range(data["capture"]),
        reference_sex_gap_pp=_range(data["sex_gap"]),
        sector_gap_pp=_range(data["sector_gap"]),
        high_reference_selected=_range(data["selected_high"]),
    ) for key, data in series.items()]

    caps = sorted({max(1, payload.outreach_capacity // 2), payload.outreach_capacity,
                   min(payload.cohort_size, max(payload.outreach_capacity+1, payload.outreach_capacity*2))})
    capacity_sensitivity = []
    for cap in caps:
        sel = selections_for(cohort, cap, payload.seed)
        h = {key: sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in selected)
             for key, selected in sel.items()}
        capacity_sensitivity.append(CapacityPoint(
            slots=cap, share_of_cohort_pct=round(100*cap/len(cohort), 2),
            higher_reference_total=high_total,
            chart_first_high_selected=h["chart_descending"],
            sector_balanced_high_selected=h["sector_balanced"],
            random_high_selected=h["seeded_random"],
        ))

    return AuditOutput(
        country=payload.country, cohort_size=len(cohort), outreach_capacity=payload.outreach_capacity,
        seed=payload.seed, sensitivity_runs=payload.sensitivity_runs,
        simulated_high_reference_count=high_total,
        cohort_sha256=_sha256_rows(cohort), source_qa=source,
        checks=checks, software_checks_passed=all(x.passed for x in checks),
        strategies=details, sensitivity=sensitivity,
        capacity_sensitivity=capacity_sensitivity,
        conclusion="The scenario passed reproducible software checks; it has NOT been clinically validated. No model calibration, prediction accuracy, health outcomes, or ethical fairness can be established from synthetic data alone." if all(x.passed for x in checks) else "SOFTWARE QA FAILURE: review failed checks before any further demonstration.",
        limitations=[
            "All 700 WHO non-laboratory chart values match a second transcription of the official PDF text layer. Full visual glyph-level check and independent expert verification remain incomplete.",
            "The WHO table supplies chart-cell reference values; PREVIA is not training or validating a new prediction model.",
            "Cohort attributes are simulated from arbitrary distributions, not representative samples from the selected country.",
            "Seed ranges are descriptive across simulated cohorts, NOT confidence or prediction intervals for a population.",
            "Chart-based capture is evaluated against the same chart used for selection; this is circular and is not clinical accuracy or benefit.",
            "Sector and reference-sex metrics show synthetic selection disparities; equitable clinical impact requires real studies and appropriate subgroup context.",
            "No real patients, adjudicated events, calibration, discrimination, screening uptake, outcomes, implementation costs, or lives saved are measured.",
            "No data are retained by the research evaluation endpoint; download exports are created locally in the user's browser.",
        ],
    )


@router.post("/audit", response_model=AuditOutput)
def audit_endpoint(payload: AuditInput) -> AuditOutput:
    return audit(payload)
