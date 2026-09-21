import { defineConfig, devices } from '@playwright/test';
const remote = process.env.E2E_BASE_URL;
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 60000,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: remote || 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: remote
    ? undefined
    : {
        command: 'python ../scripts/run_e2e_server.py',
        url: 'http://127.0.0.1:8000/health',
        reuseExistingServer: false,
        timeout: 30000,
      },
});
