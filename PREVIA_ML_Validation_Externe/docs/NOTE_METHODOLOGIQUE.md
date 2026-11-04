# Note méthodologique — PREVIA ML validation cross-cycle

## Séparation des sources et gel

- Développement / optimisation sur données 2017–2018, sans consulter la validation externe.
- Les résultats du test 2017–2018 de la première expérimentation ont déjà été consultés : ils ne sont **plus** un test neuf pour les optimisations suivantes.
- Décisions de modèle, hyperparamètres, variables, seuil et empreinte des fichiers de développement figées dans `DEVELOPMENT_FROZEN.json`.
- Examen unique des performances sur 2015–2016, distinct de l'entraînement, sans choix opportuniste du meilleur score externe.
- Pour toute itération future après lecture de 2015–2016 : conserver un troisième cycle indépendant pour une nouvelle évaluation finale.

## Sens des indicateurs

- ROC-AUC : classement relatif des profils présentant une HbA1c mesurée élevée.
- PR-AUC (average precision) : précision moyenne intégrée selon le rappel, sensible à la fréquence de la cible.
- Brier : erreur quadratique moyenne des probabilités par rapport à la présence de l'HbA1c élevée.
- Sensibilité/spécificité/PPV : taux sous un seuil **choisi sur le développement**. Aucune valeur de seuil n'est recommandée pour la clinique.
- Baseline : probabilité constante correspondant au taux non pondéré en développement (non représentatif d'une population).
- Les écarts par âge et sexe sont seulement descriptifs, non des preuves d'équité.

## Limitations supplémentaires

- Même HbA1c, mais les phases d'enquête peuvent différer par population, instruments et conditions opérationnelles.
- NHANES 2017–2018 a eu un taux de réponse plus faible que le cycle antérieur (CDC). Les différences de composition exigent une lecture prudente.
- Des prédicteurs auto-déclarés (hypertension, cholestérol, activité) peuvent refléter les différences d'accès aux soins.
- L'ajout de variables ne prouve aucune amélioration ; comparer 5 contre 10 entrées à la lumière des résultats externes.
- La validation croisée ordinaire ne reproduit pas la structure de grappes et de poids NHANES : les scores sont des diagnostics de recherche non pondérés.
- Aucune conséquence médicale ne doit découler automatiquement des scores sans validation locale et contrôle humain.
