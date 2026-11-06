# Jury brief — potential health impact

## Core message

PREVIA does not claim to have reduced cardiovascular events. It currently demonstrates, reproducibly, an ability to **make capacity-constrained screening allocation auditable** and expose its trade-offs.

## Quantitative demonstration

- Experiment: 30 synthetic cohorts of 240 profiles, four capacities, three existing rules.
- Baseline: 121/240 profiles in the descriptive WHO chart-cell ≥10% category.
- At 45 slots: chart ordering and sector balancing each select 45 category profiles (37.19%); the random control selects 22 (18.18%).
- Across 30 seeds at 45 slots: median coverage is 44.12% for both chart-guided rules and 18.52% for random selection.
- Median fictional-sector selection-rate gap: 10.00 points for chart ordering, 1.67 for sector balancing, and 10.00 for random selection.

## Correct interpretation

Chart ordering must perform strongly on a category defined by the same chart. This is algorithmic consistency, **not** clinical validation. Sector balancing reduces the gap it optimises, but does not prove equitable access or outcomes.

## Potential value

PREVIA could help a health system test capacity, document rules, identify profiles left unselected, explain trade-offs, and prepare a supervised pilot. The next evidence must measure real timeliness, appropriate referral, completed follow-up, errors, acceptability, and group differences.

## Verifiability

The repository includes all 360 experiment rows, aggregate tables, charts, configurations, and SHA-256 fingerprints. One command regenerates the results, with regression tests protecting the baseline.
