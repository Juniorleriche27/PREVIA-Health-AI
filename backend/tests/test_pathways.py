"""PREVIA v0.7 — verify the synthetic-only prevention workflow contract."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.pathways import DEMO_PROGRESS_RATIOS, MILESTONES, PathwayInput, simulate_pathway
from app.population import make_synthetic_cohort
from app.prioritization import choose_by_chart, choose_by_sector, choose_random

client = TestClient(app)
URL = "/api/v1/pathways/simulate"
BASE = dict(country="Togo", cohort_size=240, outreach_capacity=45, seed=2026,
            strategy="chart_descending", confirm_synthetic_demo=True)


def call(**changes):
    return client.post(URL, json={**BASE, **changes})


def scenario(**changes):
    r = call(**changes)
    assert r.status_code == 200, r.text
    return r.json()


def test_health_version_bumped():
    assert client.get("/health").json()["version"] == "0.8.0"


def test_default_pathway_end_to_end():
    s = scenario()
    assert s["data_type"] == "synthetic_workflow_simulation"
    assert s["clinical_use"].startswith("RESEARCH DEMONSTRATION")
    assert s["summary"]["selected"] == 45
    assert [step["count"] for step in s["funnel"]] == [45, 38, 30, 24, 18, 12, 6]
    assert s["summary"]["attended"] == 12
    assert s["summary"]["reviewed"] == 6
    assert s["events_replayed"] == 0
    assert len(s["cases"]) == 45
    assert len({row["synthetic_id"] for row in s["cases"]}) == 45
    assert all(row["synthetic_id"].startswith("SYN-") for row in s["cases"])
    assert not any(x in s.keys() for x in ("email", "phone", "full_name", "patient"))


def test_demonstration_counts_are_explicitly_not_observed_rates():
    s = scenario()
    assert "arbitrary" in " ".join(s["limitations"]).lower()
    assert "not clinical" in " ".join(s["limitations"]).lower() or "not a validated" in " ".join(s["limitations"]).lower()
    assert DEMO_PROGRESS_RATIOS[-1] == 0.14


def test_production_patient_data_are_not_accepted():
    r = call(name="Person One", phone="+123456789")
    assert r.status_code == 422
    r = call(events=[{"synthetic_id": "SYN-0002", "action":"invite", "notes":"personal history"}])
    assert r.status_code == 422


def test_explicit_synthetic_confirmation_required():
    r = call(confirm_synthetic_demo=False)
    assert r.status_code == 422
    assert "fictitious" in r.json()["detail"]


@pytest.mark.parametrize("country", ["United States", "France", "Unknown", "Ghana "])
def test_unsupported_regions_rejected(country):
    assert call(country=country).status_code == 422


@pytest.mark.parametrize("strategy,selector", [
    ("chart_descending", choose_by_chart),
    ("sector_balanced", choose_by_sector),
    ("seeded_random", choose_random),
])
def test_selected_ids_reuse_prior_validated_strategy(strategy, selector):
    s = scenario(strategy=strategy)
    cohort = make_synthetic_cohort(240, 2026)
    if strategy == "seeded_random":
        expected = selector(cohort, 45, 2026)
    else:
        expected = selector(cohort, 45)
    assert set(x["synthetic_id"] for x in s["cases"]) == set(x["synthetic_id"] for x in expected)


def test_reproducibility_and_reset():
    a, b = scenario(), scenario()
    assert a == b
    assert [x["synthetic_id"] for x in a["cases"]] == sorted(x["synthetic_id"] for x in a["cases"])
    assert a["summary"] == b["summary"]


def test_replay_one_transition_then_reset():
    baseline = scenario()
    target = next(x for x in baseline["cases"] if x["stage"] == "identified")
    updated = scenario(events=[{"synthetic_id": target["synthetic_id"], "action":"invite"}])
    changed = next(x for x in updated["cases"] if x["synthetic_id"] == target["synthetic_id"])
    assert changed["stage"] == "invited"
    assert updated["summary"]["invited"] == baseline["summary"]["invited"] + 1
    assert updated["events_replayed"] == 1
    assert scenario()["events_replayed"] == 0
    assert scenario()["summary"] == baseline["summary"]


def test_full_workflow_for_identified_case():
    target = next(row for row in scenario()["cases"] if row["stage"] == "identified")["synthetic_id"]
    actions = ["invite", "acknowledge", "offer_screening", "book", "attend", "review"]
    events = [{"synthetic_id": target, "action": action} for action in actions]
    done = scenario(events=events)
    row = next(row for row in done["cases"] if row["synthetic_id"] == target)
    assert row["stage"] == "reviewed" and row["next_actions"] == []
    assert done["summary"]["reviewed"] == scenario()["summary"]["reviewed"] + 1
    assert done["funnel"][-1]["count"] == done["summary"]["reviewed"]


def test_decline_followed_by_reopen_and_advance():
    row = next(r for r in scenario()["cases"] if r["stage"] == "booked")
    id_ = row["synthetic_id"]
    events = [{"synthetic_id":id_,"action":"decline"}]
    declined = scenario(events=events)
    record = next(r for r in declined["cases"] if r["synthetic_id"] == id_)
    assert record["stage"] == "declined"
    assert record["furthest_step"] == "booked"
    assert declined["summary"]["declined"] == 1
    reopened = scenario(events=events + [{"synthetic_id":id_,"action":"reopen"}])
    record = next(r for r in reopened["cases"] if r["synthetic_id"] == id_)
    assert record["stage"] == "invited"
    assert record["furthest_step"] == "booked"
    assert reopened["summary"]["declined"] == 0


@pytest.mark.parametrize("stage,illegal_action", [
    ("identified", "book"), ("identified", "decline"),
    ("invited", "attend"), ("engaged", "book"),
    ("offered", "review"), ("booked", "invite"),
    ("attended", "attend"), ("reviewed", "invite"),
])
def test_invalid_transitions_rejected(stage,illegal_action):
    row = next(x for x in scenario()["cases"] if x["stage"] == stage)
    assert call(events=[{"synthetic_id":row["synthetic_id"],"action":illegal_action}]).status_code == 422


def test_id_not_selected_rejected():
    s = scenario()
    selected = set(c["synthetic_id"] for c in s["cases"])
    missed = next(c for c in make_synthetic_cohort(240,2026) if c["synthetic_id"] not in selected)
    assert call(events=[{"synthetic_id":missed["synthetic_id"],"action":"invite"}]).status_code == 422


@pytest.mark.parametrize("bad_id", ["SYN-001", "SYN-12345", "123", "PAT-0001", "SYN-1234<script>"])
def test_bad_id_format_rejected(bad_id):
    assert call(events=[{"synthetic_id":bad_id,"action":"invite"}]).status_code == 422


def test_invalid_action_rejected():
    assert call(events=[{"synthetic_id":"SYN-0001","action":"send_email"}]).status_code == 422


def test_event_limit_prevents_unbounded_input():
    events = [{"synthetic_id":"SYN-0001", "action":"invite"}] * 201
    assert call(events=events).status_code == 422


@pytest.mark.parametrize("capacity", [1,2,7,22,45,90,240])
def test_funnel_monotonic_and_reconciles_at_various_capacities(capacity):
    s = scenario(outreach_capacity=capacity)
    counts = [v["count"] for v in s["funnel"]]
    assert counts[0] == capacity
    assert all(x >= y for x, y in zip(counts,counts[1:]))
    assert len(s["cases"]) == capacity
    assert sum(v["selected"] for v in s["demonstration_sectors"]) == capacity
    assert sum(v["reviewed_in_demo"] for v in s["demonstration_sectors"]) == s["summary"]["reviewed"]
    assert s["summary"]["awaiting_action"] + s["summary"]["declined"] + sum(r["stage"] == "reviewed" for r in s["cases"]) == capacity
    assert all(v["share_of_selected_pct"] <= 100 for v in s["funnel"])


@pytest.mark.parametrize("seed", [0,42,2026,999999])
def test_seed_reproducibility_and_bounds(seed):
    a = scenario(seed=seed, strategy="seeded_random")
    b = scenario(seed=seed, strategy="seeded_random")
    assert a["cases"] == b["cases"]
    assert a["summary"]["selected"] == 45


def test_minimum_cohort_size_and_inputs():
    s = scenario(cohort_size=40, outreach_capacity=3)
    assert s["selected_count"] == 3
    assert call(cohort_size=39).status_code == 422
    assert call(cohort_size=240, outreach_capacity=241).status_code == 422


def test_all_guidance_uses_reputable_source_and_no_prescriptions():
    s = scenario()
    assert s["who_hearts_source_url"].startswith("https://www.who.int/")
    assert len(s["guidance"]) >= 3
    text = " ".join(g["description"] for g in s["guidance"]).lower()
    assert "qualified professional" in text
    assert "prototype never prescribes" in text
    assert "not a diagnosis" in " ".join(s["limitations"]).lower() or "not a validated individualized diagnosis" in " ".join(s["limitations"]).lower()


def test_no_persistence_or_external_operations():
    s = scenario()
    assert "No case data" in s["data_storage"]
    assert "does not contact" in " ".join(s["limitations"])
    assert client.get("/api/v1/pathways/simulate").status_code == 405


def test_all_stages_are_declared():
    assert tuple(STAGE for STAGE in MILESTONES) == ("identified", "invited", "engaged", "offered", "booked", "attended", "reviewed")
