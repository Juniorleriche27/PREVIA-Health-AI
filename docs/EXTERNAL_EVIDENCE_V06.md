# PREVIA Health AI 0.6 — Source verification and real public-data input compatibility

**Status:** research software quality assurance. **Not a clinical risk-model validation study.**

## Achievements

1. Rechecked 700 values (7 age groups × 4 chart-reference sex/smoking groups × 5 SBP rows × 5 BMI columns) against a separately recorded text-layer extraction from the **official WHO Western Sub-Saharan Africa non-laboratory PDF, page 2**.
2. Found and corrected two discrepancies in the previous v0.5 implementation:

   | Age | Chart quadrant | Systolic BP | BMI | v0.5 | v0.6 / official PDF text |
   |---|---|---|---|---:|---:|
   | 70–74 | female smoker (FS) | 120–139 mmHg | 20–<25 | 18% | **17%** |
   | 40–44 | female non-smoker (FN) | 120–139 mmHg | 25–<30 | 1% | **2%** |

3. Stored the **separate** WHO PDF-text transcription in `backend/data/who2019_wssa_nonlab_pdf_text.txt`, and added exhaustive cross-checks in `backend/app/source_verification.py`.
4. Added a CDC NHANES 2017–2018 **data-readiness** ETL that downloads five official, de-identified public `.xpt` files onto the user's own PC; checks joins, smoking-status coding, BP readings, BMI and self-reported cardiovascular history; and writes **only an unweighted aggregate quality summary**.
5. Added a dedicated `/evidence` page and GET `/api/v1/evidence/status` endpoint that distinguishes software/reference quality from real-world clinical effectiveness.

## Critical source-validation scope

Matching **all 700 values against the publisher PDF text layer** is stronger than the 28-anchor spot check in v0.5, but does **not** establish that every glyph was correctly represented by the PDF text extractor. The separate text-layer transcription is not an independent visual or clinician-certified audit. No original PDF binary SHA-256 has been verified in this workflow. A complete visual check and medical review are still required for any deployment beyond a research demo.

Source: [WHO Western Sub-Saharan Africa laboratory and non-laboratory charts (PDF)](https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf), p. 2. Background: [WHO CVD Risk Charts Working Group, Lancet Global Health (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7025029/).

## Official CDC NHANES data mapping (2017–2018)

All files are linked by unique participant sequence identifier `SEQN`, which is never published to the PREVIA API or reported in the output.

| CDC public file | Fields used | Transformation |
|---|---|---|
| DEMO_J | RIDAGEYR, RIAGENDR | Age 40–74; recorded sex reference |
| BMX_J | BMXBMI | BMI kg/m² in supported input range |
| BPX_J | BPXSY1, BPXSY2, BPXSY3 | Mean of available valid systolic readings |
| SMQ_J | SMQ020, SMQ040 | Ever 100 cigarettes and now smoke every day/some days/not at all; unknown coded as missing |
| MCQ_J | MCQ160B/C/D/E/F | Known self-reported CHF/CHD/angina/heart attack/stroke; exclude positive; unknown excluded from complete primary-prevention inputs |

Documentation: [CDC NHANES public data catalog](https://wwwn.cdc.gov/Nchs/Nhanes/Search/DataPage.aspx?Cycle=2017-2018), [CDC smoking codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/SMQ_J.htm), [CDC medical-conditions codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/MCQ_J.htm).

### Download and compute the real survey input-quality report (on a PC with Internet)

From the root of the installed PREVIA folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_nhanes_v06.ps1
```

The script uses the public CDC XPT URLs, records SHA-256 per downloaded file, joins five files, and writes `backend/data/nhanes2017_2018_aggregate.json`. It does not upload individual records, train a model, or compute risk for US respondents with the Western African chart. If the CDC endpoint is unavailable or the XPT inputs are missing, it **fails with a visible error**; no fabricated NHANES values are shown. For datasets already obtained from CDC, run `python scripts/prepare_nhanes_v06.py --input-dir path_to_directory` from the project root (inside activated venv with pandas installed).

**Source data residency:** `local_public_data/NHANES_2017_2018/` on the user's machine, excluded from Git. In the web app, only the aggregate JSON is read. Its counts are unweighted and must **not** be interpreted as national prevalence estimates.

### Scientific interpretation

NHANES 2017–2018 is a US cross-sectional dataset, not a Togolese cohort; it is therefore used **only to study completeness and interoperability of real-world input variables**. It does not provide the required prospective, adjudicated **ten-year incident fatal/nonfatal MI or stroke outcomes** in this workflow. No C-index, AUROC, sensitivity, specificity, calibration, observed risk, reduction in events, or benefits of screening are evaluated. WHO's original model paper has its own external validation on cohorts; that published performance must **not** be presented as PREVIA's validation.

A proper prospective regional validation would need: (a) an independent relevant cohort, (b) baseline WHO input variables, (c) exclusion of pre-existing CVD, (d) ten-year adjudicated events with censoring, (e) calibration and discrimination evaluation, and (f) subgroup analyses and local clinical review.

## Commands and locations

- Verify v0.6: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_v06.ps1`.
- Run optional CDC dataset ETL: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_nhanes_v06.ps1`.
- Backend `/api/v1/evidence/status`: inspect text verification and aggregate status.
- Frontend `/evidence`: inspect source corrections, loaded/missing dataset, and claim register.
- Files changed: `backend/app/who_chart.py` (two table cells), `backend/app/source_verification.py` (cross-check), `backend/app/evidence.py` (endpoint), `backend/app/public_data.py` (ETL calculations), `backend/app/main.py` (router), `backend/app/evaluation.py` (updated audit status), `frontend/app/evidence/page.tsx` (new page), nav pages and CSS, tests, verification scripts, source transcript and documentation.

## Acceptance and outstanding work

- **Verified locally in build environment:** Python automated tests, 700/700 transcribed official PDF text cells, TSX syntax parsing.
- **To verify on user's Windows installation:** full Next.js build, route rendering, successful CDC source download and real aggregate statistics.
- **Not completed:** visual cell-by-cell PDF verification; external clinical validation; any model calibration to prospective local outcomes.
