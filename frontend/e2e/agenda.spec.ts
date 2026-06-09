import { test, expect } from '@playwright/test';
import { AgendaPage } from '../../e2e/pages/agenda.page';

test.describe('Agenda', () => {
  let agendaPage: AgendaPage;

  test.beforeEach(async ({ page }) => {
    agendaPage = new AgendaPage(page);
    await agendaPage.abrirPagina();
  });

  test('deve exibir página de agenda', async () => {
    await expect(agendaPage.cardTabelaEventos).toBeVisible();
  });

  test('deve abrir modal de novo evento', async () => {
    await agendaPage.clicarNovoEvento();
    await agendaPage.verificarModalAberto();
    await expect(agendaPage.modalTitulo).toContainText('Novo Evento');
  });

  test('deve fechar modal ao clicar em cancelar', async () => {
    await agendaPage.clicarNovoEvento();
    await agendaPage.verificarModalAberto();
    await agendaPage.cancelarModal();
    await agendaPage.verificarModalFechado();
  });

  test('deve preencher filtro de busca', async () => {
    await agendaPage.preencherFiltroBusca('visita');
    await expect(agendaPage.inputBuscaAgenda).toHaveValue('visita');
  });

  test('deve selecionar filtro de tipo', async () => {
    await agendaPage.selecionarTipoFiltro('visita');
    await expect(agendaPage.selectTipoAgenda).toHaveValue('visita');
  });

  test('deve selecionar filtro de status', async () => {
    await agendaPage.selecionarStatusFiltro('agendado');
    await expect(agendaPage.selectStatusAgenda).toHaveValue('agendado');
  });

  test('deve preencher modal de evento', async () => {
    await agendaPage.clicarNovoEvento();
    
    await agendaPage.preencherModalEvento({
      titulo: 'Visita Técnica E2E',
      tecnico: '1', // ID do técnico
      cliente: '1', // ID do cliente
      dataInicio: '2026-12-31T10:00',
      dataFim: '2026-12-31T12:00',
      tipoEvento: 'servico',
      cor: '#6C63FF',
      endereco: 'Rua Teste, 123',
      observacoes: 'Observações de teste'
    });
    
    await expect(agendaPage.inputTituloModal).toHaveValue('Visita Técnica E2E');
  });

  test('deve criar evento sem cliente', async () => {
    await agendaPage.clicarNovoEvento();
    
    await agendaPage.preencherModalEvento({
      titulo: 'Reunião Interna',
      tecnico: '1',
      dataInicio: '2026-12-31T14:00',
      dataFim: '2026-12-31T15:00',
      tipoEvento: 'reuniao',
      cor: '#10B981',
      observacoes: 'Reunião de equipe'
    });
    
    await expect(agendaPage.inputTituloModal).toHaveValue('Reunião Interna');
  });

  test('deve salvar evento', async () => {
    await agendaPage.clicarNovoEvento();
    
    await agendaPage.preencherModalEvento({
      titulo: 'Evento para salvar',
      tecnico: '1',
      dataInicio: '2026-12-31T09:00',
      dataFim: '2026-12-31T11:00',
      tipoEvento: 'manutencao',
      cor: '#F59E0B'
    });
    
    await agendaPage.salvarEvento();
    await agendaPage.verificarModalFechado();
  });

  test('deve criar evento de visita', async () => {
    await agendaPage.clicarNovoEvento();
    
    await agendaPage.preencherModalEvento({
      titulo: 'Visita ao Cliente',
      tecnico: '1',
      cliente: '1',
      dataInicio: '2026-12-31T08:00',
      dataFim: '2026-12-31T10:00',
      tipoEvento: 'visita',
      cor: '#6366F1',
      endereco: 'Av. Principal, 456'
    });
    
    await expect(agendaPage.inputEnderecoModal).toHaveValue('Av. Principal, 456');
  });

  test('deve criar evento de manutenção', async () => {
    await agendaPage.clicarNovoEvento();
    
    await agendaPage.preencherModalEvento({
      titulo: 'Manutenção Preventiva',
      tecnico: '1',
      cliente: '1',
      dataInicio: '2026-12-31T13:00',
      dataFim: '2026-12-31T16:00',
      tipoEvento: 'manutencao',
      cor: '#F59E0B',
      observacoes: 'Verificar sistema de ar condicionado'
    });
    
    await expect(agendaPage.textareaObservacoesModal).toHaveValue('Verificar sistema de ar condicionado');
  });
});
