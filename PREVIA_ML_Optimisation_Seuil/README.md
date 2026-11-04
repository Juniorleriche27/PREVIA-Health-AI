# PREVIA — Analyse des seuils de dépistage (v1.1)

Il s'agit d'une étude des **seuils de décision** sur les données de **validation existantes**, sans retoucher le modèle, sans analyser de nouveau le test et sans calculer de nouveaux scores de test indépendants.

## Installation et exécution (Windows PowerShell)

L'archive contient `PREVIA_ML_Optimisation_Seuil/`. Extraire dans le dossier racine de PREVIA existant, puis lancer :

```powershell
$root = "C:\Users\DELL WORKSTATION\previa-health-ai-starter"
Expand-Archive "$env:USERPROFILE\Downloads\PREVIA_ML_Optimisation_Seuil.zip" -DestinationPath $root -Force
cd $root
& ".\PREVIA_ML_NHANES\.venv_ml\Scripts\python.exe" ".\PREVIA_ML_Optimisation_Seuil\scripts\optimize_decisions.py"
```

Rapport : `PREVIA_ML_NHANES/results/threshold_study/RAPPORT_SEUILS.md`.

Ne pas interpréter les politiques simulées comme recommandations cliniques. Une sensibilité plus élevée impose davantage de faux positifs et le modèle n'est pas validé pour la population togolaise.
