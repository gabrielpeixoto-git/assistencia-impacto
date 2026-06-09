import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/login.page';

test.describe('Autenticação — Login', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('LOGIN: exibe erro com credenciais inválidas', async ({ page }) => {
    await loginPage.login({
      email: 'invalido@teste.com',
      senha: 'senhaerrada',
    });

    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
  });

  test('LOGIN: exibe erro com email vazio', async ({ page }) => {
    await loginPage.campoEmail.fill('');
    await loginPage.campoSenha.fill('qualquer');
    await loginPage.botaoEntrar.click();

    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
  });

  test('LOGIN: exibe erro com senha vazia', async ({ page }) => {
    await loginPage.campoEmail.fill('teste@teste.com');
    await loginPage.campoSenha.fill('');
    await loginPage.botaoEntrar.click();

    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
  });

  test('LOGIN: redireciona para dashboard após login bem-sucedido', async ({ page }) => {
    await loginPage.login({
      email: process.env.ADMIN_EMAIL!,
      senha: process.env.ADMIN_SENHA!,
    });

    await expect(page).toHaveURL(/.*\/$/, { timeout: 15000 });
  });
});
