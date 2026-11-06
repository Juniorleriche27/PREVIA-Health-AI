# Indicateurs Clés de Performance (KPIs) et Protocole d'Évaluation Pilote
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Cadre d'Évaluation Multidimensionnel

L'évaluation d'un outil d'aide à la décision en santé publique ne peut se limiter à des métriques informatiques conventionnelles. Elle doit appréhender simultanément la **rigueur mathématique**, la **faisabilité soignante**, la **justice allocative (équité)** et la **viabilité médico-économique**.

PREVIA Health AI définit une matrice de **12 indicateurs clés de performance (KPI)** mesurables, auditables et classés selon trois niveaux de preuve reconnus en santé publique :
- **Niveau 1 (Conformité déterministe & technique)** : Contrôles automatisés vérifiables par machine (exhaustivité du code, intégrité mathématique, sécurité des données).
- **Niveau 2 (Faisabilité & utilisabilité de terrain)** : Mesures observationnelles directes lors de la campagne pilote (chronométrage, enquêtes soignantes, disparités de sélection).
- **Niveau 3 (Impact sur le parcours de soins réel)** : Suivi longitudinal de la conversion des patients à haut risque vers une confirmation médicale et un suivi effectif.

---

## 2. Tableau Exhaustif des 12 KPIs du Pilote

| ID | Catégorie | Nom de l'indicateur | Cible Pilote | Méthode de collecte | Niveau de preuve |
|---|---|---|---|---|---|
| **KPI-01** | Faisabilité opérationnelle | Taux de complétude des dossiers | **≥ 98,0 %** | Contrôle serveur bloquant des 5 champs obligatoires. | Niveau 2 (Qualité des données) |
| **KPI-02** | Faisabilité opérationnelle | Durée moyenne d'évaluation par profil | **≤ 90 secondes** | Horodatage serveur précis entre l'ouverture et la validation du cas. | Niveau 2 (Efficience soignante) |
| **KPI-03** | Fiabilité clinique | Concordance déterministe avec la table OMS | **100,0 %** | Audit exhaustif des 700 cellules OMS 2019 et sondage par double calcul. | Niveau 1 (Exactitude mathématique) |
| **KPI-04** | Allocation de ressources | Respect de la contrainte de capacité | **100,0 %** | Vérification automatique que le nombre de profils sélectionnés ne dépasse pas le quota alloué. | Niveau 1 (Intégrité de l'algorithme) |
| **KPI-05** | Équité & Accès | Disparité de sélection inter-secteurs | **≤ 5,0 pp** | Calcul de l'écart max-min de taux de sélection entre quartiers (Stratégie sectorielle). | Niveau 2 (Équité territoriale documentée) |
| **KPI-06** | Adoption soignante | Score d'utilisabilité système (SUS) | **≥ 80 / 100** | Questionnaire standardisé SUS en 10 items administré à la clôture du pilote. | Niveau 2 (Acceptabilité utilisateur) |
| **KPI-07** | Technique & Disponibilité | Disponibilité de la plateforme (Uptime) | **≥ 99,5 %** | Surveillance continue automatisée par sondes réseau externes (Sentry / Uptime). | Niveau 1 (Fiabilité infrastructure) |
| **KPI-08** | Sécurité & Confidentialité | Incidents de fuite ou stockage nominatif | **0 incident** | Audit des journaux et contrôle d'absence d'identifiants nominatifs au repos. | Niveau 1 (Conformité éthique et légale) |
| **KPI-09** | Viabilité économique | Coût marginal direct par profil évalué | **≤ 0,50 €** | Dépenses variables d'infrastructure et de requêtes divisées par le volume de profils. | Niveau 2 (Médiation médico-économique) |
| **KPI-10** | Aide à la décision | Concordance des soignants aux propositions | **≥ 90,0 %** | Ratio des orientations préventives validées sans modification par le médecin référent. | Niveau 2 (Pertinence perçue) |
| **KPI-11** | Documentation & IA | Précision des citations du moteur RAG | **100,0 %** | Contrôle par échantillonnage que toute citation renvoie à une source officielle OMS/CDC réelle. | Niveau 1 (Absence d'hallucination) |
| **KPI-12** | Parcours de soins | Taux de conversion vers le suivi préventif | **≥ 60,0 %** | Pointage à 30 jours des participants à risque OMS ≥ 10 % ayant consulté un soignant référent. | Niveau 3 (Parcours de soins effectif) |

---

## 3. Fiches Méthodologiques Détaillées par Indicateur

### KPI-01 : Taux de complétude des dossiers
- **Définition** : Proportion des dossiers de dépistage soumis comportant l'intégralité des 5 paramètres cliniques requis (âge 40–74 ans, sexe de référence, statut tabagique, pression artérielle systolique et IMC).
- **Formule** :
  $$\text{Taux de complétude} = \frac{\text{Nombre de dossiers complets sans valeur manquante}}{\text{Nombre total de dossiers initiés}} \times 100$$
- **Seuil d'alerte** : Si le taux passe sous 95 %, un atelier de rappel sur l'ergonomie de saisie est immédiatement organisé.

---

### KPI-02 : Durée moyenne d'évaluation par profil
- **Définition** : Temps moyen passé par le soignant entre l'ouverture du formulaire de dépistage et l'affichage de la restitution du risque.
- **Formule** :
  $$\bar{T} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{validation}, i} - t_{\text{ouverture}, i})$$
- **Justification médico-économique** : Une durée inférieure à 90 secondes garantit que le dépistage s'intègre naturellement dans la prise de constantes sans allonger l'attente des patients.

---

### KPI-03 : Concordance mathématique avec la table OMS 2019
- **Définition** : Vérification que la catégorie de risque et le pourcentage attribués par le moteur Python correspondent rigoureusement à la cellule exacte de la grille régionale OMS sans analyses de laboratoire.
- **Formule** :
  $$\text{Concordance} = \frac{\text{Nombre d'évaluations rigoureusement conformes au PDF OMS}}{\text{Nombre total d'évaluations auditées}} \times 100 = 100\,\%$$
- **Niveau de tolérance** : 0 erreur tolérée. Le modèle de calcul est entièrement déterministe et couvert par tests automatisés.

---

### KPI-04 : Respect de la contrainte de capacité allouée
- **Définition** : Capacité de la plateforme à restreindre strictement le nombre de rendez-vous ou de bilans prioritaires alloués à la capacité d'accueil fixée par les organisateurs.
- **Formule** :
  $$\text{Écart de capacité} = |\text{Nombre de profils sélectionnés} - \text{Capacité paramétrée}| = 0$$

---

### KPI-05 : Disparité de sélection inter-secteurs (Équité territoriale)
- **Définition** : Différence maximale observée entre le taux de sélection du secteur géographique le plus retenu et celui du secteur le moins retenu, sous stratégie sectorielle équilibrée.
- **Formule** (dérivée directement du chantier 15) :
  $$\Delta_{\text{secteur}} = \max_{s \in \text{Secteurs}} \left( \frac{n_{\text{sélectionnés}, s}}{N_s} \right) - \min_{s \in \text{Secteurs}} \left( \frac{n_{\text{sélectionnés}, s}}{N_s} \right)$$
- **Valeur cible** : $\le 5,0$ points de pourcentage.

---

### KPI-06 : Score d'utilisabilité système (System Usability Scale - SUS)
- **Définition** : Score composite standardisé mesurant la facilité d'utilisation, l'intuitivité et l'acceptabilité soignante de l'interface.
- **Méthode** : Questionnaire anonyme de 10 questions à échelle de Likert (1 à 5) complété par les 5 à 10 soignants utilisateurs à la fin du pilote.
- **Interprétation** : Un score SUS $\ge 80 / 100$ classe la plateforme dans le percentile supérieur ("Excellent / Grade A").

---

### KPI-07 : Disponibilité de la plateforme (Uptime cloud)
- **Définition** : Pourcentage de temps pendant lequel l'ensemble des modules web et API sont pleinement opérationnels et répondent en moins de 3 secondes.
- **Formule** :
  $$\text{Uptime} = \frac{\text{Temps de disponibilité opérationnelle}}{\text{Temps total de la période de campagne}} \times 100 \ge 99,5\,\%$$

---

### KPI-08 : Sécurité et absence de stockage nominatif
- **Définition** : Nombre d'incidents impliquant la persistance non chiffrée ou la fuite de données d'identité personnelle directe (nom, prénom, numéro d'identité national).
- **Cible absolue** : **0 incident**.

---

### KPI-09 : Coût marginal direct par profil évalué
- **Définition** : Dépenses d'infrastructure cloud, de maintenance serveur et de consommation de tokens IA divisées par le nombre total de profils évalués pendant la période.
- **Formule** :
  $$\text{Coût direct unitaire} = \frac{\text{Frais serveurs Netcup} + \text{Vercel} + \text{Tokens IA Knowlia}}{\text{Volume de profils traités}} \le 0,50 \text{ €}$$

---

### KPI-10 : Taux de concordance soignante aux orientations
- **Définition** : Pourcentage de cas où l'orientation proposée par PREVIA (conseils hygiéno-diététiques, alerte tensionnelle, consultation médicale) est validée telle quelle par le soignant référent sans contestation.
- **Cible** : $\ge 90,0\,\%$.

---

### KPI-11 : Précision des citations du moteur documentaire RAG
- **Définition** : Proportion des réponses formulées par l'assistant documentaire pour lesquelles 100 % des citations [ID] renvoient textuellement à un extrait authentique du corpus OMS, CDC ou NIDDK sans hallucination.
- **Cible** : **100,0 %**.

---

### KPI-12 : Taux de conversion vers le suivi préventif effectif
- **Définition** : Proportion des personnes identifiées à risque cardiovasculaire élevé (risque OMS $\ge 10\,\%$) qui effectuent effectivement leur consultation médicale confirmatoire dans les 30 jours suivant le dépistage forain.
- **Cible** : $\ge 60,0\,\%$. Ce KPI constitue la passerelle entre l'aide à la décision logicielle et l'impact sanitaire réel sur les populations.

---

## 4. Articulation Méthodologique avec les Résultats du Chantier 15

Le chantier 15 a établi une référence fondamentale en démontrant sur **360 runs expérimentaux** (30 graines aléatoires × 4 capacités × 3 stratégies) le comportement intrinsèque des algorithmes d'allocation :
- **Rendement de capture** : La priorisation par risque OMS sélectionne systématiquement 100 % de profils prioritaires jusqu'à saturation de la capacité, contre seulement 48 % pour une sélection aléatoire.
- **Équité sectorielle** : La stratégie équilibrée par secteur parvient à maintenir une disparité de sélection quasi-nulle (médiane à 1,67 point de pourcentage) tout en conservant un rendement de capture élevé.

> **Frontière scientifique non négociable** : Les résultats du chantier 15 ont été obtenus sur des cohortes synthétiques artificielles. Ils ont servi à calibrer les cibles numériques des KPIs 04 et 05, mais ne prétendent en aucun cas se substituer aux données réelles qui seront collectées dans le cadre du présent protocole pilote.
