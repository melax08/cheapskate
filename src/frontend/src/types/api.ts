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
  symbol: string | null;
};

export type CurrencyPayload = {
  name: string;
  letter_code: string;
  country: string;
  symbol: string | null;
};

export type CurrencyUpdatePayload = {
  name?: string;
  letter_code?: string;
  country?: string;
  symbol?: string | null;
};

export type MoneySpent = {
  budget: string | number;
  money_spent: string | number;
  current_datetime: string;
  default_currency: Currency;
};

export type StatisticsPeriod = {
  year: number;
  month: number;
};

export type CategoryStatistics = {
  name: string;
  amount: string | number;
};

export type DayStatistics = {
  date: string;
  total: string | number;
  categories: CategoryStatistics[];
};

export type MonthYearStatistics = {
  period: StatisticsPeriod;
  days: DayStatistics[];
  average_per_day: string | number;
  summary: {
    total: string | number;
    categories: CategoryStatistics[];
  };
  currency: Currency;
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

export type Expense = {
  id: number;
  amount: string | number;
  description: string | null;
  category_id: number;
  currency_id: number | null;
  date: string;
  user_id?: number | null;
};

export type ExpenseDetail = {
  id: number;
  amount: string | number;
  description: string | null;
  category: Category;
  currency: Currency | null;
  date: string;
};

export type ExpenseWithMoneyLeft = ExpenseDetail & {
  money_left: string | number;
};

export type ExpensePayload = {
  amount: string;
  description?: string | null;
  category_id: number;
  currency_id?: number | null;
};

export type ExpenseUpdatePayload = {
  amount?: string;
  description?: string | null;
  category_id?: number;
  currency_id?: number | null;
};

export type CursorPage<T> = {
  items: T[];
  total?: number | null;
  current_page?: string | null;
  current_page_backwards?: string | null;
  previous_page?: string | null;
  next_page?: string | null;
};
