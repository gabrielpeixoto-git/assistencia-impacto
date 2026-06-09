# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Autenticação >> deve fazer login com credenciais válidas
- Location: e2e\auth.spec.ts:13:3

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /.*dashboard/
Received string:  "http://localhost:5173/"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    11 × unexpected value "http://localhost:5173/login"
    2 × unexpected value "http://localhost:5173/"

```

```yaml
- complementary:
  - img
  - heading "Assistência Impacto" [level=1]
  - button:
    - img
  - navigation:
    - paragraph: VISÃO GERAL
    - link "Dashboard":
      - /url: /
      - img
      - text: Dashboard
    - paragraph: OPERAÇÕES
    - link "Ordens de Serviço":
      - /url: /ordens-servico
      - img
      - text: Ordens de Serviço
    - link "Orçamentos":
      - /url: /orcamentos
      - img
      - text: Orçamentos
    - link "Agenda":
      - /url: /agenda
      - img
      - text: Agenda
    - link "Clientes":
      - /url: /clientes
      - img
      - text: Clientes
    - paragraph: FINANCEIRO
    - link "Visão Financeira":
      - /url: /financeiro
      - img
      - text: Visão Financeira
    - link "Transações":
      - /url: /transacoes
      - img
      - text: Transações
    - paragraph: RECURSOS
    - link "Estoque":
      - /url: /estoque
      - img
      - text: Estoque
    - link "Equipe":
      - /url: /equipe
      - img
      - text: Equipe
    - paragraph: ANÁLISE
    - link "Relatórios":
      - /url: /relatorios
      - img
      - text: Relatórios
    - paragraph: SISTEMA
    - link "Configurações":
      - /url: /configuracoes
      - img
      - text: Configurações
  - button "Sair":
    - img
    - text: Sair
- banner:
  - img
  - textbox "Buscar... (Cmd+K)"
  - button:
    - img
  - button:
    - img
    - paragraph
    - img
- main:
  - heading "Dashboard" [level=1]
  - paragraph: Visão geral do sistema
  - img
  - text: ↑ 12% 0 OS Hoje
  - img
  - text: ↑ 8% 17 OS Semana
  - img
  - text: ↑ 15% R$ 22.163,50 Receita Mensal
  - img
  - text: ↑ 10% R$ 3.713,50 Lucro Mensal
  - img
  - text: 41 Orçamentos Pendentes
  - img
  - text: 0 Pagamentos Atrasados
  - img
  - text: 3 Estoque Crítico
  - heading "Receita Últimos 7 Dias" [level=2]
  - img: 17/05 18/05 19/05 20/05 21/05 22/05 23/05 24/05 R$ 0 R$ 2.500 R$ 5.000 R$ 7.500 R$ 10.000
  - heading "Ordens de Serviço Recentes" [level=2]
  - table:
    - rowgroup:
      - row "Número Título Status Prioridade Data":
        - columnheader "Número"
        - columnheader "Título"
        - columnheader "Status"
        - columnheader "Prioridade"
        - columnheader "Data"
    - rowgroup:
      - row "OS202605-18 OS teste trimestre 2 pendente normal 23/05/2026":
        - cell "OS202605-18"
        - cell "OS teste trimestre 2"
        - cell "pendente"
        - cell "normal"
        - cell "23/05/2026"
      - row "OS202605-17 OS teste trimestre 1 pendente normal 23/05/2026":
        - cell "OS202605-17"
        - cell "OS teste trimestre 1"
        - cell "pendente"
        - cell "normal"
        - cell "23/05/2026"
      - row "OS202605-16 OS teste trimestre 0 pendente normal 23/05/2026":
        - cell "OS202605-16"
        - cell "OS teste trimestre 0"
        - cell "pendente"
        - cell "normal"
        - cell "23/05/2026"
      - row "OS202605-15 OS teste mês 3 pendente normal 23/05/2026":
        - cell "OS202605-15"
        - cell "OS teste mês 3"
        - cell "pendente"
        - cell "normal"
        - cell "23/05/2026"
      - row "OS202605-14 OS teste mês 2 pendente normal 23/05/2026":
        - cell "OS202605-14"
        - cell "OS teste mês 2"
        - cell "pendente"
        - cell "normal"
        - cell "23/05/2026"
  - heading "Agenda - Próximos Dias" [level=2]
  - paragraph: Nenhum evento agendado para os próximos dias
  - heading "Top Clientes" [level=2]
  - text: "1"
  - heading "Cliente Teste" [level=3]
  - text: R$ 0,00 2
  - heading "8888888" [level=3]
  - text: R$ 0,00 3
  - heading "gabriel" [level=3]
  - text: R$ 0,00 4
  - heading "Cliente Teste Agenda" [level=3]
  - text: R$ 0,00 5
  - heading "Cliente Teste At" [level=3]
  - text: R$ 0,00
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
> 24 |     await expect(page).toHaveURL(/.*dashboard/);
     |                        ^ Error: expect(page).toHaveURL(expected) failed
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
  41 |     await expect(page.locator('text=erro').or(page.locator('text=Erro').or(page.locator('text=inválidas')))).toBeVisible({ timeout: 5000 });
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