import { defineConfig } from "vite";

// In development the Go service runs separately; LEARNBOX_API points at it.
const api = process.env.LEARNBOX_API ?? "http://localhost:8080";

export default defineConfig({
  server: {
    proxy: {
      "/api": { target: api, ws: true, changeOrigin: false },
      "/healthz": api,
    },
  },
  build: {
    target: "es2022",
    chunkSizeWarningLimit: 900,
  },
});
