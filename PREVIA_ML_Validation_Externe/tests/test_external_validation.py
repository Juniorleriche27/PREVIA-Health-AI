from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "external_validation.py"
spec = importlib.util.spec_from_file_location("previa_external", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_components(n=360, seed=7, start=2000):
    rng = np.random.default_rng(seed)
    seqn = np.arange(start, start + n, dtype=float)
    age = rng.integers(40, 75, n).astype(float)
    bmi = rng.normal(28.5, 5, n).clip(16, 50)
    waist = 55 + bmi * 1.55 + rng.normal(0, 9, n)
    sbp = 100 + age * .35 + bmi * .35 + rng.normal(0, 16, n)
    smoker = rng.choice([1, 2], n, p=[.35, .65])
    smq040 = rng.choice([1, 2, 3], n)
    sex = rng.choice([1, 2], n)
    # Provide a plausible correlation for technical smoke test ONLY.
    effect = -3.5 + .055 * bmi + .009 * (age - 40) + .014 * (waist - 90)
    prob = 1 / (1 + np.exp(-effect))
    target = rng.binomial(1, prob)
    hba1c = np.where(target, 6.1, 5.25) + rng.normal(0, .11, n)
    d = {
        "DEMO": pd.DataFrame({"SEQN": seqn, "RIDAGEYR": age, "RIAGENDR": sex,
                              "WTMEC2YR": np.ones(n)}),
        "BMX": pd.DataFrame({"SEQN": seqn, "BMXBMI": bmi, "BMXWAIST": waist}),
        "BPX": pd.DataFrame({"SEQN": seqn, "BPXSY1": sbp, "BPXSY2": sbp + 2,
                             "BPXSY3": sbp - 3}),
        "SMQ": pd.DataFrame({"SEQN": seqn, "SMQ020": smoker, "SMQ040": smq040}),
        "DIQ": pd.DataFrame({"SEQN": seqn, "DIQ010": np.full(n, 2)}),
        "GHB": pd.DataFrame({"SEQN": seqn, "LBXGH": hba1c}),
        "BPQ": pd.DataFrame({"SEQN": seqn, "BPQ020": rng.choice([1, 2, 9], n),
                             "BPQ080": rng.choice([1, 2, 9], n)}),
        "PAQ": pd.DataFrame({"SEQN": seqn, "PAQ605": rng.choice([1, 2, 9], n),
                             "PAQ620": rng.choice([1, 2, 9], n),
                             "PAQ650": rng.choice([1, 2, 9], n),
                             "PAQ665": rng.choice([1, 2, 9], n)}),
    }
    return d


def test_yes_no_refused_not_negative():
    x = mod.yes_no(pd.Series([1, 2, 7, 9, np.nan]))
    assert x.iloc[0] == "yes" and x.iloc[1] == "no"
    assert x.iloc[2:].isna().all()


def test_activity_missing_handling():
    x = mod.activity_any(pd.Series([1, 2, 9, 2]), pd.Series([9, 2, 2, 1]))
    assert list(x.iloc[[0, 1, 3]]) == ["yes", "no", "yes"]
    assert pd.isna(x.iloc[2])


def test_build_cohort_no_lab_or_subject_id_leakage():
    X, y, counts = mod.build_cohort_from_components(fake_components(), "J")
    assert len(X) == len(y) == counts["labeled_n"]
    assert set(X.columns) == set(mod.EXTENDED_FEATURES)
    assert not set(["SEQN", "LBXGH", "target", "DIQ010", "hba1c"]).intersection(X)
    assert y.nunique() == 2


def test_diagnosed_diabetes_exclusion():
    d = fake_components(400)
    d["DIQ"].loc[:9, "DIQ010"] = 1
    d["DIQ"].loc[10, "DIQ010"] = 9
    _, _, counts = mod.build_cohort_from_components(d, "I")
    assert counts["without_self_reported_diagnosed_diabetes"] == 389


def test_join_duplicate_seqs_rejected():
    d = fake_components()
    d["PAQ"] = pd.concat([d["PAQ"], d["PAQ"].iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Non-unique"):
        mod.build_cohort_from_components(d, "J")


def test_threshold_meets_dev_sensitivity():
    y = np.array([1, 1, 1, 1, 0, 0])
    p = np.array([.7, .8, .2, .1, .3, .4])
    t = mod.choose_threshold(y, p, .75)
    assert (p[y == 1] >= t).mean() >= .75
    assert np.isclose(t, .2)


def test_metrics_confusion_consistent():
    stats = mod.metrics([1, 1, 0, 0], np.array([.8, .1, .9, .2]), .5)
    assert stats["confusion"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
    assert stats["sensitivity"] == .5
    assert stats["specificity"] == .5


def test_full_pipeline_smoke_synthetic(monkeypatch, tmp_path):
    data = {}
    for suffix, seed in (("J", 11), ("I", 22)):
        data[suffix] = mod.build_cohort_from_components(fake_components(400, seed), suffix)
    monkeypatch.setattr(mod, "build_cohort", lambda raw, suffix: data[suffix])
    for suffix in ("J", "I"):
        raw = tmp_path / suffix
        raw.mkdir()
        for prefix in mod.FILES:
            (raw / f"{prefix}_{suffix}.xpt").write_bytes(b"HEADER RECORD mock-file-test")
    out = tmp_path / "outputs"
    report = mod.run(tmp_path / "J", tmp_path / "I", out,
                     folds=3, iterations=1, bootstrap_repeats=10, quick=True)
    assert len(report["external"]["all_predeclared_candidate_scores"]) == 5
    assert report["development"]["winner"] in report["development"]["candidates_frozen"]
    assert 0 <= report["external"]["winner_scores"]["roc_auc"] <= 1
    assert (out / "DEVELOPMENT_FROZEN.json").exists()
    assert (out / "SCORES_VALIDATION_EXTERNE.json").exists()
    assert (out / "RAPPORT_VALIDATION_EXTERNE.md").exists()
    assert (out / "PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib").exists()
    selected = report["development"]["winner"]
    frozen = json.loads((out / "DEVELOPMENT_FROZEN.json").read_text(encoding="utf-8"))
    assert frozen["winner"] == selected
    assert "SEQN" not in report["development"]["candidates_frozen"][selected]["features"]
