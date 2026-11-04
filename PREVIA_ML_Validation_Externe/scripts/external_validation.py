"""PREVIA | NHANES 2017-18 development, 2015-16 held-out cycle evaluation.

Research-only ML for *observed* HbA1c >= 5.7%; neither clinical triage
nor future cardiovascular event prediction. No US survey prevalence claims.

The final external cycle is deliberately never involved in model, feature,
threshold or hyperparameter selection. Its labels are opened for evaluation
only after the development-cycle decision is frozen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, balanced_accuracy_score, brier_score_loss,
    confusion_matrix, f1_score, log_loss, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.inspection import permutation_importance

BASE = Path(__file__).resolve().parents[1]
LEGACY = BASE.parent / "PREVIA_ML_NHANES" / "data" / "raw"
EXTERNAL = BASE / "data" / "raw" / "2015_2016"
OUT = BASE / "results" / "cross_cycle"
SEED = 2026
TARGET_THRESHOLD = 5.7
FILES = ("DEMO", "BMX", "BPX", "SMQ", "DIQ", "GHB", "BPQ", "PAQ")
BASE_FEATURES = ["age", "sex", "bmi", "sbp", "smoking"]
ADDITIONAL = ["waist_cm", "hypertension_history", "high_cholesterol_history", "leisure_activity", "work_activity"]
EXTENDED_FEATURES = BASE_FEATURES + ADDITIONAL
NUMERIC = {"age", "bmi", "sbp", "waist_cm"}
CATEGORICAL = set(EXTENDED_FEATURES) - NUMERIC

SELECTED_FIELDS = {
    "DEMO": ["RIDAGEYR", "RIAGENDR", "WTMEC2YR"],
    "BMX": ["BMXBMI", "BMXWAIST"],
    "BPX": ["BPXSY1", "BPXSY2", "BPXSY3"],
    "SMQ": ["SMQ020", "SMQ040"],
    "DIQ": ["DIQ010"],
    "GHB": ["LBXGH"],
    "BPQ": ["BPQ020", "BPQ080"],
    "PAQ": ["PAQ605", "PAQ620", "PAQ650", "PAQ665"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_component(raw: Path, prefix: str, suffix: str) -> pd.DataFrame:
    file = raw / f"{prefix}_{suffix}.xpt"
    if not file.is_file():
        raise FileNotFoundError(f"Missing CDC XPT source: {file}. Use run_validation.ps1.")
    with file.open("rb") as stream:
        magic = stream.read(80)
    if b"HEADER RECORD" not in magic:
        raise ValueError(f"{file}: file header is not SAS XPORT; download may be an HTML error page")
    df = pd.read_sas(file, format="xport", encoding="utf-8")
    expected = ["SEQN", *SELECTED_FIELDS[prefix]]
    missing = sorted(set(expected) - set(df.columns))
    if missing:
        raise ValueError(f"{file.name}: NHANES schema mismatch, missing {missing}")
    df = df.loc[:, expected].copy()
    if df.SEQN.isna().any() or df.SEQN.duplicated().any():
        raise ValueError(f"{file.name}: invalid or duplicate SEQN; unsafe join")
    return df


def yes_no(series: pd.Series) -> pd.Series:
    # Codes 7 and 9 correspond to refusal or missing information, NOT 'no'.
    return series.map({1: "yes", 2: "no"})


def activity_any(first: pd.Series, second: pd.Series) -> pd.Series:
    # PAQ answers 1=yes 2=no; any unknown with no definite yes => missing.
    result = pd.Series(index=first.index, dtype=object)
    result.loc[first.eq(2) & second.eq(2)] = "no"
    result.loc[first.eq(1) | second.eq(1)] = "yes"
    return result


def build_cohort_from_components(components: dict[str, pd.DataFrame], suffix: str):
    demo = components["DEMO"]
    data = demo.loc[demo.RIDAGEYR.between(40, 74)].copy()
    counts: dict[str, Any] = {"cycle_suffix": suffix, "aged_40_74": int(len(data))}
    if counts["aged_40_74"] < 1:
        raise ValueError("No participants aged 40–74")
    for prefix in FILES:
        if prefix == "DEMO":
            continue
        right = components[prefix]
        if right.SEQN.isna().any() or right.SEQN.duplicated().any():
            raise ValueError(f"Non-unique SEQN for {prefix}")
        old_size = len(data)
        data = data.merge(right, on="SEQN", how="left", validate="one_to_one")
        if len(data) != old_size:
            raise AssertionError(f"Join expanded participant rows: {prefix}")
    # Exclude known diabetes (DIQ010=1) and unknown/refused diagnosis codes.
    # DIQ010=3 ('borderline') is included, to match the original baseline protocol.
    data = data.loc[data.DIQ010.isin([2, 3])].copy()
    counts["without_self_reported_diagnosed_diabetes"] = int(len(data))

    vals = data.loc[:, ["BPXSY1", "BPXSY2", "BPXSY3"]]
    vals = vals.where(vals.ge(70) & vals.le(260))
    data["sbp"] = vals.mean(axis=1)
    data["age"] = data.RIDAGEYR
    data["bmi"] = data.BMXBMI.where(data.BMXBMI.between(12, 75))
    data["waist_cm"] = data.BMXWAIST.where(data.BMXWAIST.between(40, 220))
    data["sex"] = data.RIAGENDR.map({1: "male", 2: "female"})
    data["smoking"] = pd.Series(index=data.index, dtype=object)
    data.loc[data.SMQ020.eq(2), "smoking"] = "never"
    data.loc[data.SMQ020.eq(1) & data.SMQ040.isin([1, 2]), "smoking"] = "current"
    data.loc[data.SMQ020.eq(1) & data.SMQ040.eq(3), "smoking"] = "former"
    data["hypertension_history"] = yes_no(data.BPQ020)
    data["high_cholesterol_history"] = yes_no(data.BPQ080)
    data["leisure_activity"] = activity_any(data.PAQ650, data.PAQ665)
    data["work_activity"] = activity_any(data.PAQ605, data.PAQ620)
    data["hba1c"] = data.LBXGH.where(data.LBXGH.between(3, 18))
    counts["before_hba1c_filter"] = int(len(data))
    data = data.loc[data.hba1c.notna()].copy()
    data["target"] = data.hba1c.ge(TARGET_THRESHOLD).astype(int)
    # No clinical input may be derived from the laboratory target.
    if any(x in EXTENDED_FEATURES for x in ("hba1c", "LBXGH", "target", "SEQN", "DIQ010")):
        raise AssertionError("Label or protected identifier leakage in feature set")
    if len(data) == 0 or data.target.nunique() < 2:
        raise ValueError("No usable two-class labeled cohort")
    # Age and sex ensure eligible rows have at least two baseline inputs.
    data = data.loc[data[BASE_FEATURES].notna().sum(axis=1).ge(2)].copy()
    counts.update({
        "labeled_n": int(len(data)),
        "target_positive_n": int(data.target.sum()),
        "target_rate_unweighted": float(data.target.mean()),
        "feature_missing": {k: int(data[k].isna().sum()) for k in EXTENDED_FEATURES},
        "feature_missing_rate": {k: float(data[k].isna().mean()) for k in EXTENDED_FEATURES},
        "reference_sex_counts": {str(k): int(v) for k, v in data.sex.value_counts(dropna=False).items()},
    })
    # no SEQN, HbA1c laboratory measurement or diagnosis status in exported features
    return data[EXTENDED_FEATURES].reset_index(drop=True), data.target.reset_index(drop=True), counts


def build_cohort(raw: Path, suffix: str):
    parts = {p: read_component(raw, p, suffix) for p in FILES}
    return build_cohort_from_components(parts, suffix)


def preprocessing(features: list[str], scale: bool) -> ColumnTransformer:
    numeric = [n for n in features if n in NUMERIC]
    categorical = [c for c in features if c in CATEGORICAL]
    num_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("num", Pipeline(num_steps), numeric),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical),
    ])


def candidates() -> dict[str, tuple[list[str], Pipeline, dict]]:
    out = {}
    for level, features in (("baseline", BASE_FEATURES), ("extended", EXTENDED_FEATURES)):
        model = Pipeline([
            ("prep", preprocessing(features, scale=True)),
            ("model", LogisticRegression(max_iter=2000, random_state=SEED)),
        ])
        out[f"{level}_logistic"] = (features, model, {
            "model__C": [0.03, 0.1, 0.3, 1.0, 3.0, 10.0],
            "model__class_weight": [None, "balanced"],
        })
        model = Pipeline([
            ("prep", preprocessing(features, scale=False)),
            ("model", RandomForestClassifier(n_jobs=1, random_state=SEED)),
        ])
        out[f"{level}_random_forest"] = (features, model, {
            "model__n_estimators": [160, 250, 350],
            "model__min_samples_leaf": [4, 8, 16, 24],
            "model__max_depth": [4, 7, None],
            "model__max_features": ["sqrt", 0.8],
        })
        if level == "extended":
            model = Pipeline([
                ("prep", preprocessing(features, scale=False)),
                ("model", HistGradientBoostingClassifier(random_state=SEED)),
            ])
            out["extended_hist_gradient_boosting"] = (features, model, {
                "model__max_leaf_nodes": [7, 15, 31],
                "model__learning_rate": [0.025, 0.05, 0.1],
                "model__min_samples_leaf": [20, 35, 50],
                "model__l2_regularization": [0, 1, 5],
            })
    return out


def metrics(y: pd.Series | np.ndarray, proba: np.ndarray, threshold: float):
    y = np.asarray(y, dtype=np.int32)
    p = np.asarray(proba, dtype=float)
    pred = p >= threshold
    tn, fp, fn, tp = (int(z) for z in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return {
        "n": int(len(y)), "positives": int(y.sum()),
        "positive_fraction_unweighted": float(y.mean()),
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc_ap": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "threshold": float(threshold),
        "sensitivity": float(recall_score(y, pred, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "precision": float(precision_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def choose_threshold(y, p, target_sensitivity: float = 0.80):
    """Largest threshold meeting specified sensitivity on *development OOF* predictions."""
    if not 0 < target_sensitivity <= 1:
        raise ValueError("target_sensitivity must be (0,1]")
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(y) != len(p) or (y == 1).sum() == 0:
        raise ValueError("Need development probabilities and positive labels")
    candidates = np.unique(np.r_[0.0, p, 1.0])
    eligible = [t for t in candidates if np.mean(p[y == 1] >= t) >= target_sensitivity - 1e-12]
    return float(max(eligible))


def subgroup_metrics(X, y, p, threshold):
    table = {}
    age_bands = pd.cut(X.age, [39, 49, 59, 69, 74],
                       labels=["40-49", "50-59", "60-69", "70-74"])
    for label, groups in (("sex", X.sex), ("age_band", age_bands)):
        entries = []
        for group in groups.dropna().unique():
            mask = np.asarray(groups.eq(group))
            yy = np.asarray(y)[mask]; pp = np.asarray(p)[mask]
            if len(yy) < 25 or len(np.unique(yy)) < 2:
                entries.append({"group": str(group), "n": int(len(yy)), "metrics": None,
                                "reason": "Too few participants or one target class"})
            else:
                row = metrics(yy, pp, threshold)
                entries.append({"group": str(group), "n": int(len(yy)), "metrics": {
                    key: row[key] for key in ("positive_fraction_unweighted", "sensitivity", "specificity", "precision", "roc_auc", "pr_auc_ap")}})
        table[label] = entries
    return table


def bootstrap_uncertainty(y, p, threshold, repeats=500):
    """Descriptive iid bootstrap only. DOES NOT account for NHANES survey clusters or weights."""
    yy = np.asarray(y, dtype=int)
    pp = np.asarray(p, dtype=float)
    rng = np.random.default_rng(SEED + 52)
    stats = {"roc_auc": [], "pr_auc_ap": [], "sensitivity": [], "specificity": []}
    for _ in range(repeats):
        idx = rng.integers(0, len(yy), len(yy))
        if len(np.unique(yy[idx])) != 2:
            continue
        z = metrics(yy[idx], pp[idx], threshold)
        for key in stats:
            if z[key] is not None:
                stats[key].append(z[key])
    return {key: {"p2_5": float(np.quantile(v, 0.025)), "p97_5": float(np.quantile(v, 0.975))}
            for key, v in stats.items() if v}


def _search_one(X, y, name, folds, iterations):
    features, model, grid = candidates()[name]
    model_cv = StratifiedKFold(folds, shuffle=True, random_state=SEED)
    max_iter = min(iterations, int(np.prod([len(v) for v in grid.values()])))
    search = RandomizedSearchCV(
        estimator=model, param_distributions=grid, n_iter=max_iter,
        scoring="average_precision", cv=model_cv, random_state=SEED,
        n_jobs=1, refit=True, error_score="raise",
    )
    search.fit(X[features], y)
    oof = cross_val_predict(search.best_estimator_, X[features], y,
                            cv=model_cv, method="predict_proba", n_jobs=1)[:, 1]
    selected_t = choose_threshold(y, oof, target_sensitivity=0.80)
    oof_m = metrics(y, oof, selected_t)
    return features, search, oof_m, selected_t


def run(development_raw: Path, external_raw: Path, out: Path, folds=4, iterations=10,
        bootstrap_repeats=500, quick=False):
    # Freeze design, input feature names and target *before* external labels are read.
    devX, devY, dev_counts = build_cohort(development_raw, "J")
    if len(devY) < 300 or devY.value_counts().min() < folds:
        raise ValueError("Insufficient development labeled sample")
    print(f"Development NHANES 2017-2018: {len(devY)} records; {int(devY.sum())} target+.", flush=True)
    freeze = {}
    fitted = {}
    for name in candidates():
        features, search, oof_m, threshold = _search_one(devX, devY, name, folds, iterations)
        freeze[name] = {
            "features": features,
            "params": search.best_params_,
            "cv_pr_auc": float(search.best_score_),
            "oof": oof_m,
            "oof_screening_threshold": threshold,
        }
        fitted[name] = search.best_estimator_
        print(f"Development: {name:33s} OOF AP={oof_m['pr_auc_ap']:.4f} ROC={oof_m['roc_auc']:.4f}", flush=True)

    # Model selection is a frozen ranking by development out-of-fold AP only.
    winner = max(freeze, key=lambda name: (freeze[name]["oof"]["pr_auc_ap"],
                                         freeze[name]["oof"]["roc_auc"]))
    print(f"Frozen winner (development ONLY): {winner}", flush=True)
    selection_fingerprint = hashlib.sha256(json.dumps({
        "winning_candidate": winner, "parameters": freeze[winner]["params"],
        "decision_threshold": freeze[winner]["oof_screening_threshold"],
        "feature_list": freeze[winner]["features"], "development_source_hashes": {
            p: sha256(development_raw / f"{p}_J.xpt") for p in FILES},
    }, sort_keys=True).encode()).hexdigest()

    # Freeze decisions before touching the external 2015-16 files.
    out.mkdir(parents=True, exist_ok=True)
    frozen = {"frozen_utc": datetime.now(timezone.utc).isoformat(),
              "selection_sha256": selection_fingerprint, "winner": winner,
              "candidate_decisions": freeze, "development_counts": dev_counts}
    (out / "DEVELOPMENT_FROZEN.json").write_text(
        json.dumps(frozen, indent=2, ensure_ascii=False), encoding="utf-8")

    # Models are now refitted on the *full* development cycle. Labels from the
    # completely different external cycle have never entered model fitting.
    for name, model in fitted.items():
        model.fit(devX[freeze[name]["features"]], devY)

    extX, extY, ext_counts = build_cohort(external_raw, "I")
    if len(extY) < 150 or extY.value_counts().min() < 20:
        raise ValueError("Too few external observations for credible two-class evaluation")
    print(f"External NHANES 2015-2016: {len(extY)} records; {int(extY.sum())} target+.", flush=True)

    results = {}
    for name, model in fitted.items():
        p = model.predict_proba(extX[freeze[name]["features"]])[:, 1]
        results[name] = metrics(extY, p, freeze[name]["oof_screening_threshold"])
        print(f"External:    {name:33s} AP={results[name]['pr_auc_ap']:.4f} ROC={results[name]['roc_auc']:.4f}", flush=True)
    external_selected = results[winner]
    chosen_p = fitted[winner].predict_proba(extX[freeze[winner]["features"]])[:, 1]
    external_base = metrics(extY, np.full(len(extY), float(devY.mean())), 0.5)
    uncertainty = bootstrap_uncertainty(extY, chosen_p,
                                        freeze[winner]["oof_screening_threshold"], bootstrap_repeats)
    subgroup = subgroup_metrics(extX, extY, chosen_p, freeze[winner]["oof_screening_threshold"])

    # Post-hoc external permutation importance is DESCRIPTIVE ONLY:
    # it is not used to tune features, thresholds or select any models.
    importance = permutation_importance(
        fitted[winner], extX[freeze[winner]["features"]], extY,
        scoring="average_precision", n_repeats=5 if quick else 8,
        random_state=SEED, n_jobs=1,
    )
    importance_table = sorted([{
        "feature": f, "external_ap_permutation_drop_mean": float(m),
        "external_ap_permutation_drop_sd": float(s),
    } for f, m, s in zip(freeze[winner]["features"],
                        importance.importances_mean, importance.importances_std)],
        key=lambda z: -z["external_ap_permutation_drop_mean"])
    source_hashes = {
        "development_2017_2018": {p: sha256(development_raw / f"{p}_J.xpt") for p in FILES},
        "external_2015_2016": {p: sha256(external_raw / f"{p}_I.xpt") for p in FILES},
    }

    output = {
        "name": "PREVIA - NHANES cross-cycle observed HbA1c>=5.7 screening research",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "development_cycle": "NHANES 2017-2018",
            "external_cycle": "NHANES 2015-2016 (earlier, distinct participants)",
            "labels": "measured LBXGH >= 5.7 percent; no future events",
            "selection": "maximum development-cycle OOF average precision; ROC AUC as tie-breaker",
            "hyperparameters": "RandomizedSearchCV on development cycle only, average_precision",
            "threshold": "highest development-cycle OOF threshold with sensitivity >= 80%",
            "external_usage": "one final evaluation after development decisions frozen; NEVER select on it",
            "data": "unweighted NHANES subsample; NOT US population prevalence",
            "training_cycle_test_reuse": "historic 2017-2018 holdout already consulted; current study uses OOF plus independent 2015-2016 cycle",
            "cross_validation": {"stratified_folds": folds, "random_seed": SEED,
                                  "random_search_iterations": iterations},
            "safe_use": "research demonstration only; no diagnostic, deployment, referral or clinical discrimination claim",
        },
        "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                        "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "development": {"counts": dev_counts, "candidates_frozen": freeze,
                        "selection_sha256": selection_fingerprint, "winner": winner},
        "external": {"counts": ext_counts, "all_predeclared_candidate_scores": results,
                      "winner_scores": external_selected, "constant_prior_baseline": external_base,
                      "descriptive_iid_bootstrap_not_survey_based": uncertainty,
                      "subgroups_descriptive_only": subgroup,
                      "posthoc_external_permutation_importance_not_used_to_tune": importance_table},
        "source_file_sha256": source_hashes,
        "limitations": [
            "Cross-sectional association, not future diabetes risk or ten-year cardiovascular risk.",
            "The 2015-16 cycle precedes training's 2017-18 cycle; this is cross-cycle, not prospective temporal forecasting.",
            "HbA1c measurement assay, procedures and survey composition should be checked for cross-cycle comparability.",
            "NHANES uses a complex survey design; reported metrics and iid bootstrap are unweighted, not nationally representative.",
            "Self-report of known diabetes used for exclusion; reporting error and undiagnosed disease possible.",
            "Missing exam or questionnaire values may introduce selection bias; missing predictors are imputed inside pipelines.",
            "Sex and age group performance differences are descriptive, not clinical fairness conclusions.",
            "External scores were consulted only after all models and thresholds were frozen; do not tune on these scores.",
            "No Togolese clinical cohort, outcome validation, clinical approval or safe referral assessment.",
            "Not intended for patient-level use. No raw SEQN or row-level predictions exported.",
        ],
    }
    (out / "SCORES_VALIDATION_EXTERNE.json").write_text(json.dumps(
        output, indent=2, ensure_ascii=False), encoding="utf-8")
    joblib.dump(fitted[winner], out / "PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib")
    report_lines = make_report(output)
    (out / "RAPPORT_VALIDATION_EXTERNE.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print("\\nFinal report: ", out / "RAPPORT_VALIDATION_EXTERNE.md", flush=True)
    return output


def make_report(output: dict) -> list[str]:
    dev = output["development"]; ext = output["external"]; win = dev["winner"]
    lines = [
        "# PREVIA — Enrichissement ML et validation sur un autre cycle NHANES",
        "", f"**Exécution UTC :** {output['generated_utc']}",
        "**Cible :** HbA1c mesurée ≥ 5,7 % ; association transversale, pas prédiction d'événement futur.",
        f"**Entraînement :** 2017–2018 (n={dev['counts']['labeled_n']}).",
        f"**Validation externe indépendante :** 2015–2016 (n={ext['counts']['labeled_n']}).",
        "", "## Décision figée avant évaluation externe",
        f"**Modèle retenu sur développement :** `{win}`.",
        f"**Seuil choisi sur prédictions OOF développement :** {dev['candidates_frozen'][win]['oof_screening_threshold']:.4f}.",
        f"**Empreinte décision SHA-256 :** `{dev['selection_sha256']}`.",
        "", "## Comparaison des modèles et variables",
        "| Modèle | Variables | PR-AUC OOF dév. | ROC-AUC OOF dév. | PR-AUC externe | ROC-AUC externe | Brier externe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, item in dev["candidates_frozen"].items():
        scores = ext["all_predeclared_candidate_scores"][name]
        lines.append(f"| {name} | {len(item['features'])} | {item['oof']['pr_auc_ap']:.3f} | "
                     f"{item['oof']['roc_auc']:.3f} | {scores['pr_auc_ap']:.3f} | "
                     f"{scores['roc_auc']:.3f} | {scores['brier']:.3f} |")
    z = ext["winner_scores"]
    lines += ["", "## Résultats du modèle choisi sur 2015–2016 (non utilisés pour l’optimisation)",
              f"- **ROC-AUC : {z['roc_auc']:.4f}**",
              f"- **PR-AUC (AP) : {z['pr_auc_ap']:.4f}**",
              f"- **Brier : {z['brier']:.4f}**",
              f"- **Sensibilité : {z['sensitivity']:.2%}**",
              f"- **Spécificité : {z['specificity']:.2%}**",
              f"- **Précision : {z['precision']:.2%}**",
              f"- Matrice TN / FP / FN / TP : {z['confusion']}",
              f"- Baseline constante, PR-AUC : {ext['constant_prior_baseline']['pr_auc_ap']:.4f}",
              "", "## Incertitude descriptive (bootstrap i.i.d., non pondéré)"]
    for key, vals in ext["descriptive_iid_bootstrap_not_survey_based"].items():
        lines.append(f"- {key} : [{vals['p2_5']:.3f} ; {vals['p97_5']:.3f}]")
    lines += ["", "## Importance descriptive des variables (permutation, cycle externe)",
              "| Variable | Baisse de PR-AUC après permutation |", "|---|---:|"]
    for row in ext["posthoc_external_permutation_importance_not_used_to_tune"]:
        lines.append(f"| {row['feature']} | {row['external_ap_permutation_drop_mean']:.4f} |")
    lines += ["", "## Qualité des données et comparabilité", "",
              "| Variable | Manquants 2017–18 | Manquants 2015–16 |", "|---|---:|---:|"]
    for feature in EXTENDED_FEATURES:
        a = dev["counts"]["feature_missing_rate"][feature]
        b = ext["counts"]["feature_missing_rate"][feature]
        lines.append(f"| {feature} | {a:.1%} | {b:.1%} |")
    lines += ["", "## Garde-fous scientifiques", *[f"- {s}" for s in output["limitations"]], "",
              "**Fichiers d'audit :** `SCORES_VALIDATION_EXTERNE.json`, `DEVELOPMENT_FROZEN.json` et empreintes SHA-256 des XPT.",
              "**Modèle de recherche :** `PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib` (chargement local uniquement)."]
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-raw", type=Path, default=LEGACY)
    parser.add_argument("--external-raw", type=Path, default=EXTERNAL)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--bootstrap-repeats", type=int, default=500)
    parser.add_argument("--quick", action="store_true", help="faster technical smoke test, not final research")
    args = parser.parse_args()
    if args.quick:
        args.folds, args.iterations, args.bootstrap_repeats = 3, 2, 25
    if args.folds < 3 or args.iterations < 1 or args.bootstrap_repeats < 10:
        parser.error("Invalid CV/search/bootstrap parameters")
    run(args.development_raw, args.external_raw, args.out,
        args.folds, args.iterations, args.bootstrap_repeats, args.quick)


if __name__ == "__main__":
    main()
