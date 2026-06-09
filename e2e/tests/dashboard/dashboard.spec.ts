import { test, expect } from '@playwright/test';
import { DashboardPage } from '../../pages/dashboard.page';
import { LoginPage } from '../../pages/login.page';

test.describe('Dashboard — Métricas e Visão Geral', () => {
  let dashboardPage: DashboardPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
    // Aguardar redirecionamento
    await page.waitForTimeout(5000);
    // Navegar para dashboard
    await page.goto('/dashboard');
    await page.waitForTimeout(5000);
    dashboardPage = new DashboardPage(page);
  });

  test('DASHBOARD: carrega métricas principais', async ({ page }) => {
    // Aguardar carregamento da página
    await page.waitForTimeout(3000);

    // Verificar que os cards de estatísticas estão visíveis
    await expect(dashboardPage.statCardReceita).toBeVisible({ timeout: 20000 });
    await expect(dashboardPage.statCardOS).toBeVisible({ timeout: 20000 });
    await expect(dashboardPage.statCardClientes).toBeVisible({ timeout: 20000 });
    await expect(dashboardPage.statCardOrcamentos).toBeVisible({ timeout: 20000 });
  });

  test('DASHBOARD: exibe gráfico de receita', async ({ page }) => {
    await page.waitForTimeout(3000);
    await expect(dashboardPage.graficoReceita).toBeVisible({ timeout: 20000 });
  });

  test('DASHBOARD: exibe gráfico de status de OS', async ({ page }) => {
    await page.waitForTimeout(3000);
    await expect(dashboardPage.graficoStatusOS).toBeVisible({ timeout: 20000 });
  });

  test('DASHBOARD: exibe tabela de OS recentes', async ({ page }) => {
    await page.waitForTimeout(3000);
    await expect(dashboardPage.tabelaRecentes).toBeVisible({ timeout: 20000 });
  });
});
