"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useI18n } from "../i18n/I18nProvider";

const GROUPS = [
  { label: "Prevention", items: [
    { href: "/", label: "Individual screening", short: "01", icon: "heart" },
    { href: "/pathways", label: "Prevention pathway", short: "02", icon: "path" },
  ]},
  { label: "Population intelligence", items: [
    { href: "/population", label: "Population overview", short: "03", icon: "people" },
    { href: "/prioritization", label: "Strategy comparison", short: "04", icon: "compare" },
  ]},
  { label: "Research & AI", items: [
    { href: "/evaluation", label: "Scientific audit", short: "05", icon: "audit" },
    { href: "/evidence", label: "External evidence", short: "06", icon: "evidence" },
    { href: "/ai", label: "ML, XAI & assistant", short: "07", icon: "spark" },
  ]},
];

function Icon({ name }: { name: string }) {
  const paths: Record<string, React.ReactNode> = {
    heart: <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.4A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z" />,
    path: <><circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h3a3 3 0 0 0 3-3v-6a3 3 0 0 1 3-3"/></>,
    people: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    compare: <><path d="M7 3v18M17 3v18M3 7l4-4 4 4M13 17l4 4 4-4"/></>,
    audit: <><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></>,
    evidence: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></>,
    spark: <><path d="m12 3-1.2 4.1a5 5 0 0 1-3.4 3.4L3 12l4.4 1.5a5 5 0 0 1 3.4 3.4L12 21l1.2-4.1a5 5 0 0 1 3.4-3.4L21 12l-4.4-1.5a5 5 0 0 1-3.4-3.4Z"/></>,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>;
}

export default function AppNavigation() {
  const { language, setLanguage, t } = useI18n();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    const saved = window.localStorage.getItem("previa-sidebar-collapsed") === "true";
    setCollapsed(saved);
    document.documentElement.dataset.sidebar = saved ? "collapsed" : "expanded";
    return () => { delete document.documentElement.dataset.sidebar; };
  }, []);
  function toggleSidebar() {
    const next = !collapsed;
    setCollapsed(next);
    window.localStorage.setItem("previa-sidebar-collapsed", String(next));
    document.documentElement.dataset.sidebar = next ? "collapsed" : "expanded";
  }
  return <aside className="appNav">
    <div className="navBrand"><span className="navBrandMark">P</span><div><strong>PREVIA</strong><small>{t("Health intelligence")}</small></div><button className="navToggle" type="button" onClick={toggleSidebar} aria-label={t(collapsed ? "Expand navigation" : "Collapse navigation")} title={t(collapsed ? "Expand navigation" : "Collapse navigation")}><svg viewBox="0 0 24 24" aria-hidden="true"><path d={collapsed ? "m9 18 6-6-6-6" : "m15 18-6-6 6-6"}/></svg></button></div>
    <nav aria-label={t("Primary navigation")}>
      {GROUPS.map(group => <section className="navGroup" key={group.label}>
        <h2>{t(group.label)}</h2>
        {group.items.map(item => {
          const active = pathname === item.href;
          return <Link href={item.href} key={item.href} className={active ? "sideLink sideLinkActive" : "sideLink"} aria-current={active ? "page" : undefined}>
            <span className="sideIcon"><Icon name={item.icon}/></span><span className="sideLabel">{t(item.label)}</span><span className="sideIndex">{item.short}</span>
          </Link>;
        })}
      </section>)}
    </nav>
    <div className="languageSwitch" role="group" aria-label="Language / Langue"><button type="button" className={language === "fr" ? "active" : ""} onClick={() => setLanguage("fr")} aria-pressed={language === "fr"}>FR</button><span aria-hidden="true">|</span><button type="button" className={language === "en" ? "active" : ""} onClick={() => setLanguage("en")} aria-pressed={language === "en"}>EN</button></div>
    <div className="navFooter"><span className="navStatus"/><div><b>{t("Research environment")}</b><small>{t("Synthetic data · No clinical use")}</small></div></div>
  </aside>;
}
