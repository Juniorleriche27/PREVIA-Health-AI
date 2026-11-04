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
console.log(`i18n audit passed: ${pages.length} pages have catalog coverage for visible static strings.`);
