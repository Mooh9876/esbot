import { defineConfig } from '@playwright/test'

/**
 * Playwright E2E configuration for ESBot.
 *
 * Prerequisites before running:
 *   1. Backend:  uv run uvicorn app.main:app --reload  (http://127.0.0.1:8000)
 *   2. Frontend: npm run dev                           (http://127.0.0.1:5173)
 */
export default defineConfig({
  // Folder containing the test files
  testDir: './playwright',

  // Base URL – matches the Vite dev server
  use: {
    baseURL: 'http://127.0.0.1:5173',

    // Collect trace on first retry to simplify debugging
    trace: 'on-first-retry',
  },

  // Run tests in a single browser (Chromium) as required by the task
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],

  // No automatic web server start – the dev server must be running already
  // (documented in docs/ui/e2e-setup.md)
})
