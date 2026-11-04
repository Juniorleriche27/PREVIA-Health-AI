# PREVIA — benchmark réel hors connexion

**Attention :** dataset scikit-learn Diabetes, 442 dossiers, **régression de progression à un an**. Ce n’est **pas** NHANES, pas l’HbA1c ni un modèle clinique PREVIA.

Partitions : 264 entraînement, 89 validation, 89 test indépendant.

| Algorithme | MAE CV | MAE validation | R² validation |
|---|---:|---:|---:|
| ridge | 44.51 | 46.80 | 0.517 |
| elasticnet | 44.49 | 46.99 | 0.514 |
| random_forest | 47.08 | 48.48 | 0.474 |
| hist_gradient_boosting | 46.57 | 51.34 | 0.398 |

**Modèle retenu :** ridge
**Test R² :** 0.528
**Test MAE :** 41.79
**Test RMSE :** 52.92
**Baseline MAE :** 68.40

Ces scores établissent que le pipeline ML sait entraîner/évaluer sur données réelles. Ils ne valident aucun score de dépistage.
