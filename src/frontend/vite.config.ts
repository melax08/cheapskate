import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.VITE_DEV_BACKEND_URL ?? "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      allowedHosts: true,
      port: 5173,
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true
        }
      }
    }
  };
});
