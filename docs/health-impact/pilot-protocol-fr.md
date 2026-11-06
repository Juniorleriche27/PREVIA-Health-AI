# Protocole de mesure pour un futur pilote

## Finalité et statut

Ce document propose une évaluation prospective à conduire **uniquement après** approbations éthique, réglementaire, clinique, sécurité et protection des données. Il ne constitue pas une autorisation de déploiement auprès de patients.

## Question principale

Dans un parcours de prévention défini par un partenaire de santé, l'utilisation supervisée de PREVIA améliore-t-elle la proportion de personnes correctement évaluées et orientées dans les délais préspécifiés, sans accroître les erreurs ni les écarts injustifiés entre groupes, par rapport au processus habituel ?

## Conception recommandée

Une étude pragmatique prospective avec déploiement échelonné par site ou grappe est préférable si l'organisation ne peut pas randomiser individuellement. Lorsque possible, utiliser une randomisation en grappes ou un essai contrôlé avec analyse en intention de traiter. Préenregistrer protocole, critère principal, comparateur, taille d'échantillon, règles d'arrêt et plan statistique avant l'accès aux résultats.

## Population et gouvernance

- définir sites, population cible, critères d'inclusion/exclusion et fenêtre temporelle;
- documenter la représentativité et les personnes non incluses;
- recueillir uniquement les données nécessaires, avec base légale/consentement adapté;
- garantir revue humaine des orientations, procédure d'escalade et possibilité d'annuler la recommandation;
- geler versions de grille, modèle, règles, interface et prompts pendant chaque phase;
- journaliser version, entrée, sortie, action humaine, motif de dérogation et délais;
- établir suivi des incidents, cybersécurité, biais, dérive et qualité des données.

## Comparateur

Le comparateur doit être le processus réel documenté avant PREVIA, et non un tirage aléatoire. Décrire ressources, critères, délais, taux d'absence, orientations et pertes de suivi. Éviter de modifier simultanément plusieurs composantes sans pouvoir attribuer les effets.

## Indicateurs préspécifiés

| Domaine | Indicateur | Définition opérationnelle minimale |
|---|---|---|
| Accès | délai jusqu'à l'évaluation | médiane et quantiles entre éligibilité et évaluation terminée |
| Capacité | proportion évaluée | personnes évaluées / personnes éligibles pendant la fenêtre |
| Orientation | orientation appropriée | concordance avec adjudication clinique indépendante et protocole local |
| Sécurité | sous-orientation | personnes nécessitant une orientation mais non orientées dans le délai |
| Surcharge | sur-orientation | orientations jugées non indiquées par l'adjudication |
| Suivi | orientation complétée | rendez-vous/service approprié effectivement achevé dans la fenêtre |
| Continuité | perte de suivi | personnes orientées sans résultat documenté |
| Expérience | acceptabilité | mesure validée auprès des professionnels et participants |
| Opérations | temps professionnel | minutes médianes par dossier et charge par rôle |
| Équité | écarts absolus/relatifs | indicateurs précédents par groupes préspécifiés, avec incertitude |
| Fiabilité | disponibilité/erreurs | taux d'échec, latence, réponses incomplètes, dérogations humaines |
| Résultats cliniques | événements exploratoires | uniquement avec suivi suffisant et adjudication; pas comme promesse initiale |

## Groupes et équité

Choisir les groupes avec les partenaires et personnes concernées : âge, sexe/genre lorsque pertinent, zone, langue, handicap, statut socio-économique et autres dimensions légalement/éthiquement appropriées. Rapporter dénominateurs, données manquantes, écarts absolus, rapports, intervalles d'incertitude et intersections lorsque les effectifs le permettent. Ne pas déclarer l'équité sur la seule parité de sélection.

## Plan d'analyse

1. Analyse principale en intention de traiter au niveau d'assignation.
2. Ajustement pour le plan en grappes, période, site et facteurs préspécifiés.
3. Estimations d'effet avec intervalles de confiance, pas uniquement valeurs p.
4. Analyse des données manquantes et de la perte de suivi.
5. Analyses de sensibilité : changements de capacité, adhérence, contamination et temps d'apprentissage.
6. Calibration/discrimination évaluées seulement si une cible prédictive, des issues et un horizon temporel clairs sont disponibles.
7. Analyse qualitative des dérogations, incidents et effets inattendus.

La taille d'échantillon doit être calculée à partir du critère principal, de la différence minimale cliniquement/organisationnellement pertinente, de la variabilité réelle, de la corrélation intra-grappe et de l'attrition. Aucun nombre n'est inventé ici.

## Critères de passage

Avant extension, définir des seuils validés par la gouvernance pour : complétude, disponibilité, sous-orientation, incidents graves, délais, écarts de groupes et capacité de revue humaine. Une dégradation de sécurité ou un écart inexpliqué doit déclencher pause et analyse. Le succès opérationnel ne remplace pas la sécurité clinique.

## Séparation des preuves

- la grille OMS doit être évaluée pour la population et le contexte d'utilisation prévus;
- le modèle NHANES HbA1c nécessite sa propre validation externe et ne doit pas être assimilé au risque cardiovasculaire;
- SHAP évalue la fidélité d'une explication au modèle, pas la causalité;
- le RAG/LLM doit être évalué sur exactitude documentaire, citations, abstention et risque d'information trompeuse;
- l'allocation doit être évaluée sur processus, sécurité et équité réelle.

## Livrables du pilote

Protocole enregistré, dictionnaire des données, plan statistique, rapport CONSORT/STROBE approprié au plan, tableau des incidents, analyse d'équité, journal des versions, résultats négatifs compris, et décision documentée de poursuivre, modifier ou arrêter.
