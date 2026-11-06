"use client";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Language, translateLiteral } from "./catalogs";
const STORAGE_KEY = "previa-language";
type I18nValue = {
  language: Language;
  setLanguage: (value: Language) => void;
  t: (english: string) => string;
  formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string;
  formatPercent: (value: number, fractionDigits?: number) => string;
};
const Context = createContext<I18nValue | null>(null);
export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setCurrent] = useState<Language>("en");
  useEffect(() => { const saved = localStorage.getItem(STORAGE_KEY); setCurrent(saved === "fr" || saved === "en" ? saved : navigator.languages.some(x => x.toLowerCase().startsWith("fr")) ? "fr" : "en"); }, []);
  const setLanguage = useCallback((next: Language) => { localStorage.setItem(STORAGE_KEY, next); setCurrent(next); }, []);
  const t = useCallback((text: string) => translateLiteral(text, language), [language]);
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dataset.language = language; }, [language]);
  const value = useMemo(() => {
    const locale = language === "fr" ? "fr-FR" : "en-US";
    return {
      language,
      setLanguage,
      t,
      formatNumber: (number: number, options?: Intl.NumberFormatOptions) => new Intl.NumberFormat(locale, options).format(number),
      formatPercent: (number: number, fractionDigits = 2) => {
        const formatted = new Intl.NumberFormat(locale, {
          minimumFractionDigits: fractionDigits,
          maximumFractionDigits: fractionDigits,
        }).format(number);
        return language === "fr" ? `${formatted}\u00a0%` : `${formatted}%`;
      },
    };
  }, [language, setLanguage, t]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useI18n() { const value = useContext(Context); if (!value) throw new Error("useI18n must be used inside I18nProvider"); return value; }
export function TranslatedText({ children }: { children: string }) {
  const { t } = useI18n();
  return <>{t(children)}</>;
}
