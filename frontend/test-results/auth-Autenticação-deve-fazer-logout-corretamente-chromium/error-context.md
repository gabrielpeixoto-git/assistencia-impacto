# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Autenticação >> deve fazer logout corretamente
- Location: e2e\auth.spec.ts:44:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForURL: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
  navigated to "http://localhost:5173/"
============================================================
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e7]:
          - img [ref=e9]
          - heading "Assistência Impacto" [level=1] [ref=e12]
          - button [ref=e13] [cursor=pointer]:
            - img [ref=e14]
        - navigation [ref=e17]:
          - generic [ref=e18]:
            - paragraph [ref=e19]: VISÃO GERAL
            - link "Dashboard" [ref=e21] [cursor=pointer]:
              - /url: /
              - img [ref=e22]
              - generic [ref=e27]: Dashboard
          - generic [ref=e28]:
            - paragraph [ref=e29]: OPERAÇÕES
            - generic [ref=e30]:
              - link "Ordens de Serviço" [ref=e31] [cursor=pointer]:
                - /url: /ordens-servico
                - img [ref=e32]
                - generic [ref=e35]: Ordens de Serviço
              - link "Orçamentos" [ref=e36] [cursor=pointer]:
                - /url: /orcamentos
                - img [ref=e37]
                - generic [ref=e40]: Orçamentos
              - link "Agenda" [ref=e41] [cursor=pointer]:
                - /url: /agenda
                - img [ref=e42]
                - generic [ref=e44]: Agenda
              - link "Clientes" [ref=e45] [cursor=pointer]:
                - /url: /clientes
                - img [ref=e46]
                - generic [ref=e51]: Clientes
          - generic [ref=e52]:
            - paragraph [ref=e53]: FINANCEIRO
            - generic [ref=e54]:
              - link "Visão Financeira" [ref=e55] [cursor=pointer]:
                - /url: /financeiro
                - img [ref=e56]
                - generic [ref=e58]: Visão Financeira
              - link "Transações" [ref=e59] [cursor=pointer]:
                - /url: /transacoes
                - img [ref=e60]
                - generic [ref=e63]: Transações
          - generic [ref=e64]:
            - paragraph [ref=e65]: RECURSOS
            - generic [ref=e66]:
              - link "Estoque" [ref=e67] [cursor=pointer]:
                - /url: /estoque
                - img [ref=e68]
                - generic [ref=e72]: Estoque
              - link "Equipe" [ref=e73] [cursor=pointer]:
                - /url: /equipe
                - img [ref=e74]
                - generic [ref=e79]: Equipe
          - generic [ref=e80]:
            - paragraph [ref=e81]: ANÁLISE
            - link "Relatórios" [ref=e83] [cursor=pointer]:
              - /url: /relatorios
              - img [ref=e84]
              - generic [ref=e86]: Relatórios
          - generic [ref=e87]:
            - paragraph [ref=e88]: SISTEMA
            - link "Configurações" [ref=e90] [cursor=pointer]:
              - /url: /configuracoes
              - img [ref=e91]
              - generic [ref=e94]: Configurações
        - button "Sair" [ref=e97] [cursor=pointer]:
          - img [ref=e98]
          - generic [ref=e101]: Sair
    - generic [ref=e102]:
      - banner [ref=e103]:
        - generic [ref=e105]:
          - img [ref=e106]
          - textbox "Buscar... (Cmd+K)" [ref=e109]
        - generic [ref=e110]:
          - button [ref=e112] [cursor=pointer]:
            - img [ref=e113]
          - button [ref=e117] [cursor=pointer]:
            - img [ref=e119]
            - generic [ref=e122]:
              - paragraph
              - img [ref=e123]
      - main [ref=e125]:
        - generic [ref=e127]:
          - generic [ref=e128]:
            - heading "Dashboard" [level=1] [ref=e129]
            - paragraph [ref=e130]: Visão geral do sistema
          - generic [ref=e131]:
            - generic [ref=e132]:
              - generic [ref=e133]:
                - img [ref=e135]
                - generic [ref=e138]:
                  - generic [ref=e139]: ↑
                  - generic [ref=e140]: 12%
              - generic [ref=e141]: "0"
              - generic [ref=e142]: OS Hoje
            - generic [ref=e143]:
              - generic [ref=e144]:
                - img [ref=e146]
                - generic [ref=e149]:
                  - generic [ref=e150]: ↑
                  - generic [ref=e151]: 8%
              - generic [ref=e152]: "17"
              - generic [ref=e153]: OS Semana
            - generic [ref=e154]:
              - generic [ref=e155]:
                - img [ref=e157]
                - generic [ref=e159]:
                  - generic [ref=e160]: ↑
                  - generic [ref=e161]: 15%
              - generic [ref=e162]: R$ 22.163,50
              - generic [ref=e163]: Receita Mensal
            - generic [ref=e164]:
              - generic [ref=e165]:
                - img [ref=e167]
                - generic [ref=e170]:
                  - generic [ref=e171]: ↑
                  - generic [ref=e172]: 10%
              - generic [ref=e173]: R$ 3.713,50
              - generic [ref=e174]: Lucro Mensal
          - generic [ref=e175]:
            - generic [ref=e176]:
              - img [ref=e179]
              - generic [ref=e182]: "41"
              - generic [ref=e183]: Orçamentos Pendentes
            - generic [ref=e184]:
              - img [ref=e187]
              - generic [ref=e189]: "0"
              - generic [ref=e190]: Pagamentos Atrasados
            - generic [ref=e191]:
              - img [ref=e194]
              - generic [ref=e198]: "3"
              - generic [ref=e199]: Estoque Crítico
          - generic [ref=e200]:
            - heading "Receita Últimos 7 Dias" [level=2] [ref=e201]
            - img [ref=e204]:
              - generic [ref=e209]:
                - generic [ref=e211]: 17/05
                - generic [ref=e213]: 18/05
                - generic [ref=e215]: 19/05
                - generic [ref=e217]: 20/05
                - generic [ref=e219]: 21/05
                - generic [ref=e221]: 22/05
                - generic [ref=e223]: 23/05
                - generic [ref=e225]: 24/05
              - generic [ref=e227]:
                - generic [ref=e229]: R$ 0
                - generic [ref=e231]: R$ 2.500
                - generic [ref=e233]: R$ 5.000
                - generic [ref=e235]: R$ 7.500
                - generic [ref=e237]: R$ 10.000
          - generic [ref=e249]:
            - heading "Ordens de Serviço Recentes" [level=2] [ref=e250]
            - table [ref=e252]:
              - rowgroup [ref=e253]:
                - row "Número Título Status Prioridade Data" [ref=e254]:
                  - columnheader "Número" [ref=e255]
                  - columnheader "Título" [ref=e256]
                  - columnheader "Status" [ref=e257]
                  - columnheader "Prioridade" [ref=e258]
                  - columnheader "Data" [ref=e259]
              - rowgroup [ref=e260]:
                - row "OS202605-18 OS teste trimestre 2 pendente normal 23/05/2026" [ref=e261]:
                  - cell "OS202605-18" [ref=e262]
                  - cell "OS teste trimestre 2" [ref=e263]
                  - cell "pendente" [ref=e264]
                  - cell "normal" [ref=e265]
                  - cell "23/05/2026" [ref=e266]
                - row "OS202605-17 OS teste trimestre 1 pendente normal 23/05/2026" [ref=e267]:
                  - cell "OS202605-17" [ref=e268]
                  - cell "OS teste trimestre 1" [ref=e269]
                  - cell "pendente" [ref=e270]
                  - cell "normal" [ref=e271]
                  - cell "23/05/2026" [ref=e272]
                - row "OS202605-16 OS teste trimestre 0 pendente normal 23/05/2026" [ref=e273]:
                  - cell "OS202605-16" [ref=e274]
                  - cell "OS teste trimestre 0" [ref=e275]
                  - cell "pendente" [ref=e276]
                  - cell "normal" [ref=e277]
                  - cell "23/05/2026" [ref=e278]
                - row "OS202605-15 OS teste mês 3 pendente normal 23/05/2026" [ref=e279]:
                  - cell "OS202605-15" [ref=e280]
                  - cell "OS teste mês 3" [ref=e281]
                  - cell "pendente" [ref=e282]
                  - cell "normal" [ref=e283]
                  - cell "23/05/2026" [ref=e284]
                - row "OS202605-14 OS teste mês 2 pendente normal 23/05/2026" [ref=e285]:
                  - cell "OS202605-14" [ref=e286]
                  - cell "OS teste mês 2" [ref=e287]
                  - cell "pendente" [ref=e288]
                  - cell "normal" [ref=e289]
                  - cell "23/05/2026" [ref=e290]
          - generic [ref=e291]:
            - heading "Agenda - Próximos Dias" [level=2] [ref=e292]
            - paragraph [ref=e293]: Nenhum evento agendado para os próximos dias
          - generic [ref=e294]:
            - heading "Top Clientes" [level=2] [ref=e295]
            - generic [ref=e296]:
              - generic [ref=e297]:
                - generic [ref=e298]: "1"
                - heading "Cliente Teste" [level=3] [ref=e300]
                - generic [ref=e301]: R$ 0,00
              - generic [ref=e302]:
                - generic [ref=e303]: "2"
                - heading "8888888" [level=3] [ref=e305]
                - generic [ref=e306]: R$ 0,00
              - generic [ref=e307]:
                - generic [ref=e308]: "3"
                - heading "gabriel" [level=3] [ref=e310]
                - generic [ref=e311]: R$ 0,00
              - generic [ref=e312]:
                - generic [ref=e313]: "4"
                - heading "Cliente Teste Agenda" [level=3] [ref=e315]
                - generic [ref=e316]: R$ 0,00
              - generic [ref=e317]:
                - generic [ref=e318]: "5"
                - heading "Cliente Teste At" [level=3] [ref=e320]
                - generic [ref=e321]: R$ 0,00
  - generic [ref=e322]: R$ 0
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
> 51 |     await page.waitForURL(/.*dashboard/);
     |                ^ Error: page.waitForURL: Test timeout of 30000ms exceeded.
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