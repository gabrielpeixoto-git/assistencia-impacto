import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  fullyParallel: false,  // serializado para evitar conflitos no banco de teste
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,
  timeout: 60000,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5174',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
  },
  projects: [
    // Setup: criar dados de teste
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    // Testes autenticados (admin)
    {
      name: 'admin-chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    // Testes autenticados (técnico)
    {
      name: 'tecnico-chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/tecnico.json',
      },
      dependencies: ['setup'],
    },
    // Testes autenticados (gerente)
    {
      name: 'gerente-chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/gerente.json',
      },
      dependencies: ['setup'],
    },
    // Portal público (sem autenticação)
    {
      name: 'portal-chromium',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /portal\/.*/,
      dependencies: ['setup'],
    },
    // Smoke test em Firefox (apenas cenários críticos)
    {
      name: 'firefox-smoke',
      use: { ...devices['Desktop Firefox'] },
      testMatch: /.*\.smoke\.ts/,
    },
  ],
  webServer: {
    command: 'docker-compose -f ../docker-compose.test.yml up --wait',
    url: 'http://localhost:5174',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
