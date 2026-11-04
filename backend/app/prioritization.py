"""Auditable, non-clinical comparison of synthetic screening-slot allocation rules.

Reuses the WHO 2019 discrete chart-cell values already implemented by PREVIA.
The outcome is *selection of synthetic high-chart-category profiles*, not
clinical benefit, model accuracy, equity in care, or events prevented.
"""
from __future__ import annotations

from collections import Counter
from random import Random
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .population import ExampleProfile, SIMULATED_AREAS, ScenarioInput, make_synthetic_cohort
from .who_chart import COUNTRIES, REGION, SOURCE

router = APIRouter(prefix="/api/v1/prioritization", tags=["Prioritization — synthetic comparison"])
STRATEGY_KEYS = ("chart_descending", "sector_balanced", "seeded_random")
REFERENCE_THRESHOLD = 10  # Chart-bin >=10%; demo comparison threshold, NOT a referral rule.


class GroupSelection(BaseModel):
    group: str
    population_count: int
    selected_count: int
    selection_rate_pct: float


class StrategyMetrics(BaseModel):
    key: Literal["chart_descending", "sector_balanced", "seeded_random"]
    label: str
    explanation: str
    selected_count: int
    unselected_count: int
    higher_reference_selected: int
    higher_reference_capture_pct: float
    higher_reference_yield_pct: float
    average_chart_value_pct: float
    sector_selection_gap_pp: float
    sex_reference_selection_gap_pp: float
    sector_selection: list[GroupSelection]
    sex_reference_selection: list[GroupSelection]
    selected_synthetic_ids: list[str]
    example_profiles: list[ExampleProfile]


class ComparisonOutput(BaseModel):
    data_type: Literal["synthetic_strategy_comparison"] = "synthetic_strategy_comparison"
    country: str
    region: str = REGION
    source_url: str = SOURCE
    cohort_size: int
    outreach_capacity: int
    seed: int
    higher_reference_in_cohort: int
    higher_reference_threshold_pct: int = REFERENCE_THRESHOLD
    strategies: list[StrategyMetrics]
    limitations: list[str] = Field(default_factory=list)
    clinical_use: str = "RESEARCH DEMONSTRATION ONLY. Not a clinical triage, referral, or outreach allocation tool."


def _groups(population: list[dict], selected: list[dict], key: str, labels: tuple[str, ...]) -> list[GroupSelection]:
    total = Counter(p[key] for p in population)
    chosen = Counter(p[key] for p in selected)
    return [
        GroupSelection(
            group=label,
            population_count=total[label],
            selected_count=chosen[label],
            selection_rate_pct=round(100 * chosen[label] / total[label], 2) if total[label] else 0.0,
        )
        for label in labels
    ]


def _gap(groups: list[GroupSelection]) -> float:
    rates = [g.selection_rate_pct for g in groups if g.population_count]
    return round(max(rates) - min(rates), 2) if rates else 0.0


def choose_by_chart(cohort: list[dict], capacity: int) -> list[dict]:
    return sorted(cohort, key=lambda p: (-p["who_chart_value_percent"], p["synthetic_id"]))[:capacity]


def choose_by_sector(cohort: list[dict], capacity: int) -> list[dict]:
    """Balance sector selection rates, ranking WITHIN each sector by chart value.

    A resource-allocation illustration, not a medically justified equal-access
    policy. Equal sector rates need not represent clinical need or fairness.
    """
    sector_pools = {
        name: sorted((p for p in cohort if p["area"] == name),
                     key=lambda p: (-p["who_chart_value_percent"], p["synthetic_id"]))
        for name in SIMULATED_AREAS
    }
    offsets = {name: 0 for name in SIMULATED_AREAS}
    selected: list[dict] = []
    for _ in range(capacity):
        eligible = [name for name in SIMULATED_AREAS if offsets[name] < len(sector_pools[name])]
        # Equalize the fractions selected, rather than absolute counts when
        # synthetic group sizes differ. Name is a deterministic tie breaker.
        sector = min(eligible, key=lambda name: (offsets[name] / len(sector_pools[name]), name))
        selected.append(sector_pools[sector][offsets[sector]])
        offsets[sector] += 1
    return selected


def choose_random(cohort: list[dict], capacity: int, seed: int) -> list[dict]:
    # Separate PRNG avoids mutating cohort generation and makes runs repeatable.
    return Random(seed ^ 0x5EA15).sample(cohort, k=capacity)


def _metrics(key: str, cohort: list[dict], selected: list[dict], high_total: int) -> StrategyMetrics:
    descriptions = {
        "chart_descending": (
            "Highest WHO chart-cell value first",
            "Select descending reference chart-cell values; tied values use synthetic ID order.",
        ),
        "sector_balanced": (
            "Balanced across demonstration sectors",
            "Approximate equal selection rates between fictitious sectors, using higher chart cells first inside each sector.",
        ),
        "seeded_random": (
            "Reproducible random baseline",
            "Draw synthetic IDs with a fixed seeded pseudorandom sample, irrespective of the WHO chart value.",
        ),
    }
    label, explanation = descriptions[key]
    area_groups = _groups(cohort, selected, "area", SIMULATED_AREAS)
    sex_groups = _groups(cohort, selected, "sex_reference", ("female", "male"))
    high_selected = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in selected)
    sorted_preview = sorted(selected, key=lambda p: (-p["who_chart_value_percent"], p["synthetic_id"]))
    return StrategyMetrics(
        key=key,  # type: ignore[arg-type]
        label=label,
        explanation=explanation,
        selected_count=len(selected),
        unselected_count=len(cohort) - len(selected),
        higher_reference_selected=high_selected,
        higher_reference_capture_pct=round(100 * high_selected / high_total, 2) if high_total else 0.0,
        higher_reference_yield_pct=round(100 * high_selected / len(selected), 2) if selected else 0.0,
        average_chart_value_pct=round(sum(p["who_chart_value_percent"] for p in selected) / len(selected), 2) if selected else 0.0,
        sector_selection_gap_pp=_gap(area_groups),
        sex_reference_selection_gap_pp=_gap(sex_groups),
        sector_selection=area_groups,
        sex_reference_selection=sex_groups,
        selected_synthetic_ids=sorted(p["synthetic_id"] for p in selected),
        example_profiles=[ExampleProfile(**p) for p in sorted_preview[:8]],
    )


@router.post("/compare", response_model=ComparisonOutput)
def compare_strategies(payload: ScenarioInput) -> ComparisonOutput:
    if payload.country not in COUNTRIES:
        raise HTTPException(status_code=422, detail="Country not covered by this WHO reference chart.")

    cohort = make_synthetic_cohort(payload.cohort_size, payload.seed)
    high_total = sum(p["who_chart_value_percent"] >= REFERENCE_THRESHOLD for p in cohort)
    capacity = payload.outreach_capacity
    selections = (
        ("chart_descending", choose_by_chart(cohort, capacity)),
        ("sector_balanced", choose_by_sector(cohort, capacity)),
        ("seeded_random", choose_random(cohort, capacity, payload.seed)),
    )
    return ComparisonOutput(
        country=payload.country,
        cohort_size=len(cohort),
        outreach_capacity=capacity,
        seed=payload.seed,
        higher_reference_in_cohort=high_total,
        strategies=[_metrics(key, cohort, selected, high_total) for key, selected in selections],
        limitations=[
            "All observations and area labels are synthetic and do not represent the population of the chosen country.",
            "The source is the WHO 2019 Western Sub-Saharan Africa non-laboratory chart; chart-bin values are not validated individual predictions.",
            "The 10% chart-cell threshold is a comparison label only, not a clinical referral threshold.",
            "Capture and yield measure selection against the same chart value used by one strategy: they do not demonstrate clinical effectiveness or predictive accuracy.",
            "Sector and sex selection gaps are descriptive differences in simulated selection rates, not proof of fairness or equal health outcomes.",
            "No prevented events, clinical diagnoses, patient outcomes, outreach tasks, or actual healthcare services are estimated or provided.",
            "Selected IDs are fabricated and requests are not persisted by this API.",
        ],
    )
