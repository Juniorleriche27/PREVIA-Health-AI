# PREVIA — Traçabilité scientifique des composants ML, XAI et RAG

## Modèle réutilisé, sans réentraînement

Artefact attendu sur le PC utilisateur :
`PREVIA_ML_Validation_Externe/results/cross_cycle/PREVIA_HBA1C_MODEL_CROSS_CYCLE.joblib`

Protocole attendu : `DEVELOPMENT_FROZEN.json`, performances rapportées : `SCORES_VALIDATION_EXTERNE.json`.

La décision modèle + seuil provient **exclusivement du cycle de développement**. La validation entre cycles 2015–2016 est conservée comme évaluation historique. Ce module ne procède à aucune nouvelle recherche d'hyperparamètres ou de seuil.

Résultats communiqués par la personne ayant exécuté le modèle :

| Indicateur | Modèle sélectionné |
|---|---:|
| Développement NHANES 2017–2018 | 2 330 participants |
| Validation entre cycles 2015–2016 | 2 322 participants |
| ROC-AUC externe | 0,6679 |
| PR-AUC externe | 0,5832 |
| Sensibilité externe | 78,99 % |
| Spécificité externe | 45,11 % |
| Seuil de développement | 0,4147 |

Ces chiffres **ne sont pas reproduits dans ce conteneur**, qui ne possède ni les fichiers CDC XPT ni le joblib entraîné sous Windows. L'API lit les fichiers de scores existants plutôt que de recopier ces chiffres dans le code. Ils ne deviennent pas de nouvelles performances avec l'ajout de SHAP.

## Vérifications XAI

- Version de test sur **modèle synthétique** (pas de données de santé réelles), mêmes catégories et même chaîne de transformations.
- Vérifier le cumul des contributions des catégories `OneHotEncoder`, y compris les indicateurs de manquants.
- Vérifier additivité : \( p(y=1\mid x) = E[f(x)] + \sum_j \phi_j \) pour le modèle de classification Random Forest.
- Vérifier aucune information de variable cible `LBXGH`, `hba1c`, `SEQN`, `target` en entrée.
- Contrôler le numéro de modèle SHA-256 et sa signature de variables.

La vérification du modèle réel et l'affichage web sur Windows sont des étapes finales de validation à effectuer à l'installation.

## Sources du RAG

Corpus local : `knowledge/curated_sources.json`. Les passages sont des **paraphrases courtes** de pages officielles :

- OMS — Risk charts 2019 : https://www.who.int/news/item/02-09-2019-who-updates-cardiovascular-risk-charts
- OMS — HEARTS risk-based CVD management : https://www.who.int/publications/i/item/hearts-technical-package
- OMS — HEARTS systems for monitoring : https://www.who.int/publications/i/item/WHO-NMH-NVI-18-5
- OMS — HEARTS healthy-lifestyle counselling : https://www.who.int/publications/i/item/WHO-NMH-NVI-18-1
- OMS — CVD factsheet : https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-%28CVDs%29
- CDC — A1C test : https://www.cdc.gov/diabetes/diabetes-testing/prediabetes-a1c-test.html
- CDC — Diabetes testing : https://www.cdc.gov/diabetes/diabetes-testing/index.html
- CDC — Preventing type 2 diabetes : https://www.cdc.gov/diabetes/prevention-type-2/index.html
- NIDDK — Tests and diagnosis : https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis

Le seuil HbA1c 5,7 % est celui retenu par les catégories usuelles du CDC pour le prédiabète. **Il s'agit d'une cible de recherche**, pas d'un test de diagnostic réalisé par PREVIA.

## Périmètre des preuves

Validé par tests du patch : cohérence de SHAP sur modèle artificiel, restitution des sources, pertinence de questions tests et refus de posologie. Non prouvé : calibrage sur une population cible, robustesse en situation médicale réelle, qualité d'un modèle LLM installé sur PC, sûreté clinique, bénéfices de santé, coût du programme de dépistage. Les tests logiciels ne constituent pas de validation médicale.
