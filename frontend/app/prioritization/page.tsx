"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "../i18n/I18nProvider";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";
const COUNTRIES = [
  "Benin", "Burkina Faso", "Cabo Verde", "Cameroon", "Chad", "Cote d'Ivoire", "Gambia",
  "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria",
  "Sao Tome and Principe", "Senegal", "Sierra Leone", "Togo",
];
const KEYS = ["chart_descending", "sector_balanced", "seeded_random"] as const;
type StrategyKey = typeof KEYS[number];
type SelectionRow = { group: string; population_count: number; selected_count: number; selection_rate_pct: number };
type DemoProfile = {
  synthetic_id: string; area: string; age_band: string; sex_reference: string;
  current_smoker: boolean; systolic_bp: number; bmi: number;
  who_chart_value_percent: number; risk_category: string;
};
type Strategy = {
  key: StrategyKey; label: string; explanation: string;
  selected_count: number; unselected_count: number; higher_reference_selected: number;
  higher_reference_capture_pct: number; higher_reference_yield_pct: number;
  average_chart_value_pct: number; sector_selection_gap_pp: number;
  sex_reference_selection_gap_pp: number;
  sector_selection: SelectionRow[]; sex_reference_selection: SelectionRow[];
  selected_synthetic_ids: string[]; example_profiles: DemoProfile[];
};
type Comparison = {
  data_type: string; country: string; region: string; source_url: string;
  cohort_size: number; outreach_capacity: number; seed: number;
  higher_reference_in_cohort: number; higher_reference_threshold_pct: number;
  strategies: Strategy[]; limitations: string[]; clinical_use: string;
};

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="metricTile"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>;
}

function RateBars({ title, rows }: { title: string; rows: SelectionRow[] }) {
  const { formatPercent } = useI18n();
  return <section className="insightCard"><h3>{title}</h3><div className="barstack">
    {rows.map(row => <div className="barline" key={row.group}>
      <span className="barlabel">{row.group}</span>
      <div className="bartrack" title={`${row.selected_count}/${row.population_count} selected`}>
        <div className="barfill" style={{ width: `${row.selection_rate_pct}%`, background: "#0d7988" }} />
      </div>
      <span className="barvalue">{formatPercent(row.selection_rate_pct, 2)}</span>
    </div>)}
  </div><p className="scope-note">Bar length shows the share of each synthetic subgroup selected, not disease prevalence.</p></section>;
}

export default function PrioritizationPage() {
  const { t, formatPercent } = useI18n();
  const [country, setCountry] = useState("Togo");
  const [size, setSize] = useState(240);
  const [capacity, setCapacity] = useState(45);
  const [seed, setSeed] = useState(2026);
  const [chosen, setChosen] = useState<StrategyKey>("chart_descending");
  const [result, setResult] = useState<Comparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const compare = useCallback(async (args: { country: string; size: number; capacity: number; seed: number }) => {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/api/v1/prioritization/compare`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country: args.country, cohort_size: args.size,
          outreach_capacity: args.capacity, seed: args.seed,
        }),
      });
      if (!response.ok) {
        throw new Error(response.status === 422
          ? "Invalid scenario: use 40–500 synthetic people and capacity no greater than cohort size."
          : `API returned status ${response.status}`);
      }
      setResult(await response.json() as Comparison);
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "The PREVIA API is unreachable.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void compare({ country: "Togo", size: 240, capacity: 45, seed: 2026 }); }, [compare]);
  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); void compare({ country, size, capacity, seed });
  };
  const active = result?.strategies.find(strategy => strategy.key === chosen);

  return <main className="populationPage"><div className="shell">
    <header className="topbar">
      <div className="brand"><span className="brandmark">P</span> PREVIA <span className="lighter">Health AI</span></div>
      <nav className="topnav" aria-label="PREVIA modules">
        <a className="navlink" href="/">Individual screening</a>
        <a className="navlink" href="/population">Population intelligence</a>
        <a className="navlink active" href="/prioritization">Strategy comparison</a>
        <a className="navlink" href="/evaluation">Scientific audit</a>
      <a className="navlink" href="/evidence">External evidence</a><a className="navlink" href="/pathways">Prevention pathway</a><a className="navlink" href="/ai">ML + XAI + RAG</a></nav>
    </header>
    <div className="popHero"><div>
      <div className="eyebrow">CAPACITY-BASED PLANNING · MODULE 04</div>
      <h1>Compare strategies.<br /><span>Make trade-offs visible.</span></h1>
      <p>Three reproducible ways to allocate limited demonstration slots to the same synthetic cohort.</p>
    </div><div className="demoTag"><span>● SYNTHETIC DATA ONLY</span><p>These are illustrative comparisons, not healthcare recommendations.</p></div></div>

    <div className="scenarioLayout">
      <section className="panel scenarioSettings"><div className="panelhead"><h2>Simulation settings</h2><span className="stepchip">Reproducible demo</span></div>
        <form onSubmit={onSubmit} className="scenarioForm">
          <label>WHO reference country <select value={country} onChange={e => setCountry(e.target.value)}>
            {COUNTRIES.map(value => <option key={value} value={value}>{value}</option>)}
          </select></label>
          <label>Synthetic profiles <input type="number" min={40} max={500} value={size} onChange={e => setSize(Number(e.target.value))} required /></label>
          <label>Demonstration slots <input type="number" min={1} max={size} value={capacity} onChange={e => setCapacity(Number(e.target.value))} required /></label>
          <label>Reproducible seed <input type="number" min={0} max={1000000} value={seed} onChange={e => setSeed(Number(e.target.value))} required /></label>
          <button type="submit" disabled={loading}>{loading ? "Comparing…" : "Compare three strategies"}<span>→</span></button>
        </form>
        <p className="scope-note">The country changes the reference-region label, not the synthetic population. All three strategies run on identical records.</p>
      </section>
      <div className="resultArea" aria-live="polite">
        {error ? <div className="panel result error" role="alert"><b>Comparison failed</b><p>{t(error)}</p><p>Confirm FastAPI is running and the frontend API address is {API}.</p></div>
          : !result ? <section className="panel"><h2>{loading ? "Comparing artificial scenarios…" : "No scenario yet"}</h2></section>
            : <>
              <div className="metricGrid">
                <Metric label="Synthetic profiles" value={String(result.cohort_size)} detail="Artificial cohort" />
                <Metric label="Slots per strategy" value={String(result.outreach_capacity)} detail="Same capacity for every method" />
                <Metric label="WHO cells ≥10%" value={String(result.higher_reference_in_cohort)} detail="Synthetic comparison category" />
                <Metric label="Capacity used" value={formatPercent(100 * result.outreach_capacity / result.cohort_size, 0)} detail="Slots ÷ cohort size" />
              </div>
              <section className="compareIntro"><h2>Side-by-side comparison</h2><p>Choose a strategy to examine its subgroup selection rates and synthetic IDs. No approach is automatically recommended.</p></section>
              <div className="strategyGrid" aria-label="Strategies">
                {result.strategies.map(strategy => <button type="button" key={strategy.key}
                  className={`strategyCard ${chosen === strategy.key ? "strategyCardActive" : ""}`}
                  aria-pressed={chosen === strategy.key} onClick={() => setChosen(strategy.key)}>
                  <span className="strategyIndicator">{chosen === strategy.key ? "SELECTED FOR INSPECTION" : "INSPECT STRATEGY"}</span>
                  <strong>{strategy.label}</strong><small>{strategy.explanation}</small>
                  <div className="strategyFacts">
                    <div><span>Chart ≥10% captured</span><b>{formatPercent(strategy.higher_reference_capture_pct, 2)}</b></div>
                    <div><span>Of selected, chart ≥10%</span><b>{formatPercent(strategy.higher_reference_yield_pct, 2)}</b></div>
                    <div><span>Sector selection gap</span><b>{strategy.sector_selection_gap_pp} pp</b></div>
                    <div><span>Reference-sex gap</span><b>{strategy.sex_reference_selection_gap_pp} pp</b></div>
                  </div>
                </button>)}
              </div>
              <div className="comparisonCaveat"><b>Important interpretation:</b> Ranking by WHO chart value is expected to score well on a metric defined by that same chart. This is a comparison of selection rules, not evidence that one strategy prevents more disease.</div>
            </>}
      </div>
    </div>

    {result && active && <>
      <section className="panel priorityDetail">
        <div className="panelhead"><div><span className="eyebrow">STRATEGY EXPLORER</span><h2>{active.label}</h2></div><span className="stepchip">Not clinical triage</span></div>
        <div className="priorityStats">
          <div><span>Higher-chart-category profiles selected</span><strong>{active.higher_reference_selected} / {result.higher_reference_in_cohort}</strong></div>
          <div><span>Average chart-cell value among selected</span><strong>{formatPercent(active.average_chart_value_pct, 2)}</strong></div>
          <div><span>Selection rate gap across demo sectors</span><strong>{active.sector_selection_gap_pp} pp</strong></div>
        </div>
        <div className="chartGrid priorityCharts">
          <RateBars title="Selection rates by demonstration sector" rows={active.sector_selection} />
          <RateBars title="Selection rates by chart-reference sex" rows={active.sex_reference_selection} />
        </div>
      </section>
      <section className="panel queuePanel">
        <div className="panelhead"><div><span className="eyebrow">AUDITABLE DEMO</span><h2>Illustrative selected profiles</h2></div><span className="stepchip">First 8 shown</span></div>
        <p className="scope-note">The API also returns all {active.selected_count} fabricated selection IDs for reproducibility. These are not patients, referrals or appointments.</p>
        <div className="tableScroll"><table className="popTable"><thead><tr>
          <th>Synthetic ID</th><th>Demo sector</th><th>Age</th><th>Chart sex</th><th>Smoker</th><th>SBP</th><th>BMI</th><th>WHO cell</th>
        </tr></thead><tbody>{active.example_profiles.map(p => <tr key={p.synthetic_id}>
          <td><b>{p.synthetic_id}</b></td><td>{p.area}</td><td>{p.age_band}</td><td>{p.sex_reference}</td>
          <td>{p.current_smoker ? "Yes" : "No"}</td><td>{p.systolic_bp}</td><td>{p.bmi}</td>
          <td><span className="riskPill">{formatPercent(p.who_chart_value_percent, 0)}</span></td>
        </tr>)}</tbody></table></div>
      </section>
      <section className="panel methodology priorityLimits"><span className="eyebrow">DEFINITIONS & GUARDRAILS</span><h2>What these indicators mean</h2>
        <p><b>Chart-category capture:</b> among all artificial profiles with a WHO chart cell of 10% or more, the proportion selected. <b>Selected yield:</b> among selected profiles, the proportion in that same chart category.</p>
        <p><b>Sector / reference-sex gap:</b> highest subgroup selection rate minus the lowest, measured in percentage points. The metric alone cannot establish equitable healthcare.</p>
        <ul>{result.limitations.map(item => <li key={item}>{item}</li>)}</ul>
        <a href={result.source_url} target="_blank" rel="noreferrer">Read the original WHO 2019 reference chart ↗</a>
      </section>
    </>}
    <footer>PREVIA Health AI · Research prototype v0.8 · Synthetic data only · Not for clinical use</footer>
  </div></main>;
}
