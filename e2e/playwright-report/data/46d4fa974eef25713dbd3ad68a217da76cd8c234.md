# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: financeiro.spec.ts >> Módulo Financeiro - CRUD de Transações >> deve filtrar transações por status
- Location: specs\financeiro.spec.ts:148:7

# Error details

```
Error: locator.inputValue: Error: Node is not an <input>, <textarea> or <select> element
Call log:
  - waiting for locator('[data-testid="select-status"]')

```

# Page snapshot

```yaml
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
            - generic [ref=e136]:
              - heading "Financeiro" [level=1] [ref=e137]
              - paragraph [ref=e138]: Gerencie as transações financeiras
            - button "Nova Transação" [ref=e139] [cursor=pointer]:
              - img [ref=e140]
              - text: Nova Transação
          - generic [ref=e142]:
            - generic [ref=e143]:
              - img [ref=e144]
              - textbox "Buscar por descrição..." [ref=e147]
            - button "Todos os Tipos ▼" [ref=e149] [cursor=pointer]:
              - generic [ref=e150]: Todos os Tipos
              - generic [ref=e151]: ▼
            - button "Pendente ▼" [ref=e153] [cursor=pointer]:
              - generic [ref=e154]: Pendente
              - generic [ref=e155]: ▼
            - button "Exportar CSV" [ref=e156] [cursor=pointer]
          - generic [ref=e158]:
            - img [ref=e160]
            - heading "Nenhuma transação encontrada" [level=3] [ref=e162]
            - paragraph [ref=e163]: Comece adicionando uma nova transação ao sistema
            - button "Adicionar Transação" [ref=e164] [cursor=pointer]
  - region "Notifications alt+T"
```

# Test source

```ts
  53  |   test('deve criar nova transação de receita', async ({ page }) => {
  54  |     // Clicar no botão nova transação
  55  |     await page.click('[data-testid="btn-nova-transacao"]');
  56  |     await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  57  |     await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Nova Transação');
  58  | 
  59  |     // Preencher formulário
  60  |     await page.click('[data-testid="select-tipo-modal"]');
  61  |     await page.click('text=Receita');
  62  |     
  63  |     await page.click('[data-testid="select-categoria-modal"]');
  64  |     // Esperar categorias carregarem
  65  |     await page.waitForTimeout(500);
  66  |     const categoriaOption = await page.locator('[data-testid="select-categoria-modal"] option').nth(1);
  67  |     if (await categoriaOption.count() > 0) {
  68  |       await page.selectOption('[data-testid="select-categoria-modal"]', await categoriaOption.getAttribute('value'));
  69  |     }
  70  | 
  71  |     await page.fill('[data-testid="input-descricao-modal"]', 'Receita de teste E2E');
  72  |     await page.fill('[data-testid="input-valor-modal"]', '500,00');
  73  |     
  74  |     // Data de vencimento (hoje + 7 dias)
  75  |     const dataVencimento = new Date();
  76  |     dataVencimento.setDate(dataVencimento.getDate() + 7);
  77  |     const dataFormatada = dataVencimento.toISOString().split('T')[0];
  78  |     await page.fill('[data-testid="input-data-vencimento-modal"]', dataFormatada);
  79  | 
  80  |     // Salvar
  81  |     await page.click('[data-testid="btn-salvar-modal"]');
  82  |     
  83  |     // Verificar sucesso
  84  |     await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
  85  |     // Verificar toast de sucesso (pode variar)
  86  |     await page.waitForTimeout(1000);
  87  |   });
  88  | 
  89  |   test('deve criar nova transação de despesa', async ({ page }) => {
  90  |     await page.click('[data-testid="btn-nova-transacao"]');
  91  |     await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  92  | 
  93  |     // Preencher como despesa
  94  |     await page.click('[data-testid="select-tipo-modal"]');
  95  |     await page.click('text=Despesa');
  96  |     
  97  |     await page.fill('[data-testid="input-descricao-modal"]', 'Despesa de teste E2E');
  98  |     await page.fill('[data-testid="input-valor-modal"]', '150,00');
  99  |     
  100 |     const dataVencimento = new Date();
  101 |     dataVencimento.setDate(dataVencimento.getDate() + 7);
  102 |     const dataFormatada = dataVencimento.toISOString().split('T')[0];
  103 |     await page.fill('[data-testid="input-data-vencimento-modal"]', dataFormatada);
  104 | 
  105 |     await page.click('[data-testid="btn-salvar-modal"]');
  106 |     await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
  107 |     await page.waitForTimeout(1000);
  108 |   });
  109 | 
  110 |   test('deve editar transação existente', async ({ page }) => {
  111 |     // Criar transação primeiro
  112 |     await criarTransacao({ descricao: 'Transação para edição E2E' });
  113 |     await page.reload();
  114 |     await page.waitForSelector('[data-testid="financeiro-container"]');
  115 | 
  116 |     // Encontrar e clicar no botão de editar da primeira transação
  117 |     const botaoEditar = page.locator('[data-testid="card-tabela-transacoes"]').locator('button').first();
  118 |     if (await botaoEditar.count() > 0) {
  119 |       await botaoEditar.click();
  120 |       await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  121 |       await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Editar Transação');
  122 | 
  123 |       // Modificar descrição
  124 |       await page.fill('[data-testid="input-descricao-modal"]', 'Transação editada E2E');
  125 |       await page.click('[data-testid="btn-salvar-modal"]');
  126 |       await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
  127 |     }
  128 |   });
  129 | 
  130 |   test('deve cancelar criação de transação', async ({ page }) => {
  131 |     await page.click('[data-testid="btn-nova-transacao"]');
  132 |     await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  133 | 
  134 |     await page.click('[data-testid="btn-cancelar-modal"]');
  135 |     await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
  136 |   });
  137 | 
  138 |   test('deve filtrar transações por tipo', async ({ page }) => {
  139 |     await page.click('[data-testid="seletor-periodo"]');
  140 |     await page.click('text=Receita');
  141 |     await page.waitForTimeout(500);
  142 |     
  143 |     // Verificar que o filtro foi aplicado
  144 |     const valorSelecionado = await page.locator('[data-testid="seletor-periodo"]').inputValue();
  145 |     expect(valorSelecionado).toBe('receita');
  146 |   });
  147 | 
  148 |   test('deve filtrar transações por status', async ({ page }) => {
  149 |     await page.click('[data-testid="select-status"]');
  150 |     await page.click('text=Pendente');
  151 |     await page.waitForTimeout(500);
  152 |     
> 153 |     const valorSelecionado = await page.locator('[data-testid="select-status"]').inputValue();
      |                                                                                  ^ Error: locator.inputValue: Error: Node is not an <input>, <textarea> or <select> element
  154 |     expect(valorSelecionado).toBe('pendente');
  155 |   });
  156 | 
  157 |   test('deve buscar transações por descrição', async ({ page }) => {
  158 |     await page.fill('[data-testid="input-busca"]', 'teste');
  159 |     await page.waitForTimeout(500);
  160 |     
  161 |     // Verificar que o campo tem o valor buscado
  162 |     const valorBusca = await page.locator('[data-testid="input-busca"]').inputValue();
  163 |     expect(valorBusca).toBe('teste');
  164 |   });
  165 | 
  166 |   test('deve validar campos obrigatórios ao criar transação', async ({ page }) => {
  167 |     await page.click('[data-testid="btn-nova-transacao"]');
  168 |     await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  169 | 
  170 |     // Tentar salvar sem preencher campos obrigatórios
  171 |     await page.click('[data-testid="btn-salvar-modal"]');
  172 |     
  173 |     // Modal deve permanecer aberto (validação impediu salvamento)
  174 |     await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
  175 |     
  176 |     await page.click('[data-testid="btn-cancelar-modal"]');
  177 |   });
  178 | });
  179 | 
```