import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/login.page';

test.describe('Estoque — Gestão de Materiais', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginComSucesso({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
  });

  test('ESTOQUE: página de estoque carrega corretamente', async ({ page }) => {
    await page.goto('/estoque');
    await expect(page.getByRole('heading', { name: /estoque/i })).toBeVisible();
  });

  test('ESTOQUE: exibe tabela de materiais', async ({ page }) => {
    await page.goto('/estoque');
    await expect(page.locator('[data-testid="tabela-estoque"]')).toBeVisible();
  });

  test('ESTOQUE: buscar material por nome', async ({ page }) => {
    await page.goto('/estoque');
    // Esperar tabela de estoque aparecer (indica que a página carregou)
    await expect(page.locator('[data-testid="tabela-estoque"]')).toBeVisible({ timeout: 15000 });
    const campoBusca = page.getByPlaceholder(/buscar por nome, código/i);
    await campoBusca.fill('parafuso');
    await expect(campoBusca).toHaveValue('parafuso');
  });

  test('ESTOQUE: botão novo material está visível', async ({ page }) => {
    await page.goto('/estoque');
    // Esperar tabela de estoque aparecer (indica que a página carregou)
    await expect(page.locator('[data-testid="tabela-estoque"]')).toBeVisible({ timeout: 15000 });
    // Agora verificar o botão
    await expect(page.getByRole('button', { name: /novo item/i })).toBeVisible({ timeout: 10000 });
  });
});
