import { test, expect } from '@playwright/test';

test.describe('Visual Regression — Login Page', () => {
  test('VISUAL: página de login deve corresponder ao snapshot', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    
    // Aguardar animações
    await page.waitForTimeout(500);
    
    await expect(page).toHaveScreenshot('login-page.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('VISUAL: formulário de login com erro deve corresponder ao snapshot', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    
    // Preencher com credenciais inválidas
    await page.locator('input[type="email"]').fill('invalido@teste.com');
    await page.locator('input[type="password"]').fill('senhaerrada');
    await page.getByRole('button', { name: 'Entrar' }).click();
    
    // Aguardar mensagem de erro
    await page.waitForTimeout(500);
    
    await expect(page).toHaveScreenshot('login-page-error.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});
