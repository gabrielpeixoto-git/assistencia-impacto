import { test as setup, expect } from '@playwright/test';
import path from 'path';

const ADMIN_AUTH_FILE = path.join(__dirname, '..', '.auth/admin.json');
const TECNICO_AUTH_FILE = path.join(__dirname, '..', '.auth/tecnico.json');
const GERENTE_AUTH_FILE = path.join(__dirname, '..', '.auth/gerente.json');

// Garante que o diretório .auth existe
import fs from 'fs';
if (!fs.existsSync(path.join(__dirname, '..', '.auth'))) {
  fs.mkdirSync(path.join(__dirname, '..', '.auth'));
}

setup('autenticar admin', async ({ page }) => {
  await page.goto('/login');
  await page.waitForSelector('[data-testid="input-email"]', { timeout: 30000 });

  await page.fill('[data-testid="input-email"]',
    process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br');
  await page.fill('[data-testid="input-senha"]',
    process.env.ADMIN_SENHA || 'Admin@123');
  await page.click('[data-testid="btn-login"]');

  // Aguarda redirect para rota raiz
  await page.waitForURL('/', { timeout: 15000 });
  await expect(page).toHaveURL('/');
  await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });

  // Salva estado de autenticação
  await page.context().storageState({ path: ADMIN_AUTH_FILE });
});

setup('autenticar tecnico', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="input-email"]',
    process.env.TECNICO_EMAIL || 'joao@assistenciaimpacto.com.br');
  await page.fill('[data-testid="input-senha"]',
    process.env.TECNICO_SENHA || 'Tecnico@123');
  await page.click('[data-testid="btn-login"]');
  await page.waitForURL('/', { timeout: 15000 });
  await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });
  await page.waitForTimeout(2000); // Aguarda auth.store persistir
  await page.context().storageState({ path: TECNICO_AUTH_FILE });
});

setup('autenticar gerente', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="input-email"]',
    process.env.GERENTE_EMAIL || 'gerente@assistenciaimpacto.com.br');
  await page.fill('[data-testid="input-senha"]',
    process.env.GERENTE_SENHA || 'Gerente@123');
  await page.click('[data-testid="btn-login"]');
  await page.waitForURL('/', { timeout: 15000 });
  await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });
  await page.context().storageState({ path: GERENTE_AUTH_FILE });
});
