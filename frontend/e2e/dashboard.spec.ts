import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Fazer login antes de cada teste
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*dashboard/);
  });

  test('deve exibir página de dashboard', async ({ page }) => {
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('deve exibir cards de resumo', async ({ page }) => {
    await expect(page.locator('text=Ordens de Serviço').or(page.locator('text=OS'))).toBeVisible();
    await expect(page.locator('text=Receita').or(page.locator('text=Financeiro'))).toBeVisible();
    await expect(page.locator('text=Clientes').or(page.locator('text=Clientes'))).toBeVisible();
  });

  test('deve exibir gráfico de receita', async ({ page }) => {
    await page.waitForTimeout(2000);
    const chart = page.locator('canvas').or(page.locator('[role="img"]'));
    await expect(chart.first()).toBeVisible({ timeout: 5000 });
  });

  test('deve exibir lista de ordens recentes', async ({ page }) => {
    await page.waitForTimeout(2000);
    await expect(page.locator('text=Ordens Recentes').or(page.locator('text=Recentes'))).toBeVisible();
  });

  test('deve exibir lista de tarefas pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);
    await expect(page.locator('text=Tarefas').or(page.locator('text=Pendentes'))).toBeVisible();
  });

  test('deve navegar para ordens de serviço ao clicar no card', async ({ page }) => {
    await page.waitForTimeout(2000);
    const cardOS = page.locator('text=Ordens de Serviço').or(page.locator('text=OS')).first();
    await cardOS.click();
    await page.waitForURL(/.*ordens-servico/, { timeout: 5000 });
  });

  test('deve navegar para financeiro ao clicar no card de receita', async ({ page }) => {
    await page.waitForTimeout(2000);
    const cardReceita = page.locator('text=Receita').or(page.locator('text=Financeiro')).first();
    await cardReceita.click();
    await page.waitForURL(/.*financeiro/, { timeout: 5000 });
  });

  test('deve navegar para clientes ao clicar no card de clientes', async ({ page }) => {
    await page.waitForTimeout(2000);
    const cardClientes = page.locator('text=Clientes').first();
    await cardClientes.click();
    await page.waitForURL(/.*clientes/, { timeout: 5000 });
  });

  test('deve exibir período de filtro', async ({ page }) => {
    await expect(page.locator('text=Últimos 30 dias').or(page.locator('text=30 dias'))).toBeVisible();
  });

  test('deve exibir indicadores de KPI', async ({ page }) => {
    await page.waitForTimeout(2000);
    await expect(page.locator('text=R$').or(page.locator('[data-testid*="kpi"]'))).toBeVisible();
  });
});
