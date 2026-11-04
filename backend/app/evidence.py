"""Evidence status for PREVIA v0.6; independent text cross-check + public-data QA.

No endpoint accepts uploads or participant rows. The CDC survey is solely for
input-completeness assessment and is intentionally not applied to the WHO WSSA
regional risk model.
"""
from __future__ import annotations

from json import JSONDecodeError, loads
from fastapi import APIRouter

from .public_data import AGGREGATE, CDC_INDEX
from .source_verification import verify_all_chart_cells

router = APIRouter(prefix='/api/v1/evidence', tags=['Evidence — research methods'])


@router.get('/status')
def status() -> dict:
    comparison = verify_all_chart_cells()
    report = None
    data_status = 'not_loaded'
    if AGGREGATE.exists():
        try:
            candidate = loads(AGGREGATE.read_text(encoding='utf-8'))
            if (candidate.get('mode') == 'real_public_data_input_quality_only'
                and candidate.get('population_region') == 'United States of America'
                and candidate.get('WHO_western_africa_risk_scored') is False
                and isinstance(candidate.get('adults_40_to_74_unweighted_n'), int)):
                report, data_status = candidate, 'aggregate_ready'
            else:
                data_status = 'aggregate_invalid'
        except (OSError, ValueError, JSONDecodeError, TypeError):
            data_status = 'aggregate_invalid'
    return {
        'version': '0.6.0',
        'scope': 'RESEARCH SOFTWARE QA / PUBLIC DATA INPUT COMPATIBILITY; NOT CLINICAL VALIDATION',
        'who_pdf_text_verification': comparison,
        'public_dataset': {
            'name': 'CDC NHANES 2017-2018',
            'index': CDC_INDEX,
            'country': 'United States of America',
            'status': data_status,
            'aggregate_report': report,
            'download_command': 'powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\run_nhanes_v06.ps1',
            'data_location': 'Local workstation, original CDC XPT files; only aggregate report read by API',
            'domain_shift_warning': 'US survey respondents are NOT the target Western Sub-Saharan African population.',
        },
        'claim_register': [
            {'claim': 'Full WHO table digital correspondence', 'status': 'checked_against_official_pdf_text_layer',
             'evidence': '700 of 700 cells compared; visual point-by-point signoff pending.'},
            {'claim': 'Software correctness', 'status': 'tested', 'evidence': 'Regression suite and deterministic checks.'},
            {'claim': 'Independent public data input completeness',
             'status': 'aggregate_ready' if report else 'awaiting_download',
             'evidence': 'Five CDC NHANES XPT datasets; US only, aggregate-only summary.'},
            {'claim': 'Ten-year CVD predictive validation', 'status': 'NOT VALIDATED',
             'evidence': 'No appropriate independent longitudinal outcome cohort in this module.'},
            {'claim': 'Clinical use or country-specific benefit', 'status': 'NOT VALIDATED',
             'evidence': 'No trial, implementation pilot or relevant adjudicated events.'},
        ],
    }
