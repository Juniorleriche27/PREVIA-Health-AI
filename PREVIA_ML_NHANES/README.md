# PREVIA — Machine Learning scientifique NHANES

Objectif : repérer les adultes de 40–74 ans **sans diabète déclaré** présentant une HbA1c observée >= 5,7 %, avec les 5 entrées pré-analytiques `age`, `sex`, `bmi`, `sbp`, `smoking`.

- Sources : fichiers XPT **officiels CDC NHANES 2017–2018**, jamais des exemples fabriqués.
- La cible est la mesure `LBXGH` du fichier `GHB_J`; cette variable n'est jamais dans les prédicteurs.
- `SEQN` sert aux jointures strictes `one_to_one`, puis est écarté du modèle et des exports.
- Les diagnostics de diabète déjà déclarés (`DIQ010 = 1`) sont exclus ; codes refus/inconnu exclus.
- Imputation et normalisation sont entraînées uniquement sur les partitions d'entraînement pour éviter les fuites.
- Modèles : Dummy, Logistic Regression, RandomForest, HistGradientBoosting.
- Split stratifié fixe 60 % entraînement, 20 % validation, 20 % test isolé ; optimisation CV sur entraînement ; choix de modèle et de seuil sur validation ; une seule mesure finale sur test.
- Métriques : ROC-AUC, PR-AUC, Brier, rappel, spécificité, précision, F1 et matrice de confusion.
- Les données NHANES sont américaines et transversales. Cette expérience **ne prédit ni maladie future, ni événements cardiovasculaires à dix ans**, ni performances au Togo.
- Aucun score réel n'est annoncé avant téléchargement et exécution du code.

## Windows PowerShell — depuis le dossier du projet

Télécharger et entraîner sans édition manuelle (après extraction de ce module dans le projet) :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\PREVIA_ML_NHANES\scripts\run_training.ps1
```

Si les scripts se trouvent dans un autre dossier, depuis celui-ci :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_training.ps1
```

L’environnement Python est isolé dans `.venv_ml` (il ne remplace pas la configuration de PREVIA).

Résultats : `results/nhanes/metrics.json`, `results/nhanes/RAPPORT_ML.md`, `results/nhanes/hba1c_screening_model.joblib`.

Pour ajouter le module à la racine existante : extraire l'archive dans `previa-health-ai-starter`, puis utiliser `powershell -NoProfile -ExecutionPolicy Bypass -File .\PREVIA_ML_NHANES\scripts\run_training.ps1`.

**Ne jamais déployer ce modèle comme diagnostic ou décision clinique sans validation externe et gouvernance adaptée.** Les poids d'enquête NHANES ne sont pas utilisés : résultats prédictifs non pondérés, sans prétention à une estimation représentative de la population.
