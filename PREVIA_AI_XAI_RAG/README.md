# PREVIA Health AI — Module IA v1.0 (ML + XAI + RAG multi-provider)

Ajout compatible avec **PREVIA v0.8 de Codex**. Aucun fichier backend/app/main.py ou scripts/previa.ps1 de la v0.8 n'est remplacé.

## Architecture

- **Moteur OMS** : conserve sa fonction indépendante pour la référence cardiovasculaire.
- **Modèle ML existant** : Random Forest enrichi sur 10 variables NHANES, entraîné sur 2017–2018 et évalué sur 2015–2016. Le modèle n'est ni réentraîné ni optimisé par ce patch.
- **XAI** : `SHAP.TreeExplainer` du vrai Random Forest local et regroupement des contributions des colonnes après encodage (dont les catégories et indicateurs de valeurs manquantes). Un test d'additivité vérifie que somme des contributions + baseline = sortie du modèle.
- **RAG documentaire indépendant du fournisseur** : index TF-IDF local de courts résumés OMS/CDC/NIDDK. LLM choisi explicitement dans la page, parmi les fournisseurs enregistrés localement. Sans LLM ou en cas d'échec, réponse extractive sourcée. Les questions et extraits sont envoyés au fournisseur externe *uniquement quand il est sélectionné*.
- **API IA isolée** : `127.0.0.1:8766`, pour ne pas perturber le FastAPI historique `8765`.
- **Interface** : `http://localhost:3001/ai` (Next.js v0.8 préservé).

## Installation Windows en terminal VS Code

Télécharger `PREVIA_v0.9_XAI_RAG_patch.zip`, puis depuis n'importe quel dossier PowerShell :

```powershell
$root = 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
Expand-Archive -Path "$env:USERPROFILE\Downloads\PREVIA_v0.9_XAI_RAG_patch.zip" -DestinationPath $root -Force
Set-Location $root
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_previa_ai.ps1
```

La procédure installe les dépendances **dans `.venv_ml` existant** (sans changer l'environnement principal `.venv`), exécute les tests, ajoute la navigation à la page IA, configure l'adresse API, compile Next.js et démarre les services. **Aucune recherche ou édition manuelle de ligne.**

Pour gérer PREVIA + l'API IA ensuite :

```powershell
.\scripts\previa_full.ps1 start
.\scripts\previa_full.ps1 status
.\scripts\previa_full.ps1 restart
.\scripts\previa_full.ps1 verify
.\scripts\previa_full.ps1 diagnose
.\scripts\previa_full.ps1 stop
```

## Choisir librement un fournisseur et un modèle

Le RAG ne dépend d'aucun modèle. Il prend en charge les protocoles **OpenAI-compatible**, **Anthropic**, **Gemini** et **Cohere** ; tout autre modèle utilisant l'un de ces protocoles peut être sélectionné sans changer le moteur documentaire. Aucune API n'est activée par défaut. Pour ajouter un fournisseur :

```powershell
.\scripts\configure_previa_llm.ps1 add -Id monfournisseur -Adapter openai_compatible -Model 'MODELE_CHOISI' -BaseUrl 'https://MON-ENDPOINT.example/v1'
.\scripts\previa_full.ps1 restart
```

Clé API demandée en saisie masquée, conservée localement chiffrée par DPAPI. Les fournisseurs utilisant un protocole différent peuvent être ajoutés au registre des adaptateurs. Voir `README_MULTIPROVIDER.md` à la racine de PREVIA.

## Exemples API

```
GET  http://127.0.0.1:8766/api/v1/ai/health
GET  http://127.0.0.1:8766/api/v1/ai/sources
GET  http://127.0.0.1:8766/api/v1/ai/providers
POST http://127.0.0.1:8766/api/v1/ai/explain
POST http://127.0.0.1:8766/api/v1/ai/ask
```

L'API XAI n'accepte que les entrées fictives explicitement déclarées (`confirm_fictitious_demo: true`). Les valeurs utilisées pour l'exemple sont simulées. Le modèle est chargé depuis un emplacement local fixe; ne pas remplacer le fichier joblib par un artefact de provenance inconnue (la désérialisation joblib repose sur pickle).

## Sécurité et limites scientifiques

- L'explication SHAP porte sur une classification d'**HbA1c contemporanément mesurée ≥5,7 %**, pas sur la survenue d'un diabète futur, un AVC ou un infarctus.
- La sortie est un **score de modèle non validé pour un usage individuel**, et non un risque clinique personnalisé.
- Les explications SHAP décrivent les mécanismes de calcul du modèle, **pas les causes médicales**.
- Les résultats NHANES viennent d'une enquête américaine ; aucune validation clinique pour le Togo ou d'autres populations cibles.
- Les données ne sont pas persistées par l'API et aucun document médical individuel n'est importé. Aucune prescription, aucun rendez-vous, aucune orientation réelle.
- TF-IDF n'est pas un LLM; n'importe quel LLM peut produire une information erronée malgré les citations. L'affichage de sources ne garantit pas que les affirmations soient exactes; revue humaine requise avant diffusion.
- Un `npm run build` reste à valider sur l'environnement Windows v0.8 ; il n'a pas pu être exécuté entièrement dans le conteneur de préparation (npm indisponible).

## Source scientifique

Voir `docs/SOURCES_ET_VALIDATION.md` pour les liens, le périmètre et les scores externes rapportés. Les sources documentaires sont une sélection de pages officielles, et non un moteur de recherche clinique exhaustif.
