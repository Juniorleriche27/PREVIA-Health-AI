"""Reproducible synthetic impact evaluation for PREVIA Health AI.

This script evaluates allocation behaviour only. It does not estimate clinical
effectiveness, diagnostic accuracy, prevented events, or population prevalence.
It reuses the frozen WHO lookup and the three allocation strategies implemented
by the PREVIA backend.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.population import RISK_BANDS, SIMULATED_AREAS, make_synthetic_cohort  # noqa: E402
from app.prioritization import (  # noqa: E402
    REFERENCE_THRESHOLD,
    STRATEGY_KEYS,
    choose_by_chart,
    choose_by_sector,
    choose_random,
)

DEFAULT_CAPACITIES = (24, 45, 72, 120)
DEFAULT_SEEDS = tuple(range(2026, 2056))
STRATEGY_LABELS = {
    "chart_descending": "WHO chart value first",
    "sector_balanced": "Sector-balanced",
    "seeded_random": "Seeded random",
}
COLORS = {
    "chart_descending": "#087f8c",
    "sector_balanced": "#49b3aa",
    "seeded_random": "#9aa9b6",
}
DISPLAY_RISK_BANDS = ("<5%", "5% to <10%", "10% to <20%", "20% to <30%", "≥30%")


def _display_risk_band(value: str) -> str:
    return "≥30%" if value in {"≥30%", "â‰¥30%"} else value


def _selections(cohort: list[dict], capacity: int, seed: int) -> dict[str, list[dict]]:
    return {
        "chart_descending": choose_by_chart(cohort, capacity),
        "sector_balanced": choose_by_sector(cohort, capacity),
        "seeded_random": choose_random(cohort, capacity, seed),
    }


def _gap(values: list[float]) -> float:
    return round(max(values) - min(values), 2) if values else 0.0


def _group_gaps(cohort: list[dict], selected: list[dict], field: str, labels: tuple[str, ...]) -> tuple[float, float]:
    selection_rates: list[float] = []
    high_capture_rates: list[float] = []
    for label in labels:
        group = [row for row in cohort if row[field] == label]
        group_selected = [row for row in selected if row[field] == label]
        group_high = [row for row in group if row["who_chart_value_percent"] >= REFERENCE_THRESHOLD]
        selected_high = [row for row in group_selected if row["who_chart_value_percent"] >= REFERENCE_THRESHOLD]
        if group:
            selection_rates.append(100 * len(group_selected) / len(group))
        if group_high:
            high_capture_rates.append(100 * len(selected_high) / len(group_high))
    return _gap(selection_rates), _gap(high_capture_rates)


def calculate_run(cohort_size: int, capacity: int, seed: int) -> list[dict]:
    cohort = make_synthetic_cohort(cohort_size, seed)
    high_total = sum(row["who_chart_value_percent"] >= REFERENCE_THRESHOLD for row in cohort)
    rows: list[dict] = []
    for key, selected in _selections(cohort, capacity, seed).items():
        selected_high = sum(row["who_chart_value_percent"] >= REFERENCE_THRESHOLD for row in selected)
        sector_selection_gap, sector_high_capture_gap = _group_gaps(
            cohort, selected, "area", SIMULATED_AREAS
        )
        sex_selection_gap, sex_high_capture_gap = _group_gaps(
            cohort, selected, "sex_reference", ("female", "male")
        )
        rows.append({
            "seed": seed,
            "cohort_size": cohort_size,
            "capacity": capacity,
            "capacity_pct": round(100 * capacity / cohort_size, 2),
            "strategy": key,
            "priority_total": high_total,
            "priority_selected": selected_high,
            "priority_capture_pct": round(100 * selected_high / high_total, 2) if high_total else 0.0,
            "priority_yield_pct": round(100 * selected_high / capacity, 2),
            "mean_chart_value_pct": round(statistics.fmean(row["who_chart_value_percent"] for row in selected), 2),
            "sector_selection_gap_pp": sector_selection_gap,
            "sector_priority_capture_gap_pp": sector_high_capture_gap,
            "sex_selection_gap_pp": sex_selection_gap,
            "sex_priority_capture_gap_pp": sex_high_capture_gap,
        })
    return rows


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min": round(min(values), 2),
        "median": round(statistics.median(values), 2),
        "mean": round(statistics.fmean(values), 2),
        "max": round(max(values), 2),
        "sd": round(statistics.pstdev(values), 2),
    }


def aggregate_stability(rows: list[dict]) -> list[dict]:
    metrics = (
        "priority_total", "priority_selected", "priority_capture_pct", "priority_yield_pct",
        "sector_selection_gap_pp", "sector_priority_capture_gap_pp",
        "sex_selection_gap_pp", "sex_priority_capture_gap_pp",
    )
    grouped: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["capacity"], row["strategy"]), []).append(row)
    output: list[dict] = []
    for capacity in sorted({key[0] for key in grouped}):
        for strategy in STRATEGY_KEYS:
            group = grouped[(capacity, strategy)]
            item: dict[str, object] = {
                "capacity": capacity,
                "capacity_pct": group[0]["capacity_pct"],
                "strategy": strategy,
                "runs": len(group),
            }
            for metric in metrics:
                for statistic, value in _summary([float(row[metric]) for row in group]).items():
                    item[f"{metric}_{statistic}"] = value
            output.append(item)
    return output


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _svg_start(width: int, height: int, title: str, subtitle: str) -> list[str]:
    safe_title = escape(title)
    safe_subtitle = escape(subtitle)
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{safe_title}</title>",
        '<rect width="100%" height="100%" fill="#ffffff" rx="16"/>',
        f'<text x="50" y="42" font-family="Arial" font-size="22" font-weight="700" fill="#10233f">{safe_title}</text>',
        f'<text x="50" y="66" font-family="Arial" font-size="13" fill="#58708d">{safe_subtitle}</text>',
    ]


def _svg_text(x: float, y: float, value: str, size: int = 12, color: str = "#334e68", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>'


def chart_risk_distribution(path: Path, cohort: list[dict], seed: int) -> None:
    counts = Counter(_display_risk_band(row["risk_category"]) for row in cohort)
    width, height = 900, 430
    lines = _svg_start(width, height, "Synthetic cohort by WHO chart category", f"Baseline seed {seed}; values are simulated, not prevalence estimates")
    left, top, chart_w, chart_h = 180, 105, 650, 250
    maximum = max(counts.values())
    for idx, category in enumerate(DISPLAY_RISK_BANDS):
        y = top + idx * 50
        bar_w = chart_w * counts[category] / maximum
        lines += [
            _svg_text(left - 15, y + 22, category, anchor="end"),
            f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="28" rx="7" fill="#168f91"/>',
            _svg_text(left + bar_w + 10, y + 20, f"{counts[category]} ({100*counts[category]/len(cohort):.1f}%)", 12, "#10233f"),
        ]
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def chart_capture(path: Path, baseline: list[dict], cohort_size: int, seed: int) -> None:
    width, height = 980, 500
    lines = _svg_start(width, height, "Priority-profile coverage under capacity constraints", f"Baseline seed {seed}; priority = WHO chart cell ≥10% (descriptive label only)")
    left, top, chart_w, chart_h = 80, 105, 820, 300
    for tick in range(0, 101, 20):
        y = top + chart_h - chart_h * tick / 100
        lines += [f'<line x1="{left}" y1="{y}" x2="{left+chart_w}" y2="{y}" stroke="#dce6ed"/>', _svg_text(left-10, y+4, str(tick), anchor="end")]
    capacities = sorted({row["capacity"] for row in baseline})
    for key in STRATEGY_KEYS:
        points = []
        for idx, capacity in enumerate(capacities):
            row = next(r for r in baseline if r["capacity"] == capacity and r["strategy"] == key)
            x = left + chart_w / 2 if len(capacities) == 1 else left + idx * chart_w / (len(capacities)-1)
            y = top + chart_h - chart_h * row["priority_capture_pct"] / 100
            points.append((x, y))
        lines.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{COLORS[key]}" stroke-width="4"/>')
        for x, y in points:
            lines.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{COLORS[key]}"/>')
    for idx, capacity in enumerate(capacities):
        x = left + chart_w / 2 if len(capacities) == 1 else left + idx * chart_w / (len(capacities)-1)
        lines.append(_svg_text(x, top+chart_h+28, f"{capacity} ({100*capacity/cohort_size:.1f}%)", anchor="middle"))
    for idx, key in enumerate(STRATEGY_KEYS):
        x = 170 + idx*265
        lines += [f'<rect x="{x}" y="452" width="18" height="4" fill="{COLORS[key]}"/>', _svg_text(x+26, 458, STRATEGY_LABELS[key])]
    lines += ['<text transform="translate(18 255) rotate(-90)" font-family="Arial" font-size="12" fill="#334e68" text-anchor="middle">Coverage (%)</text>', "</svg>"]
    path.write_text("\n".join(lines), encoding="utf-8")


def chart_stability(path: Path, stability: list[dict], seed_count: int) -> None:
    capacities = sorted({int(row["capacity"]) for row in stability})
    capacity = 45 if 45 in capacities else capacities[0]
    rows = [row for row in stability if row["capacity"] == capacity]
    width, height = 920, 440
    lines = _svg_start(width, height, f"Stability across {seed_count} synthetic cohorts", f"Priority coverage at {capacity} slots; whiskers show min–max, point shows median")
    left, top, chart_w = 220, 115, 610
    for tick in range(0, 61, 10):
        x = left + chart_w * tick / 60
        lines += [f'<line x1="{x}" y1="{top-20}" x2="{x}" y2="{top+210}" stroke="#e1e9ef"/>', _svg_text(x, top+235, str(tick), anchor="middle")]
    for idx, row in enumerate(rows):
        y = top + idx*75
        low = left + chart_w * float(row["priority_capture_pct_min"]) / 60
        high = left + chart_w * float(row["priority_capture_pct_max"]) / 60
        med = left + chart_w * float(row["priority_capture_pct_median"]) / 60
        key = str(row["strategy"])
        lines += [
            _svg_text(left-20, y+5, STRATEGY_LABELS[key], anchor="end"),
            f'<line x1="{low}" y1="{y}" x2="{high}" y2="{y}" stroke="{COLORS[key]}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{med}" cy="{y}" r="7" fill="#10233f"/>',
            _svg_text(high+12, y+5, f'{row["priority_capture_pct_min"]:.2f}–{row["priority_capture_pct_max"]:.2f}%'),
        ]
    lines += [_svg_text(left+chart_w/2, 395, "Priority-profile coverage (%)", anchor="middle"), "</svg>"]
    path.write_text("\n".join(lines), encoding="utf-8")


def chart_gaps(path: Path, baseline: list[dict]) -> None:
    capacities = sorted({int(row["capacity"]) for row in baseline})
    capacity = 45 if 45 in capacities else capacities[0]
    rows = [row for row in baseline if row["capacity"] == capacity]
    width, height = 940, 470
    lines = _svg_start(width, height, f"Descriptive selection-rate gaps at {capacity} slots", "Percentage-point gaps on the baseline synthetic cohort; not a fairness certification")
    left, top, chart_w = 240, 115, 600
    for idx, row in enumerate(rows):
        y = top + idx*95
        key = row["strategy"]
        sector = float(row["sector_selection_gap_pp"])
        sex = float(row["sex_selection_gap_pp"])
        lines += [
            _svg_text(left-20, y+18, STRATEGY_LABELS[key], anchor="end"),
            f'<rect x="{left}" y="{y}" width="{sector*25:.1f}" height="24" rx="5" fill="#168f91"/>',
            _svg_text(left+sector*25+8, y+17, f"Sector {sector:.2f} pp"),
            f'<rect x="{left}" y="{y+34}" width="{sex*25:.1f}" height="24" rx="5" fill="#86a8b7"/>',
            _svg_text(left+sex*25+8, y+51, f"Reference sex {sex:.2f} pp"),
        ]
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def run(output_dir: Path, cohort_size: int, capacities: tuple[int, ...], seeds: tuple[int, ...]) -> dict:
    if not capacities or any(capacity < 1 or capacity > cohort_size for capacity in capacities):
        raise ValueError("capacities must be between 1 and cohort_size")
    if not seeds:
        raise ValueError("at least one seed is required")
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = output_dir / "figures"
    figures.mkdir(exist_ok=True)

    all_rows = [row for seed in seeds for capacity in capacities for row in calculate_run(cohort_size, capacity, seed)]
    baseline = [row for row in all_rows if row["seed"] == seeds[0]]
    stability = aggregate_stability(all_rows)
    cohort = make_synthetic_cohort(cohort_size, seeds[0])
    risk_counts = Counter(_display_risk_band(row["risk_category"]) for row in cohort)
    risk_rows = [{
        "seed": seeds[0], "cohort_size": cohort_size, "risk_category": category,
        "count": risk_counts[category], "percentage": round(100*risk_counts[category]/cohort_size, 2),
    } for category in DISPLAY_RISK_BANDS]

    files = {
        "risk_distribution": output_dir / "risk_distribution.csv",
        "baseline_capacity_results": output_dir / "baseline_capacity_results.csv",
        "all_seed_runs": output_dir / "all_seed_runs.csv",
        "stability_summary": output_dir / "stability_summary.csv",
    }
    _write_csv(files["risk_distribution"], risk_rows)
    _write_csv(files["baseline_capacity_results"], baseline)
    _write_csv(files["all_seed_runs"], all_rows)
    _write_csv(files["stability_summary"], stability)
    figure_files = {
        "figure_risk_distribution": figures / "risk_distribution.svg",
        "figure_coverage_by_capacity": figures / "coverage_by_capacity.svg",
        "figure_stability": figures / "stability_45_slots.svg",
        "figure_selection_gaps": figures / "selection_gaps_45_slots.svg",
    }
    chart_risk_distribution(figure_files["figure_risk_distribution"], cohort, seeds[0])
    chart_capture(figure_files["figure_coverage_by_capacity"], baseline, cohort_size, seeds[0])
    chart_stability(figure_files["figure_stability"], stability, len(seeds))
    chart_gaps(figure_files["figure_selection_gaps"], baseline)
    files.update(figure_files)

    manifest = {
        "analysis": "PREVIA synthetic health-impact demonstration",
        "schema_version": "1.0.0",
        "configuration": {
            "cohort_size": cohort_size,
            "capacities": list(capacities),
            "seeds": list(seeds),
            "baseline_seed": seeds[0],
            "priority_definition": f"WHO chart-cell value >= {REFERENCE_THRESHOLD}%",
            "strategies": list(STRATEGY_KEYS),
        },
        "scientific_boundaries": [
            "All profiles, sectors and results are synthetic.",
            "The priority label is descriptive and is not a referral threshold.",
            "Chart-based coverage is circular for the chart-ranked strategy and is not independent clinical validation.",
            "No diagnostic accuracy, prevalence, health outcome, event prevention or causal benefit is estimated.",
            "WHO chart lookup, NHANES HbA1c model, SHAP explanations and allocation simulation remain separate components.",
        ],
        "cohort_sha256": hashlib.sha256(json.dumps(cohort, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "files": {
            name: {"path": path.relative_to(output_dir).as_posix(), "sha256": _sha256(path)}
            for name, path in files.items()
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "health-impact" / "results")
    parser.add_argument("--cohort-size", type=int, default=240)
    parser.add_argument("--capacities", type=int, nargs="+", default=list(DEFAULT_CAPACITIES))
    parser.add_argument("--seed-start", type=int, default=DEFAULT_SEEDS[0])
    parser.add_argument("--seed-count", type=int, default=len(DEFAULT_SEEDS))
    args = parser.parse_args()
    if args.seed_count < 1:
        parser.error("--seed-count must be positive")
    manifest = run(args.output_dir, args.cohort_size, tuple(args.capacities), tuple(range(args.seed_start, args.seed_start + args.seed_count)))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
