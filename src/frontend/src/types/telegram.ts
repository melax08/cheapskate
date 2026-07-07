export type TelegramThemeParams = {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
  header_bg_color?: string;
  accent_text_color?: string;
  section_bg_color?: string;
  section_header_text_color?: string;
  destructive_text_color?: string;
};

export type TelegramWebAppUser = {
  id: number;
  is_bot?: boolean;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
};

export type TelegramWebApp = {
  initData: string;
  initDataUnsafe?: {
    user?: TelegramWebAppUser;
    auth_date?: number;
    hash?: string;
  };
  colorScheme: "light" | "dark";
  themeParams: TelegramThemeParams;
  ready: () => void;
  expand: () => void;
  close: () => void;
  MainButton?: {
    hide: () => void;
  };
};

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export {};
