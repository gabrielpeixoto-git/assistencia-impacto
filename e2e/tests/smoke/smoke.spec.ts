import { test, expect } from '@playwright/test';

test.describe('Smoke Tests — Verificação de Saúde do Sistema', () => {
  test('SMOKE: página de login carrega sem erros', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('heading', { name: 'Assistência Impacto' }).first()).toBeVisible({ timeout: 10000 });
  });

  test('SMOKE: formulário de login está presente', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input[type="password"]')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible({ timeout: 10000 });
  });

  test('SMOKE: login com credenciais corretas funciona', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    
    // Preencher credenciais
    await page.locator('input[type="email"]').fill(process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br');
    await page.locator('input[type="password"]').fill(process.env.ADMIN_SENHA || 'admin123');
    
    // Clicar no botão de entrar
    await page.getByRole('button', { name: 'Entrar' }).click();
    
    // Verificar que saiu da página de login (login bem-sucedido)
    await expect(page).not.toHaveURL('/login', { timeout: 10000 });
  });
});
