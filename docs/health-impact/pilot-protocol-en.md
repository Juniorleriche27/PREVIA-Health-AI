# Measurement protocol for a future pilot

## Purpose and status

This document proposes a prospective evaluation to be conducted **only after** ethical, regulatory, clinical, security, and data-protection approvals. It is not authorisation for patient deployment.

## Primary question

Within a prevention pathway defined by a health-system partner, does supervised PREVIA use improve the proportion of people appropriately assessed and referred within prespecified timeframes, without increasing errors or unjustified group gaps, compared with usual practice?

## Recommended design

A prospective pragmatic stepped-wedge site or cluster design may suit organisations unable to randomise individuals. Where feasible, use cluster randomisation or a controlled trial with intention-to-treat analysis. Preregister the protocol, primary endpoint, comparator, sample size, stopping rules, and statistical plan before outcome access.

## Population and governance

- define sites, target population, inclusion/exclusion criteria, and time window;
- document representativeness and people not enrolled;
- collect only necessary data under an appropriate legal basis/consent;
- require human review, escalation, and override of referrals;
- freeze chart, model, rule, interface, and prompt versions within each phase;
- log version, input, output, human action, override reason, and timestamps;
- establish incident, cybersecurity, bias, drift, and data-quality monitoring.

## Comparator

The comparator must be documented real practice before PREVIA—not random allocation. Characterise resources, criteria, delays, no-shows, referrals, and loss to follow-up. Avoid changing multiple pathway components simultaneously when effects cannot be attributed.

## Prespecified measures

| Domain | Measure | Minimum operational definition |
|---|---|---|
| Access | time to assessment | median and quantiles from eligibility to completed assessment |
| Capacity | assessed proportion | assessed people / eligible people within window |
| Referral | appropriate referral | agreement with independent clinical adjudication and local protocol |
| Safety | under-referral | people requiring referral but not referred within timeframe |
| Burden | over-referral | referrals adjudicated as not indicated |
| Follow-up | completed referral | appropriate service actually completed within window |
| Continuity | loss to follow-up | referred people without a documented result |
| Experience | acceptability | validated measure for professionals and participants |
| Operations | staff time | median minutes per case and workload by role |
| Equity | absolute/relative gaps | preceding measures by prespecified groups, with uncertainty |
| Reliability | availability/errors | failure rate, latency, incomplete responses, human overrides |
| Clinical outcomes | exploratory events | only with sufficient follow-up and adjudication; not an initial promise |

## Groups and equity

Select dimensions with partners and affected communities: age, sex/gender where relevant, geography, language, disability, socioeconomic position, and other legally and ethically appropriate factors. Report denominators, missingness, absolute gaps, ratios, uncertainty intervals, and intersections where sample sizes allow. Do not claim equity from selection parity alone.

## Analysis plan

1. Primary intention-to-treat analysis at the assignment level.
2. Account for clustering, period, site, and prespecified factors.
3. Report effect estimates with confidence intervals, not only p-values.
4. Analyse missing data and loss to follow-up.
5. Sensitivity analyses for capacity, adherence, contamination, and learning effects.
6. Evaluate calibration/discrimination only when a clear predictive target, outcomes, and horizon exist.
7. Qualitatively analyse overrides, incidents, and unintended effects.

Sample size must follow the primary endpoint, meaningful target difference, observed variability, intracluster correlation, and attrition. No number is invented here.

## Progression criteria

Before scale-up, governance must approve thresholds for completeness, availability, under-referral, serious incidents, timeliness, group gaps, and human-review capacity. Safety deterioration or unexplained disparity should trigger pause and investigation. Operational success does not replace clinical safety.

## Evidence separation

- validate the WHO chart for the intended population and use context;
- externally validate the NHANES HbA1c model separately; it is not a CVD-risk model;
- evaluate SHAP explanation fidelity, not causality;
- evaluate RAG/LLM documentary accuracy, citations, abstention, and misleading-information risk;
- evaluate allocation using real process, safety, and equity outcomes.

## Pilot deliverables

Registered protocol, data dictionary, statistical analysis plan, design-appropriate CONSORT/STROBE report, incident table, equity analysis, version log, negative findings included, and a documented decision to proceed, modify, or stop.
