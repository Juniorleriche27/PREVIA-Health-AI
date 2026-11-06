# Stakeholders Analysis and Value Proposition
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**

---

## 1. Comprehensive Mapping of the 5 Institutional Segments

Public health technology implementations almost universally fail when system architects confuse the field operator (who inputs data), the decision-maker (who authorizes deployment), and the funding body (who releases capital).

PREVIA Health AI systematically defines and separates these roles across all five target segments.

---

### Segment 1: Health NGOs and Humanitarian Actors
*Representative examples: Doctors of the World, ALIMA, Red Cross / Red Crescent, Community Health Coalitions.*

- **Final Beneficiary**: Vulnerable, rural, and peri-urban populations with limited or no access to formal clinical centers or laboratory testing.
- **Direct Users**: Outreach mission coordinators, community health supervisors, and field triage nurses.
- **Institutional Decision-Maker**: Country Program Director and NGO Head of Mission, in coordination with the headquarters Health Advisor.
- **Funding Body**: Humanitarian and development donors (USAID/BHA, European Commission DG ECHO, bilateral cooperation agencies, private philanthropic foundations).
- **Adoption Process**: Short to medium timeline (3 to 6 months). Technical demonstration, internal medical board review, bilateral pilot project agreement for a defined operational district.
- **Specific Value Proposition**:
  - *Maximized Public Health Yield under Fixed Budgets*: Enables exact calibration of screened cohorts against available mobile medical teams.
  - *Audit-Proof Donor Reporting*: Generates verifiable statistical audits demonstrating the allocative efficiency of donor grant funding.
  - *Field Operational Resilience*: Operates on 5 non-invasive clinical inputs without venous blood sampling, reagents, or cold-chain storage.
- **Identified Barriers & PREVIA Mitigations**:
  - *Barrier*: Unreliable or absent cellular connectivity in remote field outposts.
  - *Mitigation*: Ultra-lightweight frontend architecture, pre-cacheable progressive web app (PWA), and offline-capable edge Docker deployment.

---

### Segment 2: Ministries of Health and National NCD Directorates
*Representative examples: National Non-Communicable Disease (NCD) Programs, Regional Health Directorates.*

- **Final Beneficiary**: The adult population aged 40 to 74 across a health district, administrative region, or national territory.
- **Direct Users**: Regional medical inspectors, district health officers (DHOs), and ministerial epidemiological statisticians.
- **Institutional Decision-Maker**: Director General of Public Health, Director of Preventive Medicine, Permanent Secretary.
- **Funding Body**: State general health budget supported by multilateral technical and financial partners (WHO, World Bank, Global Fund, regional development banks).
- **Adoption Process**: Long and highly regulated procurement cycle (12 to 24 months). National NCD strategic plan integration, national ethical committee clearance, formal public tender.
- **Specific Value Proposition**:
  - *Macro-Simulation Policy Planning*: Simulates future referral volumes and antihypertensive drug requirements before committing national program budgets.
  - *Protocol Standardization*: Enforces uniform 2019 WHO non-lab guidelines, eliminating arbitrary triage differences between urban centers and rural clinics.
  - *Health Data Sovereignty*: Full deployment capability on dedicated sovereign state cloud infrastructure.
- **Identified Barriers & PREVIA Mitigations**:
  - *Barrier*: Bureaucratic inertia and concern over foreign black-box algorithmic dependencies.
  - *Mitigation*: Open-core inspectable codebase, zero international data leakage, 100% adherence to published WHO HEARTS technical packages.

---

### Segment 3: Primary Healthcare Networks, District Hospitals, and Health Centers
*Representative examples: Private-not-for-profit health networks, faith-based hospitals, regional primary care clinics.*

- **Final Beneficiary**: Primary care outpatients seeking care for varied acute or routine reasons.
- **Direct Users**: Triage nurses, medical intake assistants, and general practitioners.
- **Institutional Decision-Maker**: Medical Director and Hospital Managing Director.
- **Funding Body**: Clinic operating budget, reimbursed through preventive care consultation tariffs or private insurance agreements.
- **Adoption Process**: Medium cycle (6 to 9 months). Workflow demonstration, nurse time-motion validation, medical executive committee approval.
- **Specific Value Proposition**:
  - *Rapid Intake Triage*: Standardized risk assessment completed in under 90 seconds during routine vital-sign checks (blood pressure, weight, height).
  - *Clinical Risk Management*: Instant automated flagging of severe hypertension (SBP ≥ 180 mmHg) requiring emergency clinical intervention.
  - *Enhanced Preventive Reputation*: Elevates clinic standing without capital equipment expenditure.
- **Identified Barriers & PREVIA Mitigations**:
  - *Barrier*: Clinical workload saturation and resistance to cumbersome software interfaces.
  - *Mitigation*: Single-screen responsive interface, zero password friction during local sessions, single-click question suggestions.

---

### Segment 4: Health Mutuals, Insurers, and Corporate Occupational Health
*Representative examples: Corporate health maintenance organizations, corporate medical centers, occupational wellness programs.*

- **Final Beneficiary**: Mutual members, insured policyholders, and corporate workforce aged 40 and older.
- **Direct Users**: Occupational physicians, employee health nurses, and corporate wellness officers.
- **Institutional Decision-Maker**: Chief Risk Officer (CRO), Chief Medical Officer (CMO), Corporate CSR / Health Director.
- **Funding Body**: Occupational hazard prevention reserves or mutual member benefit funds.
- **Adoption Process**: Medium timeline (6 to 12 months). Health-economic return on investment (ROI) actuarial analysis and strict GDPR / privacy compliance.
- **Specific Value Proposition**:
  - *Catastrophic Cost Containment*: Avoidance of acute stroke and myocardial infarction hospitalizations that heavily burden loss ratios.
  - *Employee Engagement*: Modern, transparent tool providing clear, personalized cardiovascular explanations during routine annual check-ups.
  - *Uncompromising Privacy*: Zero persistence of nominative employee records, guaranteeing that corporate employers never receive individual health status data.
- **Identified Barriers & PREVIA Mitigations**:
  - *Barrier*: Strict demand for short-term economic proof.
  - *Mitigation*: Focus on early detection of severe unmanaged hypertension, yielding immediate reductions in critical sick leave and emergency interventions.

---

### Segment 5: Epidemiological Research Institutes and Academic Universities
*Representative examples: Global health research departments, schools of public health, clinical epidemiology units.*

- **Final Beneficiary**: The international scientific community and epidemiological study cohorts.
- **Direct Users**: Academic epidemiologists, biostatisticians, and clinical research fellows.
- **Institutional Decision-Maker**: Laboratory Director, Department Chair, Principal Investigator (PI).
- **Funding Body**: Competitive research grants (Horizon Europe, NIH, Wellcome Trust, national science foundations).
- **Adoption Process**: Rapid timeline (2 to 4 months). Research collaboration agreement or academic data transfer protocol.
- **Specific Value Proposition**:
  - *Complete Algorithmic Transparency*: Open formulas, verified synthetic reference cohorts, and reproducible simulation code.
  - *Methodological Benchmarking*: Ready-to-use software suite to benchmark novel allocation rules and predictive models against WHO standards.
- **Identified Barriers & PREVIA Mitigations**:
  - *Barrier*: Skepticism toward closed proprietary black boxes.
  - *Mitigation*: Open-core licensing, public non-regression tests, and bitwise-reproducible CSV outputs.

---

## 2. Priority Pilot Target Selection & Justification

### Strategic Target: Health NGOs and Community Health Coalitions

To execute its first real-world supervised pilot, PREVIA focuses its post-challenge partnership outreach on **international health NGOs conducting primary healthcare and mobile screening campaigns**.

```
Decision Matrix for Initial Pilot:
1. Decision and Ethical Review Speed:     NGO (★★★★★) vs Ministry (★★☆☆☆)
2. Concordance with Laboratory Absence:   NGO (★★★★★) vs Private Clinic (★★★☆☆)
3. Acute Capacity Constraint Reality:     NGO (★★★★★) vs Hospital (★★★☆☆)
4. Agility in Supervised Innovation:     NGO (★★★★☆) vs Insurance Mutual (★★★☆☆)
```

Targeting this segment enables rapid operational validation of PREVIA without getting delayed by multi-year public procurement processes, while delivering immediate utility where unmet cardiovascular screening needs are most urgent.

---

## 3. Value Proposition Matrix Across PREVIA Functional Modules

| Module in Codebase | Actual Implemented Feature | Concrete Field Workflow | Health-Economic Added Value |
|---|---|---|---|
| **Modules 01 & 02: Screening & Pathway** | Instant 5-parameter non-lab WHO 2019 chart lookup. | Nurse enters blood pressure, age, smoking status, and BMI; receives instant risk category (green to dark red). | Eliminates manual lookup errors; prevents unnecessary, expensive lipid testing. |
| **Module 03: Population Intelligence** | Synthetic local cohort generation with reproducible random seeds. | Campaign coordinator simulates expected risk distributions prior to field team dispatch. | Enables precise advance logistics sizing for blood pressure cuffs, intake forms, and staff hours. |
| **Module 04: Strategy Comparison** | Constrained allocation simulation (WHO Risk-Descending vs. Sector-Balanced vs. Random). | Campaign manager selects the screening slot allocation rule based on equity or capture targets. | Maximizes high-risk patient capture without neglecting isolated peripheral sectors. |
| **Module 05: Scientific Audit** | Quantified selection disparities across geographic sectors and reference sex. | Data analyst verifies that chosen allocation strategy introduces no geographic or gender discrimination. | Documents allocative equity for institutional donors and review boards. |
| **Module 06: Evidence Verification** | Digital verification of all 700 WHO chart cells against official source PDFs. | Medical officer verifies that digital tables exactly correspond to official WHO publications. | Guarantees complete medico-legal safety with zero algorithmic hallucination. |
| **Module 07: ML, XAI & RAG Assistant** | SHAP feature contribution explanations and source-grounded Knowlia RAG assistant. | Clinician explains to patient why elevated blood pressure drives their risk score; queries WHO/CDC guidelines. | Strengthens patient adherence and provides continuous on-the-job guideline education for junior staff. |

---

## 4. Objective Comparison with Alternative Solutions

### Alternative A: Paper Registers & Tally Sheets
- *Current Reality*: Dominates over 80% of rural primary health posts in developing regions.
- *Major Weaknesses*: 20% to 35% estimated record attrition, impossibility of cross-referencing complex colored paper charts, zero campaign-level visibility.
- *PREVIA Edge*: 90-second structured entry, local digital persistence, zero lost records, immediate clinical alerts.

### Alternative B: Office Spreadsheets (Excel / Google Sheets)
- *Current Reality*: Improvised by coordinators for end-of-day data consolidation.
- *Major Weaknesses*: Vulnerable to formula errors, file corruption risks, zero capacity-constrained optimization algorithms, virtually zero patient data privacy safeguards.
- *PREVIA Edge*: Mathematically verified optimization logic, secure containerized environment, SHA-256 cryptographic audit logs.

### Alternative C: Isolated Online Calculators (Framingham, SCORE2)
- *Current Reality*: Consulted sporadically by individual physicians on smartphones.
- *Major Weaknesses*: Purely individual patient tools. Incapable of managing cohort campaigns, optimizing collective slot limits, auditing geographic disparities, or providing grounded documentary assistance.
- *PREVIA Edge*: Complete public health decision platform connecting individual screening, population dynamics, and resource allocation.
