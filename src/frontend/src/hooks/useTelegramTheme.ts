import { useEffect } from "react";
import { getTelegramWebApp } from "../services/authService";

export const useTelegramTheme = () => {
  useEffect(() => {
    const webApp = getTelegramWebApp();

    webApp?.ready();
    webApp?.expand();
    webApp?.MainButton?.hide();

    const themeParams = webApp?.themeParams ?? {};
    const root = document.documentElement;

    Object.entries(themeParams).forEach(([key, value]) => {
      if (value) {
        root.style.setProperty(`--tg-${key.replace(/_/g, "-")}`, value);
      }
    });

    if (webApp?.colorScheme) {
      root.dataset.theme = webApp.colorScheme;
    }
  }, []);
};
