# Reproducible methodology

## Evaluation question

Under simulated screening capacities, how do PREVIA's three implemented allocation rules change coverage of a descriptive WHO category, selection gaps across fictional groups, and stability across synthetic cohorts?

## Source, population, and provenance

The study uses the WHO 2019 non-laboratory chart for Western Sub-Saharan Africa referenced in `backend/app/who_chart.py`. The implementation contains 700 cells (7 age bands × 4 reference-sex/smoking quadrants × 5 blood-pressure rows × 5 BMI columns). The audit compares all 700 values with a second transcription of the PDF text layer and checks 28 anchor cells. An independent visual glyph-by-glyph review remains pending.

`make_synthetic_cohort` generates the cohort and does not represent any country. Selecting a supported country changes a label, not the variable distributions.

| Variable | Synthetic generation |
|---|---|
| Age | uniform integer 40–74 years |
| Chart-reference sex | pseudorandom male/female choice |
| Current smoking | Bernoulli probability 0.22 |
| Systolic blood pressure | uniform integer 105–190 mmHg |
| BMI | uniform 19.0–39.0, rounded to 0.1 |
| Sector | cyclic assignment A–D, fictional labels |

## Prespecified configuration

```json
{
  "cohort_size": 240,
  "capacities": [24, 45, 72, 120],
  "seeds": [2026, 2027, "...", 2055],
  "baseline_seed": 2026,
  "priority_definition": "WHO chart-cell value >= 10%",
  "strategies": ["chart_descending", "sector_balanced", "seeded_random"]
}
```

Seeds are sensitivity scenarios, not a statistical population sample. No population hypothesis test or confidence interval is calculated.

## Implemented comparators

1. `chart_descending`: descending WHO chart-cell value with synthetic ID as deterministic tie-breaker.
2. `sector_balanced`: repeatedly select from the sector with the lowest selected fraction, then select higher WHO values within that sector.
3. `seeded_random`: reproducible pseudorandom sample without replacement using a separate seed.

All rules receive the same cohort object and capacity; no strategy regenerates its own profiles.

## Metrics

Let `N` be profiles, `K` capacity, `H` profiles with WHO cell ≥10%, `Hₛ` selected profiles in that category, and `Nᵍ`/`Kᵍ` population/selected counts in group `g`.

- descriptive priority coverage: `100 × Hₛ / H`;
- descriptive yield: `100 × Hₛ / K`;
- group selection rate: `100 × Kᵍ / Nᵍ`;
- selection-rate gap: maximum minus minimum group rate, in percentage points;
- group priority coverage: selected ≥10% profiles in `g` divided by all ≥10% profiles in `g`;
- priority-coverage gap: maximum minus minimum group priority coverage among groups with non-zero denominators;
- stability: minimum, median, mean, maximum, and population SD across 30 artificial seeds.

Reported values are rounded to two decimals after integer counts are calculated.

## Circular dependence

`chart_descending` directly optimises the value defining `H`; strong coverage is therefore expected by construction. `sector_balanced` also ranks by that value within each sector. Consequently:

- the comparison measures adherence to an allocation rule;
- it does not measure clinical sensitivity, calibration, or utility;
- random selection is an allocation control, not standard care;
- no “best clinical strategy” ranking is produced.

## Quality controls and traceability

- bounds `0 ≤ priority selected ≤ min(K,H)`;
- unique identifiers and no cohort mutation;
- reconciliation of global and subgroup counts;
- byte-identical repetition in two temporary directories;
- SHA-256 fingerprint of the baseline cohort and each CSV;
- timestamp-free manifest to support exact comparison;
- regression checks against the historical 45-slot scenario.

## Reproduction

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_health_impact.py
& .\.venv\Scripts\python.exe -m pytest backend\tests\test_health_impact.py -q
```

An alternative, explicitly labelled run can use command-line options documented by `--help`.

## Existing-component audit

| Module | Verification | Conclusion |
|---|---|---|
| WHO screening | bounds, 700 cells, anchors, categories, source | software consistency; clinical validation not established |
| Population | deterministic generation, distributions, no real records | suitable only for software demonstration |
| Strategies | identical profiles/capacity, explicit rules/ties | reproducible comparison; dependent WHO criterion |
| Scientific audit | integrity, fingerprints, sensitivities | software QA, not effectiveness research |
| NHANES/SHAP | separation of HbA1c target and explanations | excluded from cardiovascular/allocation evaluation |
| RAG/Knowlia | separation of documentary synthesis | no contribution to calculated results |

## Limitations

Artificial distributions, limited group dimensions, and absent outcomes preclude epidemiological or causal conclusions. The 10% threshold is experimental. Binary reference-sex categories follow the chart structure and do not measure gender comprehensively. Sectors have no real geography. Results must not be extrapolated.
