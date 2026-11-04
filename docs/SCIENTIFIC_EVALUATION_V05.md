# PREVIA Health AI — Module 05: research software audit

**Version:** v0.5.0  
**Challenge:** Future Health Digital Innovation Challenge 2026, Population Health — Precision Prevention and Screening  
**Status:** Reproducible software quality assurance (QA) of a synthetic demonstration. **Not clinical validation.**

## Question

What can the current demonstration establish, how can reviewers inspect its arithmetic, and which claims remain unsupported?

The answer is deliberately narrower than medical effectiveness. The app consumes artificial records, applies the WHO 2019 *non-laboratory* reference chart for Western Sub-Saharan Africa, and compares three deterministic ways to select a fixed number of fabricated screening slots. The app records neither clinical outcomes nor personal data. No predictive ML model has been trained or evaluated.

## Source and transcription QA

Original: [WHO 2019 Western Sub-Saharan Africa risk-chart PDF](https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf), non-laboratory chart on the second page.

- The implemented table has 7 age groups × 4 sex/smoking quadrants × 5 systolic-BP rows × 5 BMI columns = **700 chart cells**.
- The 700 cells pass internal shape/range checks and directional monotonicity checks for BP and BMI.
- **28 independently transcribed reference anchor cells** (one per age × quadrant) match the published WHO chart.
- **672 cells are not yet independently cross-checked against the WHO PDF.** Passing structural checks does not certify transcription accuracy. Full double-entry or automated cross-check plus expert review is still needed before any real-world use.
- Population validity and individual calibration of the WHO table, even if transcribed perfectly, are separate scientific questions. A single region chart does not quantify true risk in any sampled country without appropriate population validation.

## Scenario and metrics

The baseline audit uses `country=Togo`, `cohort_size=240`, `outreach_capacity=45`, `seed=2026`, `sensitivity_runs=12`. Since all data are artificial, choosing a different country within the same WHO chart region changes only a label and **does not** create a country-specific simulation.

**Reference threshold:** chart cell ≥10%. For this prototype, it is a **descriptive comparison threshold**, not a referral instruction or clinical guideline cutoff.

Definitions (percentage points = pp):

- **Chart-category capture** = `selected synthetic profiles with WHO cell ≥10% ÷ all synthetic profiles with WHO cell ≥10% ×100`.
- **Chart-category yield** = `selected synthetic profiles with WHO cell ≥10% ÷ all selected synthetic profiles ×100`.
- **Subgroup selection rate** = `selected in subgroup ÷ subgroup population ×100`.
- **Subgroup selection-rate gap** = `maximum subgroup selection rate − minimum subgroup selection rate`, in pp.
- **Subgroup high-category capture** = `selected subgroup synthetic profiles with WHO cell ≥10% ÷ all subgroup synthetic profiles with WHO cell ≥10% ×100`; null/N/A when denominator is zero.
- **Seed sensitivity** = minimum, median, maximum over 12 artificial cohorts produced from seeds 2026–2037; these are **not** confidence intervals or population estimates.
- **Capacity sensitivity** = repeat the three selection rules on the same cohort at 22, 45, and 90 slots.

### Baseline results (simulation only)

| Allocation strategy | Selected from ≥10% chart category | Category capture | Sector selection gap | Reference-sex selection gap |
|---|---:|---:|---:|---:|
| Descending WHO chart-cell value | 45 | 37.19% | 8.33 pp | 7.35 pp |
| Equalized selection rates across four fictitious sectors | 45 | 37.19% | 1.67 pp | 10.70 pp |
| Seeded pseudorandom baseline | 22 | 18.18% | 8.33 pp | 7.35 pp |

The simulated cohort contains 121 profiles meeting the chart category. The chart-ranking rule must perform well on the same quantity by construction. **This metric is not an independent measure of diagnosis accuracy, deaths averted, or clinical effectiveness.** The balanced rule has a smaller sector selection gap **on this artificial cohort**, but may have larger gaps on another dimension; a sector parity result does not establish clinical equity.

### Seed sensitivity (12 artificial cohorts)

| Strategy | Chart-category capture: min, median, max | Sector selection gap: min, median, max |
|---|---|---|
| Chart cell descending | 37.19 / 46.64 / 51.72% | 6.66 / 10.00 / 16.66 pp |
| Sector balanced | 37.19 / 46.64 / 51.72% | 1.67 / 1.67 / 1.67 pp |
| Seeded random | 13.86 / 17.42 / 24.44% | 5.00 / 8.33 / 20.00 pp |

These numbers are reproducible by the included code, but they illustrate sensitivity to *artificial seed choices* only.

## Integrity audit and reproducibility

1. Verify that the table contains 700 values and 28 selected WHO anchors match.
2. Generate 240 synthetic records; verify all IDs are unique.
3. Send the exact same cohort to each of the three selection algorithms; do not mutate it.
4. Verify exact capacity, unique selected IDs and subset membership.
5. Reconcile selected counts, category counts and high-category counts across sectors and chart-reference sex.
6. Verify reruns with the same seed are bit-for-bit reproducible.
7. Use `cohort_sha256` and per-strategy `selected_ids_sha256` as inspectable fingerprints.
8. Show three capacity points and min/median/max across seed runs, never interpreting the ranges as population uncertainty.
9. Export the full API result locally in JSON, including assumptions and scientific limitations.

Run from `backend`:

```powershell
& "..\.venv\Scripts\python.exe" -m pytest -q
```

All 66 backend tests in the v0.5 test suite pass in the authoring environment. The full Next.js build must also be verified locally (`npm run build` from `frontend`).

## What is NOT established

- **No model performance**: sensitivity, specificity, discrimination (e.g., AUC), calibration, PPV/NPV, event rates and generalization cannot be measured without observed outcomes and a defined population.
- **No clinical utility**: no referrals completed, screening uptake, patients helped, cardiovascular events avoided, implementation costs, or trial impact have been measured.
- **No fairness certificate**: synthetic selection-rate differences are not equal opportunity in healthcare, and chart-based sex categories are a reference-chart input rather than a comprehensive demographic or gender assessment.
- **No deployment readiness**: the app has no real-patient governance framework, clinician-approved decision support workflow, external clinical validation, or evidence of real-world safety.
- **No geographic prevalence claims**: the current generator uses arbitrary factor distributions, irrespective of selected country within the WHO region.

## Evidence needed for a future clinical-science study

A consented, properly governed, representative and appropriately documented cohort, with clinical adjudication and measured follow-up, will be needed. Preregister target population, exclusion criteria, decision thresholds, outcomes, subgroup assessment, and error costs. Compare against relevant baselines; measure calibration, discrimination, sensitivity, missed-high-risk cases, uptake, referral completion, operational capacity and subgroup errors. Obtain clinical oversight before any live screening or referrals. These are proposals for future work, not claims that the present prototype has done them.

## API

`POST /api/v1/evaluation/audit`

```json
{"country":"Togo","cohort_size":240,"outreach_capacity":45,"seed":2026,"sensitivity_runs":12}
```

The response includes `source_qa`, `checks`, `strategies`, `sensitivity`, `capacity_sensitivity`, `cohort_sha256`, `validation_status`, and `limitations`.

## Reading guide for jury

1. Start with individual WHO chart-cell demonstration in `/`.
2. Inspect population simulation at `/population`.
3. Compare allocation rules at `/prioritization`.
4. Open `/evaluation`, rerun with a new seed, inspect group-level coverage and source QA, and download the JSON.
5. End with the scientific boundary: **software correctness on synthetic inputs is not evidence of clinical performance**.
