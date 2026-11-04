# PREVIA — Optimisation du seuil sur validation

**Important :** ceci optimise les décisions possibles avec le modèle existant, **sans réentraîner** le ML, **sans reconsulter le jeu de test** et **sans prouver d’efficacité clinique**.

- Modèle initial : `random_forest`
- Observations validation : 466
- ROC-AUC validation : 0.6456
- PR-AUC validation : 0.5984
- Brier validation : 0.2320

| Politique | Seuil | Sensibilité | Spécificité | Précision | Faux négatifs | Faux positifs |
|---|---:|---:|---:|---:|---:|---:|
| Spécificité ≥80 % (v1) | 0.5566 | 33.8% | 80.8% | 60.3% | 143 | 48 |
| Sensibilité ≥70 % | 0.4461 | 70.4% | 51.6% | 55.7% | 64 | 121 |
| Sensibilité ≥80 % | 0.4085 | 80.1% | 40.8% | 53.9% | 43 | 148 |
| Précision équilibrée maximale | 0.3950 | 85.6% | 38.0% | 54.4% | 31 | 155 |

## Lecture correcte
- Les contraintes de sensibilité ou de spécificité sont appliquées uniquement sur validation.
- Un meilleur rappel n’augmente pas nécessairement ROC-AUC ou PR-AUC.
- Un seuil ne peut être proposé pour un usage réel sans critères de coûts, une validation externe et une gouvernance clinique.
- La validation a servi à choisir les seuils : les scores affichés ne sont pas des performances finales indépendantes.

## Audit des groupes (source : fichier JSON)
Les taux sont descriptifs ; les groupes peuvent présenter des tailles et prévalences différentes. Aucun jugement sur l’équité clinique.

## Travail scientifique restant
Conserver la v1 comme seule évaluation test historique, valider le protocole sur un cycle NHANES différent et, à terme, dans la population cible avant tout usage en santé.
