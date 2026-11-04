"""v0.6 reference data provenance and real-public-data INPUT QUALITY (not clinical performance)."""
from copy import deepcopy
from hashlib import sha256
from json import dumps

import pytest
from fastapi.testclient import TestClient

from app import source_verification
from app.main import app
from app.public_data import aggregate_tables, cvd_status, smoking_status, digest_aggregate
from app.who_chart import CHART, lookup

client = TestClient(app)


def test_complete_who_pdf_text_reference_matches_entire_700_cells():
    result = source_verification.verify_all_chart_cells()
    assert result['cells_compared'] == result['cells_matching'] == 700
    assert result['mismatches'] == []
    assert result['text_cross_check_passed']
    assert not result['visual_cell_by_cell_verification']
    assert not result['clinical_validation']


def test_two_real_transcription_defects_fixed():
    assert lookup(72, 'female', True, 130, 23.0).value == 17
    assert lookup(41, 'female', False, 125, 27.0).value == 2


def test_malformed_transcription_fail_closed(tmp_path, monkeypatch):
    bad = tmp_path / 'bad.txt'
    bad.write_text('70: 1 2 3\n', encoding='utf-8')
    monkeypatch.setattr(source_verification, 'TRANSCRIPTION', bad)
    with pytest.raises(ValueError, match='layout'):
        source_verification.verify_all_chart_cells()


def test_mismatch_detection_when_chart_is_tampered(monkeypatch):
    changed = deepcopy(CHART)
    q = list(changed[50]['FN'])
    row = list(q[3]); row[2] = 99; q[3] = tuple(row)
    changed[50]['FN'] = tuple(q)
    monkeypatch.setattr(source_verification, 'CHART', changed)
    res = source_verification.verify_all_chart_cells()
    assert res['cells_matching'] == 699
    assert len(res['mismatches']) == 1
    assert res['mismatches'][0]['age_start'] == 50


def test_v06_evidence_route_real_status_no_fake_public_data(monkeypatch, tmp_path):
    from app import evidence
    monkeypatch.setattr(evidence, 'AGGREGATE', tmp_path / 'not_here.json')
    res = client.get('/api/v1/evidence/status')
    assert res.status_code == 200
    j = res.json()
    assert j['version'] == '0.6.0'
    assert j['who_pdf_text_verification']['cells_matching'] == 700
    assert j['public_dataset']['status'] == 'not_loaded'
    assert j['public_dataset']['aggregate_report'] is None
    assert any(x['status'] == 'NOT VALIDATED' for x in j['claim_register'])
    assert '/api/v1/evidence/status' in client.get('/openapi.json').text


def test_rejects_malformed_public_aggregate(monkeypatch, tmp_path):
    from app import evidence
    fake = tmp_path / 'aggregate.json'
    fake.write_text('{"mode":"fake","complete_primary_prevention_inputs_n":8000}')
    monkeypatch.setattr(evidence, 'AGGREGATE', fake)
    j = client.get('/api/v1/evidence/status').json()
    assert j['public_dataset']['status'] == 'aggregate_invalid'
    assert j['public_dataset']['aggregate_report'] is None


@pytest.mark.parametrize('ever,now,expected',[(2,None,False),(1,1,True),(1,2,True),(1,3,False),(1,7,None),(7,1,None),(None,None,None)])
def test_cdc_smoking_codes(ever, now, expected):
    assert smoking_status(ever, now) is expected


@pytest.mark.parametrize('answers,expected',[
    ([2,2,2,2,2],False),([2,1,2,None,2],True),([2,2,None,2,2],None),([9,9,9,9,9],None),
])
def test_conservative_known_cvd(answers,expected):
    assert cvd_status(answers) is expected


def mock_tables():
    pd = pytest.importorskip('pandas')
    return {
        'DEMO_J': pd.DataFrame({'SEQN':[1,2,3,4,5,6,7], 'RIDAGEYR':[52,62,44,70,31,55,41], 'RIAGENDR':[2,1,2,1,1,2,1]}),
        'BMX_J': pd.DataFrame({'SEQN':[1,2,3,4,5,6,7], 'BMXBMI':[26.1,31.0,None,23.0,25.0,42.0,28.0]}),
        'BPX_J': pd.DataFrame({'SEQN':[1,2,3,4,5,6,7], 'BPXSY1':[128,150,142,None,111,160,115], 'BPXSY2':[126,148,143,None,113,156,119], 'BPXSY3':[130,152,144,None,112,158,118]}),
        'SMQ_J': pd.DataFrame({'SEQN':[1,2,3,4,5,6,7], 'SMQ020':[2,1,1,1,2,1,2], 'SMQ040':[None,1,9,3,None,2,None]}),
        'MCQ_J': pd.DataFrame({'SEQN':[1,2,3,4,5,6,7], 'MCQ160B':[2,2,2,2,2,2,2], 'MCQ160C':[2,2,2,2,2,2,2], 'MCQ160D':[2,2,2,2,2,2,2], 'MCQ160E':[2,2,2,2,2,1,2], 'MCQ160F':[2,2,2,2,2,2,2]}),
    }


def test_external_public_tables_aggregate_only():
    tables = mock_tables()
    report = aggregate_tables(tables, {n:'digest' for n in tables})
    assert report['adults_40_to_74_unweighted_n'] == 6
    assert report['complete_primary_prevention_inputs_n'] == 3  # SEQN 1,2,7 only
    assert report['complete_input_share_pct_unweighted'] == 50.0
    assert report['WHO_western_africa_risk_scored'] is False
    assert report['actual_ten_year_CVD_outcomes_available'] is False
    assert report['validates_WHO_western_africa_model'] is False
    assert all('SEQN' not in name for name in report.keys())
    assert report['source_join_matches_n']['BMX_J'] == 6
    assert digest_aggregate(report) == digest_aggregate(report)


def test_join_uniqueness_and_missing_required_fields_rejected():
    tables = mock_tables()
    tables['BPX_J'].loc[1, 'SEQN'] = 1
    with pytest.raises(ValueError, match='duplicate'):
        aggregate_tables(tables)
    tables = mock_tables()
    tables['SMQ_J'] = tables['SMQ_J'].drop(columns=['SMQ040'])
    with pytest.raises(ValueError, match='SMQ040'):
        aggregate_tables(tables)


def test_partial_joins_measured_not_silently_removed():
    tables = mock_tables()
    tables['BMX_J'] = tables['BMX_J'][tables['BMX_J']['SEQN'] != 2]
    report = aggregate_tables(tables)
    assert report['adults_40_to_74_unweighted_n'] == 6
    assert report['source_join_matches_n']['BMX_J'] == 5
    assert report['complete_primary_prevention_inputs_n'] == 2


def test_nhanes_never_outputs_us_wssa_chart_estimates():
    report = aggregate_tables(mock_tables())
    assert 'who_chart_values' not in report
    assert report['survey_weighted_estimates_computed'] is False
    assert 'Western Sub-Saharan Africa risk/prevalence estimates' in report['must_not_be_used_for']
