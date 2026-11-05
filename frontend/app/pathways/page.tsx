"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useI18n } from "../i18n/I18nProvider";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";
const COUNTRIES = ["Benin", "Burkina Faso", "Cabo Verde", "Cameroon", "Chad", "Cote d'Ivoire", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Sao Tome and Principe", "Senegal", "Sierra Leone", "Togo"];
const STRATEGIES = [
  { key: "chart_descending", label: "WHO reference-value first" },
  { key: "sector_balanced", label: "Balanced demo sectors" },
  { key: "seeded_random", label: "Seeded random baseline" },
] as const;
type Strategy = typeof STRATEGIES[number]["key"];
type Action = "invite" | "acknowledge" | "offer_screening" | "book" | "attend" | "review" | "decline" | "reopen";
type Step = "identified" | "invited" | "engaged" | "offered" | "booked" | "attended" | "reviewed" | "declined";
type Event = { synthetic_id: string; action: Action };
type Case = {
  synthetic_id: string;
  demonstration_sector: string;
  age_band: string;
  chart_value_percent: number;
  stage: Step;
  furthest_step: string;
  next_actions: Action[];
};
type Summary = {
  selected: number; invited: number; engaged: number; offered: number; booked: number;
  attended: number; reviewed: number; declined: number; awaiting_action: number;
  invited_share_pct: number; attended_share_pct: number; reviewed_share_pct: number;
  sector_reviewed_rate_gap_pp: number;
};
type PathwayResult = {
  data_type: string; country: string; strategy: Strategy; cohort_size: number;
  selected_count: number; seed: number; events_replayed: number;
  summary: Summary;
  funnel: Array<{ key: string; count: number; share_of_selected_pct: number; conversion_from_previous_pct: number | null }>;
  demonstration_sectors: Array<{ sector: string; selected: number; reviewed_in_demo: number; reviewed_rate_pct: number }>;
  cases: Case[];
  guidance: Array<{ title: string; description: string; basis: string }>;
  limitations: string[]; clinical_use: string; data_storage: string;
  who_hearts_source_url: string;
};
const ACTION_LABELS: Record<Action, string> = {
  invite: "Simulate invitation", acknowledge: "Simulate engagement", offer_screening: "Offer demo assessment",
  book: "Book fictitious visit", attend: "Mark fictitious attendance", review: "Mark fictitious review",
  decline: "Simulate declining", reopen: "Reopen fictitious case",
};
const STAGE_NAMES: Record<Step, string> = {
  identified: "Identified", invited: "Invited", engaged: "Engaged", offered: "Offered",
  booked: "Booked", attended: "Attended", reviewed: "Reviewed", declined: "Declined",
};
const STEP_LABELS: Record<string, string> = {
  identified: "Selected", invited: "Invited", engaged: "Engaged", offered: "Offered",
  booked: "Booked", attended: "Attended", reviewed: "Reviewed",
};

function Metric({ label, value, note }: {label: string; value: string; note: string}) {
  const { t } = useI18n();
  return (
    <div className="metricTile">
      <span>{t(label)}</span>
      <strong>{t(value)}</strong>
      <small>{t(note)}</small>
    </div>
  );
}

function exportScenario(result: PathwayResult, events: Event[]) {
  const json = JSON.stringify({ ...result, local_user_events: events }, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `PREVIA_v0.7_Fictional_Pathway_${result.seed}.json`;
  document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
}

export default function PathwaysPage() {
  const { t, formatPercent } = useI18n();
  const [country, setCountry] = useState("Togo");
  const [cohortSize, setCohortSize] = useState(240);
  const [capacity, setCapacity] = useState(45);
  const [seed, setSeed] = useState(2026);
  const [strategy, setStrategy] = useState<Strategy>("chart_descending");
  const [result, setResult] = useState<PathwayResult | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const fetchScenario = useCallback(async (
    newEvents: Event[], options: {country: string; cohortSize: number; capacity: number; seed: number; strategy: Strategy},
  ) => {
    const response = await fetch(`${API}/api/v1/pathways/simulate`, {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({country: options.country, cohort_size: options.cohortSize,
        outreach_capacity: options.capacity, seed: options.seed, strategy: options.strategy,
        confirm_synthetic_demo: true, events: newEvents}),
    });
    const body = await response.json();
    if (!response.ok) {
      const detail = body?.detail;
      throw new Error(typeof detail === "string" ? detail : `API returned ${response.status}`);
    }
    return body as PathwayResult;
  }, []);

  const load = useCallback(async () => {
    setError(""); setWorking(true);
    try {
      const data = await fetchScenario([], {country, cohortSize, capacity, seed, strategy});
      setResult(data); setEvents([]);
      setSelectedId(data.cases.find(c => c.next_actions.length)?.synthetic_id || data.cases[0]?.synthetic_id || "");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not run synthetic scenario."); }
    finally { setWorking(false); }
  }, [country, cohortSize, capacity, seed, strategy, fetchScenario]);

  useEffect(() => {
    let cancelled = false;
    void fetchScenario([], {country: "Togo", cohortSize: 240, capacity: 45, seed: 2026, strategy: "chart_descending"})
      .then(data => { if (!cancelled) { setResult(data); setSelectedId(data.cases.find(c => c.next_actions.length)?.synthetic_id || ""); } })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : "Could not load demo."); });
    return () => { cancelled = true; };
  }, [fetchScenario]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (capacity > cohortSize) { setError("Demo slots cannot exceed fictitious profiles."); return; }
    await load();
  }

  async function apply(id: string, action: Action) {
    if (!result || working) return;
    setError(""); setWorking(true);
    const nextEvents = [...events, { synthetic_id: id, action }];
    try {
      const data = await fetchScenario(nextEvents, {country: result.country, cohortSize: result.cohort_size,
        capacity: result.selected_count, seed: result.seed, strategy: result.strategy});
      setResult(data); setEvents(nextEvents); setSelectedId(id);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Transition failed."); }
    finally { setWorking(false); }
  }

  const selectedCase = result?.cases.find(c => c.synthetic_id === selectedId);
  const rows = (result?.cases || []).filter(c => filter === "all" || c.stage === filter);
  const maxChart = Math.max(1, ...((result?.demonstration_sectors || []).map(r => r.reviewed_rate_pct)));

  return (
    <main className="populationPage">
      <div className="shell">
        <header className="topbar">
          <div className="brand"><span className="brandmark">P</span>PREVIA <span className="lighter">Health AI</span></div>
          <nav className="topnav" aria-label={t("PREVIA modules")}>
            <a className="navlink" href="/">{t("Individual screening")}</a>
            <a className="navlink" href="/population">{t("Population intelligence")}</a>
            <a className="navlink" href="/prioritization">{t("Strategy comparison")}</a>
            <a className="navlink" href="/evaluation">{t("Scientific audit")}</a>
            <a className="navlink" href="/evidence">{t("External evidence")}</a>
            <a className="navlink active" href="/pathways">{t("Prevention pathway")}</a>
            <a className="navlink" href="/ai">{t("ML + XAI + RAG")}</a>
          </nav>
        </header>
        <section className="popHero">
          <div>
            <div className="eyebrow">{t("FROM SCREENING SIGNAL TO A FOLLOW-UP PATH · MODULE 07")}</div>
            <h1>{t("Turn insights into steps.")}<br/><span>{t("Show what follows.")}</span></h1>
            <p>{t("Explore an auditable, fictional journey from prioritization to a simulated clinical-review milestone — without making appointments, sending messages or using patient data.")}</p>
          </div>
          <div className="demoTag">
            <span>● {t("FICTIONAL WORKFLOW ONLY")}</span>
            <p>{t("Every case and conversion stage is synthetic. No care is delivered or scheduled.")}</p>
          </div>
        </section>
        <div className="scenarioLayout">
          <aside className="panel scenarioSettings">
            <div className="panelhead">
              <h2>{t("Scenario controls")}</h2>
              <span className="stepchip">{t("Stateless demo")}</span>
            </div>
            <form className="scenarioForm" onSubmit={submit}>
              <label>{t("WHO reference country")}
                <select value={country} onChange={e=>setCountry(e.target.value)}>
                  {COUNTRIES.map(c=><option key={c} value={c}>{t(c)}</option>)}
                </select>
              </label>
              <label>{t("Synthetic cohort")}
                <input type="number" min={40} max={500} value={cohortSize} onChange={e=>setCohortSize(Number(e.target.value))} required/>
              </label>
              <label>{t("Illustrative slots")}
                <input type="number" min={1} max={500} value={capacity} onChange={e=>setCapacity(Number(e.target.value))} required/>
              </label>
              <label>{t("Reproducible seed")}
                <input type="number" min={0} max={1000000} value={seed} onChange={e=>setSeed(Number(e.target.value))} required/>
              </label>
              <label>{t("Illustrative allocation")}
                <select value={strategy} onChange={e=>setStrategy(e.target.value as Strategy)}>
                  {STRATEGIES.map(s=><option value={s.key} key={s.key}>{t(s.label)}</option>)}
                </select>
              </label>
              <button disabled={working} type="submit">
                {working ? t("Calculating…") : t("Run fictional pathway")}
                <span aria-hidden="true">→</span>
              </button>
            </form>
            <p className="scope-note">{t("Running a new scenario discards local replay actions. The backend stores no case histories.")}</p>
          </aside>
          <div className="resultArea" aria-live="polite">
            {error && <div className="result error" role="alert">{t(error)}</div>}
            {!result ? (
              <div className="panel">{t("Loading fictional pathway…")}</div>
            ) : (
              <>
                <div className="metricGrid pathMetrics">
                  <Metric label="Fictional cases selected" value={String(result.summary.selected)} note="From the existing strategy engine"/>
                  <Metric label="Invited in simulation" value={String(result.summary.invited)} note={`${formatPercent(result.summary.invited_share_pct, 2)} ${t("of fictitious selection")}`}/>
                  <Metric label="Mock visits attended" value={String(result.summary.attended)} note={`${formatPercent(result.summary.attended_share_pct, 2)} ${t("of fictitious selection")}`}/>
                  <Metric label="Mock review stage" value={String(result.summary.reviewed)} note="Not real clinical completion"/>
                </div>
                <section className="insightCard pathFunnel">
                  <div className="pathHead">
                    <div>
                      <span className="eyebrow">{t("ILLUSTRATIVE FUNNEL")}</span>
                      <h3>{t("From selection to simulated review")}</h3>
                    </div>
                    <span className="stepchip">{result.events_replayed} {t("user event(s)")}</span>
                  </div>
                  <div className="pathFunnelGrid">
                    {result.funnel.map((step, i) => (
                      <div className="pathStep" key={step.key}>
                        <div className="pathStepTop">
                          <b>{String(i + 1).padStart(2, "0")}</b>
                          <span>{t(STEP_LABELS[step.key] || step.key)}</span>
                        </div>
                        <strong>{step.count}<small> / {result.selected_count}</small></strong>
                        <div className="bartrack">
                          <div className="barfill" style={{width:`${step.share_of_selected_pct}%`,background:"#0f7e8b"}}/>
                        </div>
                        <small>{formatPercent(step.share_of_selected_pct, 2)} {t("of selected")}</small>
                      </div>
                    ))}
                  </div>
                  <p className="pathCaveat">{t("Initial conversion counts are based on deliberately invented demonstration ratios, not healthcare uptake, appointments or patient outcomes. Actions below change only fictitious state.")}</p>
                </section>
              </>
            )}
          </div>
        </div>
        {result && (
          <>
            <div className="pathBottom">
              <section id="pathway-console-anchor" className="panel pathConsole">
                <span className="eyebrow">{t("INTERACTIVE WORKFLOW")}</span>
                <h2>{t("Advance a fictional case")}</h2>
                <p className="scope-note">{t("Choose a fabricated identifier. Every button merely replays an allowed transition against the current deterministic scenario.")}</p>
                <label className="pathSelect">{t("Synthetic identifier")}
                  <select value={selectedId} onChange={e=>setSelectedId(e.target.value)}>
                    {result.cases.map(c=>(
                      <option key={c.synthetic_id} value={c.synthetic_id}>
                        {c.synthetic_id} · {t(STAGE_NAMES[c.stage])}
                      </option>
                    ))}
                  </select>
                </label>
                {selectedCase && (
                  <div className="pathCase">
                    <div><span>{t("ID")}</span><b>{selectedCase.synthetic_id}</b></div>
                    <div><span>{t("Status")}</span><b>{t(STAGE_NAMES[selectedCase.stage])}</b></div>
                    <div><span>{t("Demo sector")}</span><b>{t(selectedCase.demonstration_sector)}</b></div>
                    <div><span>{t("WHO chart cell")}</span><b>{formatPercent(selectedCase.chart_value_percent, 0)}</b></div>
                  </div>
                )}
                <div className="pathActions">
                  {selectedCase?.next_actions.map(action => (
                    <button
                      type="button"
                      key={action}
                      disabled={working}
                      className={action === "decline" ? "pathDanger" : ""}
                      onClick={() => void apply(selectedCase.synthetic_id, action)}
                    >
                      {t(ACTION_LABELS[action])} <span aria-hidden="true">→</span>
                    </button>
                  ))}
                </div>
                {selectedCase?.next_actions.length === 0 && (
                  <div className="pathResolved">{t("This fictitious case has reached its final demo state.")}</div>
                )}
                <div className="pathLog">
                  <b>{t("Session-only replay log")}</b>
                  {events.length === 0 ? (
                    <p>{t("No manual events yet. You can advance a fictitious case to demonstrate the transition rules.")}</p>
                  ) : (
                    <ol>
                      {events.slice(-8).map((event, idx)=>(
                        <li key={`${idx}-${event.synthetic_id}-${event.action}`}>
                          <code>{event.synthetic_id}</code> {t(ACTION_LABELS[event.action])}
                        </li>
                      ))}
                    </ol>
                  )}
                </div>
                <button type="button" className="secondarybutton pathExport" onClick={()=>exportScenario(result, events)}>
                  {t("Export reproducible JSON ↓")}
                </button>
              </section>
              <section className="panel pathAnalytics">
                <span className="eyebrow">{t("TRANSPARENT MONITORING")}</span>
                <h2>{t("Fictitious sectors and milestones")}</h2>
                <div className="pathSectorBars">
                  {result.demonstration_sectors.map(s=>(
                    <div key={s.sector} className="pathSector">
                      <div><b>{t(s.sector)}</b><span>{s.reviewed_in_demo}/{s.selected} {t("reviewed")}</span></div>
                      <div className="bartrack">
                        <div className="barfill" style={{width:`${maxChart ? 100*s.reviewed_rate_pct/maxChart : 0}%`,background:"#0d7485"}}/>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="pathThree">
                  <div><span>{t("Awaiting demo action")}</span><strong>{result.summary.awaiting_action}</strong></div>
                  <div><span>{t("Declined (demo)")}</span><strong>{result.summary.declined}</strong></div>
                  <div><span>{t("Sector gap")}</span><strong>{result.summary.sector_reviewed_rate_gap_pp} pp</strong></div>
                </div>
                <p className="scope-note">{t("Gap = maximum minus minimum fabricated review-stage rate across sectors with selected records. This does not measure equity of clinical care.")}</p>
              </section>
            </div>
            <section className="panel pathTablePanel">
              <div className="pathHead">
                <div>
                  <span className="eyebrow">{t("FICTIONAL CASE QUEUE")}</span>
                  <h2>{t("Review the entire simulated selection")}</h2>
                </div>
                <label className="pathFilter">{t("Filter stage")}
                  <select value={filter} onChange={e=>setFilter(e.target.value)}>
                    <option value="all">{t("All statuses")}</option>
                    {Object.keys(STAGE_NAMES).map(x=><option key={x} value={x}>{t(STAGE_NAMES[x as Step])}</option>)}
                  </select>
                </label>
              </div>
              <div className="tableScroll">
                <table className="popTable">
                  <thead>
                    <tr>
                      <th>{t("Synthetic ID")}</th>
                      <th>{t("Fictitious sector")}</th>
                      <th>{t("Age band")}</th>
                      <th>{t("WHO reference")}</th>
                      <th>{t("Current status")}</th>
                      <th>{t("Further milestone")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map(c=>(
                      <tr key={c.synthetic_id}>
                        <td>
                          <button
                            type="button"
                            className="pathIdButton"
                            onClick={()=>{
                              setSelectedId(c.synthetic_id);
                              document.getElementById("pathway-console-anchor")?.scrollIntoView({behavior:"smooth",block:"start"});
                            }}
                          >
                            {c.synthetic_id}
                          </button>
                        </td>
                        <td>{t(c.demonstration_sector)}</td>
                        <td>{t(c.age_band)}</td>
                        <td>{formatPercent(c.chart_value_percent, 0)}</td>
                        <td><span className={`pathStatus ${c.stage === "declined" ? "pathStatusDeclined" : ""}`}>{t(STAGE_NAMES[c.stage])}</span></td>
                        <td>{t(STEP_LABELS[c.furthest_step] || c.furthest_step)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="scope-note">{rows.length} {t("of")} {result.cases.length} {t("fictitious identifiers displayed. No personal data are included.")}</p>
            </section>
            <section className="panel methodology pathGuidance">
              <span className="eyebrow">{t("EVIDENCE-ALIGNED EDUCATIONAL DESIGN")}</span>
              <h2>{t("What a real prevention service would need")}</h2>
              <div className="pathGuidanceGrid">
                {result.guidance.map(item=>(
                  <div key={item.title}>
                    <h3>{t(item.title)}</h3>
                    <p>{t(item.description)}</p>
                    <small>{t(item.basis)}</small>
                  </div>
                ))}
              </div>
              <p><a target="_blank" rel="noreferrer" href={result.who_hearts_source_url}>{t("WHO HEARTS — Risk-based CVD management ↗")}</a></p>
              <div className="pathLimits">
                <b>{t("Scientific and operational boundaries")}</b>
                <ul>{result.limitations.map((line,i)=><li key={i}>{t(line)}</li>)}</ul>
              </div>
            </section>
          </>
        )}
        <footer>{t("PREVIA Health AI · Module 07 · Synthetic events only · No referrals, scheduling or messages · Not for clinical use.")}</footer>
      </div>
    </main>
  );
}
