import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const catalog = fs.readFileSync(path.join(root, "app/i18n/catalogs.ts"), "utf8");
const translated = new Set([...catalog.matchAll(/"([^"]+)"\s*:/g)].map(match => match[1]));
const allowed = new Set(["PREVIA", "Health AI", "ML + XAI + RAG", "BMI", "SBP", "01 · SHAP", "02 · RAG"]);
const pages = [];
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(target);
    else if (entry.name === "page.tsx") pages.push(target);
  }
}
walk(path.join(root, "app"));
const missing = [];
for (const file of pages) {
  const source = fs.readFileSync(file, "utf8");
  for (const match of source.matchAll(/>([^<>{}\r\n]+)</g)) {
    const text = match[1].trim();
    if (!/[A-Za-z]/.test(text) || text.length < 3 || text.startsWith(":") || text.includes("Promise")) continue;
    if (!translated.has(text) && !allowed.has(text)) missing.push(`${path.relative(root, file)}: ${text}`);
  }
}
if (missing.length) {
  console.error("Visible English strings missing from the FR catalog:\n" + [...new Set(missing)].join("\n"));
  process.exit(1);
}

const requiredDynamic = [
  "SHAP baseline:", "Positive contributions raise the fitted model output; negative contributions lower it. These are",
  "not causal effects.", "Additivity residual:", "Frozen model:", "percentage points",
  "Explainability unavailable.", "Document retrieval unavailable.", "Passed", "Failed",
];
const absentDynamic = requiredDynamic.filter(text => !translated.has(text));
if (absentDynamic.length) {
  console.error("Dynamic interface strings missing from the FR catalog:\n" + absentDynamic.join("\n"));
  process.exit(1);
}

const aiPage = fs.readFileSync(path.join(root, "app/ai/page.tsx"), "utf8");
const provider = fs.readFileSync(path.join(root, "app/i18n/I18nProvider.tsx"), "utf8");
const layout = fs.readFileSync(path.join(root, "app/layout.tsx"), "utf8");
const regressions = [
  [!aiPage.includes("QUESTIONS[language]"), "AI suggestions must follow the selected language"],
  [!aiPage.includes("language, t, formatNumber, formatPercent"), "AI dynamic strings and numbers must use i18n helpers"],
  [/probability_unvalidated_percent\.toFixed/.test(aiPage), "SHAP percentages must not use locale-blind toFixed()"],
  [!aiPage.includes("ReactMarkdown") || !aiPage.includes("remarkGfm"), "Assistant Markdown rendering must remain enabled"],
  [!provider.includes('STORAGE_KEY = "previa-language"') || !provider.includes("localStorage.setItem(STORAGE_KEY"), "Language selection must persist"],
  [!provider.includes("formatPercent"), "Locale-aware percentage formatting must remain available"],
  [!layout.includes("previa-language"), "Saved language must be restored before hydration"],
];
const failures = regressions.filter(([failed]) => failed).map(([, message]) => message);
if (failures.length) {
  console.error("i18n regression checks failed:\n" + failures.join("\n"));
  process.exit(1);
}

console.log(`i18n audit passed: ${pages.length} pages, dynamic AI strings, locale formatting, Markdown and persistence covered.`);
