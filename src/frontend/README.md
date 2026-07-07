# Cheapskate Telegram WebApp

React + TypeScript frontend for the Cheapskate Telegram WebApp.

## Scripts

```shell
npm install
npm run dev
npm run build
```

During local development Vite proxies `/api` to `http://127.0.0.1:8000`.
Override it with:

```shell
VITE_DEV_BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

For production builds served from another origin, set:

```shell
VITE_API_BASE_URL=https://your-api-domain.example npm run build
```

Authentication uses `window.Telegram.WebApp.initData`, so the real login flow works only when the app is opened inside Telegram.
