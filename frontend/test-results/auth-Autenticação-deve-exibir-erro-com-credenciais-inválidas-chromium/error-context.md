# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Autenticação >> deve exibir erro com credenciais inválidas
- Location: e2e\auth.spec.ts:30:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=erro').or(locator('text=Erro').or(locator('text=inválidas')))
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=erro').or(locator('text=Erro').or(locator('text=inválidas')))

```

```yaml
- img
- heading "Assistência Impacto" [level=1]
- paragraph: Sistema de Gestão
- text: Email
- img
- textbox "seu@email.com": admin@assistenciaimpacto.com.br
- text: Senha
- img
- textbox "••••••••"
- button "Entrar"
- paragraph: Esqueceu sua senha? Entre em contato com o administrador.
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Autenticação', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('/');
  6  |   });
  7  | 
  8  |   test('deve exibir página de login quando não autenticado', async ({ page }) => {
  9  |     await expect(page).toHaveTitle(/Assistência Impacto/);
  10 |     await expect(page.locator('text=Login')).toBeVisible();
  11 |   });
  12 | 
  13 |   test('deve fazer login com credenciais válidas', async ({ page }) => {
  14 |     // Preencher email
  15 |     await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
  16 |     
  17 |     // Preencher senha
  18 |     await page.fill('input[type="password"]', 'admin123');
  19 |     
  20 |     // Clicar no botão de login
  21 |     await page.click('button[type="submit"]');
  22 | 
  23 |     // Verificar redirecionamento para dashboard
  24 |     await expect(page).toHaveURL(/.*dashboard/);
  25 |     
  26 |     // Verificar se o usuário está autenticado (verificar se há elementos do dashboard)
  27 |     await expect(page.locator('text=Dashboard')).toBeVisible();
  28 |   });
  29 | 
  30 |   test('deve exibir erro com credenciais inválidas', async ({ page }) => {
  31 |     // Preencher email inválido
  32 |     await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
  33 |     
  34 |     // Preencher senha inválida
  35 |     await page.fill('input[type="password"]', 'senhaerrada');
  36 |     
  37 |     // Clicar no botão de login
  38 |     await page.click('button[type="submit"]');
  39 | 
  40 |     // Verificar se mensagem de erro é exibida
> 41 |     await expect(page.locator('text=erro').or(page.locator('text=Erro').or(page.locator('text=inválidas')))).toBeVisible({ timeout: 5000 });
     |                                                                                                              ^ Error: expect(locator).toBeVisible() failed
  42 |   });
  43 | 
  44 |   test('deve fazer logout corretamente', async ({ page }) => {
  45 |     // Fazer login primeiro
  46 |     await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
  47 |     await page.fill('input[type="password"]', 'admin123');
  48 |     await page.click('button[type="submit"]');
  49 | 
  50 |     // Aguardar redirecionamento
  51 |     await page.waitForURL(/.*dashboard/);
  52 | 
  53 |     // Clicar no botão de logout (geralmente no menu de usuário)
  54 |     const logoutButton = page.locator('button').filter({ hasText: /Sair|Logout/ }).or(
  55 |       page.locator('[aria-label*="Sair"]').or(page.locator('[aria-label*="Logout"]'))
  56 |     );
  57 |     
  58 |     if (await logoutButton.isVisible({ timeout: 5000 })) {
  59 |       await logoutButton.click();
  60 |     } else {
  61 |       // Tentar abrir menu de usuário primeiro
  62 |       const userMenu = page.locator('button').filter({ hasText: /admin/i }).or(
  63 |         page.locator('[aria-label*="usuário"]').or(page.locator('[aria-label*="menu"]'))
  64 |       );
  65 |       
  66 |       if (await userMenu.isVisible({ timeout: 3000 })) {
  67 |         await userMenu.click();
  68 |         await page.waitForTimeout(500);
  69 |         await logoutButton.click();
  70 |       }
  71 |     }
  72 | 
  73 |     // Verificar redirecionamento para login
  74 |     await expect(page).toHaveURL(/.*login/, { timeout: 5000 });
  75 |   });
  76 | 
  77 |   test('deve validar campos obrigatórios no login', async ({ page }) => {
  78 |     // Tentar fazer login sem preencher campos
  79 |     await page.click('button[type="submit"]');
  80 | 
  81 |     // Verificar validação HTML5
  82 |     const emailInput = page.locator('input[type="email"]');
  83 |     await expect(emailInput).toHaveAttribute('required', '');
  84 | 
  85 |     const passwordInput = page.locator('input[type="password"]');
  86 |     await expect(passwordInput).toHaveAttribute('required', '');
  87 |   });
  88 | });
  89 | 
```