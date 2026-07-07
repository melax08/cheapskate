import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { authService, getTelegramWebApp } from "./services/authService";
import { ApiError, categoriesApi } from "./services/apiClient";
import type { CategoryWithExpenses, User } from "./types/api";
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

const navigationItems: Array<{ id: View; label: string; isComingSoon?: boolean }> = [
  { id: "overview", label: "Профиль" },
  { id: "categories", label: "Категории" },
  { id: "expenses", label: "Траты", isComingSoon: true },
  { id: "currencies", label: "Валюты", isComingSoon: true },
  { id: "settings", label: "Настройки", isComingSoon: true }
];

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "long",
    year: "numeric"
  }).format(new Date(value));

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
          <button type="button" className="ghost-button" onClick={() => void loadCategories()}>
            Обновить
          </button>
        </div>
      </div>

      <form className="category-form" onSubmit={(event) => void createCategory(event)}>
        <label className="text-field">
          <span>Новая категория</span>
          <input
            type="text"
            value={newCategoryName}
            onChange={(event) => setNewCategoryName(event.target.value)}
            placeholder="Например, продукты"
            maxLength={255}
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
        <button type="submit" className="primary-button" disabled={isCreating || !newCategoryName.trim()}>
          {isCreating ? "Создаем..." : "Добавить"}
        </button>
      </form>

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

export const App = () => {
  useTelegramTheme();

  const [authState, setAuthState] = useState<AuthState>({
    status: "loading",
    user: null,
    error: null
  });
  const [activeView, setActiveView] = useState<View>("overview");

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
