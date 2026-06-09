import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Fluxo Completo — OS → Transação Financeira', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

  test('FLUXO: acessar módulo financeiro', async ({ page }) => {
    await page.goto('/transacoes');
    await page.waitForTimeout(1000);

    await expect(page.getByRole('heading', { name: /financeiro|transações/i }).or(page.getByRole('heading', { name: /transações/i }))).toBeVisible({ timeout: 10000 });
  });

  test('FLUXO: dashboard carrega corretamente', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(3000);

    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });
});
