import { test, expect } from '@playwright/test';
import path from 'path';
import { criarNotificacao, buscarUsuarioPorEmail } from '../helpers/api.helper';

test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

test.describe('Módulo Notificações - Sino e Badge', () => {

  test('badge do sino exibe contagem de não lidas', async ({ page }) => {
    const admin = await buscarUsuarioPorEmail(
      process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
    );

    await criarNotificacao(admin.id);

    await page.goto('/dashboard');
    await page.waitForSelector('[data-testid=\"sino-notificacoes\"]');

    const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
    await expect(badge).toBeVisible();
  });

  test('sino de notificações está visível no header', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('[data-testid=\"sino-notificacoes\"]')).toBeVisible();
  });

  test('badge não aparece quando não há notificações não lidas', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForSelector('[data-testid=\"sino-notificacoes\"]');

    const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
    await expect(badge).not.toBeVisible();
  });
});

test.describe('Módulo Notificações - Dropdown e Leitura', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('dropdown de notificações abre e fecha', async ({ page }) => {
    await page.click('[data-testid=\"sino-notificacoes\"]');
    await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
      .toBeVisible({ timeout: 5000 });

    await page.click('body', { position: { x: 10, y: 10 } });
    await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
      .not.toBeVisible({ timeout: 3000 });
  });

  test('dropdown exibe lista de notificações', async ({ page }) => {
    const admin = await buscarUsuarioPorEmail(
      process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
    );
    await criarNotificacao(admin.id);

    await page.reload();
    await page.click('[data-testid=\"sino-notificacoes\"]');
    await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');

    const notificacoes = await page.locator('[data-testid^=\"notificacao-item-\"]').count();
    expect(notificacoes).toBeGreaterThan(0);
  });

  test('marcar todas como lidas zera o badge', async ({ page }) => {
    const admin = await buscarUsuarioPorEmail(
      process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
    );
    await criarNotificacao(admin.id);

    await page.reload();
    await page.click('[data-testid=\"sino-notificacoes\"]');
    await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');

    await page.click('[data-testid=\"btn-marcar-todas-lidas\"]');
    await page.waitForTimeout(1000);

    const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
    await expect(badge).not.toBeVisible();
  });

  test('clicar em notificação individual marca como lida', async ({ page }) => {
    const admin = await buscarUsuarioPorEmail(
      process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
    );
    await criarNotificacao(admin.id);

    await page.reload();
    await page.click('[data-testid=\"sino-notificacoes\"]');
    await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');

    const primeiraNotificacao = page.locator('[data-testid^=\"notificacao-item-\"]').first();
    await primeiraNotificacao.click();

    await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
      .not.toBeVisible({ timeout: 3000 });
  });

  test('dropdown exibe mensagem quando não há notificações', async ({ page }) => {
    await page.click('[data-testid=\"sino-notificacoes\"]');
    await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');

    const mensagem = page.locator('text=Nenhuma notificação');
    await expect(mensagem).toBeVisible();
  });
});

test.describe('Módulo Notificações - Menu de Usuário', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('menu de usuário abre e fecha', async ({ page }) => {
    await page.click('[data-testid=\"btn-menu-usuario\"]');
    await expect(page.locator('[data-testid=\"dropdown-usuario\"]')).toBeVisible();

    await page.click('body', { position: { x: 10, y: 10 } });
    await expect(page.locator('[data-testid=\"dropdown-usuario\"]')).not.toBeVisible();
  });

  test('botão de configurações está visível', async ({ page }) => {
    await page.click('[data-testid=\"btn-menu-usuario\"]');
    await expect(page.locator('[data-testid=\"btn-configuracoes\"]')).toBeVisible();
  });

  test('botão de logout está visível', async ({ page }) => {
    await page.click('[data-testid=\"btn-menu-usuario\"]');
    await expect(page.locator('[data-testid=\"btn-logout\"]')).toBeVisible();
  });

  test('clicar em logout redireciona para login', async ({ page }) => {
    await page.click('[data-testid=\"btn-menu-usuario\"]');
    await page.click('[data-testid=\"btn-logout\"]');

    await page.waitForURL('**/login', { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });
});
