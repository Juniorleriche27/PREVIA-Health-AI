# Références Scientifiques, Économiques et Cadres Institutionnels
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Références Cliniques et Grilles Internationales de Référence

1. **World Health Organization (WHO) — 2019**
   *WHO cardiovascular disease risk charts: guiding principles and development of new charts for 21 global regions.*
   The Lancet Global Health, 7(10), e1332-e1345.
   - Base méthodologique des grilles régionales prédisant le risque d'accident cardiovasculaire fatal ou non fatal à 10 ans. PREVIA implémente rigoureusement la version "sans analyses biologiques" (laboratoire optionnel) pour 700 cellules d'âge, sexe, tabac, pression artérielle systolique et indice de masse corporelle.
   - Source numérique auditée : `docs/WHO_CVD_Risk_Chart_2019_West_Africa_non_lab.pdf` (SHA-256 : `139e2485e065027ef35575eb4aef604d59bbb9cde4ec4cc02403c51835d57abe4`).

2. **World Health Organization — HEARTS Technical Package (2020)**
   *HEARTS: Technical package for cardiovascular disease management in primary health care.*
   Genève : Organisation Mondiale de la Santé.
   - Module "R : Risk-based CVD management" et "E : Evidence-based protocols". Cadre d'intégration du dépistage non invasif dans les structures de soins primaires en milieu à ressources limitées.

3. **Centers for Disease Control and Prevention (CDC) & NCHS — 2017–2018**
   *National Health and Nutrition Examination Survey (NHANES) public dataset.*
   Hyattsville, MD : U.S. Department of Health and Human Services.
   - Utilisé pour le modèle de recherche prédictif XAI (association statistique de marqueurs métaboliques HbA1c ≥ 5,7 %, sans prétention pronostique cardiovasculaire autonome).

---

## 2. Littérature Médico-Économique et Fardeau Global de Santé

4. **GBD 2019 Diseases and Injuries Collaborators — 2020**
   *Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019.*
   The Lancet, 396(10258), 1204-1222.
   - Données de référence sur la primauté des MCV dans la mortalité mondiale (17,9 millions de décès/an) et la concentration de plus de 75 % des décès dans les pays à revenu faible ou intermédiaire.

5. **World Heart Federation (WHF) — 2023**
   *World Heart Report 2023: Confronting the World's Number One Killer.*
   Genève : World Heart Federation.
   - Évaluation du coût économique mondial des maladies cardiovasculaires (> 863 milliards USD annuels) et de la rentabilité médico-économique des interventions préventives de premier recours (*Best Buys* de l'OMS).

6. **World Health Organization — 2023**
   *First WHO report on the devastating global impact of high blood pressure.*
   Genève : World Health Organization.
   - Données empiriques sur la prévalence mondiale de l'hypertension (1,3 milliard d'adultes) et les faibles taux de contrôle en soins primaires (moins de 20 %).

---

## 3. Cadres Réglementaires et Standards d'Évaluation de la Santé Numérique

7. **World Health Organization — 2021**
   *Global Strategy on Digital Health 2020–2025.*
   Genève : Organisation Mondiale de la Santé.
   - Principes directeurs de l'interopérabilité, de la souveraineté des données de santé, de l'open-source en santé publique et de la frugalité technologique des solutions numériques déployées dans les pays émergents.

8. **USAID — 2020**
   *Vision for Action in Digital Health: Accelerating Country Journeys to Self-Reliance in the Digital Era.*
   Washington, D.C. : United States Agency for International Development.
   - Analyse du marché de la santé numérique dans le développement international et méthodologie d'allocation des financements multilatéraux pour les outils d'aide à la décision.

9. **Haute Autorité de Santé (HAS) — 2021**
   *Grille de classification et d'évaluation médico-économique des solutions d'aide à la décision médicale (SADM).*
   Saint-Denis : Haute Autorité de Santé.
   - Critères d'innocuité, de traçabilité, de transparence des algorithmes et de maintien sous contrôle humain de toute recommandation préventive.

10. **National Institute for Health and Care Excellence (NICE) — 2022**
    *Evidence Standards Framework for Digital Health Technologies.*
    Londres : NICE.
    - Échelons de preuve (Tier A, Tier B, Tier C) distinguant l'efficacité opérationnelle d'un logiciel de santé, l'adhésion soignante et la validation clinique d'issues de santé.

---

## 4. Références Méthodologiques, IA et Ergonomie

11. **Brooke, J. — 1996**
    *SUS: A 'quick and dirty' usability scale.*
    Usability Evaluation in Industry, Taylor & Francis, Londres, 189-194.
    - Outil standardisé utilisé pour l'indicateur KPI-06 (*System Usability Scale*), cible fixée à ≥ 80 / 100 pour qualifier une ergonomie soignante de rang supérieur (Grade A).

12. **Lundberg, S. M., & Lee, S.-I. — 2017**
    *A unified approach to interpreting model predictions.*
    Advances in Neural Information Processing Systems (NeurIPS 30), 4765-4774.
    - Fondement théorique des valeurs SHAP (*SHapley Additive exPlanations*) intégrées dans le Module 07 de PREVIA pour expliquer les contributions additives positives ou négatives des facteurs de risque.

---

## 5. Renvois Internes au Dépôt PREVIA Health AI

13. **PREVIA Health AI — Chantier 15 (Novembre 2026)**
    *Dossier d'impact sanitaire reproductible : Évaluation synthétique de 3 stratégies d'allocation sous 4 capacités sur 30 graines aléatoires (360 expériences).*
    - [`docs/health-impact/health-impact-report-fr.md`](../health-impact/health-impact-report-fr.md)
    - [`docs/health-impact/methodology-fr.md`](../health-impact/methodology-fr.md)
    - [`docs/health-impact/results/manifest.json`](../health-impact/results/manifest.json)
