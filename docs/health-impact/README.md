# PREVIA Health AI — Health-impact evidence package

This directory contains the reproducible scientific demonstration prepared for the Future Health Digital Innovation Challenge 2026. It evaluates **synthetic resource-allocation behaviour**, not clinical effectiveness.

## Reading order

| Audience | Français | English |
|---|---|---|
| Jury (2-minute brief) | [Synthèse jury](jury-summary-fr.md) | [Jury summary](jury-summary-en.md) |
| Full assessment | [Rapport d'impact](health-impact-report-fr.md) | [Health-impact report](health-impact-report-en.md) |
| Reproduction and formulas | [Méthodologie](methodology-fr.md) | [Methodology](methodology-en.md) |
| Future real-world evaluation | [Protocole pilote](pilot-protocol-fr.md) | [Pilot protocol](pilot-protocol-en.md) |

## Evidence files

- [`results/manifest.json`](results/manifest.json): configuration, scientific boundaries, cohort fingerprint and SHA-256 checksums.
- [`results/risk_distribution.csv`](results/risk_distribution.csv): baseline synthetic WHO chart categories.
- [`results/baseline_capacity_results.csv`](results/baseline_capacity_results.csv): strategy results for the baseline seed.
- [`results/all_seed_runs.csv`](results/all_seed_runs.csv): 360 complete experiment rows (30 seeds × 4 capacities × 3 strategies).
- [`results/stability_summary.csv`](results/stability_summary.csv): min/median/mean/max/population SD across synthetic seeds.
- [`results/figures/`](results/figures/): four dependency-free SVG figures generated from the CSV results.

## Reproduce

From the repository root on Windows:

```powershell
& .\.venv\Scripts\python.exe scripts\evaluate_health_impact.py
& .\.venv\Scripts\python.exe -m pytest backend\tests\test_health_impact.py -q
```

The script overwrites only the generated files in `docs/health-impact/results/`. Identical code and configuration produce byte-identical CSV and JSON evidence files.

## Non-negotiable scientific boundary

The profiles and sectors are artificial. The ≥10% WHO chart-cell label is a comparison convention, not a referral rule. Because the WHO chart value both orders one strategy and defines the principal coverage indicator, that comparison is circular and cannot establish diagnostic accuracy or clinical benefit. No mortality reduction, event prevention, hospitalisation reduction or real-world equity claim is made.
