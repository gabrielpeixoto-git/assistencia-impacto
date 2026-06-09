# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: notificacoes.spec.ts >> Módulo Notificações - Dropdown e Leitura >> dropdown exibe mensagem quando não há notificações
- Location: specs\notificacoes.spec.ts:101:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Nenhuma notificação')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Nenhuma notificação')

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
  - text: A
  - paragraph: Administrador
  - paragraph: admin@assistenciaimpacto.com.br
  - button "Sair":
    - img
    - text: Sair
- banner:
  - img
  - textbox "Buscar... (Cmd+K)"
  - button:
    - img
  - heading "Notificações" [level=3]
  - button "Marcar todas como lidas"
  - paragraph: Nova ordem de serviço
  - paragraph: "OS #1234 foi criada"
  - paragraph: 04/06/2026
  - paragraph: Orçamento aprovado
  - paragraph: "Orçamento #567 foi aprovado"
  - paragraph: 04/06/2026
  - button "Administrador":
    - img
    - paragraph: Administrador
    - img
- main:
  - heading "Dashboard" [level=1]
  - paragraph: Visão geral do sistema
  - img
  - text: ↑ 12% 0 OS Hoje
  - img
  - text: ↑ 8% 0 OS Semana
  - img
  - text: ↑ 15% R$ 0,00 Receita Mensal
  - img
  - text: ↑ 10% R$ 0,00 Lucro Mensal
  - img
  - text: 0 Clientes Ativos
  - img
  - text: 0 Orçamentos Pendentes
  - img
  - text: 0 Pagamentos Atrasados
  - img
  - text: 0 Estoque Crítico
  - heading "Receita Últimos 7 Dias" [level=2]
  - img: 01/06 02/06 03/06 04/06 R$ 0 R$ 1 R$ 2 R$ 3 R$ 4
  - heading "Ordens de Serviço por Status" [level=2]
  - paragraph: Sem dados disponíveis
  - heading "Ordens de Serviço Recentes" [level=2]
  - text: Nenhum registro encontrado
  - heading "Agenda - Próximos Dias" [level=2]
  - paragraph: Nenhum evento agendado para os próximos dias
  - heading "Top Clientes" [level=2]
  - paragraph: Nenhum cliente encontrado
- region "Notifications alt+T"
```

# Test source

```ts
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
  33  |     await expect(badge).not.toBeVisible();
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
> 106 |     await expect(mensagem).toBeVisible();
      |                            ^ Error: expect(locator).toBeVisible() failed
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
  134 |   test('clicar em logout redireciona para login', async ({ page }) => {
  135 |     await page.click('[data-testid=\"btn-menu-usuario\"]');
  136 |     await page.click('[data-testid=\"btn-logout\"]');
  137 | 
  138 |     await page.waitForURL('**/login', { timeout: 5000 });
  139 |     expect(page.url()).toContain('/login');
  140 |   });
  141 | });
  142 | 
```