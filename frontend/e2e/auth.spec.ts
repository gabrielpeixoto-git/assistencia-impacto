import { test, expect } from '@playwright/test';

test.describe('Autenticação', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('deve exibir página de login quando não autenticado', async ({ page }) => {
    await expect(page).toHaveTitle(/Assistência Impacto/);
    await expect(page.locator('text=Login')).toBeVisible();
  });

  test('deve fazer login com credenciais válidas', async ({ page }) => {
    // Preencher email
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    
    // Preencher senha
    await page.fill('input[type="password"]', 'admin123');
    
    // Clicar no botão de login
    await page.click('button[type="submit"]');

    // Verificar redirecionamento para dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Verificar se o usuário está autenticado (verificar se há elementos do dashboard)
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('deve exibir erro com credenciais inválidas', async ({ page }) => {
    // Preencher email inválido
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    
    // Preencher senha inválida
    await page.fill('input[type="password"]', 'senhaerrada');
    
    // Clicar no botão de login
    await page.click('button[type="submit"]');

    // Verificar se mensagem de erro é exibida
    await expect(page.locator('text=erro').or(page.locator('text=Erro').or(page.locator('text=inválidas')))).toBeVisible({ timeout: 5000 });
  });

  test('deve fazer logout corretamente', async ({ page }) => {
    // Fazer login primeiro
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Aguardar redirecionamento
    await page.waitForURL(/.*dashboard/);

    // Clicar no botão de logout (geralmente no menu de usuário)
    const logoutButton = page.locator('button').filter({ hasText: /Sair|Logout/ }).or(
      page.locator('[aria-label*="Sair"]').or(page.locator('[aria-label*="Logout"]'))
    );
    
    if (await logoutButton.isVisible({ timeout: 5000 })) {
      await logoutButton.click();
    } else {
      // Tentar abrir menu de usuário primeiro
      const userMenu = page.locator('button').filter({ hasText: /admin/i }).or(
        page.locator('[aria-label*="usuário"]').or(page.locator('[aria-label*="menu"]'))
      );
      
      if (await userMenu.isVisible({ timeout: 3000 })) {
        await userMenu.click();
        await page.waitForTimeout(500);
        await logoutButton.click();
      }
    }

    // Verificar redirecionamento para login
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 });
  });

  test('deve validar campos obrigatórios no login', async ({ page }) => {
    // Tentar fazer login sem preencher campos
    await page.click('button[type="submit"]');

    // Verificar validação HTML5
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toHaveAttribute('required', '');

    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toHaveAttribute('required', '');
  });
});
