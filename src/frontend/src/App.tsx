import { FormEvent, useCallback, useEffect, useRef, useMemo, useState } from "react";
import { authService, getTelegramWebApp } from "./services/authService";
import {
  ApiError,
  categoriesApi,
  currenciesApi,
  expensesApi,
  settingsApi,
  statisticsApi,
  usersApi
} from "./services/apiClient";
import type {
  CategoryWithExpenses,
  Currency,
  CurrencyPayload,
  Expense,
  ExpenseDetail,
  ExpensePayload,
  MoneySpent,
  Settings,
  User
} from "./types/api";
import { useTelegramTheme } from "./hooks/useTelegramTheme";

type AuthState =
  | { status: "loading"; user: null; error: null }
  | { status: "authenticated"; user: User; error: null }
  | { status: "error"; user: null; error: string };

type View = "statistics" | "overview" | "categories" | "currencies" | "expenses" | "settings";

type CategoriesState = {
  status: "idle" | "loading" | "ready" | "error";
  items: CategoryWithExpenses[];
  error: string | null;
};

type CurrenciesState = {
  status: "idle" | "loading" | "ready" | "error";
  items: Currency[];
  error: string | null;
};

type SettingsState = {
  status: "idle" | "loading" | "ready" | "error";
  settings: Settings | null;
  currencies: Currency[];
  error: string | null;
};

type ExpensesState = {
  status: "idle" | "loading" | "ready" | "error";
  items: Expense[];
  nextCursor: string | null;
  error: string | null;
};

type ExpenseFilters = {
  user: number | null;
  category: number | null;
  currency: number | null;
};

const navigationItems: Array<{ id: View; label: string; isComingSoon?: boolean; isHidden?: boolean }> = [
  { id: "expenses", label: "Траты" },
  { id: "statistics", label: "Статистика" },
  { id: "categories", label: "Категории" },
  { id: "currencies", label: "Валюты" },
  { id: "settings", label: "Настройки" },
  { id: "overview", label: "Профиль" }
];

type StatisticPeriod = {
  spent: number;
  previous: number;
  days: number[];
  categories: Array<{ name: string; amount: number; color: string }>;
};

const statisticData: Record<number, Record<number, StatisticPeriod>> = {
  2026: {
    7: {
      spent: 46280,
      previous: 51240,
      days: [900, 1280, 640, 2100, 1780, 1200, 2450, 980, 1600, 2840, 1340, 820, 1980, 1160, 2500, 740, 1560, 2240, 1100, 2920, 1370, 860, 1740, 2310, 940, 1860, 1260, 2040, 1520, 1160, 720],
      categories: [
        { name: "Продукты", amount: 14240, color: "#2f80ed" },
        { name: "Кафе", amount: 9840, color: "#f59e0b" },
        { name: "Транспорт", amount: 7210, color: "#8b5cf6" },
        { name: "Дом", amount: 6780, color: "#10b981" },
        { name: "Другое", amount: 8210, color: "#94a3b8" }
      ],
    },
    6: {
      spent: 51240,
      previous: 48790,
      days: [1200, 1700, 900, 2300, 1400, 1900, 2800, 1100, 2100, 1600, 900, 2500, 1800, 1300, 2200, 950, 1750, 2600, 1450, 2050, 1200, 2900, 1000, 1850, 2350, 1250, 1950, 1500, 2700, 1490],
      categories: [
        { name: "Продукты", amount: 16520, color: "#2f80ed" },
        { name: "Дом", amount: 11240, color: "#10b981" },
        { name: "Кафе", amount: 9080, color: "#f59e0b" },
        { name: "Транспорт", amount: 6840, color: "#8b5cf6" },
        { name: "Другое", amount: 7560, color: "#94a3b8" }
      ],
    }
  },
  2025: {
    11: {
      spent: 43860,
      previous: 47120,
      days: [980, 1420, 2100, 760, 1880, 1240, 2520, 950, 1680, 2250, 1180, 860, 1940, 1340, 2480, 720, 1590, 2170, 1040, 2760, 1310, 810, 1650, 2260, 920, 1770, 1210, 1980, 1450, 880],
      categories: [
        { name: "Продукты", amount: 13900, color: "#2f80ed" },
        { name: "Транспорт", amount: 8860, color: "#8b5cf6" },
        { name: "Кафе", amount: 7640, color: "#f59e0b" },
        { name: "Дом", amount: 6920, color: "#10b981" },
        { name: "Другое", amount: 6540, color: "#94a3b8" }
      ],
    }
  }
};

const monthNames = [
  "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "long",
    year: "numeric"
  }).format(new Date(value));

const formatDateTime = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));

const formatBudget = (value: string | number) =>
  new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(Number(value));

const formatWholeMoney = (value: string | number) =>
  new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Number(value));

const formatMoney = (value: string | number) =>
  new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3
  }).format(Number(value));

const getDisplayName = (user: User) =>
  [user.telegram_first_name, user.telegram_last_name].filter(Boolean).join(" ");

const getExpenseUserName = (user: User) => {
  if (user.telegram_last_name) {
    return `${user.telegram_first_name} ${user.telegram_last_name}`;
  }

  return user.telegram_username ? `@${user.telegram_username}` : user.telegram_first_name;
};

const getInitials = (user: User) =>
  [user.telegram_first_name, user.telegram_last_name]
    .filter(Boolean)
    .map((name) => name?.[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

const confirmDeletion = (itemName: string) =>
  window.confirm(`Вы уверены, что хотите удалить ${itemName}?`);

const getErrorMessage = (error: unknown): string => {
  if (error instanceof ApiError) {
    if (typeof error.detail === "string") {
      return error.detail;
    }

    if (error.detail && typeof error.detail === "object" && "detail" in error.detail) {
      const detail = error.detail.detail;

      if (typeof detail === "string") {
        return detail;
      }

      if (
        detail &&
        typeof detail === "object" &&
        "message" in detail &&
        typeof detail.message === "string"
      ) {
        return detail.message;
      }
    }

    return `Сервер вернул ошибку ${error.status}`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Что-то пошло не так";
};

const EmptyModule = ({ title }: { title: string }) => (
  <section className="panel empty-module">
    <p className="eyebrow">Скоро</p>
    <h2>{title}</h2>
    <p>Раздел уже зарезервирован в интерфейсе, чтобы позже добавить управление без смены общей навигации.</p>
  </section>
);

const OverviewView = ({
  user,
  subtitle,
  onRefresh,
  onReauthorize
}: {
  user: User;
  subtitle: string;
  onRefresh: () => void;
  onReauthorize: () => void;
}) => (
  <>
    <section className="profile-card">
      <div className="avatar">{getInitials(user)}</div>
      <div>
        <p className="profile-label">Пользователь Telegram</p>
        <h2>{getDisplayName(user)}</h2>
        <p>{subtitle}</p>
      </div>
    </section>

    <section className="details-grid" aria-label="Информация о пользователе">
      <article className="detail-item">
        <span>ID в приложении</span>
        <strong>{user.id}</strong>
      </article>
      <article className="detail-item">
        <span>Telegram ID</span>
        <strong>{user.telegram_id}</strong>
      </article>
      <article className="detail-item">
        <span>Дата регистрации</span>
        <strong>{formatDate(user.created_at)}</strong>
      </article>
      <article className="detail-item">
        <span>Refresh токен</span>
        <strong>Хранится локально</strong>
      </article>
    </section>

    <section className="quick-actions">
      <button type="button" className="primary-button" onClick={onRefresh}>
        Обновить данные
      </button>
      <button type="button" className="secondary-button" onClick={onReauthorize}>
        Переавторизоваться
      </button>
    </section>
  </>
);

const CategoriesView = () => {
  const [categoriesState, setCategoriesState] = useState<CategoriesState>({
    status: "idle",
    items: [],
    error: null
  });
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newCategoryVisible, setNewCategoryVisible] = useState(true);
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState("");
  const [pendingCategoryId, setPendingCategoryId] = useState<number | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);

  const loadCategories = useCallback(async () => {
    setCategoriesState((current) => ({
      status: current.items.length ? "ready" : "loading",
      items: current.items,
      error: null
    }));

    try {
      const items = await categoriesApi.list();
      setCategoriesState({ status: "ready", items, error: null });
    } catch (error) {
      setCategoriesState((current) => ({
        status: "error",
        items: current.items,
        error: getErrorMessage(error)
      }));
    }
  }, []);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  const createCategory = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const name = newCategoryName.trim();
    if (!name) {
      return;
    }

    setIsCreating(true);
    setCategoriesState((current) => ({ ...current, error: null }));

    try {
      await categoriesApi.create({ name, is_visible: newCategoryVisible });
      setNewCategoryName("");
      setNewCategoryVisible(true);
      setIsCreateFormOpen(false);
      await loadCategories();
    } catch (error) {
      setCategoriesState((current) => ({ ...current, status: "error", error: getErrorMessage(error) }));
    } finally {
      setIsCreating(false);
    }
  };

  const startEditing = (category: CategoryWithExpenses) => {
    setEditingCategoryId(category.id);
    setEditingName(category.name);
  };

  const cancelEditing = () => {
    setEditingCategoryId(null);
    setEditingName("");
  };

  const saveCategoryName = async (category: CategoryWithExpenses) => {
    const name = editingName.trim();

    if (!name || name === category.name) {
      cancelEditing();
      return;
    }

    setPendingCategoryId(category.id);

    try {
      await categoriesApi.update(category.id, { name });
      cancelEditing();
      await loadCategories();
    } catch (error) {
      setCategoriesState((current) => ({ ...current, status: "error", error: getErrorMessage(error) }));
    } finally {
      setPendingCategoryId(null);
    }
  };

  const toggleVisibility = async (category: CategoryWithExpenses) => {
    setPendingCategoryId(category.id);

    try {
      await categoriesApi.update(category.id, { is_visible: !category.is_visible });
      await loadCategories();
    } catch (error) {
      setCategoriesState((current) => ({ ...current, status: "error", error: getErrorMessage(error) }));
    } finally {
      setPendingCategoryId(null);
    }
  };

  const deleteCategory = async (category: CategoryWithExpenses) => {
    if (
      category.expenses_count > 0 ||
      !confirmDeletion(`категорию «${category.name}»`)
    ) {
      return;
    }

    setPendingCategoryId(category.id);

    try {
      await categoriesApi.delete(category.id);
      await loadCategories();
    } catch (error) {
      setCategoriesState((current) => ({ ...current, status: "error", error: getErrorMessage(error) }));
    } finally {
      setPendingCategoryId(null);
    }
  };

  return (
    <section className="module">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Справочник</p>
          <h2>Категории трат</h2>
        </div>
        <div className="heading-actions">
          <div className="category-count" aria-label="Всего категорий">
            <span>Всего</span>
            <strong>{categoriesState.items.length}</strong>
          </div>
          <button
            type="button"
            className="primary-button compact-primary-button"
            onClick={() => setIsCreateFormOpen((isOpen) => !isOpen)}
          >
            {isCreateFormOpen ? "Скрыть" : "Добавить"}
          </button>
          <button type="button" className="ghost-button" onClick={() => void loadCategories()}>
            Обновить
          </button>
        </div>
      </div>

      {isCreateFormOpen && (
        <form className="category-form" onSubmit={(event) => void createCategory(event)}>
          <label className="text-field">
            <span>Новая категория</span>
            <input
              type="text"
              value={newCategoryName}
              onChange={(event) => setNewCategoryName(event.target.value)}
              placeholder="Например, продукты"
              maxLength={255}
              autoFocus
            />
          </label>
          <label className="toggle-field">
            <input
              type="checkbox"
              checked={newCategoryVisible}
              onChange={(event) => setNewCategoryVisible(event.target.checked)}
            />
            <span>Показывать в боте</span>
          </label>
          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={isCreating || !newCategoryName.trim()}>
              {isCreating ? "Создаем..." : "Создать"}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setIsCreateFormOpen(false);
                setNewCategoryName("");
                setNewCategoryVisible(true);
              }}
            >
              Отмена
            </button>
          </div>
        </form>
      )}

      {categoriesState.error && <p className="inline-error">{categoriesState.error}</p>}

      {categoriesState.status === "loading" && (
        <div className="list-state" aria-live="polite">
          <div className="loader small-loader" />
          <p>Загружаем категории.</p>
        </div>
      )}

      {categoriesState.status !== "loading" && categoriesState.items.length === 0 && (
        <div className="list-state">
          <h3>Категорий пока нет</h3>
          <p>Создайте первую категорию, чтобы потом привязывать к ней траты.</p>
        </div>
      )}

      {categoriesState.items.length > 0 && (
        <div className="category-list">
          {categoriesState.items.map((category) => {
            const isEditing = editingCategoryId === category.id;
            const isPending = pendingCategoryId === category.id;
            const canDelete = category.expenses_count === 0;

            return (
              <article className="category-item" key={category.id}>
                <div className="category-main">
                  <span className={category.is_visible ? "visibility-dot" : "visibility-dot muted"} />
                  <div className="category-copy">
                    {isEditing ? (
                      <input
                        className="inline-input"
                        type="text"
                        value={editingName}
                        onChange={(event) => setEditingName(event.target.value)}
                        maxLength={255}
                        autoFocus
                      />
                    ) : (
                      <h3>{category.name}</h3>
                    )}
                    <p>
                      {category.is_visible ? "Отображается в списках" : "Скрыта из списков"} ·{" "}
                      {category.expenses_count} трат
                    </p>
                  </div>
                </div>

                <div className="category-actions">
                  {isEditing ? (
                    <>
                      <button
                        type="button"
                        className="compact-button"
                        disabled={isPending}
                        onClick={() => void saveCategoryName(category)}
                      >
                        Сохранить
                      </button>
                      <button type="button" className="compact-button muted-button" onClick={cancelEditing}>
                        Отмена
                      </button>
                    </>
                  ) : (
                    <>
                      <button type="button" className="compact-button" onClick={() => startEditing(category)}>
                        Изменить
                      </button>
                      <button
                        type="button"
                        className="compact-button"
                        disabled={isPending}
                        onClick={() => void toggleVisibility(category)}
                      >
                        {category.is_visible ? "Скрыть" : "Показать"}
                      </button>
                      <button
                        type="button"
                        className="compact-button danger-button"
                        disabled={!canDelete || isPending}
                        title={canDelete ? "Удалить категорию" : "Нельзя удалить категорию с тратами"}
                        onClick={() => void deleteCategory(category)}
                      >
                        Удалить
                      </button>
                    </>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
};

const createEmptyExpense = (): ExpensePayload => ({
  amount: "",
  description: "",
  category_id: 0,
  currency_id: null
});

const normalizeAmountInput = (value: string) => value.replace(",", ".");

const normalizeExpenseDetail = (expense: ExpenseDetail, userId?: number | null): Expense => ({
  id: expense.id,
  amount: expense.amount,
  description: expense.description,
  category_id: expense.category.id,
  currency_id: expense.currency?.id ?? null,
  date: expense.date,
  user_id: userId
});

const ExpensesView = ({ onExpensesChanged }: { onExpensesChanged: () => void }) => {
  const [expensesState, setExpensesState] = useState<ExpensesState>({
    status: "idle",
    items: [],
    nextCursor: null,
    error: null
  });
  const [categories, setCategories] = useState<CategoryWithExpenses[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [filters, setFilters] = useState<ExpenseFilters>({
    user: null,
    category: null,
    currency: null
  });
  const [newExpense, setNewExpense] = useState<ExpensePayload>(createEmptyExpense);
  const [expensePositions, setExpensePositions] = useState<string[]>([""]);
  const [editingExpenseId, setEditingExpenseId] = useState<number | null>(null);
  const [editingExpense, setEditingExpense] = useState<ExpensePayload>(createEmptyExpense);
  const [pendingExpenseId, setPendingExpenseId] = useState<number | null>(null);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const createFormRef = useRef<HTMLFormElement | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const loadingCursorRef = useRef<string | null>(null);
  const expensesRequestIdRef = useRef(0);
  const activeFiltersCount = Object.values(filters).filter((value) => value !== null).length;
  const visibleCategories = useMemo(
    () => categories.filter((category) => category.is_visible),
    [categories]
  );
  const expensePositionsTotal = useMemo(
    () =>
      Number(
        expensePositions
          .reduce((total, position) => {
            const value = Number(position);
            return total + (position.trim() && Number.isFinite(value) ? value : 0);
          }, 0)
          .toFixed(3)
      ),
    [expensePositions]
  );
  const areExpensePositionValuesValid =
    expensePositions.length > 0 &&
    expensePositions.every((position) => {
      const value = Number(position);
      return position.trim() !== "" && Number.isFinite(value);
    });
  const areExpensePositionsValid = areExpensePositionValuesValid && expensePositionsTotal > 0;

  const syncDefaultCategory = useCallback((items: CategoryWithExpenses[]) => {
    const visibleItems = items.filter((category) => category.is_visible);

    setNewExpense((current) => ({
      ...current,
      category_id: visibleItems.some((category) => category.id === current.category_id)
        ? current.category_id
        : visibleItems[0]?.id || 0
    }));
  }, []);

  const loadDictionaries = useCallback(async () => {
    const [categoriesItems, currenciesItems, usersItems] = await Promise.all([
      categoriesApi.list(),
      currenciesApi.list(),
      usersApi.list()
    ]);
    setCategories(categoriesItems);
    setCurrencies(currenciesItems);
    setUsers(usersItems);
    syncDefaultCategory(categoriesItems);
  }, [syncDefaultCategory]);

  const loadExpenses = useCallback(
    async (cursor: string | null = null) => {
      const isNextPage = Boolean(cursor);
      if (isNextPage) {
        if (loadingCursorRef.current === cursor) {
          return;
        }

        loadingCursorRef.current = cursor;
        setIsLoadingMore(true);
      } else {
        loadingCursorRef.current = null;
        setExpensesState({
          status: "loading",
          items: [],
          nextCursor: null,
          error: null
        });
      }
      const requestId = ++expensesRequestIdRef.current;

      try {
        const page = await expensesApi.list({ cursor, size: 10, ...filters });
        if (requestId !== expensesRequestIdRef.current) {
          return;
        }

        setExpensesState((current) => ({
          status: "ready",
          items: isNextPage ? [...current.items, ...page.items] : page.items,
          nextCursor: page.next_page ?? null,
          error: null
        }));
      } catch (error) {
        if (requestId !== expensesRequestIdRef.current) {
          return;
        }

        setExpensesState((current) => ({
          status: "error",
          items: current.items,
          nextCursor: current.nextCursor,
          error: getErrorMessage(error)
        }));
      } finally {
        if (requestId === expensesRequestIdRef.current) {
          loadingCursorRef.current = null;
          setIsLoadingMore(false);
        }
      }
    },
    [filters]
  );

  useEffect(() => {
    void loadDictionaries().catch((error) => {
      setExpensesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    });
  }, [loadDictionaries]);

  useEffect(() => {
    void loadExpenses();
  }, [loadExpenses]);

  useEffect(() => {
    if (isCreateFormOpen) {
      createFormRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center"
      });
    }
  }, [isCreateFormOpen]);

  useEffect(() => {
    const sentinel = loadMoreRef.current;
    const nextCursor = expensesState.nextCursor;

    if (!sentinel || !nextCursor || isLoadingMore) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          void loadExpenses(nextCursor);
        }
      },
      { rootMargin: "240px 0px" }
    );

    observer.observe(sentinel);

    return () => observer.disconnect();
  }, [expensesState.nextCursor, isLoadingMore, loadExpenses]);

  const setNewExpenseField = (field: keyof ExpensePayload, value: string) => {
    setNewExpense((current) => ({
      ...current,
      [field]:
        field === "category_id" || field === "currency_id"
          ? value
            ? Number(value)
            : field === "currency_id"
              ? null
              : 0
          : field === "amount"
            ? normalizeAmountInput(value)
            : value
    }));
  };

  const setEditingExpenseField = (field: keyof ExpensePayload, value: string) => {
    setEditingExpense((current) => ({
      ...current,
      [field]:
        field === "category_id" || field === "currency_id"
          ? value
            ? Number(value)
            : field === "currency_id"
              ? null
              : 0
          : field === "amount"
            ? normalizeAmountInput(value)
            : value
    }));
  };

  const setExpensePosition = (index: number, value: string) => {
    setExpensePositions((current) =>
      current.map((position, positionIndex) =>
        positionIndex === index ? normalizeAmountInput(value) : position
      )
    );
  };

  const addExpensePosition = () => {
    setExpensePositions((current) => [...current, ""]);
  };

  const removeExpensePosition = (index: number) => {
    setExpensePositions((current) => current.filter((_, positionIndex) => positionIndex !== index));
  };

  const setFilter = (field: keyof ExpenseFilters, value: string) => {
    setFilters((current) => ({
      ...current,
      [field]: value ? Number(value) : null
    }));
  };

  const resetFilters = () => {
    setFilters({ user: null, category: null, currency: null });
  };

  const isExpensePayloadValid = (payload: ExpensePayload) => {
    const amount = Number(payload.amount);
    return Number.isFinite(amount) && amount > 0 && payload.category_id > 0;
  };

  const buildExpensePayload = (payload: ExpensePayload): ExpensePayload => ({
    amount: payload.amount.trim(),
    description: payload.description?.trim() || null,
    category_id: payload.category_id,
    currency_id: payload.currency_id || null
  });

  const createExpense = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!areExpensePositionsValid || newExpense.category_id <= 0) {
      return;
    }

    setIsCreating(true);
    setExpensesState((current) => ({ ...current, error: null }));

    try {
      await expensesApi.create(
        buildExpensePayload({ ...newExpense, amount: String(expensePositionsTotal) })
      );
      onExpensesChanged();
      setNewExpense({
        ...createEmptyExpense(),
        category_id: visibleCategories[0]?.id || 0
      });
      setExpensePositions([""]);
      setIsCreateFormOpen(false);
      await loadExpenses();
    } catch (error) {
      setExpensesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setIsCreating(false);
    }
  };

  const startEditingExpense = (expense: Expense) => {
    setEditingExpenseId(expense.id);
    setEditingExpense({
      amount: String(expense.amount),
      description: expense.description ?? "",
      category_id: expense.category_id,
      currency_id: expense.currency_id
    });
  };

  const cancelEditingExpense = () => {
    setEditingExpenseId(null);
    setEditingExpense(createEmptyExpense());
  };

  const saveExpense = async (expense: Expense) => {
    if (!isExpensePayloadValid(editingExpense)) {
      return;
    }

    setPendingExpenseId(expense.id);

    try {
      const updatedExpense = await expensesApi.update(expense.id, buildExpensePayload(editingExpense));
      onExpensesChanged();
      setExpensesState((current) => ({
        ...current,
        status: "ready",
        items: current.items.map((item) =>
          item.id === expense.id ? normalizeExpenseDetail(updatedExpense, expense.user_id) : item
        ),
        error: null
      }));
      cancelEditingExpense();
    } catch (error) {
      setExpensesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setPendingExpenseId(null);
    }
  };

  const deleteExpense = async (expense: Expense) => {
    if (!confirmDeletion(`трату на сумму ${formatMoney(expense.amount)}`)) {
      return;
    }

    setPendingExpenseId(expense.id);

    try {
      await expensesApi.delete(expense.id);
      onExpensesChanged();
      setExpensesState((current) => ({
        ...current,
        status: "ready",
        items: current.items.filter((item) => item.id !== expense.id),
        error: null
      }));
    } catch (error) {
      setExpensesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setPendingExpenseId(null);
    }
  };

  const renderExpenseForm = (
    payload: ExpensePayload,
    setField: (field: keyof ExpensePayload, value: string) => void,
    submitLabel: string,
    isDisabled: boolean,
    categoryOptions: CategoryWithExpenses[],
    options: {
      showAmount?: boolean;
      isValid?: boolean;
      onCancel?: () => void;
    } = {}
  ) => (
    <>
      {options.showAmount !== false && (
        <label className="text-field">
          <span>Сумма</span>
          <input
            type="number"
            min="0"
            step="0.001"
            value={payload.amount}
            onChange={(event) => setField("amount", event.target.value)}
            placeholder="0"
            autoFocus
          />
        </label>
      )}
      <label className="text-field">
        <span>Категория</span>
        <select
          value={payload.category_id || ""}
          onChange={(event) => setField("category_id", event.target.value)}
          disabled={categoryOptions.length === 0}
        >
          <option value="">Выберите категорию</option>
          {categoryOptions.map((category) => (
            <option value={category.id} key={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </label>
      <label className="text-field">
        <span>Валюта</span>
        <select
          value={payload.currency_id ?? ""}
          onChange={(event) => setField("currency_id", event.target.value)}
        >
          <option value="">По умолчанию</option>
          {currencies.map((currency) => (
            <option value={currency.id} key={currency.id}>
              {currency.name} ({getCurrencySymbol(currency)})
            </option>
          ))}
        </select>
      </label>
      <label className="text-field">
        <span>Описание</span>
        <input
          type="text"
          value={payload.description ?? ""}
          onChange={(event) => setField("description", event.target.value)}
          placeholder="Опционально"
          maxLength={255}
        />
      </label>
      <div className="form-actions">
        <button
          type="submit"
          className="primary-button"
          disabled={
            isDisabled ||
            !(options.isValid ?? isExpensePayloadValid(payload)) ||
            categoryOptions.length === 0
          }
        >
          {submitLabel}
        </button>
        {options.onCancel && (
          <button type="button" className="secondary-button" onClick={options.onCancel}>
            Отмена
          </button>
        )}
      </div>
    </>
  );

  return (
    <section className="module">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Журнал</p>
          <h2>Траты</h2>
        </div>
        <div className="heading-actions">
          <button
            type="button"
            className={`ghost-button${activeFiltersCount ? " active-filter-button" : ""}`}
            aria-expanded={isFiltersOpen}
            aria-controls="expense-filters"
            onClick={() => setIsFiltersOpen((isOpen) => !isOpen)}
          >
            Фильтры{activeFiltersCount ? ` · ${activeFiltersCount}` : ""}
          </button>
          <button
            type="button"
            className="primary-button compact-primary-button"
            onClick={() => setIsCreateFormOpen((isOpen) => !isOpen)}
          >
            {isCreateFormOpen ? "Скрыть" : "Добавить"}
          </button>
          <button type="button" className="ghost-button" onClick={() => void loadExpenses()}>
            Обновить
          </button>
        </div>
      </div>

      {isFiltersOpen && (
        <div id="expense-filters" className="expense-filters" aria-label="Фильтры трат">
          <div className="filter-heading">
            <div>
              <strong>Фильтры</strong>
              <span>
                {activeFiltersCount
                  ? `Выбрано: ${activeFiltersCount}`
                  : "Показаны все траты"}
              </span>
            </div>
            {activeFiltersCount > 0 && (
              <button type="button" className="ghost-button" onClick={resetFilters}>
                Сбросить
              </button>
            )}
          </div>
          <div className="filter-grid">
            <label className="text-field">
              <span>Пользователь</span>
              <select
                value={filters.user ?? ""}
                onChange={(event) => setFilter("user", event.target.value)}
              >
                <option value="">Все пользователи</option>
                {users.map((user) => (
                  <option value={user.id} key={user.id}>
                    {getExpenseUserName(user)}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-field">
              <span>Категория</span>
              <select
                value={filters.category ?? ""}
                onChange={(event) => setFilter("category", event.target.value)}
              >
                <option value="">Все категории</option>
                {categories.map((category) => (
                  <option value={category.id} key={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-field">
              <span>Валюта</span>
              <select
                value={filters.currency ?? ""}
                onChange={(event) => setFilter("currency", event.target.value)}
              >
                <option value="">Все валюты</option>
                {currencies.map((currency) => (
                  <option value={currency.id} key={currency.id}>
                    {currency.name} ({getCurrencySymbol(currency)})
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      )}

      {isCreateFormOpen && (
        <form
          ref={createFormRef}
          className="expense-form"
          onSubmit={(event) => void createExpense(event)}
        >
          <div className="expense-positions">
            <div className="expense-positions-heading">
              <div>
                <strong>Позиции</strong>
                <span>Можно указывать положительные и отрицательные значения</span>
              </div>
              <button type="button" className="ghost-button" onClick={addExpensePosition}>
                Добавить позицию
              </button>
            </div>
            <div className="expense-position-list">
              {expensePositions.map((position, index) => (
                <div className="expense-position-row" key={index}>
                  <label className="text-field">
                    <span>Позиция {index + 1}</span>
                    <input
                      type="number"
                      step="0.001"
                      value={position}
                      onChange={(event) => setExpensePosition(index, event.target.value)}
                      placeholder="0"
                      autoFocus={index === 0}
                    />
                  </label>
                  <button
                    type="button"
                    className="compact-button danger-button"
                    disabled={expensePositions.length === 1}
                    aria-label={`Удалить позицию ${index + 1}`}
                    onClick={() => removeExpensePosition(index)}
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </div>
            <div className={`expense-total${expensePositionsTotal > 0 ? "" : " invalid"}`}>
              <span>Итоговая сумма</span>
              <strong>{formatMoney(expensePositionsTotal)}</strong>
            </div>
            {!areExpensePositionsValid && expensePositions.some((position) => position.trim()) && (
              <p className="expense-total-hint">
                {areExpensePositionValuesValid
                  ? "Итоговая сумма должна быть больше нуля."
                  : "Заполните все добавленные позиции."}
              </p>
            )}
          </div>
          {renderExpenseForm(
            newExpense,
            setNewExpenseField,
            isCreating ? "Создаем..." : "Создать",
            isCreating,
            visibleCategories,
            {
              showAmount: false,
              isValid: areExpensePositionsValid && newExpense.category_id > 0,
              onCancel: () => {
                setIsCreateFormOpen(false);
                setNewExpense({
                  ...createEmptyExpense(),
                  category_id: visibleCategories[0]?.id || 0
                });
                setExpensePositions([""]);
              }
            }
          )}
        </form>
      )}

      {visibleCategories.length === 0 && expensesState.status !== "loading" && (
        <p className="inline-error">
          Чтобы добавить трату, сначала создайте или покажите хотя бы одну категорию.
        </p>
      )}

      {expensesState.error && <p className="inline-error">{expensesState.error}</p>}

      {expensesState.status === "loading" && (
        <div className="list-state" aria-live="polite">
          <div className="loader small-loader" />
          <p>Загружаем траты.</p>
        </div>
      )}

      {expensesState.status !== "loading" && expensesState.items.length === 0 && (
        <div className="list-state">
          <h3>{activeFiltersCount ? "Ничего не найдено" : "Трат пока нет"}</h3>
          <p>
            {activeFiltersCount
              ? "Попробуйте изменить или сбросить фильтры."
              : "Добавьте первую запись, чтобы вести историю расходов."}
          </p>
        </div>
      )}

      {expensesState.items.length > 0 && (
        <>
          <div className="expense-list">
            {expensesState.items.map((expense) => {
              const isEditing = editingExpenseId === expense.id;
              const isPending = pendingExpenseId === expense.id;
              const category = categories.find((item) => item.id === expense.category_id);
              const currency = expense.currency_id
                ? currencies.find((item) => item.id === expense.currency_id)
                : null;
              const expenseUser = expense.user_id
                ? users.find((item) => item.id === expense.user_id)
                : null;

              return (
                <article className="expense-item" key={expense.id}>
                  {isEditing ? (
                    <form className="expense-edit-form" onSubmit={(event) => {
                      event.preventDefault();
                      void saveExpense(expense);
                    }}>
                      {renderExpenseForm(
                        editingExpense,
                        setEditingExpenseField,
                        "Сохранить",
                        Boolean(isPending),
                        categories,
                        { onCancel: cancelEditingExpense }
                      )}
                    </form>
                  ) : (
                    <>
                      <div className="expense-main">
                        <div>
                          <h3>{category?.name ?? `Категория #${expense.category_id}`}</h3>
                          <p>{expense.description || "Без описания"}</p>
                        </div>
                        <strong>
                          {formatMoney(expense.amount)}
                          {currency ? ` ${getCurrencySymbol(currency)}` : ""}
                        </strong>
                      </div>
                      <div className="expense-meta">
                        <span>{formatDateTime(expense.date)}</span>
                        <span>{currency?.name ?? "Валюта по умолчанию"}</span>
                        <span>
                          {expenseUser
                            ? getExpenseUserName(expenseUser)
                            : expense.user_id
                              ? "Пользователь не найден"
                              : "Пользователь не указан"}
                        </span>
                      </div>
                      <div className="category-actions">
                        <button
                          type="button"
                          className="compact-button"
                          onClick={() => startEditingExpense(expense)}
                        >
                          Изменить
                        </button>
                        <button
                          type="button"
                          className="compact-button danger-button"
                          disabled={isPending}
                          onClick={() => void deleteExpense(expense)}
                        >
                          Удалить
                        </button>
                      </div>
                    </>
                  )}
                </article>
              );
            })}
          </div>

          {expensesState.nextCursor && (
            <div className="scroll-loader" ref={loadMoreRef} aria-live="polite">
              {isLoadingMore && (
                <>
                  <div className="loader small-loader" />
                  <p>Загружаем еще.</p>
                </>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
};

const createEmptyCurrency = (): CurrencyPayload => ({
  name: "",
  letter_code: "",
  country: "",
  symbol: ""
});

const normalizeCurrencyCode = (value: string) =>
  value
    .replace(/[^a-zA-Z]/g, "")
    .slice(0, 3)
    .toUpperCase();

const normalizeCurrencySymbol = (value: string) => Array.from(value.trim()).slice(0, 1).join("");

const getCurrencySymbol = (currency: Currency) => currency.symbol || currency.letter_code;

const CurrenciesView = () => {
  const [currenciesState, setCurrenciesState] = useState<CurrenciesState>({
    status: "idle",
    items: [],
    error: null
  });
  const [newCurrency, setNewCurrency] = useState<CurrencyPayload>(createEmptyCurrency);
  const [editingCurrencyId, setEditingCurrencyId] = useState<number | null>(null);
  const [editingCurrency, setEditingCurrency] = useState<CurrencyPayload>(createEmptyCurrency);
  const [pendingCurrencyId, setPendingCurrencyId] = useState<number | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);

  const loadCurrencies = useCallback(async () => {
    setCurrenciesState((current) => ({
      status: current.items.length ? "ready" : "loading",
      items: current.items,
      error: null
    }));

    try {
      const items = await currenciesApi.list();
      setCurrenciesState({ status: "ready", items, error: null });
    } catch (error) {
      setCurrenciesState((current) => ({
        status: "error",
        items: current.items,
        error: getErrorMessage(error)
      }));
    }
  }, []);

  useEffect(() => {
    void loadCurrencies();
  }, [loadCurrencies]);

  const setNewCurrencyField = (field: keyof CurrencyPayload, value: string) => {
    setNewCurrency((current) => ({
      ...current,
      [field]: field === "letter_code"
        ? normalizeCurrencyCode(value)
        : field === "symbol"
          ? normalizeCurrencySymbol(value)
          : value
    }));
  };

  const setEditingCurrencyField = (field: keyof CurrencyPayload, value: string) => {
    setEditingCurrency((current) => ({
      ...current,
      [field]: field === "letter_code"
        ? normalizeCurrencyCode(value)
        : field === "symbol"
          ? normalizeCurrencySymbol(value)
          : value
    }));
  };

  const isCurrencyPayloadValid = (currency: CurrencyPayload) =>
    Boolean(currency.name.trim() && currency.country.trim() && currency.letter_code.length === 3);

  const createCurrency = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!isCurrencyPayloadValid(newCurrency)) {
      return;
    }

    setIsCreating(true);
    setCurrenciesState((current) => ({ ...current, error: null }));

    try {
      await currenciesApi.create({
        name: newCurrency.name.trim(),
        letter_code: newCurrency.letter_code,
        country: newCurrency.country.trim(),
        symbol: newCurrency.symbol?.trim() || null
      });
      setNewCurrency(createEmptyCurrency());
      setIsCreateFormOpen(false);
      await loadCurrencies();
    } catch (error) {
      setCurrenciesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setIsCreating(false);
    }
  };

  const startEditingCurrency = (currency: Currency) => {
    setEditingCurrencyId(currency.id);
    setEditingCurrency({
      name: currency.name,
      letter_code: currency.letter_code,
      country: currency.country,
      symbol: currency.symbol ?? ""
    });
  };

  const cancelEditingCurrency = () => {
    setEditingCurrencyId(null);
    setEditingCurrency(createEmptyCurrency());
  };

  const saveCurrency = async (currency: Currency) => {
    if (!isCurrencyPayloadValid(editingCurrency)) {
      return;
    }

    const payload: CurrencyPayload = {
      name: editingCurrency.name.trim(),
      letter_code: editingCurrency.letter_code,
      country: editingCurrency.country.trim(),
      symbol: editingCurrency.symbol?.trim() || null
    };

    if (
      payload.name === currency.name &&
      payload.letter_code === currency.letter_code &&
      payload.country === currency.country &&
      payload.symbol === currency.symbol
    ) {
      cancelEditingCurrency();
      return;
    }

    setPendingCurrencyId(currency.id);

    try {
      await currenciesApi.update(currency.id, payload);
      cancelEditingCurrency();
      await loadCurrencies();
    } catch (error) {
      setCurrenciesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setPendingCurrencyId(null);
    }
  };

  const deleteCurrency = async (currency: Currency) => {
    if (!confirmDeletion(`валюту «${currency.name} (${getCurrencySymbol(currency)})»`)) {
      return;
    }

    setPendingCurrencyId(currency.id);

    try {
      await currenciesApi.delete(currency.id);
      await loadCurrencies();
    } catch (error) {
      setCurrenciesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setPendingCurrencyId(null);
    }
  };

  return (
    <section className="module">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Справочник</p>
          <h2>Валюты</h2>
        </div>
        <div className="heading-actions">
          <div className="category-count" aria-label="Всего валют">
            <span>Всего</span>
            <strong>{currenciesState.items.length}</strong>
          </div>
          <button
            type="button"
            className="primary-button compact-primary-button"
            onClick={() => setIsCreateFormOpen((isOpen) => !isOpen)}
          >
            {isCreateFormOpen ? "Скрыть" : "Добавить"}
          </button>
          <button type="button" className="ghost-button" onClick={() => void loadCurrencies()}>
            Обновить
          </button>
        </div>
      </div>

      {isCreateFormOpen && (
        <form className="currency-form" onSubmit={(event) => void createCurrency(event)}>
          <label className="text-field">
            <span>Название</span>
            <input
              type="text"
              value={newCurrency.name}
              onChange={(event) => setNewCurrencyField("name", event.target.value)}
              placeholder="Российский рубль"
              maxLength={255}
              autoFocus
            />
          </label>
          <label className="text-field code-field">
            <span>Код</span>
            <input
              type="text"
              value={newCurrency.letter_code}
              onChange={(event) => setNewCurrencyField("letter_code", event.target.value)}
              placeholder="RUB"
              maxLength={3}
              inputMode="text"
            />
          </label>
          <label className="text-field symbol-field">
            <span>Символ</span>
            <input
              type="text"
              value={newCurrency.symbol ?? ""}
              onChange={(event) => setNewCurrencyField("symbol", event.target.value)}
              placeholder="₽"
              maxLength={1}
              aria-label="Символ валюты"
            />
          </label>
          <label className="text-field">
            <span>Страна</span>
            <input
              type="text"
              value={newCurrency.country}
              onChange={(event) => setNewCurrencyField("country", event.target.value)}
              placeholder="Россия"
              maxLength={255}
            />
          </label>
          <div className="form-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={isCreating || !isCurrencyPayloadValid(newCurrency)}
            >
              {isCreating ? "Создаем..." : "Создать"}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setIsCreateFormOpen(false);
                setNewCurrency(createEmptyCurrency());
              }}
            >
              Отмена
            </button>
          </div>
        </form>
      )}

      {currenciesState.error && <p className="inline-error">{currenciesState.error}</p>}

      {currenciesState.status === "loading" && (
        <div className="list-state" aria-live="polite">
          <div className="loader small-loader" />
          <p>Загружаем валюты.</p>
        </div>
      )}

      {currenciesState.status !== "loading" && currenciesState.items.length === 0 && (
        <div className="list-state">
          <h3>Валют пока нет</h3>
          <p>Добавьте первую валюту, чтобы затем использовать ее в тратах и настройках.</p>
        </div>
      )}

      {currenciesState.items.length > 0 && (
        <div className="category-list">
          {currenciesState.items.map((currency) => {
            const isEditing = editingCurrencyId === currency.id;
            const isPending = pendingCurrencyId === currency.id;

            return (
              <article className="currency-item" key={currency.id}>
                <div className="currency-copy">
                  {isEditing ? (
                    <div className="currency-edit-grid">
                      <label className="text-field">
                        <span>Название</span>
                        <input
                          type="text"
                          value={editingCurrency.name}
                          onChange={(event) => setEditingCurrencyField("name", event.target.value)}
                          maxLength={255}
                          autoFocus
                        />
                      </label>
                      <label className="text-field code-field">
                        <span>Код</span>
                        <input
                          type="text"
                          value={editingCurrency.letter_code}
                          onChange={(event) => setEditingCurrencyField("letter_code", event.target.value)}
                          maxLength={3}
                        />
                      </label>
                      <label className="text-field symbol-field">
                        <span>Символ</span>
                        <input
                          type="text"
                          value={editingCurrency.symbol ?? ""}
                          onChange={(event) => setEditingCurrencyField("symbol", event.target.value)}
                          placeholder="₽"
                          maxLength={1}
                          aria-label="Символ валюты"
                        />
                      </label>
                      <label className="text-field">
                        <span>Страна</span>
                        <input
                          type="text"
                          value={editingCurrency.country}
                          onChange={(event) => setEditingCurrencyField("country", event.target.value)}
                          maxLength={255}
                        />
                      </label>
                    </div>
                  ) : (
                    <>
                      <div className="currency-title-row">
                        <h3>{currency.name}</h3>
                        <span className="currency-symbol">{getCurrencySymbol(currency)}</span>
                        <span className="currency-letter-code">{currency.letter_code}</span>
                      </div>
                      <p>{currency.country}</p>
                    </>
                  )}
                </div>

                <div className="category-actions">
                  {isEditing ? (
                    <>
                      <button
                        type="button"
                        className="compact-button"
                        disabled={isPending || !isCurrencyPayloadValid(editingCurrency)}
                        onClick={() => void saveCurrency(currency)}
                      >
                        Сохранить
                      </button>
                      <button
                        type="button"
                        className="compact-button muted-button"
                        onClick={cancelEditingCurrency}
                      >
                        Отмена
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="compact-button"
                        onClick={() => startEditingCurrency(currency)}
                      >
                        Изменить
                      </button>
                      <button
                        type="button"
                        className="compact-button danger-button"
                        disabled={isPending}
                        onClick={() => void deleteCurrency(currency)}
                      >
                        Удалить
                      </button>
                    </>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
};

const MonthlyBalance = () => {
  const [data, setData] = useState<MoneySpent | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadMoneySpent = useCallback(async () => {
    setError(null);

    try {
      setData(await statisticsApi.getMoneySpent());
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }, []);

  useEffect(() => {
    void loadMoneySpent();
  }, [loadMoneySpent]);

  if (!data) {
    return (
      <section className={`balance-card balance-card-state${error ? " error" : ""}`} aria-live="polite">
        {error ? (
          <>
            <div><strong>Не удалось загрузить бюджет</strong><span>{error}</span></div>
            <button type="button" onClick={() => void loadMoneySpent()}>Повторить</button>
          </>
        ) : (
          <><div className="balance-loader" /><span>Загружаем бюджет за месяц…</span></>
        )}
      </section>
    );
  }

  const budget = Number(data.budget);
  const spent = Number(data.money_spent);
  const balance = budget - spent;
  const isOverBudget = balance < 0;
  const spentPercent = budget > 0 ? Math.round((spent / budget) * 100) : spent > 0 ? 100 : 0;
  const remainingPercent = Math.max(0, 100 - spentPercent);
  const overrunPercent = Math.max(0, spentPercent - 100);
  const progressWidth = Math.min(100, spentPercent);
  const currencySymbol = getCurrencySymbol(data.default_currency);
  const month = new Intl.DateTimeFormat("ru-RU", { month: "long" }).format(new Date(data.current_datetime));
  const displayedAmount = Math.abs(balance);

  return (
    <section
      className={`balance-card${isOverBudget ? " over-budget" : ""}`}
      aria-label={isOverBudget ? "Перерасход бюджета" : `Остаток бюджета на ${month}`}
    >
      <div className="balance-card-main">
        <div>
          <span>{isOverBudget ? "Перерасход бюджета" : `Остаток на ${month}`}</span>
          <strong>{formatWholeMoney(displayedAmount)} {currencySymbol}</strong>
        </div>
        <div className="balance-percent">
          {isOverBudget ? `+${overrunPercent}%` : `${remainingPercent}%`}
        </div>
      </div>
      <div className="budget-progress" aria-label={`Потрачено ${spentPercent}% бюджета`}>
        <span style={{ width: `${progressWidth}%` }} />
      </div>
      <div className="balance-meta">
        <span>Потрачено {formatWholeMoney(spent)} {currencySymbol}</span>
        <span>Бюджет {formatBudget(budget)} {currencySymbol}</span>
      </div>
    </section>
  );
};

const StatisticsView = () => {
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(7);
  const [mode, setMode] = useState<"month" | "today">("month");
  const [selectedDay, setSelectedDay] = useState<number | null>(null);

  const availableMonths = Object.keys(statisticData[year] ?? {}).map(Number).sort((a, b) => b - a);
  const period = statisticData[year]?.[month] ?? statisticData[year]?.[availableMonths[0]];

  useEffect(() => {
    if (!statisticData[year]?.[month] && availableMonths.length) {
      setMonth(availableMonths[0]);
    }
  }, [year, month, availableMonths]);

  useEffect(() => {
    setSelectedDay(null);
  }, [year, month, mode]);

  if (!period) {
    return null;
  }

  const maxDay = Math.max(...period.days);
  const todayAmount = 2840;
  const displaySpent = mode === "today" ? todayAmount : period.spent;
  const selectedDayAmount = selectedDay === null ? null : period.days[selectedDay];
  const selectedDate = selectedDay === null ? null : new Date(year, month, selectedDay + 1);
  const selectedDateLabel = selectedDate
    ? new Intl.DateTimeFormat("ru-RU", { weekday: "long", day: "numeric", month: "long" }).format(selectedDate)
    : null;
  const selectedDayCategories = selectedDayAmount === null ? null : (() => {
    const patterns = [[0.52, 0.28, 0.2], [0.38, 0.35, 0.27], [0.61, 0.24, 0.15]];
    const pattern = patterns[(selectedDay ?? 0) % patterns.length];
    const names = ["Продукты", "Кафе", "Транспорт"];
    const colors = ["#2f80ed", "#f59e0b", "#8b5cf6"];
    let allocated = 0;

    return pattern.map((weight, index) => {
      const amount = index === pattern.length - 1
        ? selectedDayAmount - allocated
        : Math.round(selectedDayAmount * weight);
      allocated += amount;
      return { name: names[index], amount, color: colors[index] };
    });
  })();
  const displayCategories = mode === "today"
    ? [
        { name: "Продукты", amount: 1460, color: "#2f80ed" },
        { name: "Кафе", amount: 890, color: "#f59e0b" },
        { name: "Транспорт", amount: 490, color: "#8b5cf6" }
      ]
    : selectedDayCategories ?? period.categories;
  const categoryTotal = mode === "today" ? todayAmount : selectedDayAmount ?? period.spent;

  return (
    <section className="statistics-view">
      <div className="section-heading statistics-heading">
        <div>
          <p className="eyebrow">Аналитика расходов</p>
          <h2>Статистика</h2>
        </div>
        <div className="period-selectors">
          <label>
            <span className="sr-only">Год</span>
            <select value={year} onChange={(event) => setYear(Number(event.target.value))}>
              {Object.keys(statisticData).map((value) => <option key={value}>{value}</option>)}
            </select>
          </label>
          <label>
            <span className="sr-only">Месяц</span>
            <select value={month} onChange={(event) => setMonth(Number(event.target.value))}>
              {availableMonths.map((value) => (
                <option value={value} key={value}>{monthNames[value]}</option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="stat-tabs" role="tablist" aria-label="Период статистики">
        <button type="button" role="tab" aria-selected={mode === "month"} className={mode === "month" ? "active" : ""} onClick={() => setMode("month")}>За месяц</button>
        <button type="button" role="tab" aria-selected={mode === "today"} className={mode === "today" ? "active" : ""} onClick={() => setMode("today")}>Сегодня</button>
      </div>

      <section className="spending-hero">
        <div>
          <p>{mode === "today" ? "Потрачено сегодня" : `Потрачено за ${monthNames[month].toLowerCase()}`}</p>
          <strong>{formatBudget(displaySpent)} ₽</strong>
        </div>
      </section>

      {mode === "month" && (
        <section className="stat-card chart-card">
          <div className="stat-card-heading">
            <div><h3>Расходы по дням</h3><p>Нажмите на столбец, чтобы посмотреть детали дня</p></div>
            <span>Среднее {formatBudget(period.spent / period.days.length)} ₽</span>
          </div>
          {selectedDay !== null && selectedDayAmount !== null && (
            <div className="selected-day-summary" aria-live="polite">
              <div>
                <span>Выбранный день</span>
                <strong>{selectedDateLabel}</strong>
              </div>
              <b>{formatBudget(selectedDayAmount)} ₽</b>
              <button type="button" onClick={() => setSelectedDay(null)}>Сбросить</button>
            </div>
          )}
          <div className="daily-chart" aria-label="График расходов по дням">
            {period.days.map((amount, index) => (
              <button
                type="button"
                className={`chart-column${selectedDay === index ? " selected" : ""}${selectedDay !== null && selectedDay !== index ? " muted" : ""}`}
                key={index}
                title={`${index + 1} ${monthNames[month].toLowerCase()}: ${formatBudget(amount)} ₽`}
                aria-label={`${index + 1} ${monthNames[month].toLowerCase()}, ${formatBudget(amount)} ₽`}
                aria-pressed={selectedDay === index}
                onClick={() => setSelectedDay((current) => current === index ? null : index)}
              >
                <span style={{ height: `${Math.max(8, (amount / maxDay) * 100)}%` }} />
                {(index === 0 || (index + 1) % 5 === 0 || index === period.days.length - 1) && <small>{index + 1}</small>}
              </button>
            ))}
          </div>
        </section>
      )}

      <div className="statistics-grid">
        <section className="stat-card">
          <div className="stat-card-heading">
            <div>
              <h3>По категориям</h3>
              <p>{selectedDateLabel && mode === "month" ? `Расходы за ${selectedDateLabel}` : "Куда ушли деньги за период"}</p>
            </div>
          </div>
          <div className="category-stat-list">
            {displayCategories.map((category) => {
              const share = Math.round((category.amount / categoryTotal) * 100);
              return (
                <div className="category-stat" key={category.name}>
                  <div className="category-stat-copy">
                    <span className="category-marker" style={{ background: category.color }} />
                    <strong>{category.name}</strong>
                    <span>{share}%</span>
                    <b>{formatBudget(category.amount)} ₽</b>
                  </div>
                  <div className="category-bar"><span style={{ width: `${share}%`, background: category.color }} /></div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </section>
  );
};

const SettingsView = () => {
  const [settingsState, setSettingsState] = useState<SettingsState>({
    status: "idle",
    settings: null,
    currencies: [],
    error: null
  });
  const [budget, setBudget] = useState("");
  const [defaultCurrencyId, setDefaultCurrencyId] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isEditFormOpen, setIsEditFormOpen] = useState(false);

  const syncForm = (settings: Settings) => {
    setBudget(String(settings.budget));
    setDefaultCurrencyId(settings.default_currency ? String(settings.default_currency.id) : "");
  };

  const loadSettings = useCallback(async () => {
    setSettingsState((current) => ({
      status: current.settings ? "ready" : "loading",
      settings: current.settings,
      currencies: current.currencies,
      error: null
    }));

    try {
      const [settings, currencies] = await Promise.all([settingsApi.get(), currenciesApi.list()]);
      setSettingsState({ status: "ready", settings, currencies, error: null });
      syncForm(settings);
    } catch (error) {
      setSettingsState((current) => ({
        status: "error",
        settings: current.settings,
        currencies: current.currencies,
        error: getErrorMessage(error)
      }));
    }
  }, []);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  const saveSettings = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedBudget = budget.trim().replace(",", ".");
    const parsedBudget = Number(normalizedBudget);

    if (!Number.isFinite(parsedBudget) || parsedBudget < 0 || !defaultCurrencyId) {
      return;
    }

    setIsSaving(true);
    setSettingsState((current) => ({ ...current, error: null }));

    try {
      const settings = await settingsApi.update({
        budget: normalizedBudget,
        default_currency_id: Number(defaultCurrencyId)
      });
      setSettingsState((current) => ({
        status: "ready",
        settings,
        currencies: current.currencies,
        error: null
      }));
      syncForm(settings);
      setIsEditFormOpen(false);
    } catch (error) {
      setSettingsState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    } finally {
      setIsSaving(false);
    }
  };

  const selectedCurrency = settingsState.settings?.default_currency;
  const isFormValid = Number.isFinite(Number(budget.trim().replace(",", "."))) && Boolean(defaultCurrencyId);

  return (
    <section className="module">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Параметры</p>
          <h2>Настройки</h2>
        </div>
        <div className="heading-actions">
          {settingsState.settings && (
            <button
              type="button"
              className="primary-button compact-primary-button"
              onClick={() => {
                if (!isEditFormOpen && settingsState.settings) {
                  syncForm(settingsState.settings);
                }
                setIsEditFormOpen((isOpen) => !isOpen);
              }}
            >
              {isEditFormOpen ? "Скрыть" : "Изменить"}
            </button>
          )}
          <button type="button" className="ghost-button" onClick={() => void loadSettings()}>
            Обновить
          </button>
        </div>
      </div>

      {settingsState.status === "loading" && (
        <div className="list-state" aria-live="polite">
          <div className="loader small-loader" />
          <p>Загружаем настройки.</p>
        </div>
      )}

      {settingsState.settings && (
        <>
          <section className="settings-summary" aria-label="Текущие настройки">
            <article className="detail-item">
              <span>Месячный бюджет</span>
              <strong>
                {formatBudget(settingsState.settings.budget)}
                {selectedCurrency ? ` ${getCurrencySymbol(selectedCurrency)}` : ""}
              </strong>
            </article>
            <article className="detail-item">
              <span>Валюта по умолчанию</span>
              <strong>
                {selectedCurrency
                  ? `${selectedCurrency.name} (${getCurrencySymbol(selectedCurrency)})`
                  : "Не выбрана"}
              </strong>
            </article>
          </section>

          {isEditFormOpen && (
            <form className="settings-form" onSubmit={(event) => void saveSettings(event)}>
              <label className="text-field">
                <span>Месячный бюджет</span>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={budget}
                  onChange={(event) => setBudget(event.target.value)}
                  placeholder="0"
                  autoFocus
                />
              </label>
              <label className="text-field">
                <span>Валюта по умолчанию</span>
                <select
                  value={defaultCurrencyId}
                  onChange={(event) => setDefaultCurrencyId(event.target.value)}
                  disabled={settingsState.currencies.length === 0}
                >
                  <option value="">Выберите валюту</option>
                  {settingsState.currencies.map((currency) => (
                    <option value={currency.id} key={currency.id}>
                      {currency.name} ({getCurrencySymbol(currency)})
                    </option>
                  ))}
                </select>
              </label>
              <div className="form-actions">
                <button
                  type="submit"
                  className="primary-button"
                  disabled={isSaving || !isFormValid || settingsState.currencies.length === 0}
                >
                  {isSaving ? "Сохраняем..." : "Сохранить"}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    if (settingsState.settings) {
                      syncForm(settingsState.settings);
                    }
                    setIsEditFormOpen(false);
                  }}
                >
                  Отмена
                </button>
              </div>
            </form>
          )}
        </>
      )}

      {settingsState.status !== "loading" && !settingsState.settings && (
        <div className="list-state">
          <h3>Настройки недоступны</h3>
          <p>Не удалось получить текущие параметры приложения.</p>
        </div>
      )}

      {settingsState.currencies.length === 0 && settingsState.status !== "loading" && (
        <p className="inline-error">Чтобы выбрать валюту по умолчанию, сначала добавьте валюту.</p>
      )}

      {settingsState.error && <p className="inline-error">{settingsState.error}</p>}
    </section>
  );
};

export const App = () => {
  useTelegramTheme();

  const [authState, setAuthState] = useState<AuthState>({
    status: "loading",
    user: null,
    error: null
  });
  const [activeView, setActiveView] = useState<View>("expenses");
  const [balanceRevision, setBalanceRevision] = useState(0);

  const telegramUser = getTelegramWebApp()?.initDataUnsafe?.user;

  const loadUser = useCallback(async (forceReauthorize = false) => {
    setAuthState({ status: "loading", user: null, error: null });

    try {
      const user = forceReauthorize
        ? await authService.reauthorize()
        : await authService.loadCurrentUser();

      setAuthState({ status: "authenticated", user, error: null });
    } catch (error) {
      setAuthState({ status: "error", user: null, error: getErrorMessage(error) });
    }
  }, []);

  useEffect(() => {
    void loadUser();
  }, [loadUser]);

  const subtitle = useMemo(() => {
    if (authState.status === "authenticated") {
      return authState.user.telegram_username
        ? `@${authState.user.telegram_username}`
        : `Telegram ID ${authState.user.telegram_id}`;
    }

    return telegramUser?.username ? `@${telegramUser.username}` : "Telegram WebApp";
  }, [authState, telegramUser]);

  const renderActiveView = () => {
    if (authState.status !== "authenticated") {
      return null;
    }

    if (activeView === "overview") {
      return (
        <OverviewView
          user={authState.user}
          subtitle={subtitle}
          onRefresh={() => void loadUser()}
          onReauthorize={() => void loadUser(true)}
        />
      );
    }

    if (activeView === "categories") {
      return <CategoriesView />;
    }

    if (activeView === "statistics") {
      return <StatisticsView />;
    }

    if (activeView === "expenses") {
      return <ExpensesView onExpensesChanged={() => setBalanceRevision((current) => current + 1)} />;
    }

    if (activeView === "currencies") {
      return <CurrenciesView />;
    }

    if (activeView === "settings") {
      return <SettingsView />;
    }

    const currentItem = navigationItems.find((item) => item.id === activeView);
    return <EmptyModule title={currentItem?.label ?? "Раздел"} />;
  };

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Cheapskate</p>
          <h1>Личный кабинет</h1>
        </div>
      </section>

      {authState.status === "loading" && (
        <section className="panel center-state" aria-live="polite">
          <div className="loader" />
          <h2>Входим через Telegram</h2>
          <p>Проверяем WebApp data и готовим защищенную сессию.</p>
        </section>
      )}

      {authState.status === "error" && (
        <section className="panel center-state error-state" aria-live="assertive">
          <div className="error-icon">!</div>
          <h2>Не получилось войти</h2>
          <p>{authState.error}</p>
          <button type="button" className="primary-button" onClick={() => void loadUser(true)}>
            Повторить вход
          </button>
          <button
            type="button"
            className="secondary-button demo-button"
            onClick={() => setAuthState({
              status: "authenticated",
              user: {
                id: 1,
                telegram_id: 100000001,
                telegram_username: "demo_user",
                telegram_first_name: "Демо",
                telegram_last_name: "Пользователь",
                created_at: "2026-01-12T10:00:00Z"
              },
              error: null
            })}
          >
            Открыть демо статистики
          </button>
        </section>
      )}

      {authState.status === "authenticated" && (
        <>
          <MonthlyBalance key={balanceRevision} />
          <nav className="app-nav" aria-label="Разделы приложения">
            {navigationItems.filter((item) => !item.isHidden).map((item) => (
              <button
                type="button"
                key={item.id}
                className={activeView === item.id ? "nav-button active" : "nav-button"}
                onClick={() => setActiveView(item.id)}
              >
                {item.label}
                {item.isComingSoon && <span>скоро</span>}
              </button>
            ))}
          </nav>

          {renderActiveView()}
        </>
      )}
    </main>
  );
};
