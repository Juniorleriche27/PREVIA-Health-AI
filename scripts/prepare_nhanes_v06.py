#!/usr/bin/env python3
"""Download public CDC NHANES 2017-18 XPTs and make aggregate-only input QA.

Run on the user's own computer. No patient/person-level records are sent to
PREVIA. Does NOT score U.S. respondents with a Western Africa WHO chart.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.public_data import (AGGREGATE, CDC_FILES, DATA_FILES, aggregate_tables)


def download_one(name: str, folder: Path, force: bool = False) -> tuple[Path, str]:
    target = folder / f'{name}.xpt'
    # Two official addresses: canonical 2017 DataFiles and older cycle URL.
    urls = [CDC_FILES[name], f'https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/{name}.XPT']
    if target.exists() and not force and target.stat().st_size > 1024:
        blob = target.read_bytes()
        if blob.startswith(b'HEADER RECORD'):
            return target, sha256(blob).hexdigest()
    errors = []
    for url in urls:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'PREVIA-Research-Public-Data-QA/0.6'})
            with urllib.request.urlopen(request, timeout=35) as response:
                data = response.read(25 * 1024 * 1024 + 1)
            if not 1024 < len(data) <= 25 * 1024 * 1024 or not data.startswith(b'HEADER RECORD'):
                raise ValueError('Downloaded response is not a valid-looking SAS XPT file')
            target.write_bytes(data)
            return target, sha256(data).hexdigest()
        except (OSError, ValueError, urllib.error.URLError) as exc:
            errors.append(f'{url}: {exc}')
    raise RuntimeError(f'Unable to download {name} from CDC.\n' + '\n'.join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, help='Use five already downloaded original XPT files from this directory')
    parser.add_argument('--force', action='store_true', help='Re-download existing CDC XPT files')
    args = parser.parse_args()
    try:
        import pandas as pd
    except ImportError:
        print('Install pandas first: python -m pip install "pandas>=2.2,<4"', file=sys.stderr)
        return 2
    folder = args.input_dir or (ROOT / 'local_public_data' / 'NHANES_2017_2018')
    folder.mkdir(parents=True, exist_ok=True)
    paths = {}
    hashes = {}
    try:
        for name in DATA_FILES:
            if args.input_dir:
                path = folder / f'{name}.xpt'
                if not path.exists():
                    raise FileNotFoundError(f'Missing original XPT file: {path}')
                blob = path.read_bytes()
                if not blob.startswith(b'HEADER RECORD'):
                    raise ValueError(f'Not an original XPT file: {path}')
                digest = sha256(blob).hexdigest()
            else:
                path, digest = download_one(name, folder, args.force)
            paths[name] = path
            hashes[name] = digest
            print(f'{name}: verified XPT header, SHA-256 {digest[:16]}...')
        tables = {name: pd.read_sas(path, format='xport') for name, path in paths.items()}
        result = aggregate_tables(tables, hashes)
        # All data output is aggregated. This is the only file read by the API.
        AGGREGATE.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=AGGREGATE.parent,
                                         delete=False, suffix='.tmp') as tmp:
            json.dump(result, tmp, indent=2, ensure_ascii=False)
            tmp_path = Path(tmp.name)
        tmp_path.replace(AGGREGATE)
        print('PREVIA NHANES input QA complete.')
        print(f'Adults 40-74 (unweighted n): {result["adults_40_to_74_unweighted_n"]}')
        print(f'Usable primary-prevention input records (n): {result["complete_primary_prevention_inputs_n"]}')
        print('No 10-year WHO risk, event accuracy, calibration or local prevalence measured.')
        print(f'Aggregate-only report: {AGGREGATE}')
        return 0
    except Exception as exc:
        print(f'NHANES public data preparation could not be completed: {exc}', file=sys.stderr)
        print('The scientific software audit remains available. No NHANES results have been invented.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
