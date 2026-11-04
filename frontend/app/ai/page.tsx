"use client";

import { useEffect, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./ai.module.css";
import { useI18n } from "../i18n/I18nProvider";

const AI_API = process.env.NEXT_PUBLIC_AI_API_URL || "http://127.0.0.1:8766";

type Impact = { feature: string; impact_percentage_points: number };
type ExplainResult = {
  model: string; model_sha256: string; probability_unvalidated_percent: number;
  experimental_threshold: number; above_experimental_threshold: boolean;
  shap_baseline_percent: number; shap_additivity_error: number;
  contributions: Impact[]; external_reference_metrics: Record<string, number>;
  task: string; limitations: string[];
};
type Source = { id: string; title: string; publisher: string; url: string; similarity: number };
type RAGResult = { answer: string; mode: string; provider: string | null; model: string | null;
  fallback_reason?: string | null; sources: Source[]; clinical_use: string };
type Provider = { id: string; label: string; adapter: string; default_model: string; ready: boolean };
type AIHealth = { status: string; version: string; model_status: string; sources: number };
type Turn = { role: "user" | "assistant"; content: string };
type ChatMessage = Turn & { id: string; result?: RAGResult };
type Draft = {
  age: number; sex: "male" | "female"; bmi: number; sbp: number; smoking: "never" | "former" | "current";
  waist_cm: number; hypertension_history: "yes" | "no" | "unknown";
  high_cholesterol_history: "yes" | "no" | "unknown";
  leisure_activity: "yes" | "no" | "unknown";
  work_activity: "yes" | "no" | "unknown";
};
const INITIAL: Draft = {
  age: 58, sex: "female", bmi: 29.2, sbp: 142, smoking: "never", waist_cm: 94,
  hypertension_history: "yes", high_cholesterol_history: "unknown", leisure_activity: "no", work_activity: "no",
};
const LABELS: Record<string, string> = {
  age: "Age", sex: "NHANES reference sex", bmi: "Body mass index", sbp: "Systolic blood pressure",
  smoking: "Smoking history", waist_cm: "Waist circumference", hypertension_history: "History of hypertension",
  high_cholesterol_history: "History of high cholesterol", leisure_activity: "Leisure-time physical activity",
  work_activity: "Work physical activity",
};
const QUESTIONS = [
  "Que signifie une HbA1c de 5,7 % ?",
  "Comment fonctionne la grille cardiovasculaire OMS ?",
  "Quels facteurs contribuent au risque cardiovasculaire ?",
  "Quel est le rôle du suivi dans WHO HEARTS ?",
];
const WELCOME: ChatMessage = { id: "welcome", role: "assistant", content: "Bonjour, je suis l’assistant documentaire PREVIA. Posez une question sur les références **OMS**, **CDC** ou **NIDDK**. Mes réponses restent informatives et affichent leurs sources." };

function MarkdownContent({ children }: { children: string }) {
  return <div className={styles.markdown}><ReactMarkdown remarkPlugins={[remarkGfm]} components={{
    a: props => <a {...props} target="_blank" rel="noreferrer noopener" />,
  }}>{children}</ReactMarkdown></div>;
}

async function postJSON<T>(endpoint: string, payload: object): Promise<T> {
  const response = await fetch(`${AI_API}${endpoint}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    cache: "no-store", body: JSON.stringify(payload),
  });
  const json = await response.json();
  if (!response.ok) {
    const detail = typeof json.detail === "string" ? json.detail : `AI API: HTTP ${response.status}`;
    throw new Error(detail);
  }
  return json as T;
}

export default function AIPage() {
  const { language, formatNumber } = useI18n();
  const [draft, setDraft] = useState<Draft>(INITIAL);
  const [xai, setXAI] = useState<ExplainResult | null>(null);
  const [xaiError, setXAIError] = useState("");
  const [busyXAI, setBusyXAI] = useState(false);
  const [query, setQuery] = useState(QUESTIONS[0]);
  const [rag, setRAG] = useState<RAGResult | null>(null);
  const [ragError, setRAGError] = useState("");
  const [busyRAG, setBusyRAG] = useState(false);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [provider, setProvider] = useState("extractive");
  const [model, setModel] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [providerError, setProviderError] = useState("");
  const [health, setHealth] = useState<AIHealth | null>(null);
  useEffect(() => {
    let active = true;
    fetch(`${AI_API}/api/v1/ai/providers`, { cache: "no-store" })
      .then(async r => { if (!r.ok) throw new Error("Unable to load provider registry."); return r.json(); })
      .then((r: {providers: Provider[]}) => { if (active) setProviders(r.providers); })
      .catch((e: unknown) => { if (active) setProviderError(e instanceof Error ? e.message : "Providers unavailable."); });
    fetch(`${AI_API}/api/v1/ai/health`, { cache: "no-store" })
      .then(async r => { if (!r.ok) throw new Error(); return r.json(); })
      .then((r: AIHealth) => { if (active) setHealth(r); })
      .catch(() => { if (active) setHealth(null); });
    return () => { active = false; };
  }, []);
  function changeProvider(next: string) {
    setProvider(next);
    setModel(providers.find(p => p.id === next)?.default_model ?? "");
  }

  function update<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft(old => ({ ...old, [key]: value }));
  }
  async function requestXAI(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setBusyXAI(true); setXAIError(""); setXAI(null);
    try { setXAI(await postJSON<ExplainResult>("/api/v1/ai/explain", { ...draft, confirm_fictitious_demo: true })); }
    catch (err) { setXAIError(err instanceof Error ? err.message : "Explainability unavailable."); }
    finally { setBusyXAI(false); }
  }
  async function requestRAG(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setBusyRAG(true); setRAGError(""); setRAG(null);
    const question = query.trim();
    const history = messages.filter(m => m.id !== "welcome").slice(-6).map(({role, content}) => ({role, content}));
    setMessages(old => [...old, { id: `user-${Date.now()}`, role: "user", content: question }]);
    try {
      const next = await postJSON<RAGResult>("/api/v1/ai/ask", {
        question, provider_id: provider, model_id: provider === "extractive" ? null : model, history, language,
      });
      setRAG(next);
      setMessages(old => [...old, { id: `assistant-${Date.now()}`, role: "assistant", content: next.answer, result: next }]);
    }
    catch (err) { setRAGError(err instanceof Error ? err.message : "Document retrieval unavailable."); }
    finally { setBusyRAG(false); }
  }
  return <main className="populationPage"><div className="shell">
    <header className="topbar">
      <div className="brand"><span className="brandmark">P</span>PREVIA <span className="lighter">Health AI</span></div>
      <nav className="topnav" aria-label="PREVIA modules">
        <a className="navlink" href="/">Individual screening</a>
        <a className="navlink" href="/population">Population intelligence</a>
        <a className="navlink" href="/prioritization">Strategy comparison</a>
        <a className="navlink" href="/evaluation">Scientific audit</a>
        <a className="navlink" href="/evidence">External evidence</a>
        <a className="navlink" href="/pathways">Prevention pathway</a>
        <a className="navlink active" href="/ai">ML + XAI + RAG</a>
      </nav>
    </header>
    <div className={styles.serviceBar} role="status">
      <span className={health ? styles.online : styles.offline} aria-hidden="true" />
      <b>{health ? "AI service ready" : "AI service unavailable"}</b>
      {health && <span>Sidecar {health.version} · SHAP model {health.model_status} · {health.sources} curated sources</span>}
      {!health && <span>Start all three services with scripts/previa_full.ps1 start.</span>}
    </div>
    <section className="popHero"><div><div className="eyebrow">EXPLAINABLE RESEARCH AI · MODULE 08</div>
      <h1>Explain the model.<br/><span>Ground the answer.</span></h1>
      <p>Local SHAP contributions for a frozen NHANES Random Forest, alongside a source-grounded documentary assistant. The WHO cardiovascular chart remains a separate scientific reference.</p>
    </div><div className="demoTag"><span>● RESEARCH DEMONSTRATION ONLY</span><p>Use fictitious inputs. Not a diagnosis, referral rule, future disease prediction or clinically validated model.</p></div></section>
    <div className={styles.columns}>
      <section className="panel"><div className="panelhead"><div><span className="stepchip">01 · SHAP</span><h2>Explain a fictional classification</h2></div></div>
        <p className={styles.explainer}>The model classifies association with <b>measured HbA1c ≥5.7%</b> in NHANES. It is not a cardiovascular risk predictor. All prefilled values are fictional.</p>
        <form onSubmit={requestXAI} className={styles.form}>
          <div className={styles.two}>
            <label>Age (40–74)<input type="number" min="40" max="74" required value={draft.age} onChange={e=>update("age", Number(e.target.value))}/></label>
            <label>Reference sex<select value={draft.sex} onChange={e=>update("sex", e.target.value as Draft["sex"])}><option value="female">Female</option><option value="male">Male</option></select></label>
            <label>Body mass index<input type="number" min="12" max="75" step="0.1" required value={draft.bmi} onChange={e=>update("bmi", Number(e.target.value))}/></label>
            <label>Systolic BP (mmHg)<input type="number" min="70" max="260" required value={draft.sbp} onChange={e=>update("sbp", Number(e.target.value))}/></label>
            <label>Waist (cm)<input type="number" min="40" max="220" step="0.1" required value={draft.waist_cm} onChange={e=>update("waist_cm", Number(e.target.value))}/></label>
            <label>Smoking history<select value={draft.smoking} onChange={e=>update("smoking", e.target.value as Draft["smoking"])}><option value="never">Never</option><option value="former">Former</option><option value="current">Current</option></select></label>
            {(["hypertension_history","high_cholesterol_history","leisure_activity","work_activity"] as const).map(name=><label key={name}>{LABELS[name]}<select value={draft[name]} onChange={e=>update(name, e.target.value as Draft[typeof name])}><option value="unknown">Unknown</option><option value="yes">Yes</option><option value="no">No</option></select></label>)}
          </div>
          <button type="submit" className={styles.action} disabled={busyXAI}>{busyXAI ? "Calculating SHAP…" : "Explain fictitious profile →"}</button>
        </form>
        {xaiError && <div role="alert" className={styles.error}>{xaiError}</div>}
        {xai && <div className={styles.result}>
          <div className={styles.headline}><div><small>Research model output</small><strong>{xai.probability_unvalidated_percent.toFixed(2)}%</strong></div><div><small>Development threshold</small><strong>{(xai.experimental_threshold * 100).toFixed(2)}%</strong></div></div>
          <p className={styles.small}>SHAP baseline: {xai.shap_baseline_percent.toFixed(2)}%. Positive contributions raise the fitted model output; negative contributions lower it. These are <b>not causal effects.</b></p>
          <h3>What moved this model output?</h3>
          <div className={styles.legend}><span><i className={styles.positive}/>Raises model output</span><span><i className={styles.negative}/>Lowers model output</span><span>pp = percentage points</span></div>
          <div className={styles.impacts}>{xai.contributions.map(item=><div className={styles.impact} key={item.feature}>
            <span>{LABELS[item.feature] || item.feature}</span><div className={styles.impactTrack} role="img" aria-label={`${LABELS[item.feature] || item.feature}: ${item.impact_percentage_points.toFixed(2)} percentage points`}><div className={styles.impactFill} style={{ width: `${Math.min(100, Math.abs(item.impact_percentage_points) / 15 * 100)}%`, background: item.impact_percentage_points >= 0 ? "#07808e" : "#b77b49" }} /></div>
            <b>{item.impact_percentage_points > 0 ? "+" : ""}{item.impact_percentage_points.toFixed(2)} pp</b></div>)}</div>
          <p className={styles.small}>Additivity residual: {xai.shap_additivity_error.toExponential(2)} · Frozen model: {xai.model} · SHA-256: {xai.model_sha256.slice(0, 16)}…</p>
          {Object.keys(xai.external_reference_metrics).length > 0 && <p className={styles.small}>Independent-cycle scores (2015–16): ROC-AUC {xai.external_reference_metrics.roc_auc?.toFixed(3) ?? "n/a"}; PR-AUC {xai.external_reference_metrics.pr_auc_ap?.toFixed(3) ?? "n/a"}. No clinical validation.</p>}
        </div>}
      </section>
      <section className={`panel ${styles.assistantPanel}`}><div className={styles.assistantHeader}><div><span className="stepchip">02 · RAG</span><h2>Reference assistant</h2><p>Grounded answers with visible sources</p></div><span className={styles.privacyPill}>Session only</span></div>
        <details className={styles.settings}>
          <summary><span>Model settings</span><small>{provider === "extractive" ? "Extractive · no LLM" : `${provider} · ${model}`}</small></summary>
          <div className={styles.providerRow}>
            <label>LLM provider
              <select aria-label="LLM provider" value={provider} onChange={e => changeProvider(e.target.value)}>
                <option value="extractive">Documentary retrieval · no LLM</option>
                {providers.map(p => <option key={p.id} value={p.id} disabled={!p.ready}>{p.label} ({p.adapter}){p.ready ? "" : " — API key missing"}</option>)}
              </select>
            </label>
            <label>Model ID
              <input aria-label="Model ID" value={model} maxLength={160} placeholder={provider === "extractive" ? "No model selected" : "Configured model"}
                 disabled={provider === "extractive"} onChange={e => setModel(e.target.value)} />
            </label>
          </div>
          {providerError && <p className={styles.small}>{providerError}</p>}
          {providers.length === 0 && <p className={styles.small}>No provider is configured. Add any supported API or local OpenAI-compatible endpoint through the PowerShell configuration script. No provider is imposed.</p>}
        </details>
        <div className={styles.chat} aria-live="polite">
          {messages.map(message => <article key={message.id} className={`${styles.message} ${message.role === "user" ? styles.userMessage : styles.assistantMessage}`}>
            <div className={styles.avatar} aria-hidden="true">{message.role === "user" ? "You" : "P"}</div>
            <div className={styles.bubble}>
              <div className={styles.messageMeta}>{message.role === "user" ? "You" : "PREVIA assistant"}{message.result && <span>{message.result.mode === "llm_grounded" ? `${message.result.provider} · ${message.result.model}` : "Extractive retrieval"}</span>}</div>
              <MarkdownContent>{message.content}</MarkdownContent>
              {message.result?.fallback_reason && <div className={styles.fallback}>{message.result.fallback_reason}</div>}
              {message.result && message.result.sources.length > 0 && <div className={styles.citationGrid}>{message.result.sources.map(s=><a key={s.id} href={s.url} target="_blank" rel="noreferrer noopener"><b>[{s.id}]</b><span>{s.title}</span><small>{s.publisher} · {language === "fr" ? "pertinence" : "relevance"} {formatNumber(s.similarity, { style: "percent", maximumFractionDigits: 0 })}</small></a>)}</div>}
            </div>
          </article>)}
          {busyRAG && <article className={`${styles.message} ${styles.assistantMessage}`}><div className={styles.avatar}>P</div><div className={styles.typing} aria-label="Assistant is searching"><i/><i/><i/><span>Searching curated sources</span></div></article>}
        </div>
        {ragError && <div role="alert" className={styles.error}>{ragError}</div>}
        <div className={styles.suggestions}>{QUESTIONS.map(q=><button type="button" key={q} onClick={()=>setQuery(q)}>{q}</button>)}</div>
        <form className={styles.composer} onSubmit={requestRAG}>
          <label className={styles.srOnly} htmlFor="rag-question">General medical-information question</label>
          <textarea id="rag-question" required minLength={5} maxLength={450} rows={2} value={query} onChange={e=>setQuery(e.target.value)} placeholder="Ask about WHO, cardiovascular prevention or HbA1c…" />
          <div className={styles.composerFooter}><span>{query.length}/450 · {provider === "extractive" ? "No data sent to an LLM" : `Selected provider: ${provider}`}</span><div><button type="button" className={styles.clearButton} onClick={() => { setMessages([WELCOME]); setRAG(null); }}>Clear</button><button className={styles.sendButton} type="submit" disabled={busyRAG || query.trim().length < 5} aria-label="Send question">{busyRAG ? "…" : "↑"}</button></div></div>
        </form>
        <div className={styles.notice}><b>Scientific boundaries</b><p>The XAI model is trained on US cross-sectional survey data; explanations are not causality. The RAG corpus contains curated paraphrases, not a live medical records database. No requests are saved by this module.</p></div>
      </section>
    </div>
  </div></main>;
}
