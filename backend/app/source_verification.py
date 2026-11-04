"""Full machine-readable WHO chart PDF-text transcription cross-check (non clinical).

Reference is copied from the publisher's text-layer extraction of PDF page 2.
This is independent of PREVIA's app/who_chart.py lookup table, but NOT an
independent visual verification of every printed cell or clinical validation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from .who_chart import CHART, SOURCE

TRANSCRIPTION = Path(__file__).resolve().parents[1] / 'data' / 'who2019_wssa_nonlab_pdf_text.txt'
QUADRANTS = ('MN', 'MS', 'FN', 'FS')
AGES = (70, 65, 60, 55, 50, 45, 40)


def verify_all_chart_cells() -> dict:
    """Fail closed on invalid oracle structure; report each discrepant cell."""
    raw = TRANSCRIPTION.read_bytes()
    age_rows: dict[int, list[list[int]]] = {age: [] for age in AGES}
    for line_number, raw_line in enumerate(raw.decode('utf-8').splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            head, tail = line.split(':', 1)
            age = int(head)
            row = [int(value) for value in tail.split()]
        except (ValueError, TypeError) as exc:
            raise ValueError(f'WHO source transcript malformed at line {line_number}') from exc
        if age not in age_rows or len(row) != 20 or len(age_rows[age]) >= 5:
            raise ValueError(f'WHO transcript unexpected cell layout line {line_number}')
        if any(not 0 <= value <= 100 for value in row):
            raise ValueError(f'WHO transcript values out of range line {line_number}')
        age_rows[age].append(row)
    if any(len(rows) != 5 for rows in age_rows.values()):
        raise ValueError('WHO source transcript incomplete: must contain 7*5 rows')
    mismatches = []
    for age in AGES:
        for sbp_row, cells in enumerate(age_rows[age]):
            for idx, quadrant in enumerate(QUADRANTS):
                for bmi_col in range(5):
                    expected = cells[idx * 5 + bmi_col]
                    actual = CHART[age][quadrant][sbp_row][bmi_col]
                    if expected != actual:
                        mismatches.append({
                            'age_start': age, 'quadrant': quadrant,
                            'sbp_row_from_high': sbp_row, 'bmi_column_from_low': bmi_col,
                            'expected_pdf_text': expected, 'actual_implementation': actual,
                        })
    return {
        'source': SOURCE,
        'source_page': 2,
        'method': 'Second transcription from WHO PDF text layer; 35 rows x 20 cells',
        'cells_compared': 700,
        'cells_matching': 700 - len(mismatches),
        'mismatches': mismatches,
        'text_transcription_sha256': sha256(raw).hexdigest(),
        'text_cross_check_passed': not mismatches,
        'visual_cell_by_cell_verification': False,
        'clinical_validation': False,
        'scope_notice': (
            'All 700 cells cross-checked against the official PDF text layer, '
            'not against 700 independently read rendered cells. Errors in the source text extraction '
            'cannot be ruled out. No patient-outcome validation is provided.'
        ),
        'corrections_v06': [
            {'age_start': 70, 'quadrant': 'FS', 'sbp_band': '120-139', 'bmi_band': '20-<25', 'was': 18, 'is': 17},
            {'age_start': 40, 'quadrant': 'FN', 'sbp_band': '120-139', 'bmi_band': '25-<30', 'was': 1, 'is': 2},
        ],
    }
