# Analyse Financière, Modèle de Coûts et Seuil de Rentabilité
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Structure Détaillée des Coûts : Réel Observé vs Extrapolations d'Échelle

La viabilité financière de PREVIA Health AI repose sur une distinction méthodologique stricte entre les **dépenses techniques réellement observées** sur l'infrastructure actuelle et les **projections d'accompagnement humain et d'exploitation** à grande échelle.

---

### 1.1. Coûts Techniques Réellement Observés (Baseline de Production v0.8/v0.9)

L'infrastructure actuelle de PREVIA fonctionne déjà en production sur deux environnements interconnectés et sécurisés :

```
┌────────────────────────────────────────────────────────┐     ┌────────────────────────────────────────────────────────┐
│             FRONTEND WEB (Vercel CDN)                  │     │         BACKEND SOUVERAIN (Serveur VPS Netcup)         │
│  • Next.js 15 App Router bilingue FR/EN                │ ──> │  • Hôte : 194.59.205.73 (Ubuntu Server LTS)            │
│  • Hébergement distribué Edge / Serverless             │     │  • Conteneurs Docker : previa_backend & previa_ai      │
│  • Coût constaté : ~20 $/mois (~240 $/an = ~220 €/an)  │     │  • Moteur IA Knowlia + Base vectorielle Qdrant         │
│                                                        │     │  • Coût constaté : ~25 €/mois (~300 €/an)              │
└────────────────────────────────────────────────────────┘     └────────────────────────────────────────────────────────┘
```

- **Nom de domaine institutionnel, DNS et certificats TLS** : ~24 € / an.
- **Stockage chiffré des sauvegardes distantes & surveillance Sentry** : ~180 € / an.
- **Socle d'infrastructure fixe minimale observée** : **~724 € à ~744 € / an (soit environ 62 € / mois)**.

---

### 1.2. Coûts de Consommation des API et Modèles d'IA (Knowlia vs Déterministe)

Le modèle économique de l'IA dans PREVIA se distingue par son extrême frugalité :
1. **Modules 01 à 06 (Dépistage OMS, Simulation, Allocation, Audit)** :
   - Fonctionnent à **100 % sur des algorithmes déterministes locaux** codés en Python/FastAPI.
   - **Coût d'API externe : 0,000 €** par évaluation.
2. **Module 07 (Assistant Documentaire RAG & Explicabilité SHAP)** :
   - Mode *Extraction documentaire pure* (sans LLM) : **0,000 €** par requête.
   - Mode *Synthèse fluide Knowlia Intelligence* : Utilise l'orchestrateur souverain multi-modèle déployé sur Netcup (routage vers Groq `gpt-oss-120b`, Cloudflare ou Cohere avec fallback).
   - Coût moyen estimé par synthèse documentaire (moyenne 450 tokens en entrée, 250 tokens en sortie) : **~0,0015 € / requête**.
   - Dans une campagne standard de 5 000 profils où 30 % des participants posent une question documentaire à l'infirmier, le coût total de tokens IA est de **2,25 € pour l'ensemble de la campagne**.

---

### 1.3. Structure des Postes de Coûts d'un Pilote de 6 Mois (12 000 € HT)

Pour un premier pilote encadré de 6 mois portant sur 1 000 profils soignés, la répartition des dépenses réelles et d'accompagnement s'établit comme suit :

```
Ventilation des Dépenses d'un Pilote (Total Coûts Directs : 9 244 €) :
[████████████████████] 31,4 %  Support terrain, ateliers soignants & astreinte (2 900 €)
[████████████████]     25,7 %  DevOps, maintien en condition opérationnelle & sécurité (2 374 €)
[█████████████]        21,4 %  Audit indépendant, comités éthiques & rapport conjoint (1 980 €)
[███████████]          17,2 %  Infrastructure souveraine dédiée, backups & monitoring (1 590 €)
[███]                   4,3 %  Consommation tokens IA & licences logicielles d'appoint (400 €)
```

- **Marge brute prévisionnelle sur le forfait pilote** : 12 000 € - 9 244 € = **+2 756 € (23,0 %)**, intégralement réinvestis dans le renforcement de l'architecture logicielle.

---

## 2. Projections Financières Comparées à 3 Ans

Le tableau ci-dessous reproduit fidèlement les calculs générés par le script `scripts/evaluate_business_pilot.py` (exportés dans `docs/business-pilot/results/financial_scenarios.csv`) :

| Scénario | Année | Pilotes | Campagnes | Licences Annuelles | Profils Évalués | CA Total (€) | Dépenses Totales (€) | Marge Brute (€) | Marge Brute (%) | Coût / Profil (€) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Prudent** | Année 1 | 1 | 0 | 0 | 1 000 | 12 000 € | 9 244 € | 2 756 € | 23,0 % | 9,24 € |
| **Prudent** | Année 2 | 1 | 3 | 0 | 8 500 | 27 500 € | 18 195 € | 9 305 € | 33,8 % | 2,14 € |
| **Prudent** | Année 3 | 0 | 6 | 1 | 20 000 | 33 000 € | 20 540 € | 12 460 € | 37,8 % | 1,03 € |
| **Central** | Année 1 | 1 | 2 | 0 | 6 000 | 17 000 € | 11 447 € | 5 553 € | 32,7 % | 1,91 € |
| **Central** | Année 2 | 0 | 6 | 2 | 25 000 | 48 000 € | 27 511 € | 20 489 € | 42,7 % | 1,10 € |
| **Central** | Année 3 | 0 | 15 | 5 | 70 000 | 127 500 € | 57 802 | 69 698 € | 54,7 % | 0,83 € |
| **Ambitieux** | Année 1 | 2 | 4 | 0 | 12 000 | 34 000 € | 19 649 € | 14 351 € | 42,2 % | 1,64 € |
| **Ambitieux** | Année 2 | 0 | 12 | 4 | 55 000 | 102 400 € | 46 025 € | 56 375 € | 55,1 % | 0,84 € |
| **Ambitieux** | Année 3 | 0 | 25 | 10 | 150 000 | 257 500 € | 105 068 € | 152 432 € | 59,2 % | 0,70 € |

---

## 3. Analyse du Seuil de Rentabilité (Point Mort)

### Formules de calcul et seuils critiques
Le point mort économique correspond au volume d'activité strict requis pour couvrir les coûts fixes incompressibles de maintien en conditions opérationnelles de la plateforme.

1. **Frais généraux fixes annuels (Overhead)** :
   - Hébergement serveur VPS Netcup (12 mois × 25 €) : 300 €
   - Hébergement Frontend Vercel Pro (12 mois × 20 €) : 240 €
   - Noms de domaine, DNS et certificats TLS : 24 €
   - Sauvegardes chiffrées distantes et monitoring automatisé : 180 €
   - Veille de sécurité, audits de dépendances et astreinte de base : 3 200 €
   - **Total des charges fixes incompressibles** : **3 944 € / an**.

2. **Marge sur coût variable par produit** :
   - *Campagne Forfaitaire Standard* : Facturation 2 500 € - Dépenses directes (support 800 €, devops 400 €, audit 300 €) = **1 000 € de marge unitaire**.
   - *Licence Annuelle Institutionnelle* : Facturation 15 000 € - Dépenses directes (support 1 800 €, devops 1 500 €, audit 800 €) = **10 900 € de marge unitaire**.

3. **Seuil de rentabilité résultant** :
   $$\text{Seuil en campagnes} = \frac{\text{Charges Fixes}}{\text{Marge par Campagne}} = \frac{3\,944}{1\,000} \approx 3,94 \text{ campagnes}$$
   $$\text{Seuil en licences} = \frac{\text{Charges Fixes}}{\text{Marge par Licence}} = \frac{3\,944}{10\,900} \approx 0,36 \text{ licence}$$

> **Conclusion économique majeure** : PREVIA atteint son autonomie financière dès la signature de **4 campagnes de dépistage forain par an** ou dès la commercialisation d'une **seule licence annuelle institutionnelle**.

---

## 4. Économie d'Échelle et Coût Unitaire par Profil Évalué

L'une des caractéristiques les plus remarquables de PREVIA est l'effondrement rapide du coût moyen par profil évalué à mesure que le volume augmente :
- **Phase Pilote (Année 1, 1 000 profils)** : **9,24 € / profil** (reflète l'investissement initial lourd en paramétrage, formation des soignants et audit médical externe).
- **Phase de Croissance (Année 2, 25 000 profils)** : **1,10 € / profil**.
- **Phase d'Échelle (Année 3, 70 000 à 150 000 profils)** : **0,70 € à 0,83 € / profil**.

Comparé au coût d'un bilan lipidique en laboratoire d'analyses (généralement facturé entre 12 € et 30 € dans les pays émergents et inaccessible hors des capitales), PREVIA offre une solution de dépistage de premier niveau **15 à 40 fois plus économique**, sans aucun consommable chimique ni délai d'attente pour le patient.
