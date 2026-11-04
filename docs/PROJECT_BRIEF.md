# PREVIA Health AI — Project Brief v0.1

**Challenge:** Future Health Digital Innovation Challenge 2026  
**Track:** [Population Health] Precision Prevention and Screening  
**Participant:** Individual applicant  
**Prototype deadline:** 20 November 2026 (subject to organizer updates)  
**Working title:** PREVIA Health AI (name and trademark availability not checked)

## Problem
Cardiovascular risk factors can remain undetected, and a screening encounter does not always lead to an actionable, documented next step. Screening programs need understandable risk assessment, targeted prioritization, and a way to measure follow-through without exposing identifiable health data.

## Proposed solution
An explainable, privacy-conscious cardiovascular screening support platform for adults eligible for a validated risk-assessment pathway. It helps determine what screening measurements are required, computes a guideline-grounded risk category where the relevant chart is available and its applicability conditions are met, proposes appropriate next-step categories for qualified human review, and tracks aggregate, simulated screening-funnel indicators in a demo.

## Scope of the 2026 hackathon prototype
1. **Intake:** age, sex as required by selected chart, current smoking, systolic blood pressure, body mass index or inputs needed to calculate it, known CVD history; explicit consent and clear scope explanation.
2. **Applicability:** distinguish chart-eligible profiles from out-of-scope cases, missing measurements and indications for professional assessment.
3. **Guideline-based risk:** validated reproduction of an authoritative WHO regional, non-laboratory-based cardiovascular risk chart; do not invent a numerical risk score or infer a diagnosis.
4. **Explainability:** show inputs, source and version of the chart, estimated category, limitations, and clinically reviewed next-step information.
5. **Demonstration:** a synthetic patient journey and a de-identified aggregate population dashboard (screened, eligible, missing measurements, screening completion, documented next step).
6. **Evaluation:** unit and integration tests, known-reference checks against original WHO chart, robustness across missing and out-of-range inputs, subgroup performance analysis where justified by data, usability scenarios.

## Not in scope for initial prototype
- Autonomous clinical diagnosis or prescription.
- Medical-grade deployment without clinical validation and regulatory review.
- Disease-risk model trained on synthetic labels presented as a clinically validated predictor.
- Patient-record ingestion or transfer of actual health information without proper authorizations and safeguards.
- Claiming the US NHANES population is representative of all global regions.

## Technical architecture
```
Next.js UI
  |-- screening journey
  |-- explanatory results
  |-- demo population dashboard
  v
FastAPI
  |-- input validation and consent boundary
  |-- applicability decision
  |-- WHO chart-based risk adapter (with reference tests)
  |-- workflow / next-step suggestions (human review)
  |-- nonidentifying demo analytics
  v
Data sources
  |-- WHO HEARTS / 2019 cardiovascular risk chart, per-region
  |-- CDC NHANES public-use data (exploratory population analysis only)
  |-- explicitly labeled synthetic scenarios (demo)
```

## Data policy
Use NHANES public-use data to prototype descriptive population analytics and measure missingness; cite sample, survey weighting, and geographic representativeness limitations. Use synthetic case records for public demonstrations, clearly labeled. Avoid retaining raw or identifiable patient screening data for the competition demo.

## Acceptance criteria for first functioning vertical slice
- [ ] Start backend and frontend locally using documented commands.
- [ ] Submit demo inputs with visible input validation.
- [ ] Return an explicit `out_of_scope`, `needs_measurements` or `eligible_for_risk_estimation` status without asserting an unimplemented risk score.
- [ ] Run source-based WHO risk tests before enabling a percentage or category in UI.
- [ ] Demonstrate three end-to-end synthetic cases, including at least one incomplete / excluded case.
- [ ] Show an informative dashboard based on clearly labeled synthetic events.
- [ ] Supply README, architecture, data sources, model card (if ML is used), safety limitations, and demo script.

## Judging alignment
- **Health impact:** prevention of cardiovascular disease, from risk recognition to follow-through.
- **Technical depth:** reproducible API, source-grounded risk engine, tests, cohort analytics.
- **Functional demo:** an end-to-end journey and dashboards.
- **Responsible AI:** clinical boundaries, data minimization, explicit model/score limitations, fairness evaluation.
- **Scale:** modular chart region selection, stateless service, deployable containers.
- **Commercial feasibility:** pilot with primary-care clinics, occupational-health programs, or screening campaigns, pending validation.

## Delivery plan
**30 October – 2 November:** requirements, source selection, UX flows, architecture, risk-model applicability.  
**3–9 November:** data inventory/quality, source-based risk implementation, API, tests.  
**10–15 November:** Next.js experience, demonstration cases, population dashboard.  
**16–19 November:** verification, documentation, screen recording, submission package.  
**20 November:** official prototype submission deadline.

## Presentation (English, draft)
> PREVIA Health AI turns a cardiovascular risk signal into a transparent screening next step. Instead of presenting a black-box diagnosis, it combines an evidence-based assessment pathway, an accessible interface, and aggregate follow-through analytics. The result is a practical prototype for earlier, more equitable preventive care.

## Evidence and official references
- Hackathon: https://hack2skill.com/event/futurehealthchallenge/
- WHO HEARTS Risk-based CVD Management: https://www.who.int/publications/i/item/9789240001367
- WHO CVD fact sheet: https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-%28cvds%29
- CDC NHANES: https://www.cdc.gov/nchs/nhanes/about/index.html
- NHANES 2017–2018: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2017
