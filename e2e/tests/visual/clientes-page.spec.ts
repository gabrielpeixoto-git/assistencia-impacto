import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/login.page';

test.describe('Visual Regression — Clientes Page', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginComSucesso({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
  });

  test('VISUAL: página de clientes deve corresponder ao snapshot', async ({ page }) => {
    await page.goto('/clientes');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);
    
    await expect(page).toHaveScreenshot('clientes-page.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('VISUAL: tabela de clientes deve corresponder ao snapshot', async ({ page }) => {
    await page.goto('/clientes');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);
    
    const tabela = page.locator('[data-testid="tabela-clientes"], table').first();
    await expect(tabela).toBeVisible();
    
    await expect(tabela).toHaveScreenshot('clientes-table.png', {
      animations: 'disabled',
    });
  });
});
