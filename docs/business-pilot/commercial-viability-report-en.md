# Commercial Viability Report, Business Model & Pilot Strategy
**PREVIA Health AI — Future Health Digital Innovation Challenge 2026**
*Strategic and Health Economics Reference Package*

---

## Executive Summary

PREVIA Health AI was engineered to address a critical operational failure in public health: **the organizational inability to systematically organize, prioritize, and document primary cardiovascular screening campaigns under severe capacity and budget constraints**.

Rather than introducing another diagnostic tool (which requires expensive laboratory infrastructure, venous blood testing, and cold-chain logistics) or an isolated risk calculator, PREVIA provides an **integrated decision-support platform combining population-level screening simulation, capacity-constrained allocation optimization, and explainable, sovereign AI assistance**.

This report establishes PREVIA's commercial viability through:
1. A structured economic problem analysis grounded in empirical data from the World Health Organization (WHO) and global health economics literature.
2. A comprehensive stakeholder matrix distinguishing end beneficiaries, field users, institutional decision-makers, and funding bodies.
3. A realistic hybrid business model combining a grant-funded or co-sponsored 6-month ethical pilot, followed by turnkey campaign packages and annual institutional SaaS licenses.
4. A bitwise-reproducible financial model based on observed server infrastructure costs (Netcup dedicated VPS and Vercel CDN), projecting 30% to 55% gross margins and operational break-even at just 4 campaigns or a single institutional license.
5. An operational 4-phase, 6-month pilot protocol featuring a 12-KPI evaluation matrix and explicit Go/No-Go safety gates.

---

## 1. Economic and Organizational Problem Analysis

### 1.1. Empirical Global Health Burden
According to the World Health Organization (WHO, 2021) and the *Global Burden of Disease Study* (Lancet, 2020):
- Cardiovascular diseases (CVDs) remain the **leading cause of death globally**, responsible for 17.9 million deaths annually, over **75% of which occur in low- and middle-income countries (LMICs)**.
- The global economic cost of CVD exceeds **$863 billion per year**, split roughly evenly between direct healthcare expenditures and lost economic productivity (World Heart Federation).
- In primary healthcare facilities in emerging regions and community screening centers, laboratory-based screening (complete lipid profiles, venous fasting glucose) is unavailable to over 70% of the population due to reagent costs, diagnostic delays, and lack of refrigeration.

### 1.2. Concrete Organizational Bottlenecks
Field screening campaigns consistently encounter six major structural bottlenecks:
1. **Severely Constrained Screening Capacity**: Field teams and primary health centers can typically evaluate only 15% to 35% of the target eligible population per cycle.
2. **Arbitrary or Inefficient Prioritization**: In the absence of an allocation decision-support engine, screening slots are assigned on a "first-come, first-served" or random walk-in basis. As proven in Chantier 15 across 360 reproducible experiments, unprioritized allocation misses up to 60% of high-risk profiles (≥10% or ≥20% 10-year risk) while consuming precious slots on low-risk individuals (<5%).
3. **Territorial and Categorical Inequities**: Uncoordinated outreach campaigns tend to over-sample central, easily accessible sectors, creating inter-sector selection rate disparities exceeding 15 percentage points.
4. **Data Fragmentation and Attrition**: Paper tally sheets and disparate spreadsheets result in high data loss rates, prevent longitudinal follow-up, and impede central reporting.
5. **Lack of Verifiable Impact Auditing for Donors**: Major health donors (The Global Fund, World Bank, regional development banks, health mutuals) require transparent allocation proof before and after allocating capital.
6. **Black-Box Skepticism and Trust Deficit**: Unexplained AI algorithms generate justifiable resistance among local clinicians when they lack source citations and understandable reasoning.

### 1.3. Factual Boundary: What PREVIA Solves vs. What Requires External Infrastructure

| Organizational Challenge | What PREVIA Solves in Current Software Release | What Requires External Human / Physical Infrastructure |
|---|---|---|
| **Capacity Constraints** | Simulates and strictly enforces capacity quotas (e.g., 15%, 25%, 50%) prior to field expenditure. | Physical outreach, patient transportation, and clinic staffing. |
| **Risk Prioritization** | Deterministic, instantaneous calculation of the WHO 2019 non-lab chart (age, sex, smoking, SBP, BMI). | Formal clinical diagnosis and medication prescription (strictly reserved for qualified clinicians). |
| **Territorial Equity** | Provides an automated sector-balanced allocation algorithm restricting selection disparity below 2 percentage points. | Logistical vehicle deployment in remote rural sectors. |
| **Decision Transparency** | Integrated SHAP explainability engine and hallucination-free, source-grounded RAG documentary assistant. | Ethical clinical deliberation and patient-clinician trust. |
| **Auditability & Governance** | Verifiable JSON/CSV export pipelines, SHA-256 cryptographic fingerprints, and stateless session boundaries. | Integration with national electronic health records (EHR). |

---

## 2. Stakeholders, Customers, and Market Segmentation

The analysis structures the healthcare delivery chain into four distinct tiers:

```
[Donor / Funding Body] ──(Funding)──> [Decision-Maker / Director] ──(Deployment)──> [Clinician / Field User] ──(Screening)──> [Patient / Beneficiary]
```

### 2.1. Comprehensive 5-Segment Matrix

| Segment | Final Beneficiary | Platform User | Decision-Maker | Funding Body | Adoption Process | Specific Value Proposition |
|---|---|---|---|---|---|---|
| **1. Health NGOs & Global Health Actors** *(e.g., Doctors of the World, ALIMA, Red Cross)* | Underserved, rural, or vulnerable populations. | Field supervisors, mobile outreach nurses, community coordinators. | Country Program Director, NGO Medical Director. | International grantmakers (USAID, ECHO, private foundations). | Short to medium cycle (3–6 months). Bilateral partnership agreement. | Maximized screening yield at fixed budget, audit-proof donor reporting. |
| **2. Ministries of Health & Public Agencies** *(e.g., National NCD Programs)* | Adult citizens aged 40–74 at unmanaged cardiovascular risk. | Epidemiologists, regional medical inspectors, district health officers. | Director General of Health, Director of Prevention. | State budget, World Bank, WHO, Global Fund. | Long procurement cycle (12–24 months). Public tender, national ethical review. | Evidence-based simulation of national screening policies and regional standardization. |
| **3. Healthcare Networks & Primary Clinics** | Primary care outpatients. | Intake nurses, triage assistants, general practitioners. | Medical Director, Chief Information Officer (CIO). | Clinic operating budget, private health insurance. | Medium cycle (6–9 months). Operational demonstration and local workflow integration. | Rapid risk standardization in under 90 seconds without burdening clinician consultation time. |
| **4. Health Mutuals & Occupational Health** | Insured employees, corporate workforce aged 40+. | Occupational physicians, corporate wellness coordinators. | Chief Risk Officer, Prevention Partnership Director. | Occupational prevention funds, corporate health plan. | Medium cycle (6–12 months). Health-economic return on investment (ROI). | Emergency hospitalization cost containment through early detection of unmanaged severe hypertension. |
| **5. Research Institutes & Academic Centers** | Epidemiological study cohorts. | Biostatisticians, clinical research associates, PhD candidates. | Principal Investigator (PI), Institutional Scientific Board. | Academic research grants (Horizon Europe, NIH, Wellcome Trust). | Rapid cycle (2–4 months). Academic institutional partnership. | Open-core auditable architecture, synthetic data reproducibility, bias auditing. |

### 2.2. Selection and Justification of Priority Pilot Segment

**Priority Pilot Target: An International Health NGO or Community Health Consortium executing targeted primary prevention campaigns.**

*Strategic Justification:*
1. **Direct Problem Fit**: NGOs operate under acute resource and staffing constraints with fixed campaign durations (e.g., 10 to 30 days) and predetermined patient slot limits.
2. **Agile Governance**: While public ministries require up to two years of bureaucratic procurement, NGO medical directorates can validate an innovative, ethically supervised pilot protocol within 2 to 4 months.
3. **Alignment with Non-Lab WHO Charts**: Humanitarian and community missions frequently operate in remote or peri-urban settings without blood chemistry laboratories. PREVIA's 5-parameter non-invasive input matches their exact field reality.
4. **Data Privacy and Risk Mitigation**: A pilot can run on completely pseudonymized tokens (no names, national IDs, or IP addresses stored), guaranteeing total data protection compliance while eliminating operational risk.

*Explicit Boundary*: No formal partnership has yet been finalized. This selection represents a targeted, realistic business development objective for post-challenge commercialization.

---

## 3. Differentiated Value Proposition and Fact-Based Benchmark

### 3.1. Core Value Proposition

> **"PREVIA Health AI is the first decision-support and allocation simulation platform for cardiovascular prevention campaigns, uniting the mathematical fidelity of the WHO 2019 non-laboratory chart, capacity-constrained slot optimization, and the auditable explainability of sovereign AI."**

### 3.2. Fact-Based Alternative Benchmark

| Feature / Dimension | Paper Records & Physical Registers | Excel / Spreadsheets | Isolated Online Calculators | Enterprise EHR (DHIS2, OpenMRS) | **PREVIA Health AI** |
|---|---|---|---|---|---|
| **Screening Duration per Profile** | 4–8 minutes | 2–4 minutes | 1–2 minutes | 5–10 minutes | **≤ 90 seconds** |
| **Constrained Allocation Simulation** | Impossible | Fragile, complex formulas | Non-existent (single patient only) | Not supported (built for patient charts) | **Real-time integrated (Modules 03 & 04)** |
| **Equity Audit (Geography & Sex)** | Impossible without manual audit | Manual, error-prone | Non-existent | Requires custom complex SQL queries | **Automated and visual (Module 05)** |
| **WHO Chart Calculation Fidelity** | Frequent lookup errors | Formula translation risk | High for single cells, but isolated | Depends on custom setup | **100% deterministic (700/700 cells verified)** |
| **Explainable Output Reasoning** | None | None | Raw risk score only | Clinical values only | **Integrated SHAP engine (Module 07)** |
| **Scientific Reference Assistant** | Bulky paper manuals | None | None | Static reference pages | **Source-grounded RAG (WHO/CDC/NIDDK)** |
| **Initial Deployment Overhead** | Low capital, very high human cost | Low capital | Free public web tool | High ($10k–$100k+ with dedicated servers) | **Low (Lightweight containerized SaaS)** |

---

## 4. Recommended Business Model

### 4.1. Comparative Model Evaluation
1. **Perpetual On-Premise License**: Discarded due to long sales cycles, high upfront friction for public health buyers, and unsustainable maintenance burden for an early-stage venture.
2. **Pure Seat-Based SaaS**: Discarded as a standalone model because preventive campaigns are frequently seasonal or periodic rather than year-round continuous.
3. **Recommended Hybrid Open-Core & Deployed Services Model**:
   - *Public Open-Core Foundation*: The deterministic WHO chart algorithms, allocation simulation engines, and scientific evaluation benchmarks remain open-source and auditable. This ensures sovereign compliance, institutional trust, and zero vendor lock-in for global health organizations.
   - *Managed Cloud & Turnkey Deployments*: Monetization occurs through dedicated high-availability cloud instances, local quota and territory customization, field clinician training, sovereign Knowlia RAG token access, and independent post-campaign impact audit reports.

### 4.2. Indicative Pricing Structure (Non-Contractual Planning Benchmarks)

- **Fully Supported 6-Month Pilot Package**: **€12,000**
  - Includes isolated sovereign cloud deployment, local geographic parameterization, training for 5–10 clinicians, technical SLA support throughout the campaign (up to 1,000 real or simulated profiles), and joint independent evaluation reporting.
- **Turnkey Screening Campaign Package**: **€2,500 / campaign**
  - Includes 60-day dedicated platform access, technical onboarding, and a base allocation capacity of 2,500 evaluated profiles (€0.30 per additional profile thereafter).
- **Annual Multi-Site Institutional License**: **€15,000 / year**
  - Designed for hospital networks, permanent health NGOs, or insurance groups: unlimited sandbox instances, up to 5 concurrent active campaigns per year, unlimited documentary RAG queries, and 24-hour priority technical SLA.

---

## 5. Financial Viability and Reproducible Cost Model

### 5.1. Observed Technical Cost Baseline
- **Frontend Next.js Hosting**: Production on Vercel Pro (~$20/month = ~€240/year).
- **Backend FastAPI & Sovereign AI Sidecar**: Deployed on dedicated Netcup VPS (Ubuntu, FastAPI, Knowlia and Qdrant containers at IP 194.59.205.73) = ~€25/month = ~€300/year.
- **Domain, DNS & TLS Security**: ~€24/year.
- **Off-site Encrypted Backups & Sentry Monitoring**: ~€180/year.
- **Total Fixed Technical Baseline**: **~€744/year (~€62/month)**.
- **AI Token Inference Costs (Knowlia RAG)**:
  - 70% of screening requests use zero LLM tokens (pure deterministic WHO chart lookup or extractive documentary search = €0.000).
  - 30% of requests leverage Knowlia's sovereign multi-model synthesis (average cost €0.0015 per query). For a 5,000-profile campaign, total token expenditure is under €2.50.

### 5.2. Three-Year Financial Scenarios (Generated by `evaluate_business_pilot.py`)

```
Revenue Projections (k€):
Ambitious Scenario  : [Y1: €34k] ──────> [Y2: €102k] ──────> [Y3: €258k]
Base Case Scenario  : [Y1: €17k] ──────> [Y2:  €48k] ──────> [Y3: €128k]
Conservative Scenario: [Y1: €12k] ──────> [Y2:  €28k] ──────> [Y3:  €33k]
```

| Scenario | Year | Pilots | Campaigns | Annual Licenses | Profiles Screened | Total Revenue (€) | Operating Costs (€) | Gross Margin (€) | Gross Margin (%) | Cost / Profile (€) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Conservative** | Y1 | 1 | 0 | 0 | 1,000 | 12,000 | 9,244 | 2,756 | 23.0% | €9.24 |
| **Conservative** | Y2 | 1 | 3 | 0 | 8,500 | 27,500 | 18,195 | 9,305 | 33.8% | €2.14 |
| **Conservative** | Y3 | 0 | 6 | 1 | 20,000 | 33,000 | 20,540 | 12,460 | 37.8% | €1.03 |
| **Base Case** | Y1 | 1 | 2 | 0 | 6,000 | 17,000 | 11,447 | 5,553 | 32.7% | €1.91 |
| **Base Case** | Y2 | 0 | 6 | 2 | 25,000 | 48,000 | 27,511 | 20,489 | 42.7% | €1.10 |
| **Base Case** | Y3 | 0 | 15 | 5 | 70,000 | 127,500 | 57,802 | 69,698 | 54.7% | €0.83 |
| **Ambitious** | Y1 | 2 | 4 | 0 | 12,000 | 34,000 | 19,649 | 14,351 | 42.2% | €1.64 |
| **Ambitious** | Y2 | 0 | 12 | 4 | 55,000 | 102,400 | 46,025 | 56,375 | 55.1% | €0.84 |
| **Ambitious** | Y3 | 0 | 25 | 10 | 150,000 | 257,500 | 105,068 | 152,432 | 59.2% | €0.70 |

### 5.3. Operational Break-Even Threshold
- **Fixed Annual Operating Overhead** (sovereign cloud, backups, continuous security watch, base DevOps): **€3,924 / year**.
- **Contribution Margin per Turnkey Campaign**: €2,500 revenue - €1,500 direct variable costs = **€1,000 net contribution**.
- **Contribution Margin per Annual License**: €15,000 revenue - €4,100 direct variable costs = **€10,900 net contribution**.
- **Break-Even Volume**:
  - Exactly **3.9 screening campaigns per year**, or
  - Exactly **0.36 annual institutional licenses**.
  - PREVIA reaches operational break-even on its first major institutional contract or a modest cadence of quarterly campaigns, demonstrating lean financial resilience.

---

## 6. Market Scope and Realistic Deployment Scenarios

### 6.1. Total Market vs. Serviceable Addressable Market
- **Global Burden**: Over 1.3 billion adults live with hypertension globally (WHO, 2023); 82% reside in emerging nations, and fewer than 1 in 5 achieve clinical blood pressure control.
- **Serviceable Addressable Market (SAM)**: Official development assistance (ODA) and multilateral grants allocated to NCD prevention programs exceed $450 million annually, with digital health and decision support accounting for 12% to 15% (USAID Digital Health Vision).
- **Serviceable Obtainable Market (SOM)**: Regional health NGOs and community health coalitions operating in West and Central Africa (representing an estimated 60 to 80 major annual screening campaigns).

### 6.2. Two Explicit Geographic Deployment Contexts
To avoid arbitrary geographic assumptions, PREVIA has modeled two distinct environments:
1. **Context A: West Africa (Low-Resource Primary Care)**
   - *Characteristics*: Lack of routine lipid laboratories, rapid 4G smartphone adoption in peri-urban corridors, intermittent connectivity in rural sectors.
   - *PREVIA Fit*: Exclusively non-lab WHO regional charts, low-bandwidth responsive UI, sovereign data hosting complying with national health data privacy laws.
2. **Context B: Occupational Health & Corporate Mutuals (Europe & North Africa)**
   - *Characteristics*: Mandatory periodic health evaluations for corporate workforces over age 40.
   - *PREVIA Fit*: Streamlined intake for occupational health nurses, priority triage toward cardiologists, strict GDPR compliance with zero storage of nominative records.

---

## 7. Operational Pilot Plan Summary

The structured pilot spans **6 months across 4 disciplined phases**:

```
[Month 1: Phase 0] ──────> [Month 2: Phase 1] ──────> [Months 3–4: Phase 2] ──────> [Months 5–6: Phase 3]
  Ethical Clearance,         Clinician Training         Supervised Field Campaign      Independent Data Audit,
  MOU & Synthetic            & Dry Run                  (500 to 1,000 Profiles)        12-KPI Calculation
  Cohort Simulation          (50 Test Profiles)         100% Medical Oversight         & Joint Final Report
```

### Emergency Stop Gates (Go / No-Go Rules)
Immediate pilot suspension occurs if any of the following triggers are met:
1. **Calculation Discrepancy**: Any variation from the verified 700 WHO chart cells during dry-run validation.
2. **Severe Platform Downtime**: Unplanned server downtime exceeding 4 consecutive hours during an active field screening day.
3. **Unsupervised Diagnostic Drift**: Any attempt to use the platform for automated drug prescription without licensed physician sign-off.

---

## 8. Pilot Key Performance Indicators (12-KPI Framework)

| KPI ID | Category | Indicator Name | Pilot Target | Collection Method | Evidence Level |
|---|---|---|---|---|---|
| **KPI-01** | Feasibility | Record Completeness Rate | **≥ 98.0%** | Server-side validation of mandatory inputs | Level 2 (Field Feasibility) |
| **KPI-02** | Feasibility | Mean Screening Duration per Profile | **≤ 90 seconds** | Server timestamps from intake start to result | Level 2 (Operational Efficiency) |
| **KPI-03** | Clinical Accuracy | Deterministic WHO Table Concordance | **100.0%** | Automated 700/700 cell audit & clinical sign-off | Level 1 (Algorithmic Truth) |
| **KPI-04** | Allocation | Capacity Constraint Compliance | **100.0%** | Automated check of allocated slot thresholds | Level 1 (Rule Adherence) |
| **KPI-05** | Equity | Inter-Sector Selection Disparity Gap | **≤ 5.0 pp** | Max-min difference in sector selection rates | Level 2 (Documented Fairness) |
| **KPI-06** | Adoption | System Usability Scale (SUS) Score | **≥ 80 / 100** | Standardized 10-item post-pilot SUS survey | Level 2 (Clinician Usability) |
| **KPI-07** | Technical | Platform Availability (Uptime) | **≥ 99.5%** | Continuous monitoring via Sentry / Uptime | Level 1 (Infrastructure Reliability) |
| **KPI-08** | Security | Data Privacy & Leak Incidents | **0 incidents** | Zero nominative persistence audit log | Level 1 (Regulatory Compliance) |
| **KPI-09** | Economic | Direct Marginal Cost per Profile | **≤ €0.50** | Direct infrastructure & tokens / profiles | Level 2 (Health Economic Viability) |
| **KPI-10** | Clinical Utility | Clinician Concordance & Adherence | **≥ 90.0%** | Physician sign-off rate on suggestions | Level 2 (Decision Support Value) |
| **KPI-11** | Documentation | RAG Citation Precision & Grounding | **100.0%** | Verification of source anchors (WHO/CDC) | Level 1 (Hallucination-Free) |
| **KPI-12** | Care Pathway | Prevention Pathway Follow-up Rate | **≥ 60.0%** | 30-day confirmation rate for ≥10% risk profiles | Level 3 (Real Care Pathway Impact) |

---

## 9. Conclusion

PREVIA Health AI demonstrates that digital health innovation can combine **uncompromising scientific rigor, technological frugality, and robust economic viability**.

By focusing on the concrete operational bottleneck of screening capacity allocation rather than opaque diagnostic automation, PREVIA offers an immediately actionable, commercially viable platform for global health organizations.

Support from the Future Health Digital Innovation Challenge 2026 will directly fund the preparatory phase of the first institutional pilot, formalize the ethical partnership agreement, and bridge the gap from a verified research prototype to an impactful real-world screening solution.
