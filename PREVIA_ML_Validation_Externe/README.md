# PREVIA Health AI — Expérience ML cross-cycle (v2)

**Objectif de recherche :** estimer la probabilité qu'une mesure de glycohémoglobine HbA1c (variable `LBXGH` de NHANES) soit ≥ 5,7 %, à partir d'informations disponibles avant le résultat du laboratoire. Cette recherche n'est ni un diagnostic ni une prédiction cardiovasculaire future.

## En une commande, depuis le dossier PREVIA dans PowerShell

1. Télécharger `PREVIA_ML_Validation_Externe.zip` et extraire dans la racine de `previa-health-ai-starter` :

```powershell
$root = 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
Expand-Archive -Path "$env:USERPROFILE\Downloads\PREVIA_ML_Validation_Externe.zip" -DestinationPath $root -Force
Set-Location $root
powershell -NoProfile -ExecutionPolicy Bypass -File .\PREVIA_ML_Validation_Externe\scripts\run_validation.ps1
```

Cela réutilise l'environnement ML `.venv_ml` déjà créé dans `PREVIA_ML_NHANES`, récupère les **fichiers CDC XPT** manquants, vérifie les tests, entraîne cinq candidats et évalue les cinq configurations prédéfinies sur 2015–2016. Le modèle recommandé est choisi **avant** l'ouverture des résultats externes.

**Aucun redémarrage de Next.js ou FastAPI n'est nécessaire.** Ce module expérimental est isolé de PREVIA v0.8 ; aucune API ni interface n'est modifiée. Pour redémarrer ultérieurement l'application principale : `Set-Location $root; .\scripts\previa.ps1 restart`.

## Résultats générés sur ton ordinateur

- `results/cross_cycle/RAPPORT_VALIDATION_EXTERNE.md` : tableau des scores **réellement mesurés** ;
- `results/cross_cycle/SCORES_VALIDATION_EXTERNE.json` : ROC-AUC, PR-AUC, Brier, sensibilité, spécificité, FN/FP, sous-groupes, incertitude descriptive ;
- `results/cross_cycle/DEVELOPMENT_FROZEN.json` : décision sélectionnée sur développement et son empreinte SHA-256, enregistrée **avant l'évaluation externe** ;
- `results/cross_cycle/PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib` : pipeline Python entraîné et sérialisé pour recherche uniquement.

Consulter le rapport en UTF-8 :

```powershell
Get-Content .\PREVIA_ML_Validation_Externe\results\cross_cycle\RAPPORT_VALIDATION_EXTERNE.md -Encoding UTF8
```

Les fichiers XPT originaux et leurs empreintes SHA-256 sont conservés. Aucune prédiction individuelle ni identifiant NHANES `SEQN` n'est exporté dans les résultats.

## Méthodologie

**Cycle de développement :** NHANES 2017–2018 (`*_J`, les six fichiers déjà présents et deux nouveaux). 40 à 74 ans, exclusion de l'autodéclaration de diabète connu (`DIQ010=1`) et des réponses invalides ; HbA1c valide (3–18 %) mesurée ; aucune colonne de laboratoire HbA1c en entrée.

**Cycle d'évaluation :** NHANES 2015–2016 (`*_I`). Participants et données distincts ; cycle antérieur, donc **validation entre cycles**, pas prévision prospective.

**Variables de référence (5) :** âge, sexe de référence NHANES, IMC, pression systolique moyenne et tabagisme.

**Variables enrichies (10 au total) :** les cinq précédentes + tour de taille (`BMXWAIST`), antécédent d'hypertension déclaré (`BPQ020`), antécédent d'hypercholestérolémie déclaré (`BPQ080`), activité physique de loisirs (`PAQ650`, `PAQ665`) et activité physique au travail (`PAQ605`, `PAQ620`). Valeurs inconnues codées manquantes, jamais « non ».

**Modèles enregistrés comme candidats avant ouverture externe :** régression logistique et Random Forest, chacun avec 5 ou 10 variables ; HistGradientBoosting avec 10 variables. Comparaison via validation croisée stratifiée et optimisation aléatoire des hyperparamètres sur 2017–2018 seulement. Le modèle retenu maximise la PR-AUC *out-of-fold* du développement, avec la ROC-AUC comme départage. Seuil choisi sur les prédictions OOF pour viser au moins 80 % de sensibilité ; ce niveau **n'est pas garanti** sur 2015–2016.

**Évaluation indépendante :** tous les candidats prédéfinis sont évalués une fois sur 2015–2016 pour comparaison descriptive, mais **aucune sélection ni modification du modèle ne doit se fonder sur ces valeurs**. Les résultats de 2015–2016 deviennent ainsi un banc d'essai consulté : toute optimisation ultérieure exige un autre cycle indépendant.

**Limites :** performances calculées sans pondération NHANES ; études de classification sur une cible transversale, pas estimation du risque de développer un diabète dans le futur. Les métriques ne sont pas représentatives de la population américaine, et encore moins de celle du Togo. Les intervalles bootstrap sont descriptifs, ignorent le plan d'échantillonnage complexe. Les caractéristiques auto-déclarées et la mesure HbA1c comportent des limites. Aucun modèle médical validé pour prise en charge.

## Sources officielles

- [NHANES 2015–2016](https://wwwn.cdc.gov/nchs/nhanes/search/DataPage.aspx?Cycle=2015-2016)
- [NHANES 2017–2018](https://wwwn.cdc.gov/nchs/nhanes/search/DataPage.aspx?Cycle=2017-2018)
- [GHB_I (HbA1c)](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/GHB_I.htm)
- [GHB_J (HbA1c)](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/GHB_J.htm)
- [BPQ_I](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/BPQ_I.htm)
- [PAQ_I](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/PAQ_I.htm)
- [CDC: NHANES Sample Design](https://wwwn.cdc.gov/nchs/nhanes/tutorials/SampleDesign.aspx)

## Intégrité / tests

`tests/test_external_validation.py` couvre notamment l'absence de fuite des identifiants et de la cible HbA1c, le rejet des clés dupliquées, le codage des réponses inconnues, le seuil de décision, la cohérence de la matrice de confusion et un entraînement de bout en bout sur données **artificielles exclusivement**.

Un test synthétique concluant prouve le bon fonctionnement logiciel, **jamais un score NHANES**. Les scores ne sont connus qu'après l'exécution sur les fichiers CDC réels.
