import "./globals.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/manrope";
import AppNavigation from "./components/AppNavigation";
import { I18nProvider } from "./i18n/I18nProvider";
export const metadata = {
  title: "PREVIA Health AI | Precision prevention research demo",
  description: "A privacy-conscious, synthetic population health research demonstration for Future Health 2026.",
};
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="en" suppressHydrationWarning><body><I18nProvider><div className="appFrame"><AppNavigation/><div className="appMain"><div className="mobileContext"><span>PREVIA</span><small>Research demonstration</small></div>{children}</div></div></I18nProvider></body></html>;
}
