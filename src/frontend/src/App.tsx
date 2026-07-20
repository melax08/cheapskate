import { FormEvent, useCallback, useEffect, useRef, useMemo, useState } from "react";
import { authService, getTelegramWebApp } from "./services/authService";
import { ApiError, categoriesApi, currenciesApi, expensesApi, settingsApi } from "./services/apiClient";
import type {
  CategoryWithExpenses,
  Currency,
  CurrencyPayload,
  Expense,
  ExpenseDetail,
  ExpensePayload,
  Settings,
  User
} from "./types/api";
import { useTelegramTheme } from "./hooks/useTelegramTheme";

type AuthState =
  | { status: "loading"; user: null; error: null }
  | { status: "authenticated"; user: User; error: null }
  | { status: "error"; user: null; error: string };

type View = "overview" | "categories" | "currencies" | "expenses" | "settings";

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

const navigationItems: Array<{ id: View; label: string; isComingSoon?: boolean }> = [
  { id: "expenses", label: "Траты" },
  { id: "categories", label: "Категории" },
  { id: "currencies", label: "Валюты" },
  { id: "settings", label: "Настройки" },
  { id: "overview", label: "Профиль" }
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

const formatMoney = (value: string | number) =>
  new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3
  }).format(Number(value));

const getDisplayName = (user: User) =>
  [user.telegram_first_name, user.telegram_last_name].filter(Boolean).join(" ");

const getInitials = (user: User) =>
  [user.telegram_first_name, user.telegram_last_name]
    .filter(Boolean)
    .map((name) => name?.[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

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
    if (category.expenses_count > 0) {
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

const normalizeExpenseDetail = (expense: ExpenseDetail): Expense => ({
  id: expense.id,
  amount: expense.amount,
  description: expense.description,
  category_id: expense.category.id,
  currency_id: expense.currency?.id ?? null,
  date: expense.date
});

const ExpensesView = () => {
  const [expensesState, setExpensesState] = useState<ExpensesState>({
    status: "idle",
    items: [],
    nextCursor: null,
    error: null
  });
  const [categories, setCategories] = useState<CategoryWithExpenses[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [newExpense, setNewExpense] = useState<ExpensePayload>(createEmptyExpense);
  const [editingExpenseId, setEditingExpenseId] = useState<number | null>(null);
  const [editingExpense, setEditingExpense] = useState<ExpensePayload>(createEmptyExpense);
  const [pendingExpenseId, setPendingExpenseId] = useState<number | null>(null);
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const loadingCursorRef = useRef<string | null>(null);

  const syncDefaultCategory = useCallback((items: CategoryWithExpenses[]) => {
    setNewExpense((current) => ({
      ...current,
      category_id: current.category_id || items[0]?.id || 0
    }));
  }, []);

  const loadDictionaries = useCallback(async () => {
    const [categoriesItems, currenciesItems] = await Promise.all([
      categoriesApi.list(),
      currenciesApi.list()
    ]);
    setCategories(categoriesItems);
    setCurrencies(currenciesItems);
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
        setExpensesState((current) => ({
          status: current.items.length ? "ready" : "loading",
          items: current.items,
          nextCursor: current.nextCursor,
          error: null
        }));
      }

      try {
        const page = await expensesApi.list({ cursor, size: 10 });
        setExpensesState((current) => ({
          status: "ready",
          items: isNextPage ? [...current.items, ...page.items] : page.items,
          nextCursor: page.next_page ?? null,
          error: null
        }));
      } catch (error) {
        setExpensesState((current) => ({
          status: "error",
          items: current.items,
          nextCursor: current.nextCursor,
          error: getErrorMessage(error)
        }));
      } finally {
        loadingCursorRef.current = null;
        setIsLoadingMore(false);
      }
    },
    []
  );

  useEffect(() => {
    void loadDictionaries().catch((error) => {
      setExpensesState((current) => ({
        ...current,
        status: "error",
        error: getErrorMessage(error)
      }));
    });
    void loadExpenses();
  }, [loadDictionaries, loadExpenses]);

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

    if (!isExpensePayloadValid(newExpense)) {
      return;
    }

    setIsCreating(true);
    setExpensesState((current) => ({ ...current, error: null }));

    try {
      await expensesApi.create(buildExpensePayload(newExpense));
      setNewExpense({
        ...createEmptyExpense(),
        category_id: categories[0]?.id || 0
      });
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
      setExpensesState((current) => ({
        ...current,
        status: "ready",
        items: current.items.map((item) =>
          item.id === expense.id ? normalizeExpenseDetail(updatedExpense) : item
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
    setPendingExpenseId(expense.id);

    try {
      await expensesApi.delete(expense.id);
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
    onCancel?: () => void
  ) => (
    <>
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
      <label className="text-field">
        <span>Категория</span>
        <select
          value={payload.category_id || ""}
          onChange={(event) => setField("category_id", event.target.value)}
          disabled={categories.length === 0}
        >
          <option value="">Выберите категорию</option>
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
          value={payload.currency_id ?? ""}
          onChange={(event) => setField("currency_id", event.target.value)}
        >
          <option value="">По умолчанию</option>
          {currencies.map((currency) => (
            <option value={currency.id} key={currency.id}>
              {currency.name} ({currency.letter_code})
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
          disabled={isDisabled || !isExpensePayloadValid(payload) || categories.length === 0}
        >
          {submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="secondary-button" onClick={onCancel}>
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

      {isCreateFormOpen && (
        <form className="expense-form" onSubmit={(event) => void createExpense(event)}>
          {renderExpenseForm(newExpense, setNewExpenseField, isCreating ? "Создаем..." : "Создать", isCreating, () => {
            setIsCreateFormOpen(false);
            setNewExpense({
              ...createEmptyExpense(),
              category_id: categories[0]?.id || 0
            });
          })}
        </form>
      )}

      {categories.length === 0 && expensesState.status !== "loading" && (
        <p className="inline-error">Чтобы добавить трату, сначала создайте хотя бы одну категорию.</p>
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
          <h3>Трат пока нет</h3>
          <p>Добавьте первую запись, чтобы вести историю расходов.</p>
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
                        cancelEditingExpense
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
                          {currency ? ` ${currency.letter_code}` : ""}
                        </strong>
                      </div>
                      <div className="expense-meta">
                        <span>{formatDateTime(expense.date)}</span>
                        <span>#{expense.id}</span>
                        <span>{currency?.name ?? "Валюта по умолчанию"}</span>
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
  country: ""
});

const normalizeCurrencyCode = (value: string) =>
  value
    .replace(/[^a-zA-Z]/g, "")
    .slice(0, 3)
    .toUpperCase();

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
      [field]: field === "letter_code" ? normalizeCurrencyCode(value) : value
    }));
  };

  const setEditingCurrencyField = (field: keyof CurrencyPayload, value: string) => {
    setEditingCurrency((current) => ({
      ...current,
      [field]: field === "letter_code" ? normalizeCurrencyCode(value) : value
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
        country: newCurrency.country.trim()
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
      country: currency.country
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
      country: editingCurrency.country.trim()
    };

    if (
      payload.name === currency.name &&
      payload.letter_code === currency.letter_code &&
      payload.country === currency.country
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
                <div className="currency-code">{currency.letter_code}</div>
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
                      <h3>{currency.name}</h3>
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
                {selectedCurrency ? ` ${selectedCurrency.letter_code}` : ""}
              </strong>
            </article>
            <article className="detail-item">
              <span>Валюта по умолчанию</span>
              <strong>
                {selectedCurrency
                  ? `${selectedCurrency.name} (${selectedCurrency.letter_code})`
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
                      {currency.name} ({currency.letter_code})
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

    if (activeView === "expenses") {
      return <ExpensesView />;
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
        </section>
      )}

      {authState.status === "authenticated" && (
        <>
          <nav className="app-nav" aria-label="Разделы приложения">
            {navigationItems.map((item) => (
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
