# Feuille de Route Stratégique et Trajectoire vers l'Industrialisation (24 Mois)
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Vue d'Ensemble de la Trajectoire

Le passage d'un prototype de recherche validé en environnement synthétique à une solution industrielle pérenne requiert une gouvernance rigoureuse articulée en **7 jalons chronologiques majeurs sur 24 mois**.

```
[Mois 0]       [Mois 1-3]       [Mois 3-6]       [Mois 6-12]      [Mois 12-15]     [Mois 15-18]     [Mois 18-24]
Jalon 1 ────>   Jalon 2 ────>   Jalon 3 ────>   Jalon 4 ────>   Jalon 5 ────>   Jalon 6 ────>   Jalon 7
Prototype       Durcissement    Partenariat &   Expérimentation Évaluation       Décision         Déploiement
de recherche    technique &     Cadrage éthique  Pilote terrain  indépendante &  industrialisation multi-pays &
validé          sécurité HDS    (MOU)           (500-1 000 p.)  publication     & marquage CE/DM échelle
```

---

## 2. Description Détaillée des 7 Jalons

---

### Jalon 1 : Prototype de Recherche Actuel (Mois 0 — État Actuel Validé)
- **Statut** : **Terminé et validé (v0.8.0 / v0.9.0)**.
- **Acquis** :
  - Plateforme web bilingue FR/EN complète déployée sur Vercel et FastAPI sur serveur Netcup (IP 194.59.205.73).
  - Implémentation certifiée de la grille OMS 2019 non-labo (700/700 cellules contrôlées).
  - Modules de simulation populationnelle et d'allocation sous contrainte (Modules 01 à 05).
  - Moteur XAI (SHAP) et assistant RAG souverain multi-modèle (Knowlia Intelligence).
  - Dossier d'impact sanitaire reproductible (Chantier 15 : 360 runs, 30 graines, 4 capacités).
- **Livrables associés** : Dépôt public GitHub vérifié, suite de 141 tests unitaires automatisés validés.

---

### Jalon 2 : Validation Technique et Scientifique Complémentaire (Mois 1 à 3)
- **Objectif** : Durcir l'application pour les conditions extrêmes de terrain et les audits de sécurité.
- **Actions clés** :
  1. *Mode PWA Hors-Ligne (Progressive Web App)* : Pré-mise en cache des grilles OMS et de la logique de calcul pour permettre la saisie en zone blanche sans aucune connexion 4G.
  2. *Tests de charge et de résilience (Stress testing)* : Simulation de 100 requêtes concurrentes de saisie sur le serveur VPS Netcup sans dégradation de la latence (< 200 ms).
  3. *Audit de sécurité des dépendances* : Revue automatisée des vulnérabilités CVE (FastAPI, Docker, Next.js) et chiffrement systématique des communications TLS 1.3.
- **Dépendances** : 1 Ingénieur Full-Stack / DevOps (0,5 ETP).
- **Livrable** : Rapport de durcissement technique et version candidate au pilote (v1.0-RC1).

---

### Jalon 3 : Recherche de Partenaire Pilote et Contractualisation Éthique (Mois 3 à 6)
- **Objectif** : Identifier, sélectionner et contractualiser avec l'organisation partenaire pour la première expérimentation terrain.
- **Actions clés** :
  1. Prospection ciblée auprès des ONG médicales et directions de santé communautaire en Afrique de l'Ouest (bénéficiant de la vitrine du Future Health Challenge).
  2. Signature d'un protocole d'accord (MOU) fixant les engagements réciproques, la gratuité d'accès pour le partenaire et la supervision médicale exclusive.
  3. Soumission du dossier au comité d'éthique de la recherche local ou de l'ONG partenaire.
  4. Déploiement et paramétrage de l'instance dédiée étanche.
- **Dépendances** : Financement d'amorçage issu du Challenge Future Health 2026 ; Lead Consultant Santé Publique (0,3 ETP).
- **Livrable** : Convention signée et avis favorable du comité d'éthique.

---

### Jalon 4 : Expérimentation Encadrée sur le Terrain (Mois 6 à 12)
- **Objectif** : Exécuter le protocole pilote en 4 phases (cf. `pilot-plan.md`) auprès de 500 à 1 000 participants réels.
- **Actions clés** :
  1. Formation pratique de 5 à 10 soignants et qualification par test à blanc sur 50 profils fictifs.
  2. Campagne de dépistage forain sous double regard soignant strict (saisie pseudonymisée).
  3. Astreinte technique continue SLA et monitoring en temps réel.
- **Dépendances** : Disponibilité des équipes soignantes du partenaire ; tensiomètres conformes validés OMS.
- **Livrable** : Base de données du pilote gelée et intègre (empreinte SHA-256).

---

### Jalon 5 : Évaluation Indépendante et Publication Scientifique (Mois 12 à 15)
- **Objectif** : Auditer scientifiquement les données collectées et publier les résultats médico-économiques.
- **Actions clés** :
  1. Calcul contradictoire des 12 KPIs du pilote avec le médecin référent du partenaire.
  2. Analyse des disparités effectives de sélection territoriale et comparaison avec les prédictions du Chantier 15.
  3. Dépouillement des scores d'utilisabilité système (SUS) des soignants.
  4. Rédaction conjointe et soumission d'un article scientifique dans une revue de santé publique à comité de lecture (ex. *Lancet Global Health* ou *BMJ Global Health*).
- **Dépendances** : Épidémiologiste / Économiste de la santé indépendant (0,2 ETP).
- **Livrable** : Rapport d'évaluation final indépendant et pré-publication scientifique.

---

### Jalon 6 : Décision d'Industrialisation et Conformité Réglementaire (Mois 15 à 18)
- **Objectif** : Adapter la structure juridique et technique aux exigences d'un déploiement commercial large.
- **Actions clés** :
  1. *Audit de qualification Dispositif Médical (DM)* : Revue avec un conseil en affaires réglementaires pour déterminer la classification exacte selon le règlement européen MDR 2017/745 ou les réglementations nationales africaines (outil d'aide à la décision vs dispositif médical de classe I/IIa).
  2. *Certification Hébergement de Données de Santé (HDS)* : Migration vers un hébergeur souverain certifié HDS pour les déploiements institutionnels européens ou respect des réglementations de souveraineté nationale locales.
  3. *Finalisation du packaging commercial* : Création de la structure d'entreprise dédiée, stabilisation des contrats types de forfaits campagnes et licences annuelles.
- **Dépendances** : Conseil juridique / réglementaire santé ; revenus du premier pilote et subventions d'échelle.
- **Livrable** : Dossier de marquage / conformité réglementaire et statuts d'entreprise finalisés.

---

### Jalon 7 : Déploiement Progressif et Mise à l'Échelle (Mois 18 à 24)
- **Objectif** : Déployer PREVIA auprès de 5 à 10 organisations partenaires et atteindre la rentabilité d'exploitation autonome.
- **Actions clés** :
  1. Commercialisation des premiers forfaits de campagne auprès d'ONG internationales de premier plan.
  2. Signature de licences annuelles auprès de réseaux de cliniques privées ou de mutuelles d'entreprise.
  3. Réponse aux premiers appels d'offres de ministères de la santé pour des programmes nationaux MNT.
- **Dépendances** : Équipe commerciale et support client dédiée (1,5 ETP).
- **Livrable** : Plus de 25 000 profils évalués annuellement et rentabilité opérationnelle confirmée.

---

## 3. Matrice des Dépendances Critiques et Gestion des Risques

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│     DÉPENDANCE            │     RISQUE IDENTIFIÉ      │     PLAN D'ATTÉNUATION    │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ **Technique**             │ Panne réseau ou coupure   │ Mode PWA avec cache local │
│ (Connectivité terrain)    │ électrique lors du dépiste│ et export différé JSON.   │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ **Humaine**               │ Rejet ou saturation des   │ Interface en 90 secondes, │
│ (Adoption soignante)      │ infirmiers surchargés     │ formation pratique et SUS.│
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ **Réglementaire**         │ Requalification en DM     │ Maintien strict du statut │
│ (Marquage logiciel)       │ lourd de classe IIb       │ d'aide à la décision OMS. │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ **Financière**            │ Décalage des paiements    │ Coûts fixes ultra-légers  │
│ (Trésorerie d'amorçage)   │ des bailleurs publics     │ (< 350 €/mois de serveurs)│
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
```
