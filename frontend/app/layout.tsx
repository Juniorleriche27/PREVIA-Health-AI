import "./globals.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/manrope";
import AppNavigation from "./components/AppNavigation";
import { I18nProvider, TranslatedText } from "./i18n/I18nProvider";
export const metadata = {
  title: "PREVIA Health AI",
  description: "A privacy-conscious, synthetic population health research demonstration for Future Health 2026.",
};
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  const restoreLanguage = `try{var l=localStorage.getItem("previa-language");if(l!=="fr"&&l!=="en")l=navigator.languages.some(function(x){return x.toLowerCase().startsWith("fr")})?"fr":"en";document.documentElement.lang=l;document.documentElement.dataset.language=l}catch(e){}`;
  return <html lang="en" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{__html: restoreLanguage}} /></head><body><I18nProvider><div className="appFrame"><AppNavigation/><div className="appMain"><div className="mobileContext"><span>PREVIA</span><small><TranslatedText>Research demonstration</TranslatedText></small></div>{children}</div></div></I18nProvider></body></html>;
}
