# Protocole d'Expérimentation Pilote Opérationnel (6 Mois)
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Cadrage Général et Objectifs de l'Expérimentation

Le présent protocole définit les modalités d'une première expérimentation en conditions réelles encadrées de PREVIA Health AI.

> **Avertissement éthique et légal** : Aucun établissement de santé, agence ministérielle ou ONG n'est présumé signataire à ce stade. Ce document constitue le protocole standardisé prêt à être soumis à la direction médicale et au comité d'éthique du futur partenaire retenu post-challenge.

### 1.1. Profil du Partenaire Recherché
- **Type d'organisation** : Une Organisation Non Gouvernementale (ONG) médicale internationale ou nationale, un réseau de centres de santé communautaires ou un district sanitaire pilote.
- **Activité cible** : Organisation d'une campagne de dépistage des maladies non transmissibles (hypertension artérielle, risque cardiovasculaire) d'une durée de 4 à 8 semaines.
- **Capacité opérationnelle** : Équipe de 5 à 10 infirmiers ou agents de santé communautaires équipés de tensiomètres manuels/électroniques et de toises/balances, sous la responsabilité d'un médecin référent.

### 1.2. Objectifs Majeurs du Pilote
1. **Évaluer la faisabilité opérationnelle** de la saisie numérique en soins primaires (temps moyen par évaluation ≤ 90 secondes, complétude ≥ 98 %).
2. **Mesurer l'impact de l'allocation sous contrainte** : Vérifier sur le terrain si l'algorithme d'équité sectorielle permet de capturer efficacement les profils à risque ≥ 10 % tout en maintenant un écart inter-quartiers inférieur à 5 points de pourcentage.
3. **Tester l'acceptabilité et l'utilisabilité soignante** (Score System Usability Scale - SUS ≥ 80 / 100).
4. **Garantir l'innocuité et la sécurité médico-légale** (zéro incident de fuite de données, 100 % de conformité algorithmique avec les tables OMS officielles).

---

## 2. Calendrier d'Exécution en 4 Phases Chronologiques

```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│        PHASE 0          │         PHASE 1         │         PHASE 2         │         PHASE 3         │
│         Mois 1          │          Mois 2         │        Mois 3 et 4      │        Mois 5 et 6      │
├─────────────────────────┼─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ • Convention & Éthique  │ • Formation soignants   │ • Déploiement terrain   │ • Audit indépendant     │
│ • Instance dédiée       │ • Guide d'usage bilingue│ • 500 à 1 000 profils   │ • Calcul des 12 KPIs    │
│ • Paramétrage local     │ • Test à blanc (50 cas) │ • Supervision médicale  │ • Enquête satisfaction  │
│ • Simulation synthétique│ • Validation Go/No-Go   │ • Astreinte technique   │ • Rapport conjoint      │
└─────────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

### Phase 0 : Cadrage Éthique, Gouvernance et Simulation Hors-Ligne (Mois 1)
- **Activités** :
  1. Signature du protocole d'accord (MOU) entre l'équipe PREVIA et la direction médicale du partenaire.
  2. Dépôt et validation auprès du comité d'éthique de la recherche ou de la commission médicale locale.
  3. Déploiement d'une instance cloud souveraine dédiée et étanche sur les serveurs Netcup.
  4. Paramétrage territorial : intégration de la grille régionale OMS appropriée (ex. Afrique de l'Ouest) et des secteurs géographiques réels de la zone sanitaire.
  5. Simulation d'allocation à blanc sur 3 cohortes synthétiques de 240 profils pour valider le comportement des quotas avec les coordinateurs.
- **Livrable de fin de phase** : Attestation de conformité éthique et rapport de simulation initiale.

---

### Phase 1 : Formation des Soignants et Qualification Technique "À Blanc" (Mois 2)
- **Activités** :
  1. Organisation d'un atelier pratique de formation de 2 demi-journées pour 5 à 10 soignants et 2 superviseurs.
  2. Remise des fiches mémo plastifiées et du guide utilisateur bilingue.
  3. **Test à blanc (Dry Run)** : Chaque soignant évalue une batterie de 10 cas cliniques fictifs standardisés (soit 50 à 100 évaluations test) couvrant l'ensemble des tranches d'âge et profils de tension (notamment cas d'alerte PAS ≥ 180 mmHg).
  4. Analyse des retours d'ergonomie et ajustements mineurs d'interface si nécessaire.
- **Revue de qualification Go / No-Go 1** :
  - *Critère obligatoire* : 100 % de concordance sur les calculs OMS des profils tests et temps moyen de saisie < 120 secondes.

---

### Phase 2 : Campagne de Terrain Encadrée et Saisie Supervisée (Mois 3 et 4)
- **Activités** :
  1. Déploiement des équipes soignantes sur les postes de dépistage fixes ou mobiles.
  2. Évaluation de **500 à 1 000 participants volontaires** éligibles (adultes de 40 à 74 ans sans maladie cardiovasculaire avérée préexistante).
  3. Modalités de saisie :
     - Identifiant unique pseudonymisé (ex. `DPO-2026-0042`), **aucun nom, prénom, numéro de téléphone ou document d'identité n'est saisi dans la plateforme**.
     - Les 5 variables cliniques sont renseignées en présence du patient : âge, sexe de référence, tabagisme actif, pression artérielle systolique (moyenne de deux mesures) et indice de masse corporelle (calculé ou déduit de la taille et du poids).
  4. **Double regard médical obligatoire** : PREVIA affiche l'estimation OMS du risque à 10 ans et l'explication SHAP. L'infirmier ou le médecin conserve l'entière autorité diagnostique et valide ou adapte le conseil préventif remis au patient.
  5. Support technique et astreinte système assurés sous SLA de 4 heures en journée ouvrée.
- **Revue de mi-parcours (fin Mois 3)** : Point d'étape à 250 dossiers pour vérifier la complétude et l'absence d'incident technique.

---

### Phase 3 : Audit des Données, Évaluation Indépendante et Restitution (Mois 5 et 6)
- **Activités** :
  1. Clôture de la base de données du pilote et gel cryptographique par hash SHA-256.
  2. Audit statistique indépendant mené conjointement par l'équipe PREVIA et le médecin référent du partenaire.
  3. Calcul exhaustif des 12 indicateurs de performance (KPIs) : complétude, temps de traitement, concordance OMS, équité sectorielle, coût réel unitaire.
  4. Administration du questionnaire standardisé *System Usability Scale* (SUS) auprès de tous les soignants ayant participé.
  5. Rédaction du rapport d'évaluation médico-économique conjoint.
  6. Restitution officielle devant le comité de direction du partenaire et les représentants des bailleurs de fonds.
- **Décision finale de fin de pilote** : Décision collégiale de poursuite vers un déploiement régulier à l'échelle du district ou d'ajournement.

---

## 3. Matrice des Rôles et Responsabilités (RACI)

| Tâche / Étape opérationnelle | Équipe PREVIA | Médecin Référent Partenaire | Soignants de Terrain | Comité Éthique / Bailleurs |
|---|:---:|:---:|:---:|:---:|
| Rédaction du protocole et convention | **R** / **A** | **C** | I | I |
| Dépôt et validation éthique réglementaire | **C** | **R** / **A** | I | **A** |
| Déploiement serveur et paramétrage quotas | **R** / **A** | **C** | I | I |
| Formation et remise des guides d'usage | **R** | **C** | **R** | I |
| Test à blanc (Dry Run sur cas fictifs) | **C** | **A** | **R** | I |
| Saisie et dépistage en conditions réelles | I | **A** (Supervision) | **R** (Exécution) | I |
| Validation des orientations médicales | I | **R** / **A** | **R** | I |
| Support et monitoring d'infrastructure | **R** / **A** | I | I | I |
| Audit statistique et calcul des 12 KPIs | **R** | **R** / **A** | I | **C** |
| Rédaction et présentation du rapport final | **R** | **R** / **A** | **C** | I |

*Légende : **R** = Réalise (Responsible) ; **A** = Approuve (Accountable) ; **C** = Consulté (Consulted) ; **I** = Informé (Informed).*

---

## 4. Règles d'Arrêt Immédiat (Go / No-Go Safety Gates)

La sécurité clinique et éthique prime sur toute considération de calendrier. Le pilote est immédiatement suspendu si l'une des conditions suivantes est constatée :

1. **Gate 1 — Discordance de calcul OMS** : Si le moindre écart de résultat est détecté entre la sortie logicielle de PREVIA et la table officielle OMS 2019 lors des vérifications manuelles par sondage (seuil de tolérance = 0 erreur).
2. **Gate 2 — Interruption de service majeure** : Si une panne d'infrastructure bloque la plateforme pendant plus de 4 heures consécutives un jour de campagne active sans solution de secours.
3. **Gate 3 — Rupture de confidentialité** : Si une tentative d'introduction de données nominatives identifiables est constatée dans les champs de saisie libre.
4. **Gate 4 — Prise de décision autonome non supervisée** : Si la plateforme est utilisée en autonomie par des patients ou sans la présence d'un soignant habilité à confirmer l'orientation clinique.
