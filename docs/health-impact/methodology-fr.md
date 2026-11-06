# Méthodologie reproductible

## Question d'évaluation

Sous des capacités de dépistage simulées, comment les trois règles d'allocation implémentées par PREVIA modifient-elles la couverture d'une catégorie descriptive OMS, les écarts de sélection entre groupes fictifs et la stabilité des résultats entre cohortes synthétiques ?

## Source, population et provenance

La grille utilisée est la grille OMS 2019 non biologique pour l'Afrique subsaharienne occidentale, référencée dans `backend/app/who_chart.py`. L'implémentation contient 700 cellules (7 âges × 4 quadrants sexe de référence/tabagisme × 5 pressions × 5 IMC). Le module d'audit compare les 700 valeurs à une seconde transcription de la couche texte du PDF et 28 cellules d'ancrage; une revue visuelle indépendante, glyphe par glyphe, reste à réaliser.

La cohorte est créée par `make_synthetic_cohort` et ne représente aucun pays. Le pays choisi ne change que le libellé régional pris en charge, pas la distribution des variables.

| Variable | Génération synthétique |
|---|---|
| Âge | entier uniforme 40–74 ans |
| Sexe de référence de la grille | choix pseudo-aléatoire homme/femme |
| Tabagisme actuel | Bernoulli, probabilité 0,22 |
| Pression systolique | entier uniforme 105–190 mmHg |
| IMC | uniforme 19,0–39,0, arrondi à 0,1 |
| Secteur | affectation cyclique A–D, libellés fictifs |

## Configuration préspécifiée

```json
{
  "cohort_size": 240,
  "capacities": [24, 45, 72, 120],
  "seeds": [2026, 2027, "...", 2055],
  "baseline_seed": 2026,
  "priority_definition": "WHO chart-cell value >= 10%",
  "strategies": ["chart_descending", "sector_balanced", "seeded_random"]
}
```

Les graines sont des scénarios de sensibilité, non un échantillon statistique d'une population. Aucun test d'hypothèse ni intervalle de confiance populationnel n'est calculé.

## Comparateurs réellement implémentés

1. `chart_descending` : valeur de cellule OMS décroissante, identifiant synthétique comme départage déterministe.
2. `sector_balanced` : sélection successive du secteur ayant la plus faible fraction déjà sélectionnée, puis valeur OMS décroissante dans ce secteur.
3. `seeded_random` : échantillon pseudo-aléatoire sans remise, avec une graine séparée et reproductible.

Les trois règles reçoivent le même objet cohorte et la même capacité; elles ne régénèrent pas leurs propres profils.

## Indicateurs

Soient `N` le nombre de profils, `K` la capacité, `H` le nombre de profils dont la cellule OMS est ≥10 %, `Hₛ` le nombre de ces profils sélectionnés, `Nᵍ` et `Kᵍ` les effectifs et sélections du groupe `g`.

- couverture descriptive des profils prioritaires : `100 × Hₛ / H`;
- rendement descriptif : `100 × Hₛ / K`;
- taux de sélection du groupe : `100 × Kᵍ / Nᵍ`;
- écart de taux de sélection : maximum moins minimum des taux de groupes, en points de pourcentage;
- couverture prioritaire du groupe : profils ≥10 % sélectionnés dans `g` divisés par tous les profils ≥10 % de `g`;
- écart de couverture prioritaire : maximum moins minimum des couvertures prioritaires des groupes ayant un dénominateur non nul;
- stabilité : minimum, médiane, moyenne, maximum et écart-type population sur les 30 graines artificielles.

Tous les arrondis de restitution sont à deux décimales. Les comptes entiers sont calculés avant arrondi.

## Dépendance circulaire

`chart_descending` optimise directement la valeur qui définit `H`. Sa bonne couverture est donc attendue par construction. `sector_balanced` classe également par cette valeur à l'intérieur de chaque secteur. En conséquence :

- la comparaison mesure la fidélité à une règle de classement;
- elle ne mesure pas la sensibilité clinique, la calibration ou l'utilité médicale;
- le tirage aléatoire est un contrôle d'allocation, pas un standard de soins;
- aucun classement de « meilleure stratégie clinique » n'est produit.

## Contrôles qualité et traçabilité

- validation des bornes `0 ≤ sélectionnés prioritaires ≤ min(K,H)`;
- unicité des identifiants et absence de mutation de la cohorte;
- réconciliation des comptes globaux et par groupe;
- répétition bit-à-bit dans deux répertoires temporaires;
- empreinte SHA-256 de la cohorte de référence et de chaque CSV;
- manifeste sans horodatage variable pour permettre une comparaison exacte;
- tests de non-régression du scénario historique à 45 places.

## Reproduction

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_health_impact.py
& .\.venv\Scripts\python.exe -m pytest backend\tests\test_health_impact.py -q
```

Pour une expérience alternative explicitement étiquetée :

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_health_impact.py `
  --output-dir .\temp-impact `
  --cohort-size 240 `
  --capacities 24 45 72 120 `
  --seed-start 2026 `
  --seed-count 30
```

## Audit des composants existants

| Module | Vérification | Conclusion |
|---|---|---|
| Dépistage OMS | bornes, 700 cellules, ancrages, catégories, source | cohérence logicielle; validation clinique non établie |
| Population | génération déterministe, distributions, absence de données réelles | appropriée à une démonstration logicielle uniquement |
| Stratégies | mêmes profils/capacités, règles et départages explicites | comparaison reproductible; critère OMS dépendant |
| Audit scientifique | intégrité, empreintes, sensibilités | QA logicielle; pas une étude d'efficacité |
| NHANES/SHAP | séparation de l'objectif HbA1c et des explications | exclus de l'évaluation cardiovasculaire/allocation |
| RAG/Knowlia | séparation de la synthèse documentaire | aucune contribution aux valeurs calculées |

## Limites

Les distributions artificielles, le faible nombre de dimensions de groupe et l'absence d'issues rendent impossible toute conclusion épidémiologique ou causale. Le seuil de 10 % est un libellé expérimental. Les catégories binaires de sexe proviennent de la structure de la grille et ne constituent pas une mesure complète du genre. Les secteurs n'ont aucune géographie réelle. Les résultats ne doivent pas être extrapolés.
