"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "../i18n/I18nProvider";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";
const COUNTRIES = [
  "Benin", "Burkina Faso", "Cabo Verde", "Cameroon", "Chad", "Cote d'Ivoire", "Gambia",
  "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria",
  "Sao Tome and Principe", "Senegal", "Sierra Leone", "Togo",
];

type Range = { minimum: number; median: number; maximum: number };
type AuditCheck = { name: string; passed: boolean; detail: string };
type Group = { label: string; population_count: number; high_reference_count: number;
  selected_count: number; high_reference_selected: number;
  high_reference_capture_pct: number | null; selection_rate_pct: number | null; };
type StrategyKey = "chart_descending" | "sector_balanced" | "seeded_random";
type Strategy = {
  key: StrategyKey; selected_count: number; high_reference_selected: number;
  high_reference_capture_pct: number; high_reference_yield_pct: number;
  sector_selection_gap_pp: number; sex_reference_selection_gap_pp: number;
  sector_high_coverage: Group[]; sex_reference_high_coverage: Group[];
  decision_rule: string; note: string; selected_ids_sha256: string;
};
type Sensitivity = { key: StrategyKey; capture_pct: Range; reference_sex_gap_pp: Range;
  sector_gap_pp: Range; high_reference_selected: Range };
type CapacityPoint = { slots: number; share_of_cohort_pct: number;
  higher_reference_total: number; chart_first_high_selected: number;
  sector_balanced_high_selected: number; random_high_selected: number };
type Audit = {
  data_type: string; version: string; country: string; region: string; source_url: string;
  cohort_size: number; outreach_capacity: number; seed: number; sensitivity_runs: number;
  reference_high_threshold_pct: number; simulated_high_reference_count: number;
  cohort_sha256: string;
  source_qa: { chart_cells: number; anchor_cells_compared: number; anchor_cells_matched: number;
    nondecreasing_bmi_rows: boolean; nonincreasing_risk_as_bp_drops: boolean;
    source_url: string; coverage_notice: string; status: string;
    pdf_text_cells_compared: number; pdf_text_cells_matched: number; pdf_text_layer_matches: boolean; visual_full_chart_check_completed: boolean };
  checks: AuditCheck[]; software_checks_passed: boolean;
  strategies: Strategy[]; sensitivity: Sensitivity[]; capacity_sensitivity: CapacityPoint[];
  conclusion: string; validation_status: string; limitations: string[];
};

const NAMES: Record<StrategyKey, string> = {
  chart_descending: "Highest WHO chart-cell first",
  sector_balanced: "Balanced by synthetic sector",
  seeded_random: "Seeded random baseline",
};

function Tile({ label, value, note }: { label: string; value: string; note: string }) {
  const { t } = useI18n();
  return (
    <div className="metricTile">
      <span>{t(label)}</span>
      <strong>{t(value)}</strong>
      <small>{t(note)}</small>
    </div>
  );
}

function RangeCell({ value }: { value: Range }) {
  const { formatNumber, t } = useI18n();
  return (
    <span title={t("Minimum · median · maximum over distinct synthetic seeds")} className="rangeCell">
      <b>{formatNumber(value.median, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</b>
      <small>[{formatNumber(value.minimum, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} – {formatNumber(value.maximum, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}]</small>
    </span>
  );
}

function Coverage({ title, rows }: { title: string; rows: Group[] }) {
  const { t, formatPercent } = useI18n();
  const pretty = (value: number | null) => value === null ? "N/A" : formatPercent(value);
  return (
    <section className="insightCard">
      <h3>{t(title)}</h3>
      <div className="barstack">
        {rows.map(group => (
          <div className="auditGroup" key={group.label}>
            <div className="auditGroupTitle">
              <b>{t(group.label)}</b>
              <span>
                {group.high_reference_selected}/{group.high_reference_count} {t("high-reference")} · {pretty(group.high_reference_capture_pct)}
              </span>
            </div>
            <div className="bartrack">
              <div
                className="barfill"
                style={{ width: `${group.high_reference_capture_pct ?? 0}%`, background: "#0b7987" }}
              />
            </div>
            <small>{group.selected_count}/{group.population_count} {t("total selected")} · {t("selection rate")} {pretty(group.selection_rate_pct)}</small>
          </div>
        ))}
      </div>
      <p className="scope-note">{t("N/A means there are no high-reference profiles in that subgroup. These are not observed patient outcomes.")}</p>
    </section>
  );
}

export default function EvaluationPage() {
  const { t, formatPercent } = useI18n();
  const [country, setCountry] = useState("Togo");
  const [size, setSize] = useState(240);
  const [capacity, setCapacity] = useState(45);
  const [seed, setSeed] = useState(2026);
  const [runs, setRuns] = useState(12);
  const [chosen, setChosen] = useState<StrategyKey>("chart_descending");
  const [result, setResult] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const runAudit = useCallback(async (data: { country: string; size: number; capacity: number; seed: number; runs: number }) => {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/api/v1/evaluation/audit`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country: data.country, cohort_size: data.size,
          outreach_capacity: data.capacity, seed: data.seed, sensitivity_runs: data.runs }),
      });
      if (!response.ok) {
        let hint = "";
        try { hint = JSON.stringify(await response.json()).slice(0, 450); } catch { /* ignore invalid body */ }
        throw new Error(`Audit API ${response.status}. ${hint}`);
      }
      setResult(await response.json() as Audit);
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "The PREVIA API is unreachable.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void runAudit({ country: "Togo", size: 240, capacity: 45, seed: 2026, runs: 12 }); }, [runAudit]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); void runAudit({ country, size, capacity, seed, runs });
  };
  const selected = result?.strategies.find(strategy => strategy.key === chosen);

  const exportReport = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `PREVIA_Research_Audit_v0.6_seed-${result.seed}.json`;
    document.body.appendChild(link);
    link.click(); link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="populationPage">
      <div className="shell">
        <header className="topbar">
          <div className="brand"><span className="brandmark">P</span> PREVIA <span className="lighter">Health AI</span></div>
          <nav className="topnav" aria-label={t("PREVIA modules")}>
            <a className="navlink" href="/">{t("Individual screening")}</a>
            <a className="navlink" href="/population">{t("Population intelligence")}</a>
            <a className="navlink" href="/prioritization">{t("Strategy comparison")}</a>
            <a className="navlink active" href="/evaluation">{t("Scientific audit")}</a>
            <a className="navlink" href="/evidence">{t("External evidence")}</a>
            <a className="navlink" href="/pathways">{t("Prevention pathway")}</a>
            <a className="navlink" href="/ai">{t("ML + XAI + RAG")}</a>
          </nav>
        </header>
        <div className="popHero">
          <div>
            <div className="eyebrow">{t("SCIENTIFIC TRANSPARENCY · MODULE 05")}</div>
            <h1>{t("Test every assumption.")}<br /><span>{t("Report what is proven.")}</span></h1>
            <p>{t("Reproducibility, integrity checks, chart-reference spot checks and sensitivity across synthetic cohorts. Not a clinical-validation study.")}</p>
          </div>
          <div className="demoTag">
            <span>● {t("RESEARCH SOFTWARE QA")}</span>
            <p>{t("No medical records or health outcomes. All cohorts are simulated.")}</p>
          </div>
        </div>

        <div className="scenarioLayout">
          <section className="panel scenarioSettings">
            <div className="panelhead">
              <h2>{t("Audit settings")}</h2>
              <span className="stepchip">{t("Reproducible")}</span>
            </div>
            <form onSubmit={submit} className="scenarioForm">
              <label>{t("WHO reference country")}
                <select value={country} onChange={e => setCountry(e.target.value)}>
                  {COUNTRIES.map(value => <option value={value} key={value}>{t(value)}</option>)}
                </select>
              </label>
              <label>{t("Synthetic profiles")}
                <input type="number" min={40} max={500} value={size} onChange={e => setSize(Number(e.target.value))} required />
              </label>
              <label>{t("Demo screening slots")}
                <input type="number" min={1} max={size} value={capacity} onChange={e => setCapacity(Number(e.target.value))} required />
              </label>
              <label>{t("Starting seed")}
                <input type="number" min={0} max={1000000} value={seed} onChange={e => setSeed(Number(e.target.value))} required />
              </label>
              <label>{t("Sensitivity runs")}
                <input type="number" min={3} max={25} value={runs} onChange={e => setRuns(Number(e.target.value))} required />
              </label>
              <button type="submit" disabled={loading}>
                {loading ? t("Running research QA…") : t("Run scientific QA audit")}
                <span>→</span>
              </button>
            </form>
            <p className="scope-note">{t("The same cohort is shared by all three methods for a given seed. Repeated seeds create new fictitious cohorts; ranges are not population confidence intervals.")}</p>
          </section>
          <div className="resultArea" aria-live="polite">
            {error ? (
              <div className="panel result error" role="alert">
                <b>{t("Audit failed")}</b>
                <p>{t(error)}</p>
                <p>{t("Check FastAPI on port 8765 and frontend API setting ")}{API}.</p>
              </div>
            ) : !result ? (
              <section className="panel">
                <h2>{loading ? t("Evaluating simulation…") : t("No audit results")}</h2>
              </section>
            ) : (
              <>
                <div className="metricGrid">
                  <Tile label="Software checks" value={`${result.checks.filter(c => c.passed).length}/${result.checks.length}`} note="Verified internal invariants" />
                  <Tile label="WHO PDF text check" value={`${result.source_qa.pdf_text_cells_matched}/${result.source_qa.pdf_text_cells_compared}`} note="Full text-layer cross-check; not a visual clinical sign-off" />
                  <Tile label="Synthetic runs" value={String(result.sensitivity_runs)} note="Min · median · max" />
                  <Tile label="Clinical validation" value="Not done" note="Real outcomes unavailable" />
                </div>
                <section className="insightCard auditStatus">
                  <div className="auditStatusTop">
                    <div>
                      <span className="eyebrow">{t("VALIDATION STATUS")}</span>
                      <h2>{result.software_checks_passed ? t("Software QA passed") : t("Software checks failed")}</h2>
                      <p>{t(result.conclusion)}</p>
                    </div>
                    <span className={`stepchip ${result.software_checks_passed ? "" : "auditFailed"}`}>
                      {result.software_checks_passed ? t("RESEARCH ONLY") : t("CHECK FAILURES")}
                    </span>
                  </div>
                  <div className="auditActions">
                    <button type="button" className="auditExport" onClick={exportReport}>
                      {t("Export full audit JSON")} <span>↓</span>
                    </button>
                  </div>
                </section>
                <section className="insightCard auditChecks">
                  <h3>{t("Reproducible integrity checks")}</h3>
                  <div className="auditChecksGrid">
                    {result.checks.map(check => (
                      <div className="auditCheck" key={check.name}>
                        <span aria-label={t(check.passed ? "Passed" : "Failed")}>{check.passed ? "✓" : "!"}</span>
                        <div>
                          <b>{t(check.name)}</b>
                          <small>{t(check.detail)}</small>
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="scope-note">
                    {t("WHO chart integrity:")} {result.source_qa.chart_cells} {t("digital cells,")} {result.source_qa.pdf_text_cells_matched} {t("text matches.")} {t(result.source_qa.coverage_notice)}
                  </p>
                </section>
              </>
            )}
          </div>
        </div>

        {result && (
          <>
            <section className="panel auditSection">
              <div className="panelhead">
                <div>
                  <span className="eyebrow">{t("SENSITIVITY STUDY")}</span>
                  <h2>{t("How results change across synthetic seeds")}</h2>
                </div>
                <span className="stepchip">{result.sensitivity_runs} {t("scenarios")}</span>
              </div>
              <p className="scope-note">{t("Median in bold; [minimum – maximum] beneath. Only simulated variation is shown. No statistical confidence interval or clinical performance is inferred.")}</p>
              <div className="tableScroll">
                <table className="popTable auditTable">
                  <thead>
                    <tr>
                      <th>{t("Strategy")}</th>
                      <th>{t("Chart ≥10% capture (%)")}</th>
                      <th>{t("Sector gap (pp)")}</th>
                      <th>{t("Reference-sex gap (pp)")}</th>
                      <th>{t("Selected high-category (n)")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.sensitivity.map(item => (
                      <tr key={item.key}>
                        <td><b>{t(NAMES[item.key])}</b></td>
                        <td><RangeCell value={item.capture_pct}/></td>
                        <td><RangeCell value={item.sector_gap_pp}/></td>
                        <td><RangeCell value={item.reference_sex_gap_pp}/></td>
                        <td><RangeCell value={item.high_reference_selected}/></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="panel auditSection">
              <div className="panelhead">
                <div>
                  <span className="eyebrow">{t("CAPACITY SENSITIVITY")}</span>
                  <h2>{t("The result also depends on available slots")}</h2>
                </div>
              </div>
              <p className="scope-note">{t("The cohort remains unchanged. Only capacity changes. Counts mean artificial profiles in a WHO chart cell ≥10% selected under each rule.")}</p>
              <div className="tableScroll">
                <table className="popTable">
                  <thead>
                    <tr>
                      <th>{t("Slots")}</th>
                      <th>{t("% of cohort")}</th>
                      <th>{t("Highest chart first")}</th>
                      <th>{t("Balanced sectors")}</th>
                      <th>{t("Random baseline")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.capacity_sensitivity.map(p => (
                      <tr key={p.slots}>
                        <td><b>{p.slots}</b></td>
                        <td>{formatPercent(p.share_of_cohort_pct, 2)}</td>
                        <td>{p.chart_first_high_selected}/{p.higher_reference_total}</td>
                        <td>{p.sector_balanced_high_selected}/{p.higher_reference_total}</td>
                        <td>{p.random_high_selected}/{p.higher_reference_total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="panel auditSection">
              <div className="panelhead">
                <div>
                  <span className="eyebrow">{t("EXPLAINABILITY & SUBGROUPS")}</span>
                  <h2>{t("Why each strategy selects its profiles")}</h2>
                </div>
              </div>
              <div className="auditSelector" aria-label={t("Select strategy for explanation")}>
                {result.strategies.map(s => (
                  <button
                    type="button"
                    key={s.key}
                    aria-pressed={chosen === s.key}
                    className={chosen === s.key ? "auditChoice auditChoiceActive" : "auditChoice"}
                    onClick={() => setChosen(s.key)}
                  >
                    {t(NAMES[s.key])}
                  </button>
                ))}
              </div>
              {selected && (
                <>
                  <div className="auditReason">
                    <h3>{t(NAMES[selected.key])}</h3>
                    <p><b>{t("Rule:")}</b> {t(selected.decision_rule)}</p>
                    <p><b>{t("Interpretation:")}</b> {t(selected.note)}</p>
                    <p>
                      <b>{t("Selected:")}</b> {selected.selected_count} {t("synthetic IDs;")} {selected.high_reference_selected} {t("at chart ≥10%.")}{" "}
                      {t("Group capture uses the number of high-reference profiles within that same group as denominator.")}
                    </p>
                    <small><b>{t("Selected ID fingerprint:")}</b> <code>{selected.selected_ids_sha256}</code></small>
                  </div>
                  <div className="chartGrid priorityCharts">
                    <Coverage title="Chart-category capture by demo sector" rows={selected.sector_high_coverage}/>
                    <Coverage title="Chart-category capture by reference sex" rows={selected.sex_reference_high_coverage}/>
                  </div>
                </>
              )}
            </section>

            <section className="panel methodology auditSection">
              <span className="eyebrow">{t("REPRODUCIBILITY & SCIENTIFIC BOUNDARY")}</span>
              <h2>{t("What still needs scientific validation")}</h2>
              <p><b>{t("Dataset SHA-256:")}</b> <code className="auditHash">{result.cohort_sha256}</code></p>
              <ul>{result.limitations.map(item => <li key={item}>{t(item)}</li>)}</ul>
              <a href={result.source_url} target="_blank" rel="noreferrer">{t("Read the official WHO 2019 regional chart ↗")}</a>
            </section>
          </>
        )}
        <footer>{t("PREVIA Health AI · Research prototype v0.8 · Software QA ≠ clinical validation")}</footer>
      </div>
    </main>
  );
}
