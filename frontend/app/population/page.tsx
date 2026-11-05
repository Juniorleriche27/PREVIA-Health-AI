"use client";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "../i18n/I18nProvider";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";
const SOURCE = "https://www.who.int/docs/default-source/cardiovascular-diseases/western-sub-saharan-africa.pdf";
const COUNTRIES = ["Benin","Burkina Faso","Cabo Verde","Cameroon","Chad","Cote d'Ivoire","Gambia","Ghana","Guinea","Guinea-Bissau","Liberia","Mali","Mauritania","Niger","Nigeria","Sao Tome and Principe","Senegal","Sierra Leone","Togo"];
const BAND_COLORS = ["#137d75", "#8bb65b", "#e6ab41", "#dc7445", "#a94353"];

type CategoryCount = {category:string;count:number;percentage:number};
type ExampleProfile = {synthetic_id:string;area:string;age_band:string;sex_reference:string;current_smoker:boolean;systolic_bp:number;bmi:number;who_chart_value_percent:number;risk_category:string};
type ScenarioResult = {
  data_type:string; clinical_use:string; message:string; country:string; region:string; source_url:string;
  cohort_size:number; outreach_capacity:number; selected_for_demo:number; unselected_for_demo:number;
  higher_chart_category_count:number; higher_chart_category_share:number;
  risk_distribution:CategoryCount[];age_distribution:CategoryCount[];area_distribution:CategoryCount[];
  sex_reference_distribution:CategoryCount[]; demonstration_queue:ExampleProfile[]; methodology:string[];
};

function BarGroup({title,rows,scheme="teal"}:{title:string;rows:CategoryCount[];scheme?:"teal"|"risk"}) {
  const { t, formatPercent } = useI18n();
  const max = Math.max(1, ...rows.map(r=>r.count));
  return (
    <section className="insightCard">
      <h3>{t(title)}</h3>
      <div className="barstack">
        {rows.map((row,i)=>(
          <div className="barline" key={row.category}>
            <span className="barlabel">{t(row.category)}</span>
            <div className="bartrack">
              <div className="barfill" style={{width:`${row.count / max * 100}%`,background:scheme==="risk"?BAND_COLORS[i]:"#117987"}}/>
            </div>
            <span className="barvalue">{row.count} <small>({formatPercent(row.percentage, 1)})</small></span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function PopulationPage(){
  const { t, formatPercent } = useI18n();
  const [country,setCountry]=useState("Togo");
  const [cohortSize,setCohortSize]=useState(240);
  const [capacity,setCapacity]=useState(45);
  const [seed,setSeed]=useState(2026);
  const [result,setResult]=useState<ScenarioResult|null>(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");

  const calculate=useCallback(async (params:{country:string;cohortSize:number;capacity:number;seed:number})=>{
    setLoading(true);setError("");
    try{
      const response=await fetch(`${API}/api/v1/population/scenario`,{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({country:params.country,cohort_size:params.cohortSize,outreach_capacity:params.capacity,seed:params.seed})
      });
      if(!response.ok)throw new Error(response.status===422?"Check that capacity does not exceed population size and that the country is supported.":`API response ${response.status}`);
      setResult(await response.json() as ScenarioResult);
    }catch(err){setError(err instanceof Error?err.message:"Unable to reach PREVIA API.");setResult(null);}
    finally{setLoading(false)}
  },[]);

  useEffect(()=>{void calculate({country:"Togo",cohortSize:240,capacity:45,seed:2026})},[calculate]);

  function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();
    void calculate({country,cohortSize,capacity,seed});
  }

  return (
    <main className="populationPage">
      <div className="shell">
        <header className="topbar">
          <div className="brand"><span className="brandmark">P</span> PREVIA <span className="lighter">Health AI</span></div>
          <nav className="topnav" aria-label={t("PREVIA modules")}>
            <a className="navlink" href="/">{t("Individual screening")}</a>
            <a className="navlink active" href="/population">{t("Population intelligence")}</a>
            <a className="navlink" href="/prioritization">{t("Strategy comparison")}</a>
            <a className="navlink" href="/evaluation">{t("Scientific audit")}</a>
            <a className="navlink" href="/evidence">{t("External evidence")}</a>
            <a className="navlink" href="/pathways">{t("Prevention pathway")}</a>
            <a className="navlink" href="/ai">{t("ML + XAI + RAG")}</a>
          </nav>
        </header>
        <div className="popHero">
          <div>
            <div className="eyebrow">{t("POPULATION HEALTH INTELLIGENCE · MODULE 03")}</div>
            <h1>{t("See the picture.")}<br/><span>{t("Plan the next step.")}</span></h1>
            <p>{t("Demonstrate how screening capacity could be explored across a synthetic population using the WHO 2019 reference chart.")}</p>
          </div>
          <div className="demoTag">
            <span>● {t("SYNTHETIC DATA ONLY")}</span>
            <p>{t("No real people, medical records or prevalence claims.")}</p>
          </div>
        </div>
        <div className="scenarioLayout">
          <section className="panel scenarioSettings">
            <div className="panelhead">
              <h2>{t("Simulation settings")}</h2>
              <span className="stepchip">{t("Educational demo")}</span>
            </div>
            <form onSubmit={submit} className="scenarioForm">
              <label>{t("WHO reference country")}
                <select value={country} onChange={e=>setCountry(e.target.value)}>
                  {COUNTRIES.map(c=><option value={c} key={c}>{t(c)}</option>)}
                </select>
              </label>
              <label>{t("Synthetic people")}
                <input type="number" min={40} max={500} value={cohortSize} onChange={e=>setCohortSize(Number(e.target.value))} required/>
              </label>
              <label>{t("Illustrative screening slots")}
                <input type="number" min={1} max={cohortSize} value={capacity} onChange={e=>setCapacity(Number(e.target.value))} required/>
              </label>
              <label>{t("Reproducible random seed")}
                <input type="number" min={0} max={1000000} value={seed} onChange={e=>setSeed(Number(e.target.value))} required/>
              </label>
              <button type="submit" disabled={loading}>
                {loading ? t("Running simulation…") : t("Run population simulation")}
                <span>→</span>
              </button>
            </form>
            <p className="scope-note">{t("Changing the country within this WHO region changes the reference label, not the synthetic cohort. Real geographic differences are not modeled.")}</p>
          </section>
          <div className="resultArea" aria-live="polite">
            {error ? (
              <div className="panel result error" role="alert">
                {t(error)}
                <p>{t("Verify FastAPI is running at ")}{API}.</p>
              </div>
            ) : !result ? (
              <section className="panel">
                <h2>{loading ? t("Preparing synthetic population…") : t("No results yet")}</h2>
              </section>
            ) : (
              <>
                <div className="metricGrid">
                  <div className="metricTile">
                    <span>{t("Synthetic population")}</span>
                    <strong>{result.cohort_size}</strong>
                    <small>{t("Artificial records")}</small>
                  </div>
                  <div className="metricTile">
                    <span>{t("Demo screening slots")}</span>
                    <strong>{result.selected_for_demo}</strong>
                    <small>{t("Capacity for this scenario")}</small>
                  </div>
                  <div className="metricTile">
                    <span>{t("Reference values ≥10%")}</span>
                    <strong>{result.higher_chart_category_count}</strong>
                    <small>{formatPercent(result.higher_chart_category_share, 1)} {t("of simulated profiles")}</small>
                  </div>
                  <div className="metricTile">
                    <span>{t("Not selected in scenario")}</span>
                    <strong>{result.unselected_for_demo}</strong>
                    <small>{t("Not selected in this example")}</small>
                  </div>
                </div>
                <div className="chartGrid">
                  <BarGroup title="WHO risk categories" rows={result.risk_distribution} scheme="risk"/>
                  <BarGroup title="Synthetic cohort by age" rows={result.age_distribution}/>
                </div>
              </>
            )}
          </div>
        </div>
        {result && (
          <>
            <div className="chartGrid lowerCharts">
              <BarGroup title="Demonstration sectors" rows={result.area_distribution}/>
              <BarGroup title="Chart reference sex" rows={result.sex_reference_distribution}/>
            </div>
            <section className="panel queuePanel">
              <div className="panelhead">
                <div>
                  <span className="eyebrow">{t("ILLUSTRATIVE SCENARIO")}</span>
                  <h2>{t("Example screening-capacity allocation")}</h2>
                </div>
                <span className="stepchip">{t("Not clinical triage")}</span>
              </div>
              <p className="scope-note">{t("For demonstration only, the highest chart-bin values are listed first. These are fictitious profiles, not people to contact or medical appointments to schedule.")}</p>
              <div className="tableScroll">
                <table className="popTable">
                  <thead>
                    <tr>
                      <th>{t("Synthetic ID")}</th>
                      <th>{t("Demo sector")}</th>
                      <th>{t("Age")}</th>
                      <th>{t("Chart sex")}</th>
                      <th>{t("Smoker")}</th>
                      <th>{t("SBP")}</th>
                      <th>{t("BMI")}</th>
                      <th>{t("WHO cell")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.demonstration_queue.map(p=>(
                      <tr key={p.synthetic_id}>
                        <td><b>{p.synthetic_id}</b></td>
                        <td>{t(p.area)}</td>
                        <td>{t(p.age_band)}</td>
                        <td>{t(p.sex_reference)}</td>
                        <td>{p.current_smoker ? t("Yes") : t("No")}</td>
                        <td>{p.systolic_bp}</td>
                        <td>{p.bmi}</td>
                        <td><span className="riskPill">{formatPercent(p.who_chart_value_percent, 0)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section className="panel methodology">
              <span className="eyebrow">{t("METHOD & TRANSPARENCY")}</span>
              <h2>{t("What the demonstration does—and does not—show")}</h2>
              <ul>{result.methodology.map(s=><li key={s}>{t(s)}</li>)}</ul>
              <a href={result.source_url||SOURCE} target="_blank" rel="noreferrer">{t("Read the original WHO 2019 regional chart ↗")}</a>
            </section>
          </>
        )}
        <footer>{t("PREVIA Health AI · Research prototype · Synthetic data only · Not for clinical use")}</footer>
      </div>
    </main>
  );
}
