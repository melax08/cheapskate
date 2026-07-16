export type AuthorizationTokens = {
  access_token: string;
  refresh_token: string;
};

export type User = {
  id: number;
  telegram_id: number;
  telegram_username: string | null;
  telegram_first_name: string;
  telegram_last_name: string | null;
  created_at: string;
};

export type Category = {
  id: number;
  name: string;
  is_visible: boolean;
};

export type CategoryWithExpenses = Category & {
  expenses_count: number;
};

export type CategoryPayload = {
  name: string;
  is_visible?: boolean;
};

export type CategoryUpdatePayload = {
  name?: string;
  is_visible?: boolean;
};

export type Currency = {
  id: number;
  name: string;
  letter_code: string;
  country: string;
};

export type CurrencyPayload = {
  name: string;
  letter_code: string;
  country: string;
};

export type CurrencyUpdatePayload = {
  name?: string;
  letter_code?: string;
  country?: string;
};

export type Settings = {
  id: number;
  budget: string | number;
  default_currency: Currency | null;
};

export type SettingsUpdatePayload = {
  budget?: string;
  default_currency_id?: number;
};
