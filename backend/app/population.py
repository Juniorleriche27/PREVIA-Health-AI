"""Synthetic population scenario for the PREVIA educational prototype.

No patient records, epidemiological rates, medical outreach orders, or
clinical decisions are produced. The cohort is artificial and seeded so
results are reproducible. No request data are persisted by this module.
"""
from __future__ import annotations

from collections import Counter
from random import Random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .who_chart import COUNTRIES, REGION, SOURCE, lookup

router = APIRouter(prefix='/api/v1/population', tags=['Population — synthetic demonstration'])

AGE_BANDS = ('40–44', '45–49', '50–54', '55–59', '60–64', '65–69', '70–74')
RISK_BANDS = ('<5%', '5% to <10%', '10% to <20%', '20% to <30%', '≥30%')
SIMULATED_AREAS = ('Demo sector A', 'Demo sector B', 'Demo sector C', 'Demo sector D')


class ScenarioInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    country: str = Field(default='Togo', min_length=1, max_length=80)
    cohort_size: int = Field(default=240, ge=40, le=500)
    outreach_capacity: int = Field(default=45, ge=1, le=500)
    seed: int = Field(default=2026, ge=0, le=1_000_000)

    @model_validator(mode='after')
    def check_capacity(self):
        if self.outreach_capacity > self.cohort_size:
            raise ValueError('outreach_capacity cannot exceed cohort_size')
        return self


class CategoryCount(BaseModel):
    category: str
    count: int
    percentage: float


class ExampleProfile(BaseModel):
    synthetic_id: str
    area: str
    age_band: str
    sex_reference: str
    current_smoker: bool
    systolic_bp: int
    bmi: float
    who_chart_value_percent: int
    risk_category: str


class ScenarioOutput(BaseModel):
    data_type: str = 'synthetic_simulation'
    clinical_use: str = 'Not for clinical screening, triage, scheduling, or individual medical decisions.'
    message: str = 'Illustrative allocation using synthetic profiles and WHO chart categories; no measured health outcomes.'
    country: str
    region: str = REGION
    source_url: str = SOURCE
    cohort_size: int
    outreach_capacity: int
    selected_for_demo: int
    unselected_for_demo: int
    higher_chart_category_count: int
    higher_chart_category_share: float
    risk_distribution: list[CategoryCount]
    age_distribution: list[CategoryCount]
    area_distribution: list[CategoryCount]
    sex_reference_distribution: list[CategoryCount]
    demonstration_queue: list[ExampleProfile]
    methodology: list[str]


def summarize(categories: list[str], labels: tuple[str, ...]) -> list[CategoryCount]:
    counts = Counter(categories)
    total = len(categories)
    return [CategoryCount(category=label, count=counts[label], percentage=round(100 * counts[label] / total, 1)) for label in labels]


def make_synthetic_cohort(cohort_size: int, seed: int) -> list[dict]:
    """Generate the SAME reproducible synthetic cohort for all demo modules."""
    rng = Random(seed)
    profiles: list[dict] = []
    for idx in range(cohort_size):
        # Artificial generation is for demonstration, not a model of local prevalence.
        age = rng.randint(40, 74)
        sex = rng.choice(('male', 'female'))
        smoker = rng.random() < 0.22
        sbp = rng.randint(105, 190)
        bmi = round(rng.uniform(19.0, 39.0), 1)
        area = SIMULATED_AREAS[idx % len(SIMULATED_AREAS)]
        cell = lookup(age, sex, smoker, sbp, bmi)
        profiles.append(dict(
            synthetic_id=f'SYN-{idx + 1:04d}',
            area=area, age_band=cell.age_band, sex_reference=sex,
            current_smoker=smoker, systolic_bp=sbp, bmi=bmi,
            who_chart_value_percent=cell.value, risk_category=cell.risk_band,
        ))

    return profiles


@router.post('/scenario', response_model=ScenarioOutput)
def scenario(payload: ScenarioInput) -> ScenarioOutput:
    if payload.country not in COUNTRIES:
        raise HTTPException(status_code=422, detail='Country is not supported by the Western Sub-Saharan Africa WHO chart.')

    profiles = make_synthetic_cohort(payload.cohort_size, payload.seed)

    # Educational ranking by chart-bin value; this is NOT an actual clinical priority list.
    ranked = sorted(profiles, key=lambda row: (-row['who_chart_value_percent'], row['synthetic_id']))
    selected = ranked[:payload.outreach_capacity]
    higher = sum(p['who_chart_value_percent'] >= 10 for p in profiles)
    return ScenarioOutput(
        country=payload.country,
        cohort_size=payload.cohort_size,
        outreach_capacity=payload.outreach_capacity,
        selected_for_demo=len(selected),
        unselected_for_demo=len(profiles) - len(selected),
        higher_chart_category_count=higher,
        higher_chart_category_share=round(100 * higher / len(profiles), 1),
        risk_distribution=summarize([p['risk_category'] for p in profiles], RISK_BANDS),
        age_distribution=summarize([p['age_band'] for p in profiles], AGE_BANDS),
        area_distribution=summarize([p['area'] for p in profiles], SIMULATED_AREAS),
        sex_reference_distribution=summarize([p['sex_reference'] for p in profiles], ('female', 'male')),
        demonstration_queue=[ExampleProfile(**profile) for profile in selected[:8]],
        methodology=[
            'All profiles are artificially generated with a reproducible pseudorandom seed; no individuals or patients are represented.',
            'The distributions of risk factors in this cohort are arbitrary and DO NOT describe prevalence in the selected country.',
            'The WHO 2019 Western Sub-Saharan Africa non-laboratory reference chart is applied as an educational lookup to each synthetic record.',
            'Outreach capacity selects the highest chart-bin values for an illustrative planning scenario only; it is not clinical triage or an outreach recommendation.',
            'No clinical diagnoses, epidemiological forecasts, or numbers of prevented cardiovascular events are estimated.',
            'No uploaded records, identifiers, or scenario data are stored by the backend.',
        ],
    )
