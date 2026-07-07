import { authorizationApi } from "./apiClient";
import { tokenStorage } from "./tokenStorage";
import type { User } from "../types/api";

export const getTelegramWebApp = () => window.Telegram?.WebApp;

const getTelegramInitData = (): string => getTelegramWebApp()?.initData ?? "";

const authorizeWithTelegram = async (): Promise<User> => {
  const initData = getTelegramInitData();

  if (!initData) {
    throw new Error("Telegram WebApp data is empty. Откройте приложение внутри Telegram.");
  }

  const tokens = await authorizationApi.authorizeTelegramWebApp(initData);
  tokenStorage.setTokens(tokens);

  return authorizationApi.getMe();
};

export const authService = {
  async loadCurrentUser(): Promise<User> {
    const hasStoredSession = Boolean(tokenStorage.getAccessToken() && tokenStorage.getRefreshToken());

    if (!hasStoredSession) {
      return authorizeWithTelegram();
    }

    try {
      return await authorizationApi.getMe();
    } catch (error) {
      tokenStorage.clear();

      if (getTelegramInitData()) {
        return authorizeWithTelegram();
      }

      throw error;
    }
  },

  async reauthorize(): Promise<User> {
    tokenStorage.clear();
    return authorizeWithTelegram();
  },

  clearSession(): void {
    tokenStorage.clear();
  }
};
