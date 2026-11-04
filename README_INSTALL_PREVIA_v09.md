# PREVIA Health AI — Installation du module ML + XAI + RAG v0.9

Cette archive contient uniquement les nouveaux fichiers nécessaires à l'ajout du module IA sur la version v0.8 créée par Codex. Le code de Codex n'est pas remplacé.

## Une seule procédure pour installer, tester, compiler et redémarrer

```powershell
$root = 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
Expand-Archive -Path "$env:USERPROFILE\Downloads\PREVIA_v0.9_XAI_RAG_patch.zip" -DestinationPath $root -Force
Set-Location $root
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_previa_ai.ps1
```

Puis ouvrir : http://localhost:3001/ai

## Commande unique de redémarrage à chaque prochaine session

```powershell
cd 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
.\scripts\previa_full.ps1 restart
```

Le script gère l'application principale avec `previa.ps1` (Codex) et le nouveau service IA via `previa_ai.ps1`.

Autres commandes : `start`, `stop`, `status`, `verify`, `diagnose`.

## Mode LLM local facultatif

Sans Ollama, le RAG fonctionne en mode **extractif sourcé**. Pour de la génération réelle en local : installer Ollama, récupérer un modèle léger (`ollama pull gemma3:1b`) puis `.\scripts\previa_full.ps1 restart -Ollama`.

Le modèle SHAP réel doit déjà exister dans `PREVIA_ML_Validation_Externe/results/cross_cycle` (réalisé lors de la validation NHANES).
