import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Im Dev-Modus (npm run dev) werden /api-Requests an FastAPI weitergeleitet.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
