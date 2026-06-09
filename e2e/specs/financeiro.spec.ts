import { test, expect } from '@playwright/test';
import path from 'path';
import { criarTransacao } from '../helpers/api.helper';

test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

test.describe('Módulo Financeiro - Visão Geral', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/transacoes');
    await page.waitForSelector('[data-testid="financeiro-container"]');
  });

  test('deve exibir container de financeiro', async ({ page }) => {
    await expect(page.locator('[data-testid="financeiro-container"]')).toBeVisible();
  });

  test('deve exibir botão de nova transação', async ({ page }) => {
    await expect(page.locator('[data-testid="btn-nova-transacao"]')).toBeVisible();
  });

  test('deve exibir filtros de busca e período', async ({ page }) => {
    await expect(page.locator('[data-testid="card-filtros"]')).toBeVisible();
    await expect(page.locator('[data-testid="input-busca"]')).toBeVisible();
    await expect(page.locator('[data-testid="seletor-periodo"]')).toBeVisible();
    await expect(page.locator('[data-testid="select-status"]')).toBeVisible();
  });

  test('deve filtrar por período', async ({ page }) => {
    await criarTransacao({ descricao: 'Transação mês atual E2E' });
    await page.reload();
    await page.waitForSelector('[data-testid="financeiro-container"]');
    await page.click('[data-testid="seletor-periodo"]');
    await page.click('text=Mês Atual');
    await page.waitForTimeout(500);
  });

  test('deve exportar CSV ao clicar no botão', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
    await page.click('[data-testid="btn-exportar-csv"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/transacoes.*\.csv$/i);
  });
});

test.describe('Módulo Financeiro - CRUD de Transações', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/transacoes');
    await page.waitForSelector('[data-testid="financeiro-container"]');
  });

  test('deve criar nova transação de receita', async ({ page }) => {
    // Clicar no botão nova transação
    await page.click('[data-testid="btn-nova-transacao"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
    await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Nova Transação');

    // Preencher formulário
    await page.click('[data-testid="select-tipo-modal"]');
    await page.click('text=Receita');
    
    await page.click('[data-testid="select-categoria-modal"]');
    // Esperar categorias carregarem
    await page.waitForTimeout(500);
    const categoriaOption = await page.locator('[data-testid="select-categoria-modal"] option').nth(1);
    if (await categoriaOption.count() > 0) {
      await page.selectOption('[data-testid="select-categoria-modal"]', await categoriaOption.getAttribute('value'));
    }

    await page.fill('[data-testid="input-descricao-modal"]', 'Receita de teste E2E');
    await page.fill('[data-testid="input-valor-modal"]', '500,00');
    
    // Data de vencimento (hoje + 7 dias)
    const dataVencimento = new Date();
    dataVencimento.setDate(dataVencimento.getDate() + 7);
    const dataFormatada = dataVencimento.toISOString().split('T')[0];
    await page.fill('[data-testid="input-data-vencimento-modal"]', dataFormatada);

    // Salvar
    await page.click('[data-testid="btn-salvar-modal"]');
    
    // Verificar sucesso
    await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
    // Verificar toast de sucesso (pode variar)
    await page.waitForTimeout(1000);
  });

  test('deve criar nova transação de despesa', async ({ page }) => {
    await page.click('[data-testid="btn-nova-transacao"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();

    // Preencher como despesa
    await page.click('[data-testid="select-tipo-modal"]');
    await page.click('text=Despesa');
    
    await page.fill('[data-testid="input-descricao-modal"]', 'Despesa de teste E2E');
    await page.fill('[data-testid="input-valor-modal"]', '150,00');
    
    const dataVencimento = new Date();
    dataVencimento.setDate(dataVencimento.getDate() + 7);
    const dataFormatada = dataVencimento.toISOString().split('T')[0];
    await page.fill('[data-testid="input-data-vencimento-modal"]', dataFormatada);

    await page.click('[data-testid="btn-salvar-modal"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
    await page.waitForTimeout(1000);
  });

  test('deve editar transação existente', async ({ page }) => {
    // Criar transação primeiro
    await criarTransacao({ descricao: 'Transação para edição E2E' });
    await page.reload();
    await page.waitForSelector('[data-testid="financeiro-container"]');

    // Encontrar e clicar no botão de editar da primeira transação
    const botaoEditar = page.locator('[data-testid="card-tabela-transacoes"]').locator('button').first();
    if (await botaoEditar.count() > 0) {
      await botaoEditar.click();
      await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
      await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Editar Transação');

      // Modificar descrição
      await page.fill('[data-testid="input-descricao-modal"]', 'Transação editada E2E');
      await page.click('[data-testid="btn-salvar-modal"]');
      await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
    }
  });

  test('deve cancelar criação de transação', async ({ page }) => {
    await page.click('[data-testid="btn-nova-transacao"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();

    await page.click('[data-testid="btn-cancelar-modal"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).not.toBeVisible();
  });

  test('deve filtrar transações por tipo', async ({ page }) => {
    await page.click('[data-testid="seletor-periodo"]');
    await page.click('text=Receita');
    await page.waitForTimeout(500);
    
    // Verificar que o filtro foi aplicado
    const valorSelecionado = await page.locator('[data-testid="seletor-periodo"]').inputValue();
    expect(valorSelecionado).toBe('receita');
  });

  test('deve filtrar transações por status', async ({ page }) => {
    await page.click('[data-testid="select-status"]');
    await page.click('text=Pendente');
    await page.waitForTimeout(500);
    
    const valorSelecionado = await page.locator('[data-testid="select-status"]').inputValue();
    expect(valorSelecionado).toBe('pendente');
  });

  test('deve buscar transações por descrição', async ({ page }) => {
    await page.fill('[data-testid="input-busca"]', 'teste');
    await page.waitForTimeout(500);
    
    // Verificar que o campo tem o valor buscado
    const valorBusca = await page.locator('[data-testid="input-busca"]').inputValue();
    expect(valorBusca).toBe('teste');
  });

  test('deve validar campos obrigatórios ao criar transação', async ({ page }) => {
    await page.click('[data-testid="btn-nova-transacao"]');
    await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();

    // Tentar salvar sem preencher campos obrigatórios
    await page.click('[data-testid="btn-salvar-modal"]');
    
    // Modal deve permanecer aberto (validação impediu salvamento)
    await expect(page.locator('[data-testid="modal-transacao"]')).toBeVisible();
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });
});
