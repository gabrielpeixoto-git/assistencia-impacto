# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: notificacoes.spec.ts >> Módulo Notificações - Sino e Badge >> badge não aparece quando não há notificações não lidas
- Location: specs\notificacoes.spec.ts:28:7

# Error details

```
Error: expect(locator).not.toBeVisible() failed

Locator:  locator('[data-testid="badge-nao-lidas"]')
Expected: not visible
Received: visible
Timeout:  5000ms

Call log:
  - Expect "not toBeVisible" with timeout 5000ms
  - waiting for locator('[data-testid="badge-nao-lidas"]')
    13 × locator resolved to <span data-testid="badge-nao-lidas" class="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
       - unexpected value "visible"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
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
          - generic [ref=e95]:
            - generic [ref=e96]:
              - generic [ref=e98]: A
              - generic [ref=e99]:
                - paragraph [ref=e100]: Administrador
                - paragraph [ref=e101]: admin@assistenciaimpacto.com.br
            - button "Sair" [ref=e102] [cursor=pointer]:
              - img [ref=e103]
              - generic [ref=e106]: Sair
      - generic [ref=e107]:
        - banner [ref=e108]:
          - generic [ref=e110]:
            - img [ref=e111]
            - textbox "Buscar... (Cmd+K)" [ref=e114]
          - generic [ref=e115]:
            - button [ref=e117] [cursor=pointer]:
              - img [ref=e118]
            - button "Administrador" [ref=e123] [cursor=pointer]:
              - img [ref=e125]
              - generic [ref=e128]:
                - paragraph [ref=e129]: Administrador
                - img [ref=e130]
        - main [ref=e132]:
          - generic [ref=e134]:
            - generic [ref=e135]:
              - heading "Dashboard" [level=1] [ref=e136]
              - paragraph [ref=e137]: Visão geral do sistema
            - generic [ref=e138]:
              - generic [ref=e139]:
                - generic [ref=e140]:
                  - img [ref=e142]
                  - generic [ref=e145]:
                    - generic [ref=e146]: ↑
                    - generic [ref=e147]: 12%
                - generic [ref=e148]: "0"
                - generic [ref=e149]: OS Hoje
              - generic [ref=e150]:
                - generic [ref=e151]:
                  - img [ref=e153]
                  - generic [ref=e156]:
                    - generic [ref=e157]: ↑
                    - generic [ref=e158]: 8%
                - generic [ref=e159]: "0"
                - generic [ref=e160]: OS Semana
              - generic [ref=e161]:
                - generic [ref=e162]:
                  - img [ref=e164]
                  - generic [ref=e166]:
                    - generic [ref=e167]: ↑
                    - generic [ref=e168]: 15%
                - generic [ref=e169]: R$ 0,00
                - generic [ref=e170]: Receita Mensal
              - generic [ref=e171]:
                - generic [ref=e172]:
                  - img [ref=e174]
                  - generic [ref=e177]:
                    - generic [ref=e178]: ↑
                    - generic [ref=e179]: 10%
                - generic [ref=e180]: R$ 0,00
                - generic [ref=e181]: Lucro Mensal
            - generic [ref=e182]:
              - generic [ref=e183]:
                - img [ref=e186]
                - generic [ref=e190]: "0"
                - generic [ref=e191]: Clientes Ativos
              - generic [ref=e192]:
                - img [ref=e195]
                - generic [ref=e198]: "0"
                - generic [ref=e199]: Orçamentos Pendentes
              - generic [ref=e200]:
                - img [ref=e203]
                - generic [ref=e205]: "0"
                - generic [ref=e206]: Pagamentos Atrasados
              - generic [ref=e207]:
                - img [ref=e210]
                - generic [ref=e214]: "0"
                - generic [ref=e215]: Estoque Crítico
            - generic [ref=e216]:
              - heading "Receita Últimos 7 Dias" [level=2] [ref=e217]
              - img [ref=e220]:
                - generic [ref=e225]:
                  - generic [ref=e227]: 01/06
                  - generic [ref=e229]: 02/06
                  - generic [ref=e231]: 03/06
                  - generic [ref=e233]: 04/06
                - generic [ref=e235]:
                  - generic [ref=e237]: R$ 0
                  - generic [ref=e239]: R$ 1
                  - generic [ref=e241]: R$ 2
                  - generic [ref=e243]: R$ 3
                  - generic [ref=e245]: R$ 4
            - generic [ref=e252]:
              - heading "Ordens de Serviço por Status" [level=2] [ref=e253]
              - paragraph [ref=e254]: Sem dados disponíveis
            - generic [ref=e255]:
              - heading "Ordens de Serviço Recentes" [level=2] [ref=e256]
              - generic [ref=e257]: Nenhum registro encontrado
            - generic [ref=e258]:
              - heading "Agenda - Próximos Dias" [level=2] [ref=e259]
              - paragraph [ref=e260]: Nenhum evento agendado para os próximos dias
            - generic [ref=e261]:
              - heading "Top Clientes" [level=2] [ref=e262]
              - paragraph [ref=e263]: Nenhum cliente encontrado
    - region "Notifications alt+T"
  - generic [ref=e264]: R$ 0
```

# Test source

```ts
  1   | ﻿import { test, expect } from '@playwright/test';
  2   | import path from 'path';
  3   | import { criarNotificacao, buscarUsuarioPorEmail } from '../helpers/api.helper';
  4   | 
  5   | test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });
  6   | 
  7   | test.describe('Módulo Notificações - Sino e Badge', () => {
  8   | 
  9   |   test('badge do sino exibe contagem de não lidas', async ({ page }) => {
  10  |     const admin = await buscarUsuarioPorEmail(
  11  |       process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
  12  |     );
  13  | 
  14  |     await criarNotificacao(admin.id);
  15  | 
  16  |     await page.goto('/dashboard');
  17  |     await page.waitForSelector('[data-testid=\"sino-notificacoes\"]');
  18  | 
  19  |     const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
  20  |     await expect(badge).toBeVisible();
  21  |   });
  22  | 
  23  |   test('sino de notificações está visível no header', async ({ page }) => {
  24  |     await page.goto('/dashboard');
  25  |     await expect(page.locator('[data-testid=\"sino-notificacoes\"]')).toBeVisible();
  26  |   });
  27  | 
  28  |   test('badge não aparece quando não há notificações não lidas', async ({ page }) => {
  29  |     await page.goto('/dashboard');
  30  |     await page.waitForSelector('[data-testid=\"sino-notificacoes\"]');
  31  | 
  32  |     const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
> 33  |     await expect(badge).not.toBeVisible();
      |                             ^ Error: expect(locator).not.toBeVisible() failed
  34  |   });
  35  | });
  36  | 
  37  | test.describe('Módulo Notificações - Dropdown e Leitura', () => {
  38  | 
  39  |   test.beforeEach(async ({ page }) => {
  40  |     await page.goto('/dashboard');
  41  |   });
  42  | 
  43  |   test('dropdown de notificações abre e fecha', async ({ page }) => {
  44  |     await page.click('[data-testid=\"sino-notificacoes\"]');
  45  |     await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
  46  |       .toBeVisible({ timeout: 5000 });
  47  | 
  48  |     await page.click('body', { position: { x: 10, y: 10 } });
  49  |     await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
  50  |       .not.toBeVisible({ timeout: 3000 });
  51  |   });
  52  | 
  53  |   test('dropdown exibe lista de notificações', async ({ page }) => {
  54  |     const admin = await buscarUsuarioPorEmail(
  55  |       process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
  56  |     );
  57  |     await criarNotificacao(admin.id);
  58  | 
  59  |     await page.reload();
  60  |     await page.click('[data-testid=\"sino-notificacoes\"]');
  61  |     await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');
  62  | 
  63  |     const notificacoes = await page.locator('[data-testid^=\"notificacao-item-\"]').count();
  64  |     expect(notificacoes).toBeGreaterThan(0);
  65  |   });
  66  | 
  67  |   test('marcar todas como lidas zera o badge', async ({ page }) => {
  68  |     const admin = await buscarUsuarioPorEmail(
  69  |       process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
  70  |     );
  71  |     await criarNotificacao(admin.id);
  72  | 
  73  |     await page.reload();
  74  |     await page.click('[data-testid=\"sino-notificacoes\"]');
  75  |     await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');
  76  | 
  77  |     await page.click('[data-testid=\"btn-marcar-todas-lidas\"]');
  78  |     await page.waitForTimeout(1000);
  79  | 
  80  |     const badge = page.locator('[data-testid=\"badge-nao-lidas\"]');
  81  |     await expect(badge).not.toBeVisible();
  82  |   });
  83  | 
  84  |   test('clicar em notificação individual marca como lida', async ({ page }) => {
  85  |     const admin = await buscarUsuarioPorEmail(
  86  |       process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br'
  87  |     );
  88  |     await criarNotificacao(admin.id);
  89  | 
  90  |     await page.reload();
  91  |     await page.click('[data-testid=\"sino-notificacoes\"]');
  92  |     await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');
  93  | 
  94  |     const primeiraNotificacao = page.locator('[data-testid^=\"notificacao-item-\"]').first();
  95  |     await primeiraNotificacao.click();
  96  | 
  97  |     await expect(page.locator('[data-testid=\"dropdown-notificacoes\"]'))
  98  |       .not.toBeVisible({ timeout: 3000 });
  99  |   });
  100 | 
  101 |   test('dropdown exibe mensagem quando não há notificações', async ({ page }) => {
  102 |     await page.click('[data-testid=\"sino-notificacoes\"]');
  103 |     await page.waitForSelector('[data-testid=\"dropdown-notificacoes\"]');
  104 | 
  105 |     const mensagem = page.locator('text=Nenhuma notificação');
  106 |     await expect(mensagem).toBeVisible();
  107 |   });
  108 | });
  109 | 
  110 | test.describe('Módulo Notificações - Menu de Usuário', () => {
  111 | 
  112 |   test.beforeEach(async ({ page }) => {
  113 |     await page.goto('/dashboard');
  114 |   });
  115 | 
  116 |   test('menu de usuário abre e fecha', async ({ page }) => {
  117 |     await page.click('[data-testid=\"btn-menu-usuario\"]');
  118 |     await expect(page.locator('[data-testid=\"dropdown-usuario\"]')).toBeVisible();
  119 | 
  120 |     await page.click('body', { position: { x: 10, y: 10 } });
  121 |     await expect(page.locator('[data-testid=\"dropdown-usuario\"]')).not.toBeVisible();
  122 |   });
  123 | 
  124 |   test('botão de configurações está visível', async ({ page }) => {
  125 |     await page.click('[data-testid=\"btn-menu-usuario\"]');
  126 |     await expect(page.locator('[data-testid=\"btn-configuracoes\"]')).toBeVisible();
  127 |   });
  128 | 
  129 |   test('botão de logout está visível', async ({ page }) => {
  130 |     await page.click('[data-testid=\"btn-menu-usuario\"]');
  131 |     await expect(page.locator('[data-testid=\"btn-logout\"]')).toBeVisible();
  132 |   });
  133 | 
```