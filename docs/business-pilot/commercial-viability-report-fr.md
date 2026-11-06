# PREVIA — viabilité commerciale et chemin vers un pilote

## Synthèse exécutive

PREVIA est un prototype de recherche bilingue déployé, associant une grille cardiovasculaire OMS non biologique, des simulations synthétiques d'allocation, un module exploratoire NHANES/SHAP distinct et un assistant documentaire RAG. Sa valeur commerciale potentielle réside dans la traçabilité, l'expérimentation des capacités et l'accompagnement d'un futur pilote supervisé. **Aucun bénéfice clinique ni chiffre d'affaires réel n'est encore démontré.**

Le modèle financier corrigé repose sur trois prix indicatifs : pilote 12 000 €, campagne 2 500 € et licence annuelle 15 000 €. Les neuf chiffres d'affaires sont strictement issus des quantités déclarées; aucun dépassement de profils n'est facturé. Les CA vont de 12 000 € à 212 500 €, avec des marges modélisées de 27,96 % à 57,78 %. Ces marges utilisent des hypothèses de coûts non justifiées par des factures ou devis dans le dépôt.

## Problème et proposition de valeur

Les organisations qui disposent d'une capacité de dépistage limitée peuvent avoir besoin de règles explicites, reproductibles et auditables pour simuler l'allocation de créneaux. PREVIA permet actuellement de comparer trois règles sur des profils fictifs et de visualiser les personnes artificielles sélectionnées ou non sélectionnées.

Le chantier 15 n'a pas mesuré des patients, un parcours réel, une baisse d'événements cardiovasculaires ou une économie de ressources. Il a montré, sur 30 cohortes synthétiques et quatre capacités, le comportement des règles implémentées. Le comparateur `seeded_random` est un tirage pseudo-aléatoire reproductible; ce n'est ni un ordre d'arrivée, ni un dépistage opportuniste observé.

## Clients et financeurs potentiels

Segments à tester par entretiens et pilotes, sans présumer d'un contrat :

- ONG et programmes de santé communautaire;
- districts et réseaux de soins primaires;
- hôpitaux ou cliniques souhaitant tester un parcours supervisé;
- instituts de recherche utilisant uniquement des protocoles autorisés;
- bailleurs finançant l'évaluation de solutions numériques de santé.

Aucun partenariat, pipeline de vente, taille de marché locale ou délai de décision n'est démontré dans le dépôt.

## Offre indicative

| Offre | Prix de planification | Contenu à contractualiser |
|---|---:|---|
| Pilote supervisé | 12 000 € | préparation, déploiement, formation, support et rapport; périmètre soumis aux autorisations |
| Campagne | 2 500 € | accès limité dans le temps, onboarding et support; volume exact à préciser au contrat |
| Licence annuelle | 15 000 € | droit d'usage et services définis par contrat; SLA, limites et données à négocier |

Ces prix ne sont pas des tarifs validés par le marché. L'ancien supplément de 0,30 €/profil n'est pas modélisé dans les scénarios corrigés.

## Résultats financiers corrigés

| Scénario | A1 | A2 | A3 |
|---|---:|---:|---:|
| Prudent | 12 000 € | 19 500 € | 30 000 € |
| Central | 17 000 € | 45 000 € | 112 500 € |
| Ambitieux | 34 000 € | 90 000 € | 212 500 € |

Voir [l'analyse financière détaillée](financial-analysis.md) et les [CSV reproductibles](results/financial_scenarios.csv). Les coûts sont des estimations, et non des dépenses observées. Le seuil de 4 campagnes ou 1 licence est conditionnel aux prix et coûts supposés.

## Architecture et coûts

L'usage de Vercel, Netcup, Knowlia et du domaine de l'API est vérifiable. Les montants de 20 €/mois, 25 €/mois, 0,0015 €/requête et les budgets de maintenance/support/audit ne le sont pas faute de justificatifs. Le modèle les classe comme hypothèses. Il sépare coût total/profil et coût technique direct/profil afin d'éviter de présenter un coût marginal artificiellement bas.

## Plan pilote

Avant tout usage avec de vraies personnes : approbation éthique et réglementaire, accord du responsable de traitement, analyse d'impact, protocole clinique local, consentement/base légale, minimisation et durée de conservation, sécurité, supervision humaine, gestion des incidents et plan statistique préenregistré.

Les KPI sont des cibles proposées. Ils doivent être mesurés prospectivement; aucune disponibilité à 99,5 %, complétude à 98 %, durée de 90 secondes, équité, validité RAG à 100 % ou suivi à 60 % n'est revendiquée comme déjà atteinte.

## Statut du code et modèle commercial

Le dépôt GitHub est publiquement consultable mais ne contient aucun fichier `LICENSE`. En l'absence de licence, la consultation publique ne confère pas un droit général de copier, modifier ou redistribuer. PREVIA ne doit donc pas être présenté aujourd'hui comme open source ou Open-Core sous licence permissive.

Une future stratégie Open-Core exige une décision explicite sur les composants, une licence rédigée, la vérification des dépendances et la définition des services commerciaux. En attendant, l'offre commerciale porte sur des services et droits contractuels à définir, sans promesse de licence open source.

## Position défendable devant le jury

PREVIA dispose d'un prototype fonctionnel, d'expériences synthétiques reproductibles et d'un modèle économique transparent après correction. La prochaine étape n'est pas de revendiquer un impact massif : elle consiste à obtenir les autorisations, valider les coûts par justificatifs, tester l'acceptabilité et mesurer sécurité, orientation appropriée, délais, suivi et écarts entre groupes dans un pilote supervisé.
