"use client";

import { useCallback, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";

type Correction = {
  age_start: number;
  quadrant: string;
  sbp_band: string;
  bmi_band: string;
  was: number;
  is: number;
};
type ChartCheck = {
  source: string;
  cells_compared: number;
  cells_matching: number;
  mismatches: Array<{ age_start: number; quadrant: string; expected_pdf_text: number; actual_implementation: number }>;
  text_cross_check_passed: boolean;
  visual_cell_by_cell_verification: boolean;
  clinical_validation: boolean;
  method: string;
  scope_notice: string;
  text_transcription_sha256: string;
  corrections_v06: Correction[];
};
type Aggregate = {
  dataset: string;
  adults_40_to_74_unweighted_n: number;
  complete_primary_prevention_inputs_n: number;
  complete_input_share_pct_unweighted: number | null;
  source_join_matches_n: Record<string, number>;
  field_quality_unweighted_n: Record<string, number>;
  complete_input_counts_by_sex_n: Record<string, number>;
  download_sha256: Record<string, string>;
  limitations: string[];
};
type Evidence = {
  version: string;
  scope: string;
  who_pdf_text_verification: ChartCheck;
  public_dataset: {
    name: string;
    index: string;
    country: string;
    status: string;
    aggregate_report: Aggregate | null;
    download_command: string;
    domain_shift_warning: string;
  };
  claim_register: Array<{ claim: string; status: string; evidence: string }>;
};

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return <div className="metricTile"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>;
}
function saveReport(report: Evidence) {
  const contents = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(contents);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "PREVIA_v0.6_Evidence_Status.json";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export default function EvidencePage() {
  const [result, setResult] = useState<Evidence | null>(null);
  const [working, setWorking] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setWorking(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/v1/evidence/status`, { cache: "no-store" });
      if (!response.ok) throw new Error(`Evidence API responded ${response.status}`);
      setResult(await response.json() as Evidence);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Evidence API inaccessible.");
    } finally { setWorking(false); }
  }, []);

  useEffect(() => { void reload(); }, [reload]);
  const checks = result?.who_pdf_text_verification;
  const dataset = result?.public_dataset;
  const aggregate = dataset?.aggregate_report;

  return <main className="populationPage"><div className="shell">
    <header className="topbar">
      <div className="brand"><span className="brandmark">P</span>PREVIA <span className="lighter">Health AI</span></div>
      <nav className="topnav" aria-label="PREVIA modules">
        <a className="navlink" href="/">Individual screening</a>
        <a className="navlink" href="/population">Population intelligence</a>
        <a className="navlink" href="/prioritization">Strategy comparison</a>
        <a className="navlink" href="/evaluation">Scientific audit</a>
        <a className="navlink active" href="/evidence">External evidence</a><a className="navlink" href="/pathways">Prevention pathway</a>
      <a className="navlink" href="/ai">ML + XAI + RAG</a></nav>
    </header>

    <div className="popHero"><div>
      <div className="eyebrow">SOURCE INTEGRITY · PUBLIC DATA · MODULE 06</div>
      <h1>Validate the source.<br/><span>Respect the evidence.</span></h1>
      <p>A complete digital text cross-check of the WHO reference grid and a separate public-data input-quality pipeline — without pretending a US cross-sectional survey validates cardiovascular outcomes in Western Africa.</p>
    </div><div className="demoTag"><span>● TRANSPARENT EVIDENCE</span>
      <p>Research engineering only. No clinical calibration or prediction-performance claim.</p></div></div>

    {error && <section className="insightCard" role="alert"><h3>Unable to load scientific evidence</h3>
      <p>{error}</p><p>Check FastAPI at <code>{API}</code>.</p>
      <button type="button" className="evidenceRefresh" onClick={() => void reload()}>Retry API request</button></section>}

    {!result && !error && <section className="insightCard"><h3>{working ? "Checking scientific sources…" : "No result available"}</h3></section>}

    {result && checks && dataset && <>
      <div className="metricGrid evidenceMetrics">
        <Metric label="WHO PDF text-layer match" value={`${checks.cells_matching}/${checks.cells_compared}`} note="Digital values; visual audit still outstanding"/>
        <Metric label="Transcription mismatches" value={`${checks.mismatches.length}`} note="Two legacy discrepancies corrected in v0.6"/>
        <Metric label="CDC NHANES public survey" value={aggregate ? "Loaded" : "Pending"} note={aggregate ? "Aggregate-only input completeness" : "Not downloaded on this computer"}/>
        <Metric label="Predictive clinical validation" value="Not done" note="No appropriate 10-year event follow-up"/>
      </div>

      <div className="evidenceLayout">
        <section className="insightCard evidenceSource">
          <div className="evidenceHeader"><span className="eyebrow">SOURCE QUALITY 01</span>
            <span className={`evidenceTag ${checks.text_cross_check_passed ? "ok" : "bad"}`}>
              {checks.text_cross_check_passed ? "ALL TEXT CELLS MATCH" : "DISCREPANCIES FOUND"}
            </span></div>
          <h2>WHO 2019 non-laboratory chart</h2>
          <p>The 700 application cells were compared with a second transcription from the official PDF text layer. This catches data-entry differences but does not independently establish the correctness of the text extraction or replace clinical validation.</p>
          <div className="evidenceFact"><b>{checks.cells_matching}</b><span>matched reference text cells</span></div>
          <h3>Two transcription issues corrected in v0.6</h3>
          <div className="tableScroll"><table className="popTable">
            <thead><tr><th>Age</th><th>Reference group</th><th>SBP</th><th>BMI</th><th>Before</th><th>Corrected</th></tr></thead>
            <tbody>{checks.corrections_v06.map((item, index) => <tr key={index}>
              <td>{item.age_start}–{item.age_start + 4}</td><td>{item.quadrant}</td><td>{item.sbp_band}</td>
              <td>{item.bmi_band}</td><td>{item.was}%</td><td><b>{item.is}%</b></td>
            </tr>)}</tbody>
          </table></div>
          <p className="scope-note">MN = male non-smoker; MS = male smoker; FN = female non-smoker; FS = female smoker. These are chart-specific reference categories.</p>
          <a href={checks.source} target="_blank" rel="noreferrer" className="evidenceLink">Read the official WHO PDF ↗</a>
        </section>

        <section className="insightCard evidenceSource">
          <div className="evidenceHeader"><span className="eyebrow">EXTERNAL DATA 02</span>
            <span className={`evidenceTag ${aggregate ? "ok" : "pending"}`}>
              {aggregate ? "INPUT QA READY" : "NOT YET LOADED"}
            </span></div>
          <h2>Public CDC NHANES 2017–2018</h2>
          <p>Public-use surveys can test whether PREVIA's expected input fields are available and complete in real observational records. They cannot validate WHO's region-specific 10-year risk estimates for Togo.</p>
          {aggregate ? <>
            <div className="evidencePairs">
              <div><small>US adults aged 40–74 · unweighted</small><strong>{aggregate.adults_40_to_74_unweighted_n.toLocaleString("en-US")}</strong></div>
              <div><small>Complete eligibility inputs · unweighted</small><strong>{aggregate.complete_primary_prevention_inputs_n.toLocaleString("en-US")}</strong></div>
              <div><small>Input completeness · unweighted</small><strong>{aggregate.complete_input_share_pct_unweighted?.toFixed(2) ?? "N/A"}%</strong></div>
            </div>
            <h3>Core field completeness</h3>
            <div className="evidenceFieldList">{["sex_recorded", "bmi_usable", "systolic_bp_usable", "current_smoking_classifiable", "cvd_history_classifiable"].map(name => {
              const n = aggregate.field_quality_unweighted_n[`${name}_present`] ?? 0;
              const pct = aggregate.adults_40_to_74_unweighted_n > 0 ? 100 * n / aggregate.adults_40_to_74_unweighted_n : 0;
              return <div className="evidenceField" key={name}>
                <div><span>{name.replace(/_/g, " ")}</span><b>{n} / {aggregate.adults_40_to_74_unweighted_n}</b></div>
                <div className="bartrack"><div className="barfill" style={{ width: `${pct}%`, background: "#0d7987" }} /></div>
              </div>;
            })}</div>
          </> : <>
            <p className="evidencePending">No NHANES figures are displayed until the original five public CDC XPT files have been downloaded and checked on your computer.</p>
            <p className="scope-note">From the PREVIA project root, run this PowerShell command (the script saves aggregated statistics only):</p>
            <code className="evidenceCommand">{dataset.download_command}</code>
          </>}
          <div className="evidenceActions"><button type="button" onClick={() => void reload()} className="evidenceRefresh" disabled={working}>
            {working ? "Refreshing…" : "Refresh data status"}<span>↻</span>
          </button></div>
          <a href={dataset.index} target="_blank" rel="noreferrer" className="evidenceLink">CDC official dataset index ↗</a>
        </section>
      </div>

      <section className="insightCard evidenceClaims"><div className="evidenceHeader"><div><div className="eyebrow">CLAIM REGISTER</div><h2>What we can and cannot demonstrate</h2></div>
        <button type="button" className="evidenceRefresh" onClick={() => saveReport(result)}>Export evidence JSON ↓</button></div>
        <div className="tableScroll"><table className="popTable">
          <thead><tr><th>Scientific claim</th><th>Status</th><th>What supports it</th></tr></thead>
          <tbody>{result.claim_register.map(item => <tr key={item.claim}>
            <td><b>{item.claim}</b></td><td>{item.status}</td><td>{item.evidence}</td>
          </tr>)}</tbody>
        </table></div>
        <p className="scope-note">All NHANES findings are unweighted quality diagnostics, not prevalence or outcome estimates. Source PDF text transcription SHA-256: <code>{checks.text_transcription_sha256}</code>.</p>
      </section>
    </>}
    <footer>PREVIA Health AI · v0.8 · Research prototype · No medical records ingested by the web application · Not for clinical use.</footer>
  </div></main>;
}
