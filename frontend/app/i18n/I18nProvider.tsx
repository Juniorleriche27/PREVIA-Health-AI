"use client";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Language, translateLiteral } from "./catalogs";
const STORAGE_KEY = "previa-language";
const textOriginals = new WeakMap<Text, string>();
const attributeOriginals = new WeakMap<Element, Map<string, string>>();
type I18nValue = { language: Language; setLanguage: (value: Language) => void; t: (english: string) => string; formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string };
const Context = createContext<I18nValue | null>(null);
export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setCurrent] = useState<Language>("en");
  useEffect(() => { const saved = localStorage.getItem(STORAGE_KEY); setCurrent(saved === "fr" || saved === "en" ? saved : navigator.languages.some(x => x.toLowerCase().startsWith("fr")) ? "fr" : "en"); }, []);
  const setLanguage = useCallback((next: Language) => { localStorage.setItem(STORAGE_KEY, next); setCurrent(next); }, []);
  const t = useCallback((text: string) => translateLiteral(text, language), [language]);
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dataset.language = language; }, [language]);
  useEffect(() => {
    const translatedAttributes = ["placeholder", "title", "aria-label"];
    let applying = false;
    const translateNode = (root: Node) => {
      applying = true;
      const texts: Text[] = [];
      if (root.nodeType === Node.TEXT_NODE) texts.push(root as Text);
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let current: Node | null;
      while ((current = walker.nextNode())) texts.push(current as Text);
      for (const node of texts) {
        const parent = node.parentElement;
        if (!parent || ["SCRIPT", "STYLE", "TEXTAREA"].includes(parent.tagName)) continue;
        const raw = textOriginals.get(node) ?? node.data;
        textOriginals.set(node, raw);
        const match = raw.match(/^(\s*)([\s\S]*?)(\s*)$/);
        if (match) node.data = `${match[1]}${translateLiteral(match[2], language)}${match[3]}`;
      }
      const elements = root.nodeType === Node.ELEMENT_NODE ? [root as Element, ...(root as Element).querySelectorAll("*")] : [];
      for (const element of elements) for (const name of translatedAttributes) if (element.hasAttribute(name)) {
        const saved = attributeOriginals.get(element) ?? new Map<string, string>();
        const raw = saved.get(name) ?? element.getAttribute(name)!;
        saved.set(name, raw); attributeOriginals.set(element, saved);
        element.setAttribute(name, translateLiteral(raw, language));
      }
      applying = false;
    };
    translateNode(document.body);
    const observer = new MutationObserver(records => {
      if (applying) return;
      for (const record of records) {
        record.addedNodes.forEach(translateNode);
      }
    });
    observer.observe(document.body, { subtree: true, childList: true });
    return () => observer.disconnect();
  }, [language]);
  const value = useMemo(() => ({ language, setLanguage, t, formatNumber: (number: number, options?: Intl.NumberFormatOptions) => new Intl.NumberFormat(language === "fr" ? "fr-FR" : "en-US", options).format(number) }), [language, setLanguage, t]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useI18n() { const value = useContext(Context); if (!value) throw new Error("useI18n must be used inside I18nProvider"); return value; }
