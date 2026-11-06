# PREVIA Health AI — Commercial Viability & Pilot Strategy Package

Ce répertoire contient le dossier stratégique, médico-économique et opérationnel préparé pour le **Future Health Digital Innovation Challenge 2026**, répondant au critère officiel : **« Commercial viability and path to pilot »**.

Il s'appuie directement sur les travaux du chantier 15 (démonstration d'impact synthétique sur 360 expérimentations, 30 graines et 4 paliers de capacité) et sur les caractéristiques réelles de l'architecture logicielle déployée de PREVIA Health AI.

---

## 🧭 Ordre de lecture recommandé / Reading Order

| Rôle / Destinataire | Français | English | Description synthétique |
|---|---|---|---|
| **Membres du Jury** (2 min) | [Synthèse jury (FR)](jury-summary-fr.md) | [Jury Summary (EN)](jury-summary-en.md) | Synthèse exécutive condensée répondant aux 7 questions clés du jury. |
| **Comité d'évaluation & Direction** | [Rapport de viabilité (FR)](commercial-viability-report-fr.md) | [Commercial Viability (EN)](commercial-viability-report-en.md) | Évaluation stratégique complète du problème économique, de la proposition de valeur et du déploiement. |
| **Business Developers & Stratèges** | [Parties prenantes & Valeur (FR)](stakeholders-and-value-proposition-fr.md) | [Stakeholders & Value (EN)](stakeholders-and-value-proposition-en.md) | Cartographie des 5 segments clients (décideurs, usagers, financeurs) et matrice de différenciation. |
| **Économistes & Directeurs Financiers** | [Modèles économiques](business-models-comparison.md) | [Financial Analysis](financial-analysis.md) | Comparatif des 5 modèles de revenus, structure des coûts réels observés, scénarios à 3 ans et point mort. |
| **Coordinateurs de santé & Partenaires** | [Protocole pilote opérationnel](pilot-plan.md) | [KPIs & Évaluation pilote](pilot-kpis-and-evaluation.md) | Protocole d'expérimentation en 4 phases (6 mois), grille des 12 KPIs mesurables et seuils Go/No-Go. |
| **Chefs de projet & Tech Leads** | [Feuille de route stratégique](roadmap.md) | [Sources & Références](references-and-sources.md) | Trajectoire en 7 étapes vers l'industrialisation, dépendances et bibliographie institutionnelle. |

---

## 📊 Données et preuves vérifiables (`results/`)

Le sous-dossier [`results/`](results/) contient les artefacts reproductibles générés par script Python :

- [`results/financial_scenarios.csv`](results/financial_scenarios.csv) : Projections chiffrées sur 3 ans pour les scénarios Prudent, Central et Ambitieux.
- [`results/cost_breakdown.csv`](results/cost_breakdown.csv) : Ventilation des coûts fixes et semi-variables (infrastructure, tokens, DevOps, support terrain, audit).
- [`results/pilot_kpis.csv`](results/pilot_kpis.csv) : Tableau de bord des 12 indicateurs clés de performance avec niveaux de preuve associés.
- [`results/manifest.json`](results/manifest.json) : Empreintes cryptographiques SHA-256 de chaque livrable et paramètres de modélisation.
- [`results/figures/`](results/figures/) : Figures vectorielles SVG sans dépendance externe :
  - `financial_scenarios.svg` : Trajectoire financière comparée (Chiffre d'affaires & Marge brute).
  - `cost_breakdown.svg` : Structure des postes de coûts d'échelle.
  - `pilot_timeline.svg` : Diagramme opérationnel des 4 phases de l'expérimentation pilote.

---

## ⚙️ Reproduction des calculs financiers

Depuis la racine du projet sous Windows / PowerShell :

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_business_pilot.py
& .\.venv\Scripts\python.exe -m pytest backend\tests\test_business_pilot.py -q
```

Le script réévalue l'ensemble des scénarios, met à jour les fichiers CSV et SVG dans `results/`, et vérifie l'intégrité du manifeste.

---

## 🛡️ Frontière de rigueur éthique et commerciale

1. **Aucun partenariat n'est pré-supposé** : Aucun établissement de santé, agence ministérielle ou ONG n'est présenté comme ayant déjà signé un accord commercial avec PREVIA.
2. **Aucune tarification arbitraire n'est imposée** : Les tarifs mentionnés constituent des hypothèses de modélisation équitables et transparentes, soumises à contractualisation.
3. **Séparation nette recherche / clinique** : Les résultats synthétiques du chantier 15 démontrent le comportement d'allocation sous contrainte mathématique, sans constituer une allégation d'efficacité clinique réelle sur la réduction de la morbidité ou de la mortalité.
