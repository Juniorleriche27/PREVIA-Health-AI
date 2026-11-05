"use client";

import { useEffect, useState, useRef, type FormEvent } from "react";
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

const PRESETS: Record<"moderate" | "high" | "low", Draft> = {
  moderate: {
    age: 58, sex: "female", bmi: 29.2, sbp: 142, smoking: "never", waist_cm: 94,
    hypertension_history: "yes", high_cholesterol_history: "unknown", leisure_activity: "no", work_activity: "no",
  },
  high: {
    age: 64, sex: "male", bmi: 33.8, sbp: 162, smoking: "current", waist_cm: 106,
    hypertension_history: "yes", high_cholesterol_history: "yes", leisure_activity: "no", work_activity: "no",
  },
  low: {
    age: 43, sex: "female", bmi: 22.8, sbp: 118, smoking: "never", waist_cm: 76,
    hypertension_history: "no", high_cholesterol_history: "no", leisure_activity: "yes", work_activity: "yes",
  },
};

const LABELS: Record<string, string> = {
  age: "Age", sex: "NHANES reference sex", bmi: "Body mass index", sbp: "Systolic blood pressure",
  smoking: "Smoking history", waist_cm: "Waist circumference", hypertension_history: "History of hypertension",
  high_cholesterol_history: "History of high cholesterol", leisure_activity: "Leisure-time physical activity",
  work_activity: "Work physical activity",
};

const QUESTIONS = {
  fr: [
    "Que signifie une HbA1c de 5,7 % ?",
    "Comment fonctionne la grille cardiovasculaire OMS ?",
    "Quels facteurs contribuent au risque cardiovasculaire ?",
    "Quel est le rôle du suivi dans WHO HEARTS ?",
  ],
  en: [
    "What does an HbA1c of 5.7% mean?",
    "How does the WHO cardiovascular risk chart work?",
    "Which factors contribute to cardiovascular risk?",
    "What is the role of follow-up in WHO HEARTS?",
  ],
};

const welcomeMessage = (language: "fr" | "en"): ChatMessage => ({
  id: "welcome",
  role: "assistant",
  content: language === "fr"
    ? "Bonjour, je suis l’assistant documentaire PREVIA. Posez une question sur les références **OMS**, **CDC** ou **NIDDK**. Mes réponses restent informatives et affichent leurs sources."
    : "Hello, I am PREVIA's documentary assistant. Ask me about **WHO**, **CDC**, or **NIDDK** references. My answers remain informational and display their sources.",
});

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
  const { language, t, formatNumber, formatPercent } = useI18n();
  const [draft, setDraft] = useState<Draft>(PRESETS.moderate);
  const [activePreset, setActivePreset] = useState<"moderate" | "high" | "low" | null>("moderate");
  const [xai, setXAI] = useState<ExplainResult | null>(null);
  const [xaiError, setXAIError] = useState("");
  const [busyXAI, setBusyXAI] = useState(false);
  const [query, setQuery] = useState(QUESTIONS.en[0]);
  const [rag, setRAG] = useState<RAGResult | null>(null);
  const [ragError, setRAGError] = useState("");
  const [busyRAG, setBusyRAG] = useState(false);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [provider, setProvider] = useState("extractive");
  const [model, setModel] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage("en")]);
  const [providerError, setProviderError] = useState("");
  const [health, setHealth] = useState<AIHealth | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([welcomeMessage(language)]);
    setRAG(null);
    setRAGError("");
    setQuery(current => Object.values(QUESTIONS).flat().includes(current) ? QUESTIONS[language][0] : current);
  }, [language]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busyRAG]);

  useEffect(() => {
    let active = true;
    fetch(`${AI_API}/api/v1/ai/providers`, { cache: "no-store" })
      .then(async r => { if (!r.ok) throw new Error("Unable to load provider registry."); return r.json(); })
      .then((r: {providers: Provider[]; default?: string}) => { if (active) {
        setProviders(r.providers);
        const selected = r.providers.find(item => item.id === r.default && item.ready);
        if (selected) { setProvider(selected.id); setModel(selected.default_model); }
      } })
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

  function applyPreset(key: "moderate" | "high" | "low") {
    setDraft(PRESETS[key]);
    setActivePreset(key);
    setXAI(null);
    setXAIError("");
  }

  function update<K extends keyof Draft>(key: K, value: Draft[K]) {
    setActivePreset(null);
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

  return (
    <main className="populationPage">
      <div className="shell">
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
          <b>{health ? (language === "fr" ? "Service IA prêt" : "AI service ready") : (language === "fr" ? "Service IA indisponible" : "AI service unavailable")}</b>
          {health && <span>{t("Sidecar")} {health.version} · {t("SHAP model")} {t(health.model_status)} · {health.sources} {t("curated sources")}</span>}
          {!health && <span>{language === "fr" ? "Démarrer les services avec scripts/previa_full.ps1 start." : "Start all three services with scripts/previa_full.ps1 start."}</span>}
        </div>

        <section className="popHero">
          <div>
            <div className="eyebrow">{language === "fr" ? "IA DE RECHERCHE EXPLICABLE · MODULE 07" : "EXPLAINABLE RESEARCH AI · MODULE 07"}</div>
            <h1>{language === "fr" ? "Expliquer le modèle." : "Explain the model."}<br/><span>{language === "fr" ? "Fonder la réponse." : "Ground the answer."}</span></h1>
            <p>{t("Local SHAP contributions for a frozen NHANES Random Forest, alongside a source-grounded documentary assistant. The WHO cardiovascular chart remains a separate scientific reference.")}</p>
          </div>
          <div className="demoTag">
            <span>● {language === "fr" ? "DÉMONSTRATION DE RECHERCHE UNIQUEMENT" : "RESEARCH DEMONSTRATION ONLY"}</span>
            <p>{t("Use fictitious inputs. Not a diagnosis, referral rule, future disease prediction or clinically validated model.")}</p>
          </div>
        </section>

        {/* Dual-Panel Workbench with Independent Scroll */}
        <div className={styles.workbench}>
          
          {/* Panel 1: SHAP Model Explainer */}
          <section className={`${styles.panelCard} ${styles.shapCard}`} aria-label="SHAP Explainer">
            <div className={styles.cardHeader}>
              <div className={styles.headerTitleGroup}>
                <span className="stepchip">01 · SHAP</span>
                <h2>{t("Explain a fictional classification")}</h2>
              </div>
              <div className={styles.presetToolbar}>
                <span className={styles.presetLabel}>{language === "fr" ? "Profils démo :" : "Presets:"}</span>
                <div className={styles.presetChips}>
                  <button
                    type="button"
                    className={`${styles.presetChip} ${activePreset === "high" ? styles.presetActive : ""}`}
                    onClick={() => applyPreset("high")}
                    title={language === "fr" ? "Charger profil risque élevé" : "Load high-risk profile"}
                  >
                    {language === "fr" ? "Élevé" : "High"}
                  </button>
                  <button
                    type="button"
                    className={`${styles.presetChip} ${activePreset === "moderate" ? styles.presetActive : ""}`}
                    onClick={() => applyPreset("moderate")}
                    title={language === "fr" ? "Charger profil modéré" : "Load moderate profile"}
                  >
                    {language === "fr" ? "Modéré" : "Moderate"}
                  </button>
                  <button
                    type="button"
                    className={`${styles.presetChip} ${activePreset === "low" ? styles.presetActive : ""}`}
                    onClick={() => applyPreset("low")}
                    title={language === "fr" ? "Charger profil favorable" : "Load low-risk profile"}
                  >
                    {language === "fr" ? "Favorable" : "Low"}
                  </button>
                </div>
              </div>
            </div>

            {/* Scrollable Content inside SHAP */}
            <div className={styles.scrollableContent}>
              <p className={styles.explainer}>
                {language === "fr"
                  ? <>Le modèle classe l&apos;association avec <b>une HbA1c mesurée ≥ 5,7 %</b> dans NHANES. Ce n&apos;est pas un prédicteur du risque cardiovasculaire. Toutes les valeurs préremplies sont fictives.</>
                  : <>The model classifies association with <b>measured HbA1c ≥5.7%</b> in NHANES. It is not a cardiovascular risk predictor. All prefilled values are fictional.</>}
              </p>

              <form onSubmit={requestXAI} className={styles.form}>
                <div className={styles.two}>
                  <label>
                    {language === "fr" ? "Âge (40–74 ans)" : "Age (40–74)"}
                    <input type="number" min="40" max="74" required value={draft.age} onChange={e => update("age", Number(e.target.value))} />
                  </label>
                  <label>
                    {language === "fr" ? "Sexe de référence" : "Reference sex"}
                    <select value={draft.sex} onChange={e => update("sex", e.target.value as Draft["sex"])}>
                      <option value="female">{language === "fr" ? "Femme" : "Female"}</option>
                      <option value="male">{language === "fr" ? "Homme" : "Male"}</option>
                    </select>
                  </label>
                  <label>
                    {language === "fr" ? "Indice de masse corporelle (IMC)" : "Body mass index"}
                    <input type="number" min="12" max="75" step="0.1" required value={draft.bmi} onChange={e => update("bmi", Number(e.target.value))} />
                  </label>
                  <label>
                    {language === "fr" ? "Pression systolique (mmHg)" : "Systolic BP (mmHg)"}
                    <input type="number" min="70" max="260" required value={draft.sbp} onChange={e => update("sbp", Number(e.target.value))} />
                  </label>
                  <label>
                    {language === "fr" ? "Tour de taille (cm)" : "Waist (cm)"}
                    <input type="number" min="40" max="220" step="0.1" required value={draft.waist_cm} onChange={e => update("waist_cm", Number(e.target.value))} />
                  </label>
                  <label>
                    {language === "fr" ? "Antécédents de tabagisme" : "Smoking history"}
                    <select value={draft.smoking} onChange={e => update("smoking", e.target.value as Draft["smoking"])}>
                      <option value="never">{language === "fr" ? "Jamais" : "Never"}</option>
                      <option value="former">{language === "fr" ? "Ancien fumeur" : "Former"}</option>
                      <option value="current">{language === "fr" ? "Fumeur actif" : "Current"}</option>
                    </select>
                  </label>
                  {(["hypertension_history", "high_cholesterol_history", "leisure_activity", "work_activity"] as const).map(name => (
                    <label key={name}>
                      {t(LABELS[name])}
                      <select value={draft[name]} onChange={e => update(name, e.target.value as Draft[typeof name])}>
                        <option value="unknown">{t("Unknown")}</option>
                        <option value="yes">{t("Yes")}</option>
                        <option value="no">{t("No")}</option>
                      </select>
                    </label>
                  ))}
                </div>

                <button type="submit" className={styles.action} disabled={busyXAI}>
                  {busyXAI
                    ? (language === "fr" ? "Calcul des valeurs SHAP…" : "Calculating SHAP…")
                    : (language === "fr" ? "Expliquer le profil fictif →" : "Explain fictitious profile →")}
                </button>
              </form>

              {xaiError && <div role="alert" className={styles.error}>{t(xaiError)}</div>}

              {xai && (
                <div className={styles.result}>
                  <div className={styles.headline}>
                    <div>
                      <small>{t("Research model output")}</small>
                      <strong>{formatPercent(xai.probability_unvalidated_percent)}</strong>
                    </div>
                    <div>
                      <small>{t("Development threshold")}</small>
                      <strong>{formatPercent(xai.experimental_threshold * 100)}</strong>
                    </div>
                  </div>

                  <p className={styles.small}>
                    {t("SHAP baseline:")} {formatPercent(xai.shap_baseline_percent)}.{" "}
                    {t("Positive contributions raise the fitted model output; negative contributions lower it. These are")}{" "}
                    <b>{t("not causal effects.")}</b>
                  </p>

                  <h3>{language === "fr" ? "Facteurs ayant influencé le résultat" : "What moved this model output?"}</h3>
                  <div className={styles.legend}>
                    <span><i className={styles.positive} />{language === "fr" ? "Augmente l'estimation" : "Raises model output"}</span>
                    <span><i className={styles.negative} />{language === "fr" ? "Diminue l'estimation" : "Lowers model output"}</span>
                    <span>{language === "fr" ? "pp = points de pourcentage" : "pp = percentage points"}</span>
                  </div>

                  <div className={styles.impacts}>
                    {xai.contributions.map(item => (
                      <div className={styles.impact} key={item.feature}>
                        <span>{t(LABELS[item.feature] || item.feature)}</span>
                        <div
                          className={styles.impactTrack}
                          role="img"
                          aria-label={`${t(LABELS[item.feature] || item.feature)}: ${formatNumber(item.impact_percentage_points, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${t("percentage points")}`}
                        >
                          <div
                            className={styles.impactFill}
                            style={{
                              width: `${Math.min(100, (Math.abs(item.impact_percentage_points) / 15) * 100)}%`,
                              background: item.impact_percentage_points >= 0 ? "linear-gradient(90deg, #0d9488, #0891b2)" : "linear-gradient(90deg, #d97706, #b45309)",
                            }}
                          />
                        </div>
                        <b>
                          {item.impact_percentage_points > 0 ? "+" : ""}
                          {formatNumber(item.impact_percentage_points, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} pp
                        </b>
                      </div>
                    ))}
                  </div>

                  <p className={styles.small}>
                    {t("Additivity residual:")} {xai.shap_additivity_error.toExponential(2)} · {t("Frozen model:")} {xai.model} · SHA-256: {xai.model_sha256.slice(0, 16)}…
                  </p>
                  {Object.keys(xai.external_reference_metrics).length > 0 && (
                    <p className={styles.small}>
                      {t("Independent-cycle scores (2015–16):")} ROC-AUC {xai.external_reference_metrics.roc_auc === undefined ? t("n/a") : formatNumber(xai.external_reference_metrics.roc_auc, { minimumFractionDigits: 3, maximumFractionDigits: 3 })}; PR-AUC {xai.external_reference_metrics.pr_auc_ap === undefined ? t("n/a") : formatNumber(xai.external_reference_metrics.pr_auc_ap, { minimumFractionDigits: 3, maximumFractionDigits: 3 })}. {t("No clinical validation.")}
                    </p>
                  )}
                </div>
              )}
            </div>
          </section>

          {/* Panel 2: Grounded RAG Assistant */}
          <section className={`${styles.panelCard} ${styles.assistantCard}`} aria-label="Reference Assistant">
            <div className={styles.cardHeader}>
              <div className={styles.headerTitleGroup}>
                <span className="stepchip">02 · RAG</span>
                <h2>{language === "fr" ? "Assistant documentaire" : "Reference assistant"}</h2>
                <p className={styles.headerSubtitle}>{language === "fr" ? "Réponses fondées avec sources visibles" : "Grounded answers with visible sources"}</p>
              </div>
              <span className={styles.privacyPill}>{language === "fr" ? "Session uniquement" : "Session only"}</span>
            </div>

            {/* Model settings accordion */}
            <details className={styles.settings}>
              <summary>
                <span>{language === "fr" ? "Paramètres du modèle" : "Model settings"}</span>
                <small>{provider === "extractive" ? (language === "fr" ? "Extractif · sans LLM" : "Extractive · no LLM") : `${provider} · ${model}`}</small>
              </summary>
              <div className={styles.providerRow}>
                <label>
                  {language === "fr" ? "Fournisseur LLM" : "LLM provider"}
                  <select aria-label="LLM provider" value={provider} onChange={e => changeProvider(e.target.value)}>
                    <option value="extractive">{language === "fr" ? "Recherche documentaire · sans LLM" : "Documentary retrieval · no LLM"}</option>
                    {providers.map(p => (
                      <option key={p.id} value={p.id} disabled={!p.ready}>
                        {p.label} ({p.adapter}){p.ready ? "" : (language === "fr" ? " — Clé API manquante" : " — API key missing")}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {language === "fr" ? "Identifiant du modèle" : "Model ID"}
                  <input
                    aria-label="Model ID"
                    value={model}
                    maxLength={160}
                    placeholder={provider === "extractive" ? (language === "fr" ? "Aucun modèle requis" : "No model selected") : "Configured model"}
                    disabled={provider === "extractive"}
                    onChange={e => setModel(e.target.value)}
                  />
                </label>
              </div>
              {providerError && <p className={styles.small}>{t(providerError)}</p>}
              {providers.length === 0 && (
                <p className={styles.small}>
                  {language === "fr"
                    ? "Aucun fournisseur configuré. Ajoutez une API compatible via le script de configuration PowerShell."
                    : "No provider is configured. Add any supported API or local OpenAI-compatible endpoint through the PowerShell configuration script. No provider is imposed."}
                </p>
              )}
            </details>

            {/* Independent scrollable Chat Feed */}
            <div className={styles.chatScrollArea} aria-live="polite">
              {messages.map(message => (
                <article
                  key={message.id}
                  className={`${styles.message} ${message.role === "user" ? styles.userMessage : styles.assistantMessage}`}
                >
                  <div className={styles.avatar} aria-hidden="true">
                    {message.role === "user" ? (language === "fr" ? "Vous" : "You") : "P"}
                  </div>
                  <div className={styles.bubble}>
                    <div className={styles.messageMeta}>
                      {message.role === "user" ? (language === "fr" ? "Vous" : "You") : "PREVIA Assistant"}
                      {message.result && (
                        <span>
                          {message.result.mode === "llm_grounded"
                            ? `${message.result.provider} · ${message.result.model}`
                            : (language === "fr" ? "Extraction documentaire" : "Extractive retrieval")}
                        </span>
                      )}
                    </div>
                    <MarkdownContent>{message.content}</MarkdownContent>
                    {message.result?.fallback_reason && <div className={styles.fallback}>{t(message.result.fallback_reason)}</div>}
                    {message.result && message.result.sources.length > 0 && (
                      <div className={styles.citationGrid}>
                        {message.result.sources.map(s => (
                          <a key={s.id} href={s.url} target="_blank" rel="noreferrer noopener">
                            <b>[{s.id}]</b>
                            <span>{s.title}</span>
                            <small>{s.publisher} · {language === "fr" ? "pertinence" : "relevance"} {formatNumber(s.similarity, { style: "percent", maximumFractionDigits: 0 })}</small>
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </article>
              ))}

              {busyRAG && (
                <article className={`${styles.message} ${styles.assistantMessage}`}>
                  <div className={styles.avatar}>P</div>
                  <div className={styles.typing} aria-label="Assistant is searching">
                    <i /><i /><i />
                    <span>{language === "fr" ? "Recherche parmi les sources contrôlées…" : "Searching curated sources…"}</span>
                  </div>
                </article>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Pinned Bottom Area (Never lost on scroll) */}
            <div className={styles.pinnedBottomArea}>
              {ragError && <div role="alert" className={styles.error}>{t(ragError)}</div>}

              {/* Suggestions chips */}
              <div className={styles.suggestions} aria-label="Suggested questions">
                {QUESTIONS[language].map(q => (
                  <button type="button" key={q} onClick={() => setQuery(q)} title={language === "fr" ? "Cliquer pour copier la question" : "Click to select question"}>
                    {q}
                  </button>
                ))}
              </div>

              {/* Message Composer */}
              <form className={styles.composer} onSubmit={requestRAG}>
                <label className={styles.srOnly} htmlFor="rag-question">
                  {language === "fr" ? "Question sur la prévention médicale" : "General medical-information question"}
                </label>
                <textarea
                  id="rag-question"
                  required
                  minLength={5}
                  maxLength={450}
                  rows={2}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder={language === "fr" ? "Posez une question sur l'OMS, la prévention cardiovasculaire ou l'HbA1c…" : "Ask about WHO, cardiovascular prevention or HbA1c…"}
                />
                <div className={styles.composerFooter}>
                  <span>
                    {query.length}/450 · {provider === "extractive" ? t("No data sent to an LLM") : `${t("Selected provider:")} ${provider}`}
                  </span>
                  <div className={styles.composerControls}>
                    <button
                      type="button"
                      className={styles.clearButton}
                      onClick={() => { setMessages([welcomeMessage(language)]); setRAG(null); }}
                    >
                      {language === "fr" ? "Effacer" : "Clear"}
                    </button>
                    <button
                      className={styles.sendButton}
                      type="submit"
                      disabled={busyRAG || query.trim().length < 5}
                      aria-label={language === "fr" ? "Envoyer la question" : "Send question"}
                      title={language === "fr" ? "Envoyer la question" : "Send question"}
                    >
                      {busyRAG ? "…" : "↑"}
                    </button>
                  </div>
                </div>
              </form>

              {/* Scientific Notice */}
              <div className={styles.notice}>
                <b>{language === "fr" ? "Limites scientifiques" : "Scientific boundaries"}</b>
                <p>
                  {language === "fr"
                    ? "Le modèle XAI est entraîné sur des données transversales américaines ; ses explications n'établissent pas de causalité. Le corpus RAG contient des résumés contrôlés, et non une base active de dossiers médicaux. Aucune requête n'est enregistrée par ce module."
                    : "The XAI model is trained on US cross-sectional survey data; explanations are not causality. The RAG corpus contains curated paraphrases, not a live medical records database. No requests are saved by this module."}
                </p>
              </div>
            </div>

          </section>
        </div>
      </div>
    </main>
  );
}
