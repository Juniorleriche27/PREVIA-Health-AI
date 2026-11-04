# PREVIA — RAG multi-provider, indépendant du fournisseur

Cette mise à jour est **un correctif pour v0.9 sur ton dépôt v0.8**, pas un remplacement complet de PREVIA. Aucun fournisseur ni modèle n'est choisi par défaut. Le mode documentaire sans LLM reste disponible en permanence.

## Architecture

- Un moteur de recherche local TF-IDF sur des résumés OMS / CDC / NIDDK.
- Une interface Python `generate()` indépendante du fournisseur.
- Quatre protocoles : **OpenAI-compatible** (Groq, OpenAI, OpenRouter, DeepSeek, LM Studio, vLLM, Ollama si *choisi*), **Anthropic Messages**, **Gemini generateContent**, **Cohere Chat v2**. Un modèle supplémentaire utilisant ces protocoles s'ajoute **sans changement du RAG**. Pour un protocole propriétaire nouveau, créer un adaptateur dans `providers.py`.
- Aucune clé ni URL arbitraire n'est envoyée par le navigateur. Le frontend ne choisit que les identifiants enregistrés localement. Modèle personnalisable dans le champ « Model ID ».
- Aucune requête à un fournisseur tant que son choix n'est pas explicite. Aucun basculement vers un autre fournisseur payant. En cas d'échec, réponse documentaire extractive sourcée.
- Conversation éphémère limitée à six messages dans la page web ; aucune sauvegarde par PREVIA. Avec un fournisseur externe sélectionné, les questions et extraits nécessaires sont envoyés à son API : vérifier ses conditions de confidentialité. Utiliser des données **fictives uniquement** dans ce prototype.

## Installer

Télécharger `PREVIA_RAG_Multifournisseur_patch.zip` puis dans PowerShell, depuis la racine du dépôt :

```powershell
$root = 'C:\Users\DELL WORKSTATION\previa-health-ai-starter'
Expand-Archive "$env:USERPROFILE\Downloads\PREVIA_RAG_Multifournisseur_patch.zip" -DestinationPath $root -Force
Set-Location $root
.\scripts\install_previa_rag_v10.ps1
```

## Configurer un fournisseur *au choix* (aucun imposé)

**API compatible OpenAI** (exemple générique, endpoint de TON choix) :

```powershell
.\scripts\configure_previa_llm.ps1 add -Id monfournisseur -Adapter openai_compatible -Model 'MODELE_CHOISI' -BaseUrl 'https://ENDPOINT-CHOISI.example/v1'
```

Une saisie de clé API masquée est demandée. La clé est protégée localement par Windows DPAPI et n'est jamais placée dans le code. Pour une API native :

```powershell
.\scripts\configure_previa_llm.ps1 add -Id gemini -Adapter gemini -Model 'MODELE_CHOISI'
.\scripts\configure_previa_llm.ps1 add -Id claude -Adapter anthropic -Model 'MODELE_CHOISI'
.\scripts\configure_previa_llm.ps1 add -Id cohere -Adapter cohere -Model 'MODELE_CHOISI'
```

Ces lignes **ne sont que des exemples** et n'activent rien sans exécution volontaire. Pour un modèle local sur serveur compatible OpenAI :

```powershell
.\scripts\configure_previa_llm.ps1 add -Id modele_local -Adapter openai_compatible -Model 'MODELE_CHOISI' -BaseUrl 'http://127.0.0.1:PORT/v1' -NoApiKey
```

Puis :

```powershell
.\scripts\previa_full.ps1 restart
.\scripts\configure_previa_llm.ps1 list
```

Tu choisis ensuite fournisseur **et modèle** dans l'interface `http://localhost:3001/ai`. Retirer un fournisseur avec :

```powershell
.\scripts\configure_previa_llm.ps1 remove -Id monfournisseur
.\scripts\previa_full.ps1 restart
```

Le serveur peut aussi recevoir les secrets par variables d'environnement, et une configuration personnalisée via `PREVIA_LLM_CONFIG_FILE` (pour déploiements non Windows).

## Contrôles

`GET /api/v1/ai/providers` expose uniquement les identifiants, modèles par défaut, adaptateurs et états de configuration **sans clés**. `POST /api/v1/ai/ask` accepte `question`, `provider_id`, `model_id`, `history`, renvoie `mode`, `provider`, `model`, `sources` et `fallback_reason`.

Les tests utilisent des réponses API simulées. **Ils ne prouvent pas qu'une clé ou un modèle distant précis fonctionnera** tant qu'il n'aura pas été sélectionné et interrogé sur ton ordinateur.

**Important :** un adaptateur peut prendre en charge des modèles très variés, mais « tous les LLM » n'implémentent pas exactement le même protocole. Un modèle avec une API propre nécessite son adaptateur ; aucun logiciel ne peut garantir la compatibilité de tous les modèles sans cette étape.
