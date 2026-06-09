# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: financeiro.spec.ts >> Módulo Financeiro - CRUD de Transações >> deve criar nova transação de receita
- Location: specs\financeiro.spec.ts:53:7

# Error details

```
Error: expect(locator).not.toBeVisible() failed

Locator:  locator('[data-testid="modal-transacao"]')
Expected: not visible
Received: visible
Timeout:  5000ms

Call log:
  - Expect "not toBeVisible" with timeout 5000ms
  - waiting for locator('[data-testid="modal-transacao"]')
    14 × locator resolved to <div data-testid="modal-transacao" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">…</div>
       - unexpected value "visible"

```

```yaml
- heading "Nova Transação" [level=2]
- text: Tipo *
- button "Receita ▼"
- text: Categoria *
- button "Selecione uma categoria ▼"
- text: Descrição *
- textbox "Descrição *":
  - /placeholder: Descrição da transação
  - text: Receita de teste E2E
- text: Valor *
- textbox "Valor *":
  - /placeholder: R$ 0,00
  - text: R$ 500,00
- text: Data de Vencimento *
- textbox "Data de Vencimento *": 2026-06-11
- text: Forma de Pagamento
- textbox "Forma de Pagamento":
  - /placeholder: "Ex: Dinheiro, Cartão, PIX"
- text: Conta Bancária
- textbox "Conta Bancária":
  - /placeholder: "Ex: Itaú, Nubank"
- text: Observações
- textbox "Observações":
  - /placeholder: Observações adicionais
- checkbox "Transação Recorrente"
- text: Transação Recorrente
- button "Cancelar":
  - img
  - text: Cancelar
- button "Salvar":
  - img
  - text: Salvar
```

# Test source

```ts
  1   | ﻿import { test, expect } from '@playwright/test';
  2   | import path from 'path';
  3   | import { criarTransacao } from '../helpers/api.helper';
  4   | 
  5   | test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });
  6   | 
  7   | test.describe('Módulo Financeiro - Visão Geral', () => {
  8   | 
  9   |   test.beforeEach(async ({ page }) => {
  10  |     await page.goto('/transacoes');
  11  |     await page.waitForSelector('[data-testid="financeiro-container"]');
  12  |   });
  13  | 
  14  |   test('deve exibir container de financeiro', async ({ page }) => {
  15  |     await expect(page.locator('[data-testid="financeiro-container"]')).toBeVisible();
  16  |   });
  17  | 
  18  |   test('deve exibir botão de nova transação', async ({ page }) => {
  19  |     await expect(page.locator('[data-testid="btn-nova-transacao"]')).toBeVisible();
  20  |   });
  21  | 
  22  |   test('deve exibir filtros de busca e período', async ({ page }) => {
  23  |     await expect(page.locator('[data-testid="card-filtros"]')).toBeVisible();
  24  |     await expect(page.locator('[data-testid="input-busca"]')).toBeVisible();
  25  |     await expect(page.locator('[data-testid="seletor-periodo"]')).toBeVisible();
  26  |     await expect(page.locator('[data-testid="select-status"]')).toBeVisible();
  27  |   });
  28  | 
  29  |   test('deve filtrar por período', async ({ page }) => {
  30  |     await criarTransacao({ descricao: 'Transação mês atual E2E' });
  31  |     await page.reload();
  32  |     await page.waitForSelector('[data-testid="financeiro-container"]');
  33  |     await page.click('[data-testid="seletor-periodo"]');
  34  |     await page.click('text=Mês Atual');
  35  |     await page.waitForTimeout(500);
  36  |   });
  37  | 
  38  |   test('deve exportar CSV ao clicar no botão', async ({ page }) => {
  39  |     const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
  40  |     await page.click('[data-testid="btn-exportar-csv"]');
  41  |     const download = await downloadPromise;
  42  |     expect(download.suggestedFilename()).toMatch(/transacoes.*\.csv$/i);
  43  |   });
  44  | });
  45  | 
  46  | test.describe('Módulo Financeiro - CRUD de Transações', () => {
  47  | 
  48  |   test.beforeEach(async ({ page }) => {
  49  |     await page.goto('/transacoes');
  50  |     await page.waitForSelector('[data-testid="financeiro-container"]');
  51  |   });
  52  | 
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
> 84  |     await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
      |                                                                       ^ Error: expect(locator).not.toBeVisible() failed
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
  153 |     const valorSelecionado = await page.locator('[data-testid="select-status"]').inputValue();
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