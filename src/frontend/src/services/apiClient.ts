import { tokenStorage } from "./tokenStorage";
import type {
  AuthorizationTokens,
  Category,
  CategoryPayload,
  CategoryUpdatePayload,
  CategoryWithExpenses,
  User
} from "../types/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const AUTH_URL = "/api/v1/authorization";
const CATEGORIES_URL = "/api/v1/categories";
const EXPIRATION_SAFETY_WINDOW_SECONDS = 30;

type RequestOptions = RequestInit & {
  auth?: boolean;
  retryOnUnauthorized?: boolean;
};

type JwtPayload = {
  exp?: number;
};

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const createUrl = (path: string) => `${API_BASE_URL}${path}`;

const parseJson = async <T>(response: Response): Promise<T> => {
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

const decodeJwtPayload = (token: string): JwtPayload | null => {
  const [, payload] = token.split(".");

  if (!payload) {
    return null;
  }

  try {
    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, "="));

    return JSON.parse(decoded) as JwtPayload;
  } catch {
    return null;
  }
};

const isTokenExpiredOrClose = (token: string): boolean => {
  const payload = decodeJwtPayload(token);

  if (!payload?.exp) {
    return false;
  }

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp - EXPIRATION_SAFETY_WINDOW_SECONDS <= currentTime;
};

const refreshTokens = async (): Promise<AuthorizationTokens> => {
  const refreshToken = tokenStorage.getRefreshToken();

  if (!refreshToken) {
    throw new ApiError(401, "Refresh token is missing");
  }

  const response = await fetch(createUrl(`${AUTH_URL}/refresh-tokens`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  const body = await parseJson<AuthorizationTokens | unknown>(response);

  if (!response.ok) {
    tokenStorage.clear();
    throw new ApiError(response.status, body);
  }

  tokenStorage.setTokens(body as AuthorizationTokens);
  return body as AuthorizationTokens;
};

const getValidAccessToken = async (): Promise<string> => {
  const accessToken = tokenStorage.getAccessToken();

  if (!accessToken) {
    throw new ApiError(401, "Access token is missing");
  }

  if (!isTokenExpiredOrClose(accessToken)) {
    return accessToken;
  }

  const tokens = await refreshTokens();
  return tokens.access_token;
};

export const apiRequest = async <T>(path: string, options: RequestOptions = {}): Promise<T> => {
  const { auth = true, retryOnUnauthorized = true, headers, ...requestInit } = options;
  const requestHeaders = new Headers(headers);

  if (!requestHeaders.has("Content-Type") && requestInit.body) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const accessToken = await getValidAccessToken();
    requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(createUrl(path), {
    ...requestInit,
    headers: requestHeaders
  });

  const body = await parseJson<T | unknown>(response);

  if (response.status === 401 && auth && retryOnUnauthorized) {
    await refreshTokens();

    return apiRequest<T>(path, {
      ...options,
      retryOnUnauthorized: false
    });
  }

  if (!response.ok) {
    throw new ApiError(response.status, body);
  }

  return body as T;
};

export const authorizationApi = {
  authorizeTelegramWebApp(webAppData: string): Promise<AuthorizationTokens> {
    return apiRequest<AuthorizationTokens>(`${AUTH_URL}/telegram-web-app`, {
      method: "POST",
      auth: false,
      body: JSON.stringify({ web_app_data: webAppData })
    });
  },

  getMe(): Promise<User> {
    return apiRequest<User>(`${AUTH_URL}/me`);
  }
};

export const categoriesApi = {
  list(): Promise<CategoryWithExpenses[]> {
    return apiRequest<CategoryWithExpenses[]>(CATEGORIES_URL);
  },

  create(payload: CategoryPayload): Promise<Category> {
    return apiRequest<Category>(CATEGORIES_URL, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  update(categoryId: number, payload: CategoryUpdatePayload): Promise<Category> {
    return apiRequest<Category>(`${CATEGORIES_URL}/${categoryId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },

  delete(categoryId: number): Promise<Category> {
    return apiRequest<Category>(`${CATEGORIES_URL}/${categoryId}`, {
      method: "DELETE"
    });
  }
};
