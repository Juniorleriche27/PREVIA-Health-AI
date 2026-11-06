# Stakeholders and value propositions to validate

## Potential segments

| Segment | Possible users | Decision/governance | Value hypothesis to test |
|---|---|---|---|
| Community-health NGOs | coordinators, nurses, analysts | medical leadership, ethics, data controller | plan limited capacity and document decisions |
| District and primary care | care teams and programme managers | health authorities and local protocols | standardise the demonstration and expose rules |
| Hospitals and clinic networks | intake, prevention, physicians | medical leadership, security, procurement | integrate supervised assessment without excessive burden |
| Occupational health/mutuals | occupational-health professionals | clinical governance and data protection | test an authorised confidential prevention pathway |
| Research and universities | researchers and biostatisticians | scientific/ethics committees and controller | reproduce simulations and study allocation trade-offs |

These segments, users, decision-makers, and values are customer-discovery hypotheses. No buying cycle, budget, priority need, or partnership is demonstrated.

## Current capabilities

- deterministic lookup of a regional WHO non-laboratory chart;
- entirely synthetic cohorts and sectors;
- comparison of three allocation rules;
- software audit and reproducible export;
- NHANES HbA1c model and SHAP kept separate from the cardiovascular chart;
- source-grounded documentary RAG assistant.

## Value boundaries

PREVIA does not model country prevalence, drug requirements, hospital savings, or prevented events. The prototype is not described as offline/PWA until that capability is implemented and verified. Ninety-second intake, zero record loss, and improved adherence remain hypotheses to measure.

Sector balancing reduces one selection-rate gap across fictional sectors in simulation; it does not prove clinical equity. The random comparator is not observed usual care.

## Alternatives to study

Relevant alternatives depend on the partner: paper workflow, spreadsheet, individual calculator, medical record, or existing campaign tool. The dossier contains no verified usage share, record-loss rate, or cost data for these alternatives. Field research should compare time, errors, completeness, security, follow-up, and total cost over the same scope.

## Code status

The repository is public and inspectable but has no `LICENSE` file. It must not be described as Open-Core or open source. Future licensing requires an explicit decision and legal review.

## Discovery questions before a pilot

1. What operational problem does the partner need to solve and how is it currently measured?
2. What documented usual practice will be the comparator?
3. Who holds clinical and data responsibility?
4. Which approvals and integrations are required?
5. What actual budget covers preparation, fieldwork, follow-up, security, and analysis?
6. Which safety and decision thresholds justify continuation or stopping?
