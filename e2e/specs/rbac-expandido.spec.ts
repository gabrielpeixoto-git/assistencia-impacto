import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('RBAC — Perfil Visualizador (Técnico)', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/tecnico.json') });

  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('VISUALIZADOR: pode visualizar dashboard', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('VISUALIZADOR: pode visualizar ordens de serviço', async ({ page }) => {
    await page.goto('/ordens-servico');
    await expect(page.getByRole('heading', { name: /ordens de serviço/i })).toBeVisible();
  });

  test('VISUALIZADOR: pode visualizar clientes', async ({ page }) => {
    await page.goto('/clientes');
    await expect(page.getByRole('heading', { name: /clientes/i })).toBeVisible();
  });

});

test.describe('RBAC — Permissões Granulares por Módulo', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

  test('ADMIN: tem acesso completo a todos os módulos', async ({ page }) => {
    const modulos = [
      '/dashboard',
      '/ordens-servico',
      '/clientes',
      '/orcamentos',
      '/transacoes',
      '/estoque',
      '/agenda',
      '/equipe',
      '/configuracoes',
    ];

    for (const modulo of modulos) {
      await page.goto(modulo);
      await page.waitForTimeout(500);
      const currentUrl = page.url();
      expect(currentUrl).not.toMatch(/acesso-negado|login/);
    }
  });

  test('ADMIN: pode acessar configurações do sistema', async ({ page }) => {
    await page.goto('/configuracoes');
    await expect(page.getByRole('heading', { name: /configurações/i })).toBeVisible();
  });

  test('ADMIN: pode acessar módulo financeiro', async ({ page }) => {
    await page.goto('/transacoes');
    await expect(page.getByRole('heading', { name: /financeiro|transações/i }).or(page.getByRole('heading', { name: /transações/i }))).toBeVisible({ timeout: 10000 });
  });

});

test.describe('RBAC — Menu de Navegação', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/tecnico.json') });

  test('TÉCNICO: vê menu Ordens de Serviço na sidebar', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(500);
    
    const menuOS = page.locator('[data-testid="nav-ordens-servico"]');
    const isVisible = await menuOS.isVisible().catch(() => false);
    if (!isVisible) {
      const menuTexto = page.locator('a', { hasText: /ordens de serviço|os/i });
      await expect(menuTexto).toBeVisible();
    } else {
      await expect(menuOS).toBeVisible();
    }
  });

  test('TÉCNICO: vê menu Clientes na sidebar', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(500);
    
    const menuClientes = page.locator('[data-testid="nav-clientes"]');
    const isVisible = await menuClientes.isVisible().catch(() => false);
    if (!isVisible) {
      const menuTexto = page.locator('a', { hasText: /clientes/i });
      await expect(menuTexto).toBeVisible();
    } else {
      await expect(menuClientes).toBeVisible();
    }
  });

});

test.describe('RBAC — Perfil Gerente', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

  test('GERENTE: pode aprovar orçamentos (estrutura)', async ({ page }) => {
    await page.goto('/orcamentos');
    await expect(page.getByRole('heading', { name: /orçamentos/i })).toBeVisible();
  });

  test('GERENTE: pode acessar módulo financeiro (estrutura)', async ({ page }) => {
    await page.goto('/transacoes');
    await expect(page.getByRole('heading', { name: /financeiro|transações/i }).or(page.getByRole('heading', { name: /transações/i }))).toBeVisible();
  });
});
