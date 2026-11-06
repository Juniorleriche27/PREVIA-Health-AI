# Synthèse Jury : Viabilité Commerciale et Plan Pilote
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**
*Note exécutive pour le jury d'évaluation (Temps de lecture : 2 minutes)*

---

### 1. Qui a besoin de PREVIA ?
Les **organisations de santé publique, ONG humanitaires et réseaux de soins primaires** qui mènent des campagnes de prévention cardiovasculaire sous de fortes contraintes budgétaires et logistiques. Elles ne peuvent pas examiner tout le monde en même temps et doivent décider objectivement qui évaluer en priorité, sans gaspiller leurs ressources humaines et sans exclure les populations isolées.

---

### 2. Pourquoi cette solution ?
Parce que PREVIA ne vend pas un algorithme obscur ou un simple calculateur isolé, mais une **plateforme complète d'optimisation d'allocation et d'aide à la décision** :
- **Zéro dépendance de laboratoire** : Évaluation déterministe certifiée de la grille OMS 2019 en 5 paramètres non invasifs (tension, âge, tabac, IMC).
- **Optimisation sous contrainte de capacité** : Modélise et applique des quotas stricts (15 %, 25 %, 50 %) pour doubler le taux de capture des profils prioritaires par rapport à un dépistage opportuniste aléatoire (démontré sur 360 expérimentations dans le chantier 15).
- **Garantie d'équité territoriale** : Réduit la disparité de sélection entre quartiers à moins de 2 points de pourcentage.
- **Transparence totale** : Explications SHAP et assistant documentaire RAG souverain strictement ancré dans les textes officiels OMS/CDC.

---

### 3. Qui pourrait la financer ?
- **À court terme (Phase Pilote)** : La dotation du Future Health Challenge et les fonds d'amorçage d'ONG internationales de santé (ex. Médecins du Monde, ALIMA, Croix-Rouge).
- **À moyen terme (Déploiement commercial)** : Les bailleurs multilatéraux (USAID, Fonds Mondial, Banque Mondiale, Agence Française de Développement), les programmes nationaux MNT des ministères de la santé et les mutuelles de prévoyance santé au travail.

---

### 4. Comment peut-elle être déployée ?
Grâce à un modèle hybride frugal :
- **Techniquement** : Architecture conteneurisée Docker ultralégère, déployable en SaaS cloud souverain (coût fixe observé : ~62 €/mois sur Netcup/Vercel) ou en mode local hors-ligne (PWA) sur PC portable tout-terrain pour les zones blanches.
- **Commercialement** : Forfaits clé en main par campagne foraine (2 500 € pour 2 500 profils) et licences annuelles multi-sites (15 000 €/an pour réseaux de cliniques).

---

### 5. Quel serait le premier pilote ?
Une **expérimentation encadrée de 6 mois avec une ONG médicale partenaire** menant une campagne de dépistage primaire auprès de 500 à 1 000 participants adultes (40–74 ans) :
- *Protocole en 4 phases* : Cadrage éthique (M1) ➔ Formation & test à blanc sur 50 cas fictifs (M2) ➔ Dépistage terrain sous double regard soignant 100 % médicalisé (M3-M4) ➔ Audit statistique indépendant et restitution (M5-M6).
- *Données pseudonymisées* : Zéro persistance de données nominatives personnelles, respect total de la vie privée.
- *Règles d'arrêt strictes* : Arrêt immédiat en cas d'écart de calcul ou de tentative d'usage sans supervision médicale.

---

### 6. Quels résultats mesurables justifieraient un investissement ?
La validation de la matrice des **12 indicateurs clés de performance (KPI)**, notamment :
1. **Complétude des dossiers ≥ 98 %** et durée moyenne d'évaluation **≤ 90 secondes** par soignant.
2. **Concordance OMS de 100 %** sans aucune anomalie mathématique.
3. **Disparité de sélection inter-secteurs ≤ 5 points** (équité d'accès prouvée).
4. **Coût marginal direct < 0,50 € par profil évalué**.
5. **Satisfaction soignante élevée** (Score System Usability Scale - SUS ≥ 80 / 100).
6. **Taux de conversion vers le suivi préventif ≥ 60 %** à 30 jours pour les profils prioritaires.

---

### 7. Pourquoi soutenir ce projet après le hackathon ?
1. **Une maturité d'ingénierie exceptionnelle** : Ce n'est pas un concept sur diapositives. La plateforme est déjà bilingue, fonctionnelle, déployée en ligne et couverte par plus de 140 tests unitaires automatisés.
2. **Une viabilité financière prouvée** : Charges fixes minimes (< 4 000 €/an) permettant d'atteindre le point mort économique dès **4 campagnes ou une seule licence annuelle**.
3. **Un impact sanitaire massif et mesurable** : Une solution prête à transformer immédiatement l'efficience des campagnes de dépistage cardiovasculaire là où l'accès aux laboratoires est impossible.
