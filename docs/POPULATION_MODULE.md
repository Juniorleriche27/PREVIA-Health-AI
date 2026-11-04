# PREVIA v0.3 — Synthetic population intelligence

## Purpose

Offer a demonstrable, interactive **population health planning simulation** for the hackathon without access to real patient records. The v0.3 module demonstrates distribution visualizations and illustrative screening-capacity scenarios based on WHO 2019 non-laboratory chart cells, with explicit boundaries against clinical use.

## Endpoints

- `POST /api/v1/population/scenario`
- Example: `{"country":"Togo","cohort_size":240,"outreach_capacity":45,"seed":2026}`

Response has full synthetic risk/age/area/sex distributions, an illustrative priority queue of max eight artificial profiles, and methodology and data-use limits.

## Data provenance

- Source of chart values: https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf (page 2).
- Cohort: randomly generated local simulation, reproducible by the `seed` parameter. All artificial. **Not a representative sample** of any population or country.
- Simulated areas A-D are fictional labels. The selected country only switches the chart's supported reference label, not the underlying profiles.
- No personal health data, population records, or results are stored.

## Limitations

- Risk values are integers from group-level lookup cells, not precision individual predictions.
- The synthetic screening slot allocation ranks by chart cell value; it is **NOT clinically validated triage**, medical advice or a legitimate way to choose patients.
- No inference about how many real people have elevated risk, how many clinical events might occur, or impact of an intervention can be made.
- Before use in real populations: authorized dataset and consent, regional chart coverage, ethics review, validation against real outcomes, clinical governance, fairness auditing and actual care referral protocols are needed.

## Next development phase

Evaluate with suitably licensed real *de-identified* data and explicit clinical review, add measurement completeness and inequity checks, and design a validated referral/follow-up pathway. No patient portal is implemented by this prototype.
