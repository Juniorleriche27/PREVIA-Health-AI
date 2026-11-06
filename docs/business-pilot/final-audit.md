# Audit final scientifique, financier et commercial

## Avis de préparation

**Prêt pour le jury avec les réserves explicites du dossier corrigé.** Le modèle est mathématiquement réconcilié et reproductible. Il reste un modèle de planification : aucune vente, marge réelle, facture fournisseur ou performance clinique de pilote n'est démontrée.

## Défauts matériels corrigés

| Domaine | Défaut initial | Correction vérifiée |
|---|---|---|
| Revenus | dépassements de profils ajoutés sans quantité facturable explicite | revenus limités aux trois prix déclarés; revenu complémentaire = 0 € |
| Marges | rapports et SVG fondés sur des CA erronés | neuf marges et graphiques régénérés |
| Coûts | hypothèses décrites comme coûts observés | séparation architecture vérifiée / justificatifs absents / hypothèses |
| Ventilation | pourcentages codés en dur | montants et parts calculés depuis les fonctions de coûts |
| Point mort | seuil continu présenté comme quantité vendable | seuil continu conservé et seuil commercial arrondi à 4 campagnes ou 1 licence |
| Coût/profil | coût total et coût marginal confondus | coût total modélisé et coût technique direct séparés |
| Science | tirage aléatoire assimilé au dépistage opportuniste | comparateur pseudo-aléatoire synthétique uniquement |
| Impact | simulations décrites comme preuve d'impact ou d'équité | cohérence algorithmique sur données synthétiques uniquement |
| Pilote | cibles formulées comme garanties | cibles proposées distinguées des résultats non mesurés |
| Open-Core | dépôt public décrit comme open source | absence de `LICENSE` explicitée; aucun droit général revendiqué |

## Contrôles de cohérence

- grain unique scénario × année : 9 lignes et clés uniques;
- CA = pilotes × 12 000 € + campagnes × 2 500 € + licences × 15 000 €;
- coûts = infrastructure + tokens + DevOps + support + audit;
- marge = CA − coûts;
- aucun revenu supplémentaire;
- manifeste et fichiers vérifiés par SHA-256;
- SVG dérivés des CSV et XML valides;
- documents FR/EN alignés sur les mêmes nombres et limites.

## Limites

Les prix et volumes sont indicatifs. Le modèle n'inclut pas encore fiscalité, TVA, assurance, frais juridiques, acquisition commerciale, coût du capital, change, impayés ou rémunération exhaustive de l'équipe. Un budget de contractualisation devra s'appuyer sur des pièces justificatives.
