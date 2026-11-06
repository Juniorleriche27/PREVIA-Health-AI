# PREVIA — commercial viability and path to pilot

## Executive summary

PREVIA is a deployed bilingual research prototype combining a WHO non-laboratory cardiovascular chart, synthetic allocation simulations, a separate exploratory NHANES/SHAP module, and a documentary RAG assistant. Its potential commercial value is traceability, capacity experimentation, and support for a future supervised pilot. **No clinical benefit or actual revenue has been demonstrated.**

The corrected financial model uses three indicative prices: €12,000 per pilot, €2,500 per campaign, and €15,000 per annual licence. All nine revenue figures now reconcile with declared quantities and include no profile-overage revenue. Revenue ranges from €12,000 to €212,500, with modeled margins from 27.96% to 57.78%. The margins depend on cost assumptions unsupported by invoices or quotes in the repository.

## Problem and value proposition

Organizations with limited screening capacity may need explicit, reproducible, auditable rules to simulate slot allocation. PREVIA currently compares three rules on fictional profiles and shows which artificial records are selected or not selected.

Chantier 15 did not observe patients, real care pathways, cardiovascular-event reduction, or resource savings. It measured implemented-rule behaviour across 30 synthetic cohorts and four capacities. `seeded_random` is a reproducible pseudorandom comparator—not observed opportunistic care or first-come-first-served screening.

## Potential customers and funders

Segments requiring validation through interviews and pilots, with no assumed contract:

- community-health NGOs and programmes;
- districts and primary-care networks;
- hospitals or clinics evaluating supervised workflows;
- research institutes operating under approved protocols;
- funders supporting evaluation of digital-health tools.

The repository provides no signed partnership, sales pipeline, local market size, or verified procurement cycle.

## Indicative offer

| Offer | Planning price | Scope requiring contract |
|---|---:|---|
| Supervised pilot | €12,000 | preparation, deployment, training, support, and reporting subject to approvals |
| Campaign | €2,500 | time-limited access, onboarding, and support; exact volume to be contracted |
| Annual licence | €15,000 | usage rights and services defined by contract; SLA, limits, and data terms negotiated |

These prices have not been validated by market evidence. The former €0.30/profile overage is not modeled in corrected scenarios.

## Corrected financial results

| Scenario | Y1 | Y2 | Y3 |
|---|---:|---:|---:|
| Conservative | €12,000 | €19,500 | €30,000 |
| Base case | €17,000 | €45,000 | €112,500 |
| Ambitious | €34,000 | €90,000 | €212,500 |

See the [detailed financial analysis](financial-analysis.md) and [reproducible CSV](results/financial_scenarios.csv). Costs are planning estimates, not observed expenditure. Break-even at four campaigns or one licence is conditional on assumed prices and costs.

## Architecture and costs

The use of Vercel, Netcup, Knowlia, and the API domain is verifiable. The €20/month, €25/month, €0.0015/query, and maintenance/support/audit budgets are not supported by repository evidence. The model labels them as assumptions. Total modeled cost per profile is kept separate from direct technical cost per profile.

## Pilot path

Before involving real people: ethics and regulatory approval, controller agreement, data-protection impact assessment, local clinical protocol, consent/legal basis, minimisation and retention rules, security controls, human supervision, incident handling, and a preregistered analysis plan.

KPIs are proposed targets. No 99.5% availability, 98% completeness, 90-second duration, equity result, 100% RAG citation validity, or 60% follow-up has been claimed as achieved.

## Code status and commercial model

The GitHub repository is publicly viewable but contains no `LICENSE` file. Public access alone does not grant general rights to copy, modify, or redistribute. PREVIA must therefore not currently be described as open source or permissively licensed Open-Core.

A future Open-Core strategy requires an explicit component boundary, selected licence, dependency review, and commercial-service definition. Until then, the proposed offer concerns services and contractually defined usage rights, without an open-source licensing promise.

## Defensible jury position

PREVIA has a functioning prototype, reproducible synthetic experiments, and a corrected transparent planning model. The next step is not to claim massive impact; it is to secure approvals, validate costs with evidence, and prospectively measure safety, appropriate referral, timeliness, follow-up, usability, and group differences in a supervised pilot.
