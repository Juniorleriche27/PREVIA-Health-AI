"use client";
import { useState, type FormEvent } from "react";
import { useI18n } from "./i18n/I18nProvider";

type Result = {
  status: string;
  message: string;
  missing_fields?: string[];
  next_step: string;
  risk_score_percent: number | null;
  risk_category?: string | null;
  risk_horizon?: string | null;
  age_band?: string | null;
  bp_band?: string | null;
  bmi_band?: string | null;
  region?: string | null;
  source_url?: string | null;
  clinical_notice: string;
  data_storage: string;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";
const COUNTRIES = [
  "Benin", "Burkina Faso", "Cabo Verde", "Cameroon", "Chad", "Cote d'Ivoire", "Gambia", "Ghana", "Guinea",
  "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Sao Tome and Principe", "Senegal",
  "Sierra Leone", "Togo",
];

export default function Home() {
  const { t, formatPercent } = useI18n();
  const [age, setAge] = useState("52");
  const [sex, setSex] = useState("female");
  const [smoker, setSmoker] = useState("false");
  const [sbp, setSbp] = useState("128");
  const [bmi, setBmi] = useState("26.1");
  const [knownCvd, setKnownCvd] = useState("false");
  const [country, setCountry] = useState("");
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const mode = ((e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null)?.value === "who" ? "who" : "eligibility";
    setResult(null);
    setError("");
    if (mode === "who" && !country) {
      setError("Select the country where the WHO regional reference chart applies before calculating a chart value.");
      return;
    }
    setLoading(true);
    try {
      const endpoint = mode === "who" ? "who-cvd-risk" : "eligibility";
      const response = await fetch(`${API}/api/v1/screenings/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          age: Number(age), sex_used_by_chart: sex, current_smoker: smoker === "true",
          systolic_bp: sbp.trim() ? Number(sbp.replace(",", ".")) : null,
          bmi: bmi.trim() ? Number(bmi.replace(",", ".")) : null,
          known_cvd: knownCvd === "true", consent_for_demo_assessment: consent,
          ...(mode === "who" ? { country } : {}),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(response.status === 422 ? "Check the field values and try again." : `API error: ${response.status}`);
      setResult(data as Result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to contact the API.");
    } finally {
      setLoading(false);
    }
  }

  return <main>
    <div className="shell">
      <header className="topbar">
        <div className="brand"><span className="brandmark">P</span> PREVIA <span className="lighter">Health AI</span></div>
        <nav className="topnav" aria-label={t("PREVIA modules")}>
          <a className="navlink active" href="/">{t("Individual screening")}</a>
          <a className="navlink" href="/population">{t("Population intelligence")} →</a>
          <a className="navlink" href="/prioritization">{t("Strategy comparison")} →</a>
          <a className="navlink" href="/evaluation">{t("Scientific audit")} →</a>
          <a className="navlink" href="/evidence">{t("External evidence")}</a>
          <a className="navlink" href="/pathways">{t("Prevention pathway")}</a>
          <a className="navlink" href="/ai">{t("ML + XAI + RAG")}</a>
        </nav>
      </header>
      <section className="hero">
        <div className="eyebrow">{t("PRECISION PREVENTION & SCREENING")}</div>
        <h1>{t("Early insight.")}<br/><span>{t("Better next steps.")}</span></h1>
        <p>{t("Explore a transparent pathway for cardiovascular screening, without confusing a preliminary assessment with a diagnosis.")}</p>
      </section>
      <div className="workspace">
        <section className="panel">
          <div className="panelhead">
            <div><span className="eyebrow">{t("STEP 01")}</span><h2>{t("Screening intake")}</h2></div>
            <span className="stepchip">{t("Demo only")}</span>
          </div>
          <form onSubmit={submit}>
            <div className="fields">
              <label>{t("Age (years)")}<input type="number" min="18" max="110" value={age} onChange={e => setAge(e.target.value)} required/></label>
              <label>{t("Chart reference sex")}
                <select value={sex} onChange={e => setSex(e.target.value)}>
                  <option value="female">{t("Female")}</option>
                  <option value="male">{t("Male")}</option>
                  <option value="not_provided">{t("Not provided")}</option>
                </select>
              </label>
              <label>{t("Current smoking")}
                <select value={smoker} onChange={e => setSmoker(e.target.value)}>
                  <option value="false">{t("No")}</option>
                  <option value="true">{t("Yes")}</option>
                </select>
              </label>
              <label>{t("Systolic pressure (mmHg)")}<input type="number" min="60" max="300" value={sbp} onChange={e => setSbp(e.target.value)} placeholder={t("e.g. 128")}/></label>
              <label>{t("Body mass index (BMI)")}<input type="number" min="10" max="80" step="0.1" value={bmi} onChange={e => setBmi(e.target.value)} placeholder={t("e.g. 26.1")}/></label>
              <label>{t("Existing cardiovascular disease")}
                <select value={knownCvd} onChange={e => setKnownCvd(e.target.value)}>
                  <option value="false">{t("No")}</option>
                  <option value="true">{t("Yes")}</option>
                </select>
              </label>
              <label className="wide">{t("Country for WHO reference chart")}
                <select value={country} onChange={e=>setCountry(e.target.value)}>
                  <option value="">{t("Select a country in Western Sub-Saharan Africa")}</option>
                  {COUNTRIES.map(c=><option key={c} value={c}>{t(c)}</option>)}
                </select>
              </label>
            </div>
            <p className="scope-note">{t("This prototype currently supports only the WHO Western Sub-Saharan Africa chart. Countries outside this region need a different chart.")}</p>
            <label className="consent">
              <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}/>
              <span>{t("I understand this is a research demonstration and consent to processing these inputs for a single assessment. No information is stored by the demo API. I will not use the result for diagnosis or treatment.")}</span>
            </label>
            <div className="actions">
              <button type="submit" value="eligibility" className="secondarybutton" disabled={loading}>{t("Check screening readiness")}</button>
              <button type="submit" value="who" disabled={loading}>{loading ? t("Reviewing inputs…") : t("Estimate WHO chart risk")}<span aria-hidden="true">→</span></button>
            </div>
          </form>
        </section>
        <aside className="panel output">
          <span className="eyebrow">{t("STEP 02")}</span>
          <h2>{t("Assessment outcome")}</h2>
          {error ? <div className="result error" role="alert">{t(error)}</div> : result ? <div className="result" aria-live="polite">
            <span className="status">{t(result.status.replaceAll("_", " "))}</span>
            {result.risk_score_percent !== null ? (
              <div className="riskmetric">
                <strong>{formatPercent(result.risk_score_percent, 0)}</strong>
                <div>{t("WHO 2019 chart cell")}<br/><b>{t(result.risk_category || "")}</b> {t("reference category")}</div>
              </div>
            ) : null}
            <h3>{t(result.message)}</h3>
            {result.risk_score_percent !== null && result.region ? (
              <div className="riskmeta">
                <p><b>{t("Region:")}</b> {t(result.region)}</p>
                <p><b>{t("Age band:")}</b> {t(result.age_band || "")}</p>
                <p><b>{t("SBP band:")}</b> {t(result.bp_band || "")} mmHg</p>
                <p><b>{t("BMI band:")}</b> {t(result.bmi_band || "")} kg/m²</p>
                <p><b>{t("Horizon:")}</b> {t(result.risk_horizon || "")}</p>
                {result.source_url ? <p><a href={result.source_url} target="_blank" rel="noreferrer">{t("Open original WHO chart")}</a></p> : null}
              </div>
            ) : null}
            <p><b>{t("Next step:")}</b> {t(result.next_step)}</p>
            {result.missing_fields?.length ? <p><b>{t("Missing inputs:")}</b> {result.missing_fields.map(f => t(f)).join(", ")}</p> : null}
            <p className="muted">{t(result.clinical_notice)}</p>
          </div> : (
            <div className="placeholder">
              <div className="circles"><span/><span/><span/></div>
              <h3>{t("Ready when you are.")}</h3>
              <p>{t("Check input completeness or view an educational WHO 2019 regional risk-chart lookup. Not a diagnosis.")}</p>
            </div>
          )}
          <div className="footnote">
            <b>{t("Scientific boundary")}</b>
            <p>{t("Chart values are rounded, grouped reference estimates and may not be accurate for an individual. Not validated for clinical use; qualified medical oversight is required.")}</p>
          </div>
        </aside>
      </div>
      <footer>{t("Future Health Digital Innovation Challenge 2026 · Independent prototype · Not for clinical use.")}</footer>
    </div>
  </main>;
}
