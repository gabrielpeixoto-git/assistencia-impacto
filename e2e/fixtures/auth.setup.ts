import { test as setup, expect } from '@playwright/test';
import path from 'path';

const adminFile = '.auth/admin.json';
const tecnicoFile = '.auth/tecnico.json';

setup('autenticar como admin', async ({ page }) => {
  await page.goto(process.env.BASE_URL + '/login');
  await page.getByTestId('login-email').fill(process.env.ADMIN_EMAIL || 'admin@teste.com');
  await page.getByTestId('login-senha').fill(process.env.ADMIN_SENHA || 'Admin123!');
  await page.getByTestId('login-botao-entrar').click();
  await expect(page).toHaveURL(/.*\/$/, { timeout: 15000 });
  
  // Aguardar React carregar e Zustand persistir no localStorage
  await page.waitForTimeout(2000);
  
  await page.context().storageState({ path: path.resolve(__dirname, adminFile) });
});

setup('autenticar como técnico', async ({ page }) => {
  await page.goto(process.env.BASE_URL + '/login');
  await page.getByTestId('login-email').fill(process.env.TECNICO_EMAIL || 'tecnico@teste.com');
  await page.getByTestId('login-senha').fill(process.env.TECNICO_SENHA || 'Tecnico123!');
  await page.getByTestId('login-botao-entrar').click();
  await expect(page).toHaveURL(/.*\/$/, { timeout: 15000 });
  
  // Aguardar React carregar e Zustand persistir no localStorage
  await page.waitForTimeout(2000);
  
  await page.context().storageState({ path: path.resolve(__dirname, tecnicoFile) });
});
