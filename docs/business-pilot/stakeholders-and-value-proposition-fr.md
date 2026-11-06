# Analyse des Parties Prenantes et Proposition de Valeur
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Cartographie Détaillée des 5 Segments Institutionnels

L'analyse de la chaîne de valeur en santé publique montre que l'adoption d'un outil numérique échoue presque toujours lorsque l'on confond l'usager direct (qui saisit les données), le décideur (qui autorise le déploiement) et le financeur (qui débloque les budgets).

PREVIA Health AI distingue méthodiquement ces rôles pour chacun des cinq segments de son écosystème.

---

### Segment 1 : Organisations Non Gouvernementales (ONG) Médicales et Acteurs Humanitaires
*Exemples types : Médecins du Monde, ALIMA, Croix-Rouge, consortiums de santé communautaire.*

- **Bénéficiaire final** : Les populations vulnérables, rurales ou périurbaines, souvent exclues des parcours de soins formels et sans accès à des analyses biologiques de laboratoire.
- **Utilisateurs directs** : Les coordinateurs de missions mobiles, les superviseurs de santé communautaire et les infirmiers de terrain.
- **Décideur institutionnel** : Le Directeur Pays / Responsable du pôle santé de l'ONG, en concertation avec le référent médical du siège.
- **Financeur** : Les bailleurs de fonds humanitaires et de développement (USAID/BHA, Direction Générale ECHO de l'Union Européenne, agences de coopération bilatérale, fondations philanthropiques privées).
- **Processus d'adoption** : Cycle court à moyen (3 à 6 mois). Présentation technique, validation par le comité médical interne, convention bilatérale de projet pilote sur une zone d'intervention ciblée.
- **Proposition de valeur spécifique** :
  - *Maximisation de l'impact sous budget contraint* : Permet de calibrer exactement le nombre de personnes dépistées en fonction du nombre d'équipes mobiles disponibles.
  - *Reporting d'impact vérifiable pour les donateurs* : Génération instantanée d'audits statistiques prouvant l'efficience allocative de la subvention.
  - *Simplicité et robustesse en zone isolée* : Fonctionne avec 5 paramètres cliniques basiques sans prise de sang ni réactifs.
- **Freins identifiés et réponses PREVIA** :
  - *Frein* : Connectivité Internet instable dans les zones reculées.
  - *Réponse* : Architecture web légère, PWA pré-cacheable et possibilité de déploiement en conteneur local sur PC portable tout-terrain.

---

### Segment 2 : Ministères de la Santé et Directions de la Prévention des MNT
*Exemples types : Programmes Nationaux de Lutte contre les Maladies Non Transmissibles (PNL-MNT), Directions Régionales de la Santé.*

- **Bénéficiaire final** : L'ensemble de la population adulte âgée de 40 à 74 ans à l'échelle d'un district, d'une région ou du territoire national.
- **Utilisateurs directs** : Les médecins inspecteurs régionaux, les chefs de districts sanitaires et les statisticiens épidémiologistes ministériels.
- **Décideur institutionnel** : Le Directeur Général de la Santé Publique et le Secrétaire Général du Ministère de la Santé.
- **Financeur** : L'État via le budget général de la santé, appuyé par les partenaires techniques et financiers multilatéraux (Organisation Mondiale de la Santé, Banque Mondiale, Fonds Mondial, Agence Française de Développement).
- **Processus d'adoption** : Cycle long et hautement réglementé (12 à 24 mois). Inscription dans le plan stratégique national MNT, avis du comité national d'éthique, procédure d'appel d'offres public.
- **Proposition de valeur spécifique** :
  - *Outil de simulation macro-sanitaire* : Permet de modéliser les besoins de prise en charge et les coûts prévisionnels d'antihypertenseurs avant le lancement d'une politique nationale.
  - *Harmonisation des pratiques* : Déploiement d'un protocole d'évaluation OMS 2019 strict, éliminant les disparités arbitraires de triage entre centres de santé urbains et ruraux.
  - *Souveraineté des données sanitaires* : Déploiement possible sur des serveurs gouvernementaux ou dans un cloud national dédié.
- **Freins identifiés et réponses PREVIA** :
  - *Frein* : Inertie bureaucratique et crainte d'ingérence technologique étrangère.
  - *Réponse* : Code socle ouvert et auditable, aucun stockage sauvage de données à l'étranger, conformité intégrale avec le guide OMS HEARTS.

---

### Segment 3 : Réseaux de Soins Primaires, Centres Médicaux et Hôpitaux de District
*Exemples types : Réseaux de cliniques privées d'intérêt public, centres de santé confessionnels, hôpitaux régionaux.*

- **Bénéficiaire final** : Les patients consultants en soins de santé primaires pour un motif divers (consultation générale, renouvellement, soins mineurs).
- **Utilisateurs directs** : Les infirmiers d'accueil et de tri, les assistants médicaux et les médecins généralistes.
- **Décideur institutionnel** : Le Directeur Médical et le Directeur Administratif et Financier de l'établissement.
- **Financeur** : Le budget d'exploitation de la clinique, compensé par les forfaits d'actes de prévention ou les accords avec les mutuelles partenaires.
- **Processus d'adoption** : Cycle moyen (6 à 9 mois). Démonstration d'efficacité organisationnelle, évaluation du temps infirmier économisé et approbation par la commission médicale d'établissement.
- **Proposition de valeur spécifique** :
  - *Fluidification du tri à l'accueil* : Évaluation standardisée en moins de 90 secondes pendant la prise des constantes habituelles (tension, poids, taille).
  - *Sécurisation médico-légale* : Traçabilité informatique de l'évaluation du risque OMS, alertant immédiatement en cas de pression artérielle ≥ 180 mmHg nécessitant un recours urgent.
  - *Valorisation de l'offre de soins préventifs* : Renforce l'image de modernité de l'établissement sans nécessiter d'investissement en matériel lourd.
- **Freins identifiés et réponses PREVIA** :
  - *Frein* : Surcharge de travail des équipes soignantes et rejet des interfaces complexes.
  - *Réponse* : Interface épurée à l'extrême, aucun mot de passe complexe en session locale, navigation fluide en 1 clic.

---

### Segment 4 : Mutuelles de Santé, Assurances et Médecine du Travail
*Exemples types : Mutuelles interentreprises, compagnies d'assurance santé privée, services autonomes de santé au travail.*

- **Bénéficiaire final** : Les adhérents des mutuelles, les assurés individuels et les salariés des entreprises clientes.
- **Utilisateurs directs** : Les médecins du travail, les infirmiers de santé au travail et les chargés de prévention en entreprise.
- **Décideur institutionnel** : Le Directeur de la Prévoyance, le Directeur Technique et Actuariel, le Responsable RSE / Santé au Travail.
- **Financeur** : Les fonds de prévention des risques professionnels ou les budgets d'action sociale de la mutuelle.
- **Processus d'adoption** : Cycle moyen (6 à 12 mois). Analyse du retour sur investissement (ROI médico-économique) et conformité stricte au RGPD / secret médical.
- **Proposition de valeur spécifique** :
  - *Prévention du risque lourd et coûteux* : Évitement des accidents vasculaires cérébraux (AVC) et infarctus précoces dont les coûts d'hospitalisation d'urgence et d'indemnisation d'invalidité pèsent lourdement sur les ratios sinistres/primes.
  - *Engagement des assurés* : Outil moderne permettant de sensibiliser les salariés lors des bilans de santé périodiques avec des explications claires et personnalisées.
  - *Respect absolu de la vie privée* : Fonctionnement sans identifiant nominatif garantissant que l'employeur n'a jamais accès aux données de santé de ses salariés.
- **Freins identifiés et réponses PREVIA** :
  - *Frein* : Exigence d'une démonstration d'impact économique à court terme.
  - *Réponse* : PREVIA met en avant la détection précoce d'hypertensions sévères asymptomatiques non diagnostiquées, dont le bénéfice économique est immédiat en termes de réduction d'arrêts maladie critiques.

---

### Segment 5 : Instituts de Recherche Épidémiologique et Universités
*Exemples types : Centres de recherche en santé mondiale, départements de santé publique, écoles de santé communautaire.*

- **Bénéficiaire final** : La communauté scientifique internationale et les cohortes de recherche en santé publique.
- **Utilisateurs directs** : Les chercheurs épidémiologistes, biostatisticiens et étudiants de troisième cycle.
- **Décideur institutionnel** : Le Directeur de laboratoire ou le Chercheur Principal (PI) d'un projet de recherche.
- **Financeur** : Les bourses de recherche et subventions compétitives (Horizon Europe, NIH, Wellcome Trust, ANRS-MIE).
- **Processus d'adoption** : Cycle rapide (2 à 4 mois). Accord de transfert de matériel ou convention de collaboration scientifique.
- **Proposition de valeur spécifique** :
  - *Transparence algorithmique totale* : Accès aux formules déterministes, aux cohortes synthétiques de référence et aux scripts de simulation.
  - *Cadre de benchmark méthodologique* : Outil prêt à l'emploi pour tester et comparer de nouvelles stratégies d'allocation ou de nouveaux modèles prédictifs.
- **Freins identifiés et réponses PREVIA** :
  - *Frein* : Réticence envers les solutions propriétaires fermées.
  - *Réponse* : Philosophie Open-Core avec publication ouverte des méthodes et des données de validation.

---

## 2. Sélection Justifiée du Segment Pilote Prioritaire

### Choix stratégique : L'ONG Médicale / Organisation de Santé Communautaire

Pour mener la première expérimentation réelle encadrée, PREVIA concentre ses efforts de prospection post-challenge sur les **ONG médicales actives dans les soins de santé primaires et les campagnes de dépistage forain**.

```
Critères de décision pour le premier pilote :
1. Vitesse d'instruction éthique et décisionnelle :  ONG (★★★★★) vs Ministère (★★☆☆☆)
2. Concordance avec l'absence de laboratoire :       ONG (★★★★★) vs Clinique privée (★★★☆☆)
3. Présence d'une contrainte aiguë de capacité :     ONG (★★★★★) vs Hôpital (★★★☆☆)
4. Tolérance à l'innovation frugale encadrée :       ONG (★★★★☆) vs Mutuelle (★★★☆☆)
```

Ce segment permet de valider sur le terrain la faisabilité organisationnelle de PREVIA sans s'enliser dans les délais d'appels d'offres publics, tout en intervenant là où le besoin médical non satisfait est le plus criant.

---

## 3. Matrice de la Proposition de Valeur selon les Modules PREVIA

| Module PREVIA dans le code | Fonctionnalité réelle déployée | Usage concret sur le terrain | Valeur ajoutée médico-économique |
|---|---|---|---|
| **Module 01 & 02 : Dépistage & Parcours** | Calcul instantané de la grille OMS 2019 non-labo en 5 paramètres. | L'infirmier saisit tension, âge, tabac, IMC et obtient instantanément la catégorie de risque (vert à rouge foncé). | Élimine les erreurs de calcul manuel ; évite les prescriptions inutiles de bilans lipidiques coûteux. |
| **Module 03 : Population** | Simulation d'une cohorte synthétique locale par graine aléatoire reproductible. | Le coordinateur de campagne simule la distribution probable des risques avant d'envoyer les équipes. | Permet de dimensionner à l'avance les stocks de tensiomètres, fiches et effectifs soignants. |
| **Module 04 : Stratégies d'Allocation** | Comparaison d'allocation sous contrainte (Risque OMS vs Équilibre sectoriel vs Aléatoire). | L'organisateur décide de la règle de sélection des créneaux selon ses objectifs d'équité ou de rendement. | Maximise le nombre de profils à haut risque détectés sans laisser pour compte les quartiers périphériques. |
| **Module 05 : Audit Scientifique** | Mesure des disparités de sélection par secteur géographique et par sexe. | L'analyste vérifie que la stratégie n'introduit pas de discrimination territoriale ou de genre. | Documente la justice allocative pour les financeurs institutionnels et comités d'éthique. |
| **Module 06 : Données Probantes** | Traçabilité des 700 cellules OMS et contrôle des formats de données publiques. | Le médecin référent vérifie la conformité rigoureuse de la table numérique avec le PDF officiel OMS. | Garantit une sécurité médico-légale absolue sans risque d'altération algorithmique. |
| **Module 07 : ML, XAI & RAG** | Explicabilité SHAP des contributions de risque et assistant documentaire sourcé Knowlia. | Le soignant explique au patient pourquoi sa tension fait grimper son risque ; pose des questions aux textes OMS. | Renforce l'adhésion thérapeutique du patient et forme en continu les jeunes soignants sur les recommandations. |

---

## 4. Comparaison Factuelle avec les Solutions Alternatives

### Alternative A : Le registre papier manuscrit
- *Usage actuel* : Utilisé dans plus de 80 % des postes de santé ruraux.
- *Faiblesses majeures* : Perte estimée de 20 % à 35 % des dossiers, aucun croisement possible avec les grilles OMS couleur (tableaux papier complexes et souvent indisponibles), absence totale de vision d'ensemble de la campagne.
- *Avantage PREVIA* : Saisie guidée en 90 secondes, persistance numérique locale, zéro perte de dossier, alertes immédiates.

### Alternative B : Le tableur bureautique (Excel / Google Sheets)
- *Usage actuel* : Bricolé par les coordinateurs pour compiler les données de fin de journée.
- *Faiblesses majeures* : Vulnérabilité aux erreurs de formules, risque de corruption de fichiers, aucune règle d'optimisation sous contrainte de capacité, conformité RGPD / confidentialité quasi nulle.
- *Avantage PREVIA* : Algorithme d'ordonnancement mathématiquement éprouvé, environnement sécurisé conteneurisé, traçabilité cryptographique SHA-256.

### Alternative C : Les calculateurs de risque isolés en ligne (Framingham, SCORE2)
- *Usage actuel* : Consultés ponctuellement par certains médecins sur smartphone.
- *Faiblesses majeures* : Outils purement individuels. Incapables de gérer une cohorte, d'optimiser une capacité globale de campagne, d'auditer les disparités géographiques ou de fournir une assistance documentaire intégrée.
- *Avantage PREVIA* : Véritable progiciel d'aide à la décision collective articulant l'individu, la population et la stratégie de santé publique.
