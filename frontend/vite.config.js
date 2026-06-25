import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false, // Fall back to next port if 5173 is busy
    proxy: {
      // All /api traffic (including /api/python) goes through Node so auth + CSRF apply.
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    }
  },
  // BUG-C2: Vitest configuration
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 50,
      },
    },
  },
})
