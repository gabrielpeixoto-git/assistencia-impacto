import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/login.page';

test.describe('Visual Regression — Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginComSucesso({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
    await page.goto('/dashboard');
  });

  test('VISUAL: dashboard deve corresponder ao snapshot', async ({ page }) => {
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500); // Aguardar animações
    
    await expect(page).toHaveScreenshot('dashboard-page.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('VISUAL: cards de estatísticas devem corresponder ao snapshot', async ({ page }) => {
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);
    
    // Focar apenas nos cards
    const statCards = page.locator('.glass-card-hover').first();
    await expect(statCards).toBeVisible();
    
    await expect(statCards).toHaveScreenshot('stat-card.png', {
      animations: 'disabled',
    });
  });
});
