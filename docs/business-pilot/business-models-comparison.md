# Comparaison des Modèles Économiques et Stratégie Tarifaire
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Analyse Comparative des 5 Modèles Économiques

Le secteur de la santé numérique publique obéit à des contraintes budgétaires singulières : les budgets sont annuels ou bisannuels, fragmentés entre bailleurs internationaux et lignes ministérielles, et caractérisés par une aversion aiguë aux coûts cachés d'infrastructure.

Cinq modèles économiques ont été évalués pour déterminer la stratégie commerciale la plus pérenne pour PREVIA Health AI.

---

### Matrice d'Évaluation Comparative des Modèles

| Modèle Économique | Description opérationnelle | Cycle de vente | Prévisibilité des revenus | Marge brute indicative | Alignement avec la santé publique | Risque principal |
|---|---|---|---|---|---|---|
| **1. Licence perpétuelle On-Premise** | Vente du code source et installation sur les serveurs du client avec redevance de maintenance annuelle (15–20 %). | Très long (18–24 mois) | Faible (paiement unique upfront) | 60–75 % (hors support sur site) | Faible (inaccessible pour la majorité des ONG et districts) | Obsolescence rapide des versions et support ingénierie démesuré. |
| **2. Abonnement SaaS B2B classique** | Facturation mensuelle ou annuelle par utilisateur soignant ou par centre de santé connecté. | Moyen (6–9 mois) | Élevée (ARR récurrent) | 70–85 % | Moyen (les campagnes terrain sont saisonnières, pas continues) | Churn élevé entre deux campagnes de dépistage. |
| **3. Prestation de service & Intégration pure** | Vente de journées d'ingénierie et de consulting pour adapter PREVIA aux systèmes d'information hospitaliers. | Variable (3–6 mois) | Faible (dépendance aux appels d'offres) | 25–40 % | Élevé (très prisé des bailleurs pour l'assistance technique) | Faible scalabilité, risque de devenir une simple ESN sans produit pérenne. |
| **4. Forfait par Campagne de Dépistage** | Facturation forfaitaire pour une campagne (60 jours d'accès, quotas de profils, support dédié et rapport). | Court à moyen (2–4 mois) | Moyenne (activité saisonnière prévisible) | 40–55 % | **Très élevé** (calqué sur le mode de financement par projet des ONG/bailleurs) | Nécessite un renouvellement commercial régulier auprès des bailleurs. |
| **5. Pilote Subventionné / Co-financement** | Prise en charge intégrale d'une expérimentation de 6 mois par une subvention de recherche ou un prix d'innovation. | Immédiat à court (post-challenge) | Garantie sur la durée du projet | 25–35 % | **Parfait pour la phase d'amorçage post-hackathon** | Financement non reconductible sans validation des KPIs de succès. |

---

## 2. Stratégie Économique Recommandée : Trajectoire en 3 Phases

Face à la maturité actuelle de PREVIA (prototype de recherche avancé v0.8/v0.9 validé en environnement synthétique), imposer un abonnement SaaS annuel rigide mènerait à un blocage commercial.

PREVIA adopte une **stratégie séquentielle pragmatique** :

```
[Phase 1 : Amorçage] ────────────> [Phase 2 : Traction] ────────────> [Phase 3 : Échelle]
Mois 1 à 6                        Mois 7 à 18                        Mois 18 et au-delà
Pilote encadré co-financé         Forfaits Campagnes Foraines        Modèle Hybride Open-Core
(Prix Challenge + Subvention)     & Licences Institutionnelles       & Déploiements Nationaux
```

### Phase 1 : Le Pilote Encadré Co-Financé (Mois 1 à 6)
- **Objectif** : Prouver la faisabilité terrain, la robustesse technique et l'acceptabilité soignante sans friction commerciale pour le premier partenaire.
- **Financement** : Financement par la dotation du *Future Health Digital Innovation Challenge 2026* complétée par un co-financement d'innovation en santé (ex. subvention d'amorçage ou fonds d'innovation d'une ONG partenaire).
- **Livrable** : Rapport d'évaluation indépendant mesurant les 12 KPIs opérationnels du pilote.

### Phase 2 : Forfaits Campagnes et Abonnements Annuels (Mois 7 à 18)
- **Objectif** : Générer les premiers revenus commerciaux autonomes et atteindre l'équilibre opérationnel (point mort).
- **Cible commerciale** :
  1. *Forfaits par Campagne* vendus aux ONG humanitaires menant des missions de 1 à 2 mois.
  2. *Licences Annuelles Institutionnelles* souscrites par des réseaux de cliniques ou mutuelles assurant un dépistage continu à l'accueil.
- **Règle de facturation** : Tarification transparente combinant un socle fixe et une composante variable par profil évalué au-delà du forfait.

### Phase 3 : Modèle Hybride Open-Core & Déploiements Grands Comptes (Mois 18+)
- **Objectif** : Déploiement à grande échelle auprès de ministères de la santé et de consortiums multi-pays.
- **Architecture de l'offre** :
  - *Noyau Open-Source* (Licence permissive type Apache-2.0 ou AGPL-3.0) : Algorithmes de calcul OMS 2019, modules d'allocation déterministes, documentation scientifique publique.
  - *Édition Entreprise & Services Managés* : Hébergement infogéré souverain certifié HDS / souveraineté locale, intégration SSO / annuaires d'agents, interfaçage avec les Dossiers Médicaux Partagés (DMP / DHIS2), moteur RAG Knowlia dédié avec modèles d'IA souverains sur site.

---

## 3. Grille Tarifaire Indicative et Hypothèses Financières

> **Avertissement de transparence** : Les tarifs ci-dessous constituent des hypothèses de modélisation équitables et cohérentes avec les standards des projets de santé numérique internationale. Aucun de ces tarifs ne constitue un devis contractuel ou un accord commercial déjà signé.

### Détail des Trois Offres Commerciales

```
┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│         FORFAIT PILOTE           │   │         PACK CAMPAGNE            │   │        LICENCE ANNUELLE          │
│       12 000 € HT / 6 mois       │   │         2 500 € HT / 60 j        │   │         15 000 € HT / an         │
├──────────────────────────────────┤   ├──────────────────────────────────┤   ├──────────────────────────────────┤
│ • Déploiement souverain dédié    │   │ • 60 jours d'accès dédié         │   │ • Accès permanent illimité       │
│ • Paramétrage territorial        │   │ • Jusqu'à 2 500 profils inclus   │   │ • Jusqu'à 5 campagnes / an       │
│ • Formation 5 à 10 soignants     │   │ • 0,30 € / profil supplémentaire │   │ • RAG documentaire illimité      │
│ • Astreinte technique SLA        │   │ • Support technique N2           │   │ • Support prioritaire SLA 24h    │
│ • Audit & rapport d'évaluation   │   │ • Export vérifié des données     │   │ • Mises à jour & audit annuel    │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
```

### 1. Forfait Pilote Encadré (12 000 € HT pour 6 mois)
- *Ce qu'il inclut* :
  - Mise à disposition d'une instance cloud souveraine isolée pendant 6 mois.
  - Paramétrage personnalisé (grille régionale OMS appropriée, découpage sectoriel local).
  - Deux sessions de formation pratique des soignants et remise des guides d'usage bilingues.
  - Accompagnement technique et supervision des 500 à 1 000 premiers profils évalués.
  - Audit indépendant des données et rédaction conjointe du rapport d'évaluation final.
- *Structure des coûts associés* : ~9 240 € de coûts directs (ingénierie, support, infrastructure, audit) dégageant une marge de sécurité de ~23 % réinvestie dans l'amélioration logicielle.

### 2. Forfait Campagne de Dépistage (2 500 € HT / campagne de 60 jours)
- *Ce qu'il inclut* :
  - Déploiement clé en main d'un espace de travail sécurisé pendant 60 jours.
  - Forfait de 2 500 profils inclus (suffisant pour une campagne type de 2 à 4 semaines).
  - Facturation de 0,30 € HT par profil au-delà de 2 500 profils.
  - Support technique réactif par courriel et messagerie soignante.
- *Structure des coûts associés* : ~1 500 € de coûts directs d'exploitation, générant une contribution brute de 1 000 € par campagne (marge brute de 40 %).

### 3. Licence Annuelle Institutionnelle Multi-Sites (15 000 € HT / an)
- *Ce qu'il inclut* :
  - Déploiement multi-établissements (jusqu'à 10 centres de soins connectés).
  - Accès permanent aux modules de simulation et d'aide à la décision.
  - Jusqu'à 5 campagnes intensives activables au cours de l'année.
  - Volume documentaire RAG illimité via le moteur souverain Knowlia.
  - Engagement de service (SLA) avec résolution sous 24 heures ouvrées.
- *Structure des coûts associés* : ~4 100 € de coûts directs de maintenance et de serveurs, générant une contribution brute de 10 900 € par contrat (marge brute de 72 %).

---

## 4. Justification de la Viabilité Économique

La viabilité économique de PREVIA repose sur trois piliers fondamentaux :
1. **Un coût marginal d'évaluation quasi-nul** : Grâce au calcul déterministe en mémoire et au modèle RAG frugal, évaluer 10 000 profils supplémentaires ne coûte que quelques dizaines d'euros d'électricité serveur et moins de 5 euros de tokens IA.
2. **Une absence d'actifs physiques lourds** : Contrairement aux dispositifs médicaux invasifs (qui exigent fabrication, pièces détachées et maintenance sur site), PREVIA est un progiciel conteneurisé immédiatement déployable sur n'importe quel serveur standard.
3. **Un point mort exceptionnellement bas** : Moins de 4 campagnes par an suffisent à couvrir l'ensemble des charges fixes de maintien en conditions opérationnelles du projet.
