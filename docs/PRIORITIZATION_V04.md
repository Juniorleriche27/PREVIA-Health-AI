# PREVIA Health AI — Module 04: synthetic allocation strategy comparison

## Scientific scope

**Research demonstration only. Not a clinical triage, referral, prevention, or population-health decision tool.**

The same synthetic cohort and WHO 2019 Western Sub-Saharan Africa non-laboratory reference chart (https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf) from Module 03 are reused, **without generating different people for different strategies**. The example cohort is a pseudorandom, arbitrarily distributed demonstration, **not** a national or local disease prevalence estimate.

The categorical threshold of WHO chart-cell value **>= 10%** is a **comparison label only**, **not** a referral threshold or medical indication. WHO chart-bin values are grouped estimates and have not been validated clinically in this prototype.

## Endpoint

`POST /api/v1/prioritization/compare` (no authentication because this is a local, synthetic-only prototype)

```json
{
  "country": "Togo",
  "cohort_size": 240,
  "outreach_capacity": 45,
  "seed": 2026
}
```

Validation: supported WHO region only; cohort size between 40 and 500; slots between 1 and cohort size; seed between 0 and 1,000,000. Returns precisely three strategies with the same synthetic profiles and equal capacity.

## Compared strategies

1. `chart_descending` — highest chart-cell value first. Ties are broken by synthetic ID. The comparison metric based on that same chart value is **inherently favorable** to this rule: it is *not independent outcome validation*.
2. `sector_balanced` — approximate equal *selection rates* across four artificial demonstration sectors. Within each sector, higher chart-cell values are selected first. This does not prove healthcare equity or optimize medical necessity.
3. `seeded_random` — an independent reproducible pseudorandom sample using the specified seed. Used as a simple baseline, not a recommended health policy.

No real individual is identified; all IDs start with `SYN-`. The API does not persist requests or selected IDs.

## Indicator definitions

Let `N` be synthetic profiles, `K` allocated slots, `H` all synthetic profiles with WHO chart-cell value >=10%, and `H_s` selected profiles in this category.

| KPI | Definition | Interpretation |
|---|---|---|
| Chart-category capture (%) | `100 × H_s / H` (0 if `H=0`) | Proportion of artificial chart-positive profiles selected; *not* a clinical sensitivity estimate |
| Selected yield (%) | `100 × H_s / K` | Artificial chart-positive percentage within selected profiles; *not* predictive precision against true disease |
| Mean chart-cell value (%) | `sum(chart-cell values of selected) / K` | Mean discretized reference value; *not* individual true risk or prevented events |
| Sector selection rate (%) | `100 × selected in sector / cohort in sector` | Selection coverage within each invented sector |
| Sector selection gap (pp) | `max(sector rates) - min(sector rates)` | Descriptive allocation disparity across invented sectors; *not* a fairness verdict |
| Reference-sex selection gap (pp) | `max(reference-sex rates) - min(reference-sex rates)` | Descriptive group difference; no inferred gender fairness or health outcomes |
| Capacity used | `100 × K / N` | Share of cohort that can be selected under current illustrative capacity |

## Safeguards and evaluation

- No treatment, medical referrals, diagnoses, prevented adverse events or quality-of-life gains are estimated.
- No patient records are uploaded, saved or processed.
- The scenario is intentionally labeled synthetic in the API and frontend.
- All comparison strategies evaluate the **same** cohort and fixed capacity.
- Deterministic sampling and tie-breaks permit independent replay.
- The same WHO source and regional constraints are retained.
- Changing the WHO-reference country within this region changes the label, **not** population distribution, as no local prevalence data are modeled.
- Dataset-internal rates are not clinical effectiveness measurements; credible clinical validation and care-partner oversight would be needed before any real-world use.

## Tests

The automated suite checks endpoint/schema/country/capacity boundaries, fixed seed repeatability, identical baseline cohort, no duplicates, coherent percentages, sector selection balance, no mutation, compatibility with Module 03, and non-clinical disclosures.

Run from `backend`:

```powershell
& ..\.venv\Scripts\python.exe -m pytest -q
```

## Next module candidates

- Methods evaluation with independent outcome data, where available and appropriately approved.
- Sensitivity analyses across different capacities and synthetic distributions.
- A clinically supervised pilot protocol; no actual patient deployments in this prototype.
