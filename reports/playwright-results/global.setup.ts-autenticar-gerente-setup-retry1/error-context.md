# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: global.setup.ts >> autenticar gerente
- Location: specs/global.setup.ts:46:6

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/login
Call log:
  - navigating to "http://localhost:5173/login", waiting until "load"

```

# Test source

```ts
  1  | import { test as setup, expect } from '@playwright/test';
  2  | import path from 'path';
  3  | 
  4  | const ADMIN_AUTH_FILE = path.join(__dirname, '..', '.auth/admin.json');
  5  | const TECNICO_AUTH_FILE = path.join(__dirname, '..', '.auth/tecnico.json');
  6  | const GERENTE_AUTH_FILE = path.join(__dirname, '..', '.auth/gerente.json');
  7  | 
  8  | // Garante que o diretório .auth existe
  9  | import fs from 'fs';
  10 | if (!fs.existsSync(path.join(__dirname, '..', '.auth'))) {
  11 |   fs.mkdirSync(path.join(__dirname, '..', '.auth'));
  12 | }
  13 | 
  14 | setup('autenticar admin', async ({ page }) => {
  15 |   await page.goto('/login');
  16 |   await page.waitForSelector('[data-testid="input-email"]', { timeout: 30000 });
  17 | 
  18 |   await page.fill('[data-testid="input-email"]',
  19 |     process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br');
  20 |   await page.fill('[data-testid="input-senha"]',
  21 |     process.env.ADMIN_SENHA || 'Admin@123');
  22 |   await page.click('[data-testid="btn-login"]');
  23 | 
  24 |   // Aguarda redirect para rota raiz
  25 |   await page.waitForURL('/', { timeout: 15000 });
  26 |   await expect(page).toHaveURL('/');
  27 |   await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });
  28 | 
  29 |   // Salva estado de autenticação
  30 |   await page.context().storageState({ path: ADMIN_AUTH_FILE });
  31 | });
  32 | 
  33 | setup('autenticar tecnico', async ({ page }) => {
  34 |   await page.goto('/login');
  35 |   await page.fill('[data-testid="input-email"]',
  36 |     process.env.TECNICO_EMAIL || 'joao@assistenciaimpacto.com.br');
  37 |   await page.fill('[data-testid="input-senha"]',
  38 |     process.env.TECNICO_SENHA || 'Tecnico@123');
  39 |   await page.click('[data-testid="btn-login"]');
  40 |   await page.waitForURL('/', { timeout: 15000 });
  41 |   await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });
  42 |   await page.waitForTimeout(2000); // Aguarda auth.store persistir
  43 |   await page.context().storageState({ path: TECNICO_AUTH_FILE });
  44 | });
  45 | 
  46 | setup('autenticar gerente', async ({ page }) => {
> 47 |   await page.goto('/login');
     |              ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/login
  48 |   await page.fill('[data-testid="input-email"]',
  49 |     process.env.GERENTE_EMAIL || 'gerente@assistenciaimpacto.com.br');
  50 |   await page.fill('[data-testid="input-senha"]',
  51 |     process.env.GERENTE_SENHA || 'Gerente@123');
  52 |   await page.click('[data-testid="btn-login"]');
  53 |   await page.waitForURL('/', { timeout: 15000 });
  54 |   await page.waitForSelector('[data-testid="sidebar"]', { timeout: 15000 });
  55 |   await page.context().storageState({ path: GERENTE_AUTH_FILE });
  56 | });
  57 | 
```