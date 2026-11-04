"""PREVIA v0.7: privacy-preserving, synthetic screening-to-review pathway demo.

Nothing in this module represents a patient, real appointment, clinical triage,
referral, outreach communication, or actual uptake. All events are re-simulated
on each request; the server keeps no workflow data or user records.
"""
from __future__ import annotations

from collections import Counter
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .population import SIMULATED_AREAS, ScenarioInput, make_synthetic_cohort
from .prioritization import choose_by_chart, choose_by_sector, choose_random
from .who_chart import COUNTRIES, REGION, SOURCE

router = APIRouter(prefix="/api/v1/pathways", tags=["Prevention pathway — synthetic demo"])

StrategyKey = Literal["chart_descending", "sector_balanced", "seeded_random"]
Stage = Literal["identified", "invited", "engaged", "offered", "booked", "attended", "reviewed", "declined"]
ActionKey = Literal["invite", "acknowledge", "offer_screening", "book", "attend", "review", "decline", "reopen"]

MILESTONES: tuple[str, ...] = ("identified", "invited", "engaged", "offered", "booked", "attended", "reviewed")
NEXT_ACTION = {
    "identified": "invite", "invited": "acknowledge", "engaged": "offer_screening",
    "offered": "book", "booked": "attend", "attended": "review", "reviewed": None,
    "declined": "reopen",
}
STAGE_FOR_ACTION = {
    "invite": "invited", "acknowledge": "engaged", "offer_screening": "offered",
    "book": "booked", "attend": "attended", "review": "reviewed", "reopen": "invited",
}
# Ratios below are invented user-interface demonstration fixtures, not health-system
# rates, priors, estimates or evidence. Each later stage is a subset of the former.
DEMO_PROGRESS_RATIOS = (1.0, 0.85, 0.67, 0.54, 0.40, 0.27, 0.14)


class DemoEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    synthetic_id: str = Field(pattern=r"^SYN-[0-9]{4}$")
    action: ActionKey


class PathwayInput(ScenarioInput):
    strategy: StrategyKey = "chart_descending"
    confirm_synthetic_demo: bool = False
    events: list[DemoEvent] = Field(default_factory=list, max_length=200)


class CaseRow(BaseModel):
    synthetic_id: str
    demonstration_sector: str
    age_band: str
    chart_value_percent: int
    stage: Stage
    furthest_step: str
    next_actions: list[ActionKey]


class FunnelStep(BaseModel):
    key: str
    count: int
    share_of_selected_pct: float
    conversion_from_previous_pct: float | None


class SectorStep(BaseModel):
    sector: str
    selected: int
    reviewed_in_demo: int
    reviewed_rate_pct: float


class PathwaySummary(BaseModel):
    selected: int
    invited: int
    engaged: int
    offered: int
    booked: int
    attended: int
    reviewed: int
    declined: int
    awaiting_action: int
    invited_share_pct: float
    attended_share_pct: float
    reviewed_share_pct: float
    sector_reviewed_rate_gap_pp: float


class PathwayOutput(BaseModel):
    data_type: Literal["synthetic_workflow_simulation"] = "synthetic_workflow_simulation"
    country: str
    region: str = REGION
    source_url: str = SOURCE
    who_hearts_source_url: str = "https://www.who.int/publications/i/item/9789240001367/"
    strategy: StrategyKey
    cohort_size: int
    selected_count: int
    seed: int
    events_replayed: int
    summary: PathwaySummary
    funnel: list[FunnelStep]
    demonstration_sectors: list[SectorStep]
    cases: list[CaseRow]
    guidance: list[dict[str, str]]
    limitations: list[str]
    clinical_use: str = "RESEARCH DEMONSTRATION ONLY — no patients, medical referrals or actual appointments."
    data_storage: str = "Stateless API. No case data, events or identifiers are saved by the server."


def _selected_profiles(cohort: list[dict], capacity: int, seed: int, strategy: str) -> list[dict]:
    if strategy == "chart_descending":
        return choose_by_chart(cohort, capacity)
    if strategy == "sector_balanced":
        return choose_by_sector(cohort, capacity)
    return choose_random(cohort, capacity, seed)


def _baseline(selected: list[dict]) -> dict[str, dict]:
    """Construct a visible, entirely fictional funnel without random rates."""
    n = len(selected)
    quotas = [int(n * r) for r in DEMO_PROGRESS_RATIOS]
    result: dict[str, dict] = {}
    for idx, profile in enumerate(sorted(selected, key=lambda p: p["synthetic_id"])):
        furthest = max(i for i, quota in enumerate(quotas) if idx < quota)
        result[profile["synthetic_id"]] = {
            "profile": profile,
            "stage": MILESTONES[furthest],
            "furthest": furthest,
        }
    return result


def _apply_event(state: dict, event: DemoEvent, position: int) -> None:
    current = state["stage"]
    action = event.action
    if action == "decline":
        if current in ("identified", "reviewed", "declined"):
            raise ValueError(f"Event {position}: decline is not permitted from {current}.")
        state["stage"] = "declined"
        return
    if NEXT_ACTION[current] != action:
        raise ValueError(f"Event {position}: {action} cannot follow {current}.")
    new_stage = STAGE_FOR_ACTION[action]
    state["stage"] = new_stage
    state["furthest"] = max(state["furthest"], MILESTONES.index(new_stage))


def _pct(a: int, b: int) -> float:
    return round(a * 100 / b, 2) if b else 0.0


def _guidance() -> list[dict[str, str]]:
    return [
        {
            "title": "Confirm context and measurement quality",
            "description": "Review the scope and reliability of blood-pressure and other inputs with a qualified professional before interpreting a chart value.",
            "basis": "WHO HEARTS risk-based cardiovascular disease management",
        },
        {
            "title": "Discuss prevention together",
            "description": "Use shared clinical discussion about modifiable risks and suitable screening. The prototype never prescribes tests, medicines, or a treatment interval.",
            "basis": "WHO HEARTS risk-based CVD management and healthy-lifestyle counselling",
        },
        {
            "title": "Document the pathway, not a diagnosis",
            "description": "A real service would require explicit consent, authenticated staff, approved protocols, and a separate auditable health-record system. None is connected in this demo.",
            "basis": "WHO HEARTS team-based care and systems for monitoring",
        },
    ]


@router.post("/simulate", response_model=PathwayOutput)
def simulate_pathway(payload: PathwayInput) -> PathwayOutput:
    if not payload.confirm_synthetic_demo:
        raise HTTPException(status_code=422, detail="Confirm this simulation uses fictitious records only.")
    if payload.country not in COUNTRIES:
        raise HTTPException(status_code=422, detail="Country outside the implemented WHO reference region.")

    cohort = make_synthetic_cohort(payload.cohort_size, payload.seed)
    selection = _selected_profiles(cohort, payload.outreach_capacity, payload.seed, payload.strategy)
    state = _baseline(selection)
    for pos, event in enumerate(payload.events, 1):
        if event.synthetic_id not in state:
            raise HTTPException(status_code=422, detail=f"Event {pos}: ID is not in this synthetic selection.")
        try:
            _apply_event(state[event.synthetic_id], event, pos)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    rows: list[CaseRow] = []
    for id_, s in sorted(state.items()):
        profile = s["profile"]
        actions: list[ActionKey] = []
        candidate = NEXT_ACTION[s["stage"]]
        if candidate is not None:
            actions.append(candidate)  # type: ignore[arg-type]
        if s["stage"] in ("invited", "engaged", "offered", "booked"):
            actions.append("decline")
        rows.append(CaseRow(
            synthetic_id=id_, demonstration_sector=profile["area"],
            age_band=profile["age_band"], chart_value_percent=profile["who_chart_value_percent"],
            stage=s["stage"], furthest_step=MILESTONES[s["furthest"]], next_actions=actions,
        ))

    n = len(rows)
    milestone_counts = [sum(s["furthest"] >= i for s in state.values()) for i in range(len(MILESTONES))]
    funnel = [FunnelStep(
        key=step, count=count, share_of_selected_pct=_pct(count, n),
        conversion_from_previous_pct=_pct(count, milestone_counts[i - 1]) if i else None,
    ) for i, (step, count) in enumerate(zip(MILESTONES, milestone_counts))]
    statuses = Counter(s["stage"] for s in state.values())
    sectors: list[SectorStep] = []
    for sector in SIMULATED_AREAS:
        local = [s for s in state.values() if s["profile"]["area"] == sector]
        reviewed = sum(s["furthest"] >= 6 for s in local)
        sectors.append(SectorStep(sector=sector, selected=len(local), reviewed_in_demo=reviewed,
                                  reviewed_rate_pct=_pct(reviewed, len(local))))
    active_rates = [s.reviewed_rate_pct for s in sectors if s.selected]
    return PathwayOutput(
        country=payload.country, strategy=payload.strategy, cohort_size=payload.cohort_size,
        selected_count=n, seed=payload.seed, events_replayed=len(payload.events),
        summary=PathwaySummary(
            selected=n, invited=milestone_counts[1], engaged=milestone_counts[2],
            offered=milestone_counts[3], booked=milestone_counts[4],
            attended=milestone_counts[5], reviewed=milestone_counts[6],
            declined=statuses["declined"],
            awaiting_action=n - statuses["reviewed"] - statuses["declined"],
            invited_share_pct=_pct(milestone_counts[1], n),
            attended_share_pct=_pct(milestone_counts[5], n),
            reviewed_share_pct=_pct(milestone_counts[6], n),
            sector_reviewed_rate_gap_pp=(round(max(active_rates) - min(active_rates), 2) if active_rates else 0.0),
        ),
        funnel=funnel, demonstration_sectors=sectors, cases=rows,
        guidance=_guidance(),
        limitations=[
            "All IDs, sectors, profiles and workflow statuses are fictitious; the application does not contact anybody.",
            "Initial funnel stages derive from arbitrary fixed demo ratios (85%, 67%, 54%, 40%, 27%, 14%), NOT research or observed uptake.",
            "Status 'reviewed' denotes a fake workflow milestone, not a completed clinical review or medical outcome.",
            "The WHO chart helps illustrate a reference value, not a validated individualized diagnosis or a referral rule.",
            "The selected strategy does not imply clinical triage, equitable healthcare delivery, or superiority in real-world prevention.",
            "The simulated conversion and sector figures are not clinical performance, program uptake or fairness metrics.",
            "No appointments, emails, messages, referrals or health records are created or stored; explicit server-side consent and authenticated clinical governance would be required for real use.",
        ],
    )
