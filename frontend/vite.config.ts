import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// La API sirve bajo /api sin reescritura (design O1): en desarrollo, Vite la reenvía tal cual.
const destinoApi = process.env.VITE_API_PROXY ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': { target: destinoApi, changeOrigin: false },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
