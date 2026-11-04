"""WHO 2019 non-laboratory CVD risk-chart LOOKUP (regional, not clinical advice).

Scope: Western Sub-Saharan Africa ONLY. The 2019 WHO chart displays
integer percentages for 10-year fatal/nonfatal MI and stroke risk.

Digitized from the official regional chart (page 2):
https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf

For each five-year age band, rows follow systolic BP descending:
    >=180, 160-179, 140-159, 120-139, <120
Within each row, columns follow BMI ascending:
    <20, 20-<25, 25-<30, 30-<35, >=35
The index for 30-35 vs >=35 is made disjoint at 35.0.

IMPORTANT: Research/prototype demonstration ONLY. Not validated for clinical
operation. Values are discrete chart-bin lookups, not model predictions.
"""
from dataclasses import dataclass

SOURCE = "https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf"
REGION = "Western Sub-Saharan Africa"
COUNTRIES = (
    "Benin", "Burkina Faso", "Cabo Verde", "Cameroon", "Chad",
    "Cote d'Ivoire", "Gambia", "Ghana", "Guinea", "Guinea-Bissau",
    "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Sao Tome and Principe",
    "Senegal", "Sierra Leone", "Togo",
)

# Age band -> chart quadrant -> 5 rows of systolic blood pressure / 5 BMI values.
# Quadrants: MN = male nonsmoker; MS = male smoker; FN = female nonsmoker; FS = female smoker.
TABLE = {
  70: {
    'MN': '23 24 26 28 30/19 20 21 23 25/15 16 17 19 20/12 13 14 15 16/10 11 11 12 13',
    'MS': '29 31 33 36 38/24 26 28 30 32/20 21 23 24 26/16 17 18 20 21/13 14 15 16 17',
    'FN': '20 21 21 22 23/17 17 18 18 19/14 14 15 15 16/11 12 12 13 13/9 10 10 10 11',
    'FS': '29 30 31 32 33/24 25 26 27 28/20 21 21 22 23/17 17 18 18 19/14 14 15 15 16',
  },
  65: {
    'MN': '17 19 21 22 24/14 15 16 18 20/11 12 13 14 16/9 9 10 11 12/7 7 8 9 10',
    'MS': '24 26 29 31 34/19 21 23 25 27/15 17 18 20 22/12 13 15 16 18/10 11 12 13 14',
    'FN': '15 16 17 17 18/12 13 13 14 15/10 10 11 11 12/8 8 9 9 9/6 7 7 7 8',
    # Source's PDF text extractor once misread the final 160–179 cell as 28.
    # It is 23 in the rendered original (checked visually).
    'FS': '24 25 26 27 29/20 21 21 22 23/16 17 17 18 19/13 13 14 15 15/10 11 11 12 12',
  },
  60: {
    'MN': '13 15 16 18 20/10 11 13 14 16/8 9 10 11 12/6 7 7 8 9/5 5 6 6 7',
    'MS': '20 22 24 27 30/16 17 19 21 24/12 13 15 17 19/9 10 12 13 15/7 8 9 10 11',
    'FN': '12 12 13 14 14/9 10 10 11 11/7 8 8 8 9/6 6 6 6 7/4 5 5 5 5',
    'FS': '20 21 22 24 25/16 17 18 19 20/13 13 14 15 16/10 11 11 12 12/8 8 9 9 10',
  },
  55: {
    'MN': '10 11 13 14 16/8 9 10 11 12/6 6 7 8 9/4 5 5 6 7/3 4 4 5 5',
    'MS': '16 18 21 23 26/12 14 16 18 20/9 11 12 14 16/7 8 9 10 12/5 6 7 8 9',
    'FN': '9 10 10 11 11/7 7 8 8 8/5 5 6 6 6/4 4 4 5 5/3 3 3 3 4',
    'FS': '17 18 19 20 21/13 14 15 16 16/10 11 11 12 13/8 8 9 9 10/6 6 7 7 7',
  },
  50: {
    'MN': '8 9 10 11 13/6 6 7 8 10/4 5 5 6 7/3 3 4 5 5/2 2 3 3 4',
    'MS': '13 15 18 20 23/10 11 13 15 18/7 8 10 11 13/5 6 7 8 10/4 5 5 6 7',
    'FN': '7 7 8 8 9/5 5 6 6 6/4 4 4 4 5/3 3 3 3 3/2 2 2 2 3',
    'FS': '14 15 16 17 18/11 11 12 13 14/8 9 9 10 10/6 6 7 7 8/4 5 5 5 6',
  },
  45: {
    'MN': '6 7 8 9 11/4 5 6 7 8/3 3 4 5 5/2 2 3 3 4/1 2 2 2 3',
    'MS': '11 13 15 17 20/8 9 11 13 15/6 7 8 9 11/4 5 6 7 8/3 3 4 5 6',
    'FN': '5 6 6 6 7/4 4 4 5 5/3 3 3 3 3/2 2 2 2 2/1 1 2 2 2',
    'FS': '12 13 14 15 16/9 9 10 11 11/6 7 7 8 8/5 5 5 6 6/3 4 4 4 4',
  },
  40: {
    'MN': '5 5 6 7 9/3 4 4 5 6/2 3 3 4 4/1 2 2 2 3/1 1 1 2 2',
    'MS': '9 11 13 15 18/6 7 9 11 13/4 5 6 8 9/3 4 4 5 6/2 3 3 4 5',
    'FN': '4 4 5 5 5/3 3 3 3 4/2 2 2 2 3/1 1 2 2 2/1 1 1 1 1',
    'FS': '10 11 12 12 13/7 8 8 9 10/5 5 6 6 7/4 4 4 4 5/2 3 3 3 3',
  },
}

CHART = {
    age: {group: tuple(tuple(int(n) for n in row.split()) for row in grid.split('/'))
          for group, grid in quadrants.items()}
    for age, quadrants in TABLE.items()
}
for age, quadrants in CHART.items():
    assert set(quadrants) == {'MN', 'MS', 'FN', 'FS'}
    for quadrant, grid in quadrants.items():
        assert len(grid) == 5 and all(len(row) == 5 for row in grid), (age, quadrant)
        assert all(0 <= value <= 100 for row in grid for value in row)

@dataclass(frozen=True)
class ChartResult:
    value: int
    age_band: str
    bp_band: str
    bmi_band: str
    risk_band: str


def lookup(age: int, sex: str, smoker: bool, sbp: float, bmi: float) -> ChartResult:
    if not 40 <= age <= 74:
        raise ValueError('WHO chart age is 40–74')
    if sex not in ('male', 'female'):
        raise ValueError('WHO chart requires chart reference sex')
    if not (60 <= sbp <= 300 and 10 <= bmi <= 80):
        raise ValueError('Measurements outside supported form bounds')
    age_start = (age // 5) * 5
    bp_index = 0 if sbp >= 180 else 1 if sbp >= 160 else 2 if sbp >= 140 else 3 if sbp >= 120 else 4
    bmi_index = 0 if bmi < 20 else 1 if bmi < 25 else 2 if bmi < 30 else 3 if bmi < 35 else 4
    quadrant = ('M' if sex == 'male' else 'F') + ('S' if smoker else 'N')
    value = CHART[age_start][quadrant][bp_index][bmi_index]
    risk_band = ('<5%' if value < 5 else '5% to <10%' if value < 10 else
                 '10% to <20%' if value < 20 else '20% to <30%' if value < 30 else '≥30%')
    bp_bands = ('≥180', '160–179', '140–159', '120–139', '<120')
    bmi_bands = ('<20', '20–<25', '25–<30', '30–<35', '≥35')
    return ChartResult(value, f'{age_start}–{age_start+4}', bp_bands[bp_index], bmi_bands[bmi_index], risk_band)
