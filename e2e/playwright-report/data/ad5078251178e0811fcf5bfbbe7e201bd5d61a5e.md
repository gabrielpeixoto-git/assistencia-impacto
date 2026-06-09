# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: agenda.spec.ts >> Módulo Agenda - CRUD de Eventos >> deve preencher e salvar novo evento
- Location: specs\agenda.spec.ts:53:7

# Error details

```
Error: expect(locator).not.toBeVisible() failed

Locator:  locator('[data-testid="modal-usuario"]')
Expected: not visible
Received: visible
Timeout:  5000ms

Call log:
  - Expect "not toBeVisible" with timeout 5000ms
  - waiting for locator('[data-testid="modal-usuario"]')
    13 × locator resolved to <div data-testid="modal-usuario" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">…</div>
       - unexpected value "visible"

```

```yaml
- heading "Novo Evento" [level=2]
- button:
  - img
- text: Título *
- textbox "Título *":
  - /placeholder: Título do evento
  - text: Evento de teste E2E
- text: Técnico *
- combobox "Técnico *":
  - option "Selecione um técnico"
  - option "João Silva" [selected]
- text: Cliente
- combobox "Cliente":
  - option "Selecione um cliente (opcional)" [selected]
- text: Data/Hora Início *
- textbox "Data/Hora Início *": 2026-06-05T10:00
- text: Data/Hora Fim *
- textbox "Data/Hora Fim *": 2026-06-05T12:00
- text: Tipo de Evento
- combobox "Tipo de Evento":
  - option "Serviço" [selected]
  - option "Reunião"
  - option "Manutenção"
  - option "Indisponível"
  - option "Outro"
- text: Cor
- textbox "Cor": "#3b82f6"
- text: "#3b82f6 Endereço"
- textbox "Endereço":
  - /placeholder: Endereço do evento
- text: Observações
- textbox "Observações":
  - /placeholder: Observações adicionais
- text: Erro ao criar evento
- button "Cancelar"
- button "Salvar":
  - img
  - text: Salvar
```

# Test source

```ts
  1   | ﻿import { test, expect } from '@playwright/test';
  2   | import path from 'path';
  3   | import { buscarUsuarioPorEmail } from '../helpers/api.helper';
  4   | 
  5   | test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });
  6   | 
  7   | test.describe('Módulo Agenda - Visão Geral', () => {
  8   | 
  9   |   test.beforeEach(async ({ page }) => {
  10  |     await page.goto('/agenda');
  11  |     await page.waitForSelector('[data-testid="agenda-container"]');
  12  |   });
  13  | 
  14  |   test('deve exibir container de agenda', async ({ page }) => {
  15  |     await expect(page.locator('[data-testid="agenda-container"]')).toBeVisible();
  16  |   });
  17  | 
  18  |   test('deve exibir botão de novo evento', async ({ page }) => {
  19  |     await expect(page.locator('[data-testid="btn-novo-evento"]')).toBeVisible();
  20  |   });
  21  | 
  22  |   test('deve exibir filtro de técnico', async ({ page }) => {
  23  |     await expect(page.locator('[data-testid="filtro-tecnico"]')).toBeVisible();
  24  |   });
  25  | 
  26  |   test('deve filtrar por técnico', async ({ page }) => {
  27  |     const tecnico = await buscarUsuarioPorEmail('joao@assistenciaimpacto.com.br');
  28  |     if (!tecnico) test.skip();
  29  | 
  30  |     await page.selectOption('[data-testid="filtro-tecnico"]', { value: tecnico.id });
  31  |     await expect(page.locator('[data-testid="agenda-container"]')).toBeVisible();
  32  |   });
  33  | 
  34  |   test('deve exibir "Todos os técnicos" como opção padrão', async ({ page }) => {
  35  |     const filtro = page.locator('[data-testid="filtro-tecnico"]');
  36  |     const valor = await filtro.inputValue();
  37  |     expect(valor).toBe('');
  38  |   });
  39  | });
  40  | 
  41  | test.describe('Módulo Agenda - CRUD de Eventos', () => {
  42  | 
  43  |   test.beforeEach(async ({ page }) => {
  44  |     await page.goto('/agenda');
  45  |     await page.waitForSelector('[data-testid="agenda-container"]');
  46  |   });
  47  | 
  48  |   test('deve abrir formulário ao clicar em Novo Evento', async ({ page }) => {
  49  |     await page.click('[data-testid="btn-novo-evento"]');
  50  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  51  |   });
  52  | 
  53  |   test('deve preencher e salvar novo evento', async ({ page }) => {
  54  |     await page.click('[data-testid="btn-novo-evento"]');
  55  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  56  | 
  57  |     // Preencher título
  58  |     await page.fill('[data-testid="input-titulo-evento"]', 'Evento de teste E2E');
  59  | 
  60  |     // Selecionar técnico
  61  |     await page.click('[data-testid="select-tecnico-evento"]');
  62  |     await page.waitForTimeout(500);
  63  |     const tecnicoOption = await page.locator('[data-testid="select-tecnico-evento"] option').nth(1);
  64  |     if (await tecnicoOption.count() > 0) {
  65  |       await page.selectOption('[data-testid="select-tecnico-evento"]', await tecnicoOption.getAttribute('value'));
  66  |     }
  67  | 
  68  |     // Preencher datas
  69  |     const dataInicio = new Date();
  70  |     dataInicio.setDate(dataInicio.getDate() + 1);
  71  |     dataInicio.setHours(10, 0, 0, 0);
  72  |     const dataInicioFormatada = new Date(dataInicio.getTime() - (dataInicio.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
  73  | 
  74  |     const dataFim = new Date(dataInicio);
  75  |     dataFim.setHours(12, 0, 0, 0);
  76  |     const dataFimFormatada = new Date(dataFim.getTime() - (dataFim.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
  77  | 
  78  |     await page.fill('[data-testid="input-data-inicio-modal"]', dataInicioFormatada);
  79  |     await page.fill('[data-testid="input-data-fim-modal"]', dataFimFormatada);
  80  | 
  81  |     // Salvar
  82  |     await page.click('[data-testid="btn-salvar-evento"]');
  83  |     
  84  |     // Modal deve fechar
> 85  |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
      |                                                                     ^ Error: expect(locator).not.toBeVisible() failed
  86  |     await page.waitForTimeout(1000);
  87  |   });
  88  | 
  89  |   test('deve cancelar criação de evento', async ({ page }) => {
  90  |     await page.click('[data-testid="btn-novo-evento"]');
  91  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  92  | 
  93  |     await page.click('[data-testid="btn-fechar-modal"]');
  94  |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  95  |   });
  96  | 
  97  |   test('deve validar campos obrigatórios ao criar evento', async ({ page }) => {
  98  |     await page.click('[data-testid="btn-novo-evento"]');
  99  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  100 | 
  101 |     // Tentar salvar sem preencher campos
  102 |     await page.click('[data-testid="btn-salvar-evento"]');
  103 |     
  104 |     // Modal deve permanecer aberto (validação impediu salvamento)
  105 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  106 |     
  107 |     await page.click('[data-testid="btn-fechar-modal"]');
  108 |   });
  109 | 
  110 |   test('deve editar evento existente', async ({ page }) => {
  111 |     // Verificar se há eventos para editar
  112 |     const eventos = await page.locator('[data-testid="agenda-container"] .cursor-pointer').count();
  113 |     
  114 |     if (eventos === 0) {
  115 |       test.skip(true, 'Nenhum evento encontrado para editar');
  116 |       return;
  117 |     }
  118 |     
  119 |     // Clicar no primeiro evento
  120 |     await page.locator('[data-testid="agenda-container"] .cursor-pointer').first().click();
  121 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  122 | 
  123 |     // Modificar título
  124 |     await page.fill('[data-testid="input-titulo-evento"]', 'Evento editado E2E');
  125 |     await page.click('[data-testid="btn-salvar-evento"]');
  126 |     
  127 |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  128 |   });
  129 | 
  130 |   test('deve selecionar tipo de evento', async ({ page }) => {
  131 |     await page.click('[data-testid="btn-novo-evento"]');
  132 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  133 | 
  134 |     await page.click('[data-testid="select-tipo-evento-modal"]');
  135 |     await page.click('text=Reunião');
  136 |     
  137 |     const valorSelecionado = await page.locator('[data-testid="select-tipo-evento-modal"]').inputValue();
  138 |     expect(valorSelecionado).toBe('reuniao');
  139 |     
  140 |     await page.click('[data-testid="btn-cancelar-modal"]');
  141 |   });
  142 | 
  143 |   test('deve preencher endereço do evento', async ({ page }) => {
  144 |     await page.click('[data-testid="btn-novo-evento"]');
  145 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  146 | 
  147 |     await page.fill('[data-testid="input-endereco-modal"]', 'Rua Teste, 123 - São Paulo, SP');
  148 |     
  149 |     const endereco = await page.locator('[data-testid="input-endereco-modal"]').inputValue();
  150 |     expect(endereco).toBe('Rua Teste, 123 - São Paulo, SP');
  151 |     
  152 |     await page.click('[data-testid="btn-cancelar-modal"]');
  153 |   });
  154 | 
  155 |   test('deve preencher observações do evento', async ({ page }) => {
  156 |     await page.click('[data-testid="btn-novo-evento"]');
  157 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  158 | 
  159 |     await page.fill('[data-testid="textarea-observacoes-modal"]', 'Observações de teste E2E');
  160 |     
  161 |     const observacoes = await page.locator('[data-testid="textarea-observacoes-modal"]').inputValue();
  162 |     expect(observacoes).toBe('Observações de teste E2E');
  163 |     
  164 |     await page.click('[data-testid="btn-cancelar-modal"]');
  165 |   });
  166 | 
  167 |   test('deve selecionar cor do evento', async ({ page }) => {
  168 |     await page.click('[data-testid="btn-novo-evento"]');
  169 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  170 | 
  171 |     await page.fill('[data-testid="input-cor-modal"]', '#FF0000');
  172 |     
  173 |     const cor = await page.locator('[data-testid="input-cor-modal"]').inputValue();
  174 |     expect(cor).toBe('#FF0000');
  175 |     
  176 |     await page.click('[data-testid="btn-cancelar-modal"]');
  177 |   });
  178 | });
  179 | 
```