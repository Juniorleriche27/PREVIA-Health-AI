# PREVIA — rapport ML NHANES 2017–2018

**Date UTC :** 2026-11-04T17:22:09.487260+00:00
**Cible :** HbA1c observée ≥5,7 % (pas une prédiction cardiovasculaire).
**Population :** 2330 adultes 40–74 ans, hors diabète déjà déclaré.
**Prévalence non pondérée de la cible :** 46.27%
**Partition :** 1398 entraînement / 466 validation / 466 test.

## Comparaison et optimisation (validation uniquement)
| Modèle | ROC-AUC CV | ROC-AUC validation | PR-AUC validation | Brier validation |
|---|---:|---:|---:|---:|
| dummy_prior | 0.500 | 0.500 | 0.464 | 0.249 |
| logistic | 0.641 | 0.644 | 0.607 | 0.235 |
| random_forest | 0.645 | 0.646 | 0.598 | 0.232 |
| hist_gradient_boosting | 0.636 | 0.631 | 0.581 | 0.235 |

**Modèle retenu :** random_forest (choisi sans consulter le test).

## Scores finaux — jeu de test indépendant
- ROC-AUC : **0.697**
- PR-AUC : **0.652**
- Brier : **0.221**
- Seuil retenu sur validation : **0.555**
- Sensibilité : **0.440**
- Spécificité : **0.808**
- Précision : **0.664**
- Matrice TN/FP/FN/TP : **{'tn': 202, 'fp': 48, 'fn': 121, 'tp': 95}**
- IC bootstrap descriptif AUC (test) : **[0.648, 0.737]**

## Importance des variables (permutation, validation)
| Variable | Baisse moyenne ROC-AUC après permutation |
|---|---:|
| age | 0.0666 |
| bmi | 0.0486 |
| sex | 0.0190 |
| sbp | 0.0149 |
| smoking | 0.0130 |

Ces importances décrivent l’association des variables au résultat du modèle; elles ne prouvent pas de causalité.

## Validité et limites
- Cross-sectional association with measured HbA1c, not future disease or 10-year CVD events.
- Self-reported known diabetes excluded, not necessarily undiagnosed cases.
- No survey-weighted or nationally representative population statistics.
- NHANES participants in United States; no validation in Togo.
- Missing measurements and social context can bias results.
- HbA1c can be misleading in some hemoglobin disorders and conditions.
- Not clinical diagnostic or referral software.
- Only validated model metrics from holdout, no clinical utility demonstrated.

Résultats : `metrics.json`. Modèle : `hba1c_screening_model.joblib`.
