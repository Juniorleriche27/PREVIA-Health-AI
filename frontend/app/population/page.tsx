"use client";
import { useCallback, useEffect, useState, type FormEvent } from "react";

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
  const max = Math.max(1, ...rows.map(r=>r.count));
  return <section className="insightCard"><h3>{title}</h3><div className="barstack">{rows.map((row,i)=><div className="barline" key={row.category}>
    <span className="barlabel">{row.category}</span><div className="bartrack"><div className="barfill" style={{width:`${row.count / max * 100}%`,background:scheme==="risk"?BAND_COLORS[i]:"#117987"}}/></div>
    <span className="barvalue">{row.count} <small>({row.percentage}%)</small></span>
  </div>)}</div></section>;
}

export default function PopulationPage(){
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
 function submit(event:FormEvent<HTMLFormElement>){event.preventDefault();void calculate({country,cohortSize,capacity,seed})}
 return <main className="populationPage"><div className="shell">
  <header className="topbar"><div className="brand"><span className="brandmark">P</span> PREVIA <span className="lighter">Health AI</span></div><nav className="topnav" aria-label="PREVIA modules"><a className="navlink" href="/">Individual screening</a><a className="navlink active" href="/population">Population intelligence</a><a className="navlink" href="/prioritization">Strategy comparison</a>
        <a className="navlink" href="/evaluation">Scientific audit</a><a className="navlink" href="/evidence">External evidence</a><a className="navlink" href="/pathways">Prevention pathway</a><a className="navlink" href="/ai">ML + XAI + RAG</a></nav></header>
  <div className="popHero"><div><div className="eyebrow">POPULATION HEALTH INTELLIGENCE · MODULE 03</div><h1>See the picture.<br/><span>Plan the next step.</span></h1><p>Demonstrate how screening capacity could be explored across a synthetic population using the WHO 2019 reference chart.</p></div><div className="demoTag"><span>● SYNTHETIC DATA ONLY</span><p>No real people, medical records or prevalence claims.</p></div></div>
  <div className="scenarioLayout"><section className="panel scenarioSettings"><div className="panelhead"><h2>Simulation settings</h2><span className="stepchip">Educational demo</span></div><form onSubmit={submit} className="scenarioForm">
  <label>WHO reference country<select value={country} onChange={e=>setCountry(e.target.value)}>{COUNTRIES.map(c=><option value={c} key={c}>{c}</option>)}</select></label>
  <label>Synthetic people<input type="number" min={40} max={500} value={cohortSize} onChange={e=>setCohortSize(Number(e.target.value))} required/></label>
  <label>Illustrative screening slots <input type="number" min={1} max={cohortSize} value={capacity} onChange={e=>setCapacity(Number(e.target.value))} required/></label>
  <label>Reproducible random seed<input type="number" min={0} max={1000000} value={seed} onChange={e=>setSeed(Number(e.target.value))} required/></label>
  <button type="submit" disabled={loading}>{loading?"Running simulation…":"Run population simulation"}<span>→</span></button>
  </form><p className="scope-note">Changing the country within this WHO region changes the reference label, not the synthetic cohort. Real geographic differences are not modeled.</p></section>
  <div className="resultArea" aria-live="polite">{error?<div className="panel result error" role="alert">{error}<p>Verify FastAPI is running at {API}.</p></div>:!result?<section className="panel"><h2>{loading?"Preparing synthetic population…":"No results yet"}</h2></section>:<>
   <div className="metricGrid"><div className="metricTile"><span>Synthetic population</span><strong>{result.cohort_size}</strong><small>Artificial records</small></div>
   <div className="metricTile"><span>Demo screening slots</span><strong>{result.selected_for_demo}</strong><small>Capacity for this scenario</small></div>
   <div className="metricTile"><span>Reference values ≥10%</span><strong>{result.higher_chart_category_count}</strong><small>{result.higher_chart_category_share}% of simulated profiles</small></div>
   <div className="metricTile"><span>Not selected in scenario</span><strong>{result.unselected_for_demo}</strong><small>Not selected in this example</small></div></div>
   <div className="chartGrid"><BarGroup title="WHO risk categories" rows={result.risk_distribution} scheme="risk"/><BarGroup title="Synthetic cohort by age" rows={result.age_distribution}/></div>
  </>}</div></div>
  {result&&<><div className="chartGrid lowerCharts"><BarGroup title="Demonstration sectors" rows={result.area_distribution}/><BarGroup title="Chart reference sex" rows={result.sex_reference_distribution}/></div>
  <section className="panel queuePanel"><div className="panelhead"><div><span className="eyebrow">ILLUSTRATIVE SCENARIO</span><h2>Example screening-capacity allocation</h2></div><span className="stepchip">Not clinical triage</span></div>
   <p className="scope-note">For demonstration only, the highest chart-bin values are listed first. These are fictitious profiles, not people to contact or medical appointments to schedule.</p>
   <div className="tableScroll"><table className="popTable"><thead><tr><th>Synthetic ID</th><th>Demo sector</th><th>Age</th><th>Chart sex</th><th>Smoker</th><th>SBP</th><th>BMI</th><th>WHO cell</th></tr></thead><tbody>{result.demonstration_queue.map(p=><tr key={p.synthetic_id}><td><b>{p.synthetic_id}</b></td><td>{p.area}</td><td>{p.age_band}</td><td>{p.sex_reference}</td><td>{p.current_smoker?"Yes":"No"}</td><td>{p.systolic_bp}</td><td>{p.bmi}</td><td><span className="riskPill">{p.who_chart_value_percent}%</span></td></tr>)}</tbody></table></div>
  </section>
  <section className="panel methodology"><span className="eyebrow">METHOD & TRANSPARENCY</span><h2>What the demonstration does—and does not—show</h2><ul>{result.methodology.map(s=><li key={s}>{s}</li>)}</ul><a href={result.source_url||SOURCE} target="_blank" rel="noreferrer">Read the original WHO 2019 regional chart ↗</a></section></>}
  <footer>PREVIA Health AI · Research prototype · Synthetic data only · Not for clinical use</footer>
 </div></main>
}
