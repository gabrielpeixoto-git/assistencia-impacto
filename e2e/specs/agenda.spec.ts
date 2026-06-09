import { test, expect } from '@playwright/test';
import path from 'path';
import { buscarUsuarioPorEmail } from '../helpers/api.helper';

test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

test.describe('Módulo Agenda - Visão Geral', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/agenda');
    await page.waitForSelector('[data-testid="agenda-container"]');
  });

  test('deve exibir container de agenda', async ({ page }) => {
    await expect(page.locator('[data-testid="agenda-container"]')).toBeVisible();
  });

  test('deve exibir botão de novo evento', async ({ page }) => {
    await expect(page.locator('[data-testid="btn-novo-evento"]')).toBeVisible();
  });

  test('deve exibir filtro de técnico', async ({ page }) => {
    await expect(page.locator('[data-testid="filtro-tecnico"]')).toBeVisible();
  });

  test('deve filtrar por técnico', async ({ page }) => {
    const tecnico = await buscarUsuarioPorEmail('joao@assistenciaimpacto.com.br');
    if (!tecnico) test.skip();

    await page.selectOption('[data-testid="filtro-tecnico"]', { value: tecnico.id });
    await expect(page.locator('[data-testid="agenda-container"]')).toBeVisible();
  });

  test('deve exibir "Todos os técnicos" como opção padrão', async ({ page }) => {
    const filtro = page.locator('[data-testid="filtro-tecnico"]');
    const valor = await filtro.inputValue();
    expect(valor).toBe('');
  });
});

test.describe('Módulo Agenda - CRUD de Eventos', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/agenda');
    await page.waitForSelector('[data-testid="agenda-container"]');
  });

  test('deve abrir formulário ao clicar em Novo Evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  });

  test('deve preencher e salvar novo evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    // Preencher título
    await page.fill('[data-testid="input-titulo-evento"]', 'Evento de teste E2E');

    // Selecionar técnico
    await page.click('[data-testid="select-tecnico-evento"]');
    await page.waitForTimeout(500);
    const tecnicoOption = await page.locator('[data-testid="select-tecnico-evento"] option').nth(1);
    if (await tecnicoOption.count() > 0) {
      await page.selectOption('[data-testid="select-tecnico-evento"]', await tecnicoOption.getAttribute('value'));
    }

    // Preencher datas
    const dataInicio = new Date();
    dataInicio.setDate(dataInicio.getDate() + 1);
    dataInicio.setHours(10, 0, 0, 0);
    const dataInicioFormatada = new Date(dataInicio.getTime() - (dataInicio.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);

    const dataFim = new Date(dataInicio);
    dataFim.setHours(12, 0, 0, 0);
    const dataFimFormatada = new Date(dataFim.getTime() - (dataFim.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);

    await page.fill('[data-testid="input-data-inicio-modal"]', dataInicioFormatada);
    await page.fill('[data-testid="input-data-fim-modal"]', dataFimFormatada);

    // Salvar
    await page.click('[data-testid="btn-salvar-evento"]');
    
    // Modal deve fechar
    await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
    await page.waitForTimeout(1000);
  });

  test('deve cancelar criação de evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.click('[data-testid="btn-fechar-modal"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  });

  test('deve validar campos obrigatórios ao criar evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    // Tentar salvar sem preencher campos
    await page.click('[data-testid="btn-salvar-evento"]');
    
    // Modal deve permanecer aberto (validação impediu salvamento)
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
    
    await page.click('[data-testid="btn-fechar-modal"]');
  });

  test('deve editar evento existente', async ({ page }) => {
    // Verificar se há eventos para editar
    const eventos = await page.locator('[data-testid="agenda-container"] .cursor-pointer').count();
    
    if (eventos === 0) {
      test.skip(true, 'Nenhum evento encontrado para editar');
      return;
    }
    
    // Clicar no primeiro evento
    await page.locator('[data-testid="agenda-container"] .cursor-pointer').first().click();
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    // Modificar título
    await page.fill('[data-testid="input-titulo-evento"]', 'Evento editado E2E');
    await page.click('[data-testid="btn-salvar-evento"]');
    
    await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  });

  test('deve selecionar tipo de evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.click('[data-testid="select-tipo-evento-modal"]');
    await page.click('text=Reunião');
    
    const valorSelecionado = await page.locator('[data-testid="select-tipo-evento-modal"]').inputValue();
    expect(valorSelecionado).toBe('reuniao');
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve preencher endereço do evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.fill('[data-testid="input-endereco-modal"]', 'Rua Teste, 123 - São Paulo, SP');
    
    const endereco = await page.locator('[data-testid="input-endereco-modal"]').inputValue();
    expect(endereco).toBe('Rua Teste, 123 - São Paulo, SP');
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve preencher observações do evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.fill('[data-testid="textarea-observacoes-modal"]', 'Observações de teste E2E');
    
    const observacoes = await page.locator('[data-testid="textarea-observacoes-modal"]').inputValue();
    expect(observacoes).toBe('Observações de teste E2E');
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve selecionar cor do evento', async ({ page }) => {
    await page.click('[data-testid="btn-novo-evento"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.fill('[data-testid="input-cor-modal"]', '#FF0000');
    
    const cor = await page.locator('[data-testid="input-cor-modal"]').inputValue();
    expect(cor).toBe('#FF0000');
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });
});
