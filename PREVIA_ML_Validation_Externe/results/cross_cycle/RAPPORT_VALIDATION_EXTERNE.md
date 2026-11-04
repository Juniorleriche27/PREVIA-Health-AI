# PREVIA — Enrichissement ML et validation sur un autre cycle NHANES

**Exécution UTC :** 2026-11-04T17:42:18.689392+00:00
**Cible :** HbA1c mesurée ≥ 5,7 % ; association transversale, pas prédiction d'événement futur.
**Entraînement :** 2017–2018 (n=2330).
**Validation externe indépendante :** 2015–2016 (n=2322).

## Décision figée avant évaluation externe
**Modèle retenu sur développement :** `extended_random_forest`.
**Seuil choisi sur prédictions OOF développement :** 0.4147.
**Empreinte décision SHA-256 :** `bcf4adf1ad707617087c1fde60bc80b2c3ec651c1497d8cee7d3445fddca46e5`.

## Comparaison des modèles et variables
| Modèle | Variables | PR-AUC OOF dév. | ROC-AUC OOF dév. | PR-AUC externe | ROC-AUC externe | Brier externe |
|---|---:|---:|---:|---:|---:|---:|
| baseline_logistic | 5 | 0.588 | 0.651 | 0.572 | 0.671 | 0.226 |
| baseline_random_forest | 5 | 0.590 | 0.652 | 0.572 | 0.662 | 0.228 |
| extended_logistic | 10 | 0.594 | 0.653 | 0.579 | 0.672 | 0.225 |
| extended_random_forest | 10 | 0.598 | 0.654 | 0.583 | 0.668 | 0.227 |
| extended_hist_gradient_boosting | 10 | 0.586 | 0.644 | 0.566 | 0.655 | 0.228 |

## Résultats du modèle choisi sur 2015–2016 (non utilisés pour l’optimisation)
- **ROC-AUC : 0.6679**
- **PR-AUC (AP) : 0.5832**
- **Brier : 0.2267**
- **Sensibilité : 78.99%**
- **Spécificité : 45.11%**
- **Précision : 52.73%**
- Matrice TN / FP / FN / TP : {'tn': 590, 'fp': 718, 'fn': 213, 'tp': 801}
- Baseline constante, PR-AUC : 0.4367

## Incertitude descriptive (bootstrap i.i.d., non pondéré)
- roc_auc : [0.649 ; 0.690]
- pr_auc_ap : [0.554 ; 0.620]
- sensitivity : [0.768 ; 0.816]
- specificity : [0.423 ; 0.479]

## Importance descriptive des variables (permutation, cycle externe)
| Variable | Baisse de PR-AUC après permutation |
|---|---:|
| age | 0.0288 |
| bmi | 0.0182 |
| sbp | 0.0090 |
| high_cholesterol_history | 0.0080 |
| waist_cm | 0.0079 |
| hypertension_history | 0.0065 |
| work_activity | 0.0026 |
| sex | 0.0022 |
| leisure_activity | 0.0018 |
| smoking | 0.0016 |

## Qualité des données et comparabilité

| Variable | Manquants 2017–18 | Manquants 2015–16 |
|---|---:|---:|
| age | 0.0% | 0.0% |
| sex | 0.0% | 0.0% |
| bmi | 1.0% | 0.9% |
| sbp | 4.2% | 2.3% |
| smoking | 0.0% | 0.1% |
| waist_cm | 3.9% | 4.2% |
| hypertension_history | 0.1% | 0.0% |
| high_cholesterol_history | 0.4% | 0.5% |
| leisure_activity | 0.0% | 0.0% |
| work_activity | 0.2% | 0.1% |

## Garde-fous scientifiques
- Cross-sectional association, not future diabetes risk or ten-year cardiovascular risk.
- The 2015-16 cycle precedes training's 2017-18 cycle; this is cross-cycle, not prospective temporal forecasting.
- HbA1c measurement assay, procedures and survey composition should be checked for cross-cycle comparability.
- NHANES uses a complex survey design; reported metrics and iid bootstrap are unweighted, not nationally representative.
- Self-report of known diabetes used for exclusion; reporting error and undiagnosed disease possible.
- Missing exam or questionnaire values may introduce selection bias; missing predictors are imputed inside pipelines.
- Sex and age group performance differences are descriptive, not clinical fairness conclusions.
- External scores were consulted only after all models and thresholds were frozen; do not tune on these scores.
- No Togolese clinical cohort, outcome validation, clinical approval or safe referral assessment.
- Not intended for patient-level use. No raw SEQN or row-level predictions exported.

**Fichiers d'audit :** `SCORES_VALIDATION_EXTERNE.json`, `DEVELOPMENT_FROZEN.json` et empreintes SHA-256 des XPT.
**Modèle de recherche :** `PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib` (chargement local uniquement).
