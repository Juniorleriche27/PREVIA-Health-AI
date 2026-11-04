"""Aggregate-only NHANES 2017-2018 INPUT-QUALITY assessment (USA, not WSSA).

This module deliberately does not calculate WSSA WHO risk values for U.S.
participants. NHANES 2017-2018, without longitudinal adjudicated incident
fatal and nonfatal MI/stroke outcomes for each participant, cannot validate
10-year model calibration, discrimination or clinical benefit.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from json import dumps
from pathlib import Path
from typing import Any

DATA_FILES = ('DEMO_J', 'BMX_J', 'BPX_J', 'SMQ_J', 'MCQ_J')
CDC_INDEX = 'https://wwwn.cdc.gov/Nchs/Nhanes/Search/DataPage.aspx?Cycle=2017-2018'
CDC_FILES = {
    name: f'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/{name}.xpt'
    for name in DATA_FILES
}
AGGREGATE = Path(__file__).resolve().parents[1] / 'data' / 'nhanes2017_2018_aggregate.json'
CVD_COLS = ('MCQ160B', 'MCQ160C', 'MCQ160D', 'MCQ160E', 'MCQ160F')


def smoking_status(ever: Any, now: Any) -> bool | None:
    """NHANES SMQ020: 1=yes/2=no; SMQ040: 1=daily/2=some days/3=not at all."""
    if ever == 2:
        return False
    if ever == 1 and now in (1, 2):
        return True
    if ever == 1 and now == 3:
        return False
    return None


def cvd_status(values: list[Any]) -> bool | None:
    """Conservative: positive any => known; all No => no known; else unknown."""
    if any(value == 1 for value in values):
        return True
    if values and all(value == 2 for value in values):
        return False
    return None


def _scalar_ok(v: Any, minimum: float, maximum: float) -> bool:
    try:
        return v is not None and minimum <= float(v) <= maximum
    except (TypeError, ValueError, OverflowError):
        return False


def _valid_sbp(values: list[Any]) -> float | None:
    good = [float(x) for x in values if _scalar_ok(x, 60, 300)]
    return sum(good) / len(good) if good else None


def aggregate_tables(tables: dict[str, Any], files_sha256: dict[str, str] | None = None) -> dict:
    """Validate XPT joins and summarize public source inputs; NO individual output."""
    expected_cols = {
        'DEMO_J': ('SEQN', 'RIDAGEYR', 'RIAGENDR'),
        'BMX_J': ('SEQN', 'BMXBMI'),
        'BPX_J': ('SEQN', 'BPXSY1', 'BPXSY2', 'BPXSY3'),
        'SMQ_J': ('SEQN', 'SMQ020', 'SMQ040'),
        'MCQ_J': ('SEQN', *CVD_COLS),
    }
    if set(tables) != set(DATA_FILES):
        raise ValueError('All five official NHANES tables required: ' + ', '.join(DATA_FILES))
    for name, required in expected_cols.items():
        table = tables[name]
        absent = sorted(set(required) - set(table.columns))
        if absent:
            raise ValueError(f'{name}: missing columns {absent}')
        if table['SEQN'].isna().any() or table['SEQN'].duplicated().any():
            raise ValueError(f'{name}: missing or duplicate SEQN identifiers')
    # Preserve left DEMO denominator: attrition by missing/non-matching files is measured.
    merged = tables['DEMO_J'][list(expected_cols['DEMO_J'])].copy()
    merged = merged.loc[merged['RIDAGEYR'].between(40, 74)].copy()
    denominator = len(merged)
    matched: dict[str, int] = {}
    for name in ('BMX_J', 'BPX_J', 'SMQ_J', 'MCQ_J'):
        subset = tables[name][list(expected_cols[name])]
        merged = merged.merge(subset, on='SEQN', how='left', indicator=True, validate='one_to_one')
        matched[name] = int((merged['_merge'] == 'both').sum())
        merged = merged.drop(columns=['_merge'])
    checks = Counter()
    sexes = Counter()
    complete_sexes = Counter()
    for row in merged.itertuples(index=False):
        x = row._asdict()
        is_sex = x['RIAGENDR'] in (1, 2)
        is_bmi = _scalar_ok(x['BMXBMI'], 10, 80)
        is_sbp = _valid_sbp([x[f'BPXSY{i}'] for i in range(1, 4)]) is not None
        is_smoker = smoking_status(x['SMQ020'], x['SMQ040']) is not None
        cvd = cvd_status([x[name] for name in CVD_COLS])
        is_cvd_known = cvd is not None
        for name, ok in [('sex_recorded',is_sex), ('bmi_usable',is_bmi),
                         ('systolic_bp_usable',is_sbp), ('current_smoking_classifiable',is_smoker),
                         ('cvd_history_classifiable',is_cvd_known)]:
            checks[name + '_present' if ok else name + '_missing'] += 1
        if cvd is True:
            checks['excluded_known_cvd'] += 1
        if cvd is False:
            checks['no_known_cvd_on_survey'] += 1
        sex_name = 'male' if x['RIAGENDR'] == 1 else 'female' if x['RIAGENDR'] == 2 else 'not_recorded'
        sexes[sex_name] += 1
        if is_sex and is_bmi and is_sbp and is_smoker and cvd is False:
            checks['complete_primary_prevention_inputs'] += 1
            complete_sexes[sex_name] += 1
    # Explicitly labeled unweighted survey-compatibility counts, not prevalence.
    result = {
        'dataset': 'CDC NHANES 2017-2018 (public-use survey data)',
        'cycle': '2017-2018',
        'population_region': 'United States of America',
        'mode': 'real_public_data_input_quality_only',
        'source_index': CDC_INDEX,
        'source_xpt_urls': CDC_FILES,
        'input_tables': list(DATA_FILES),
        'download_sha256': files_sha256 or {},
        'adults_40_to_74_unweighted_n': denominator,
        'source_join_matches_n': matched,
        'unweighted_sex_counts_n': dict(sexes),
        'complete_input_counts_by_sex_n': dict(complete_sexes),
        'field_quality_unweighted_n': dict(checks),
        'complete_primary_prevention_inputs_n': int(checks['complete_primary_prevention_inputs']),
        'complete_input_share_pct_unweighted': round(100 * checks['complete_primary_prevention_inputs'] / denominator, 2) if denominator else None,
        'survey_weighted_estimates_computed': False,
        'WHO_western_africa_risk_scored': False,
        'actual_ten_year_CVD_outcomes_available': False,
        'validates_WHO_western_africa_model': False,
        'may_be_used_for': ['external public-data field compatibility', 'missingness', 'record linkage QA'],
        'must_not_be_used_for': [
            'Western Sub-Saharan Africa risk/prevalence estimates',
            '10-year WHO chart discrimination or calibration',
            'actual benefit, patient triage, diagnostic guidance, clinical fairness',
        ],
        'limitations': [
            'NHANES samples the United States, not Togo or Western Sub-Saharan Africa.',
            'The 2017-2018 survey snapshot here has no adjudicated 10-year individual incident MI/stroke outcome labels.',
            'Smoking derivation uses cigarette questions SMQ020 and SMQ040, not all tobacco products.',
            'Exclusion of known CVD uses self-report MCQ items and may misclassify history.',
            'Unweighted counts are data completeness diagnostics, NOT US population estimates.',
            'No individual SEQN, participant input or row-level health data is returned or stored in the aggregate report.',
        ],
    }
    return result


def digest_aggregate(data: dict) -> str:
    return sha256(dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
