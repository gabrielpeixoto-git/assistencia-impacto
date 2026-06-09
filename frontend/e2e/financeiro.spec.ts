import { test, expect } from '@playwright/test';
import { FinanceiroPage } from '../../e2e/pages/financeiro.page';

test.describe('Financeiro', () => {
  let financeiroPage: FinanceiroPage;

  test.beforeEach(async ({ page }) => {
    financeiroPage = new FinanceiroPage(page);
    await financeiroPage.abrirPagina();
  });

  test('deve exibir página de financeiro', async () => {
    await expect(financeiroPage.cardTabelaTransacoes).toBeVisible();
  });

  test('deve abrir modal de nova transação', async () => {
    await financeiroPage.clicarNovaTransacao();
    await financeiroPage.verificarModalAberto();
    await expect(financeiroPage.modalTitulo).toContainText('Nova Transação');
  });

  test('deve fechar modal ao clicar em cancelar', async () => {
    await financeiroPage.clicarNovaTransacao();
    await financeiroPage.verificarModalAberto();
    await financeiroPage.cancelarModal();
    await financeiroPage.verificarModalFechado();
  });

  test('deve preencher filtro de busca', async () => {
    await financeiroPage.preencherFiltroBusca('serviço');
    await expect(financeiroPage.inputBusca).toHaveValue('serviço');
  });

  test('deve selecionar filtro de tipo', async () => {
    await financeiroPage.selecionarTipoFiltro('receita');
    await expect(financeiroPage.selectTipo).toHaveValue('receita');
  });

  test('deve selecionar filtro de status', async () => {
    await financeiroPage.selecionarStatusFiltro('pendente');
    await expect(financeiroPage.selectStatus).toHaveValue('pendente');
  });

  test('deve preencher modal de transação', async () => {
    await financeiroPage.clicarNovaTransacao();
    
    await financeiroPage.preencherModalTransacao({
      tipo: 'receita',
      categoria: '1', // ID da categoria
      descricao: 'Transação de teste E2E',
      valor: '1500,00',
      dataVencimento: '2026-12-31',
      formaPagamento: 'PIX',
      contaBancaria: 'Nubank',
      observacoes: 'Observações de teste',
      recorrente: false
    });
    
    await expect(financeiroPage.inputDescricaoModal).toHaveValue('Transação de teste E2E');
  });

  test('deve criar transação recorrente', async () => {
    await financeiroPage.clicarNovaTransacao();
    
    await financeiroPage.preencherModalTransacao({
      tipo: 'receita',
      categoria: '1',
      descricao: 'Transação recorrente',
      valor: '500,00',
      dataVencimento: '2026-12-31',
      recorrente: true,
      intervaloRecorrencia: 'mensal'
    });
    
    await expect(financeiroPage.checkboxRecorrenteModal).toBeChecked();
  });

  test('deve salvar transação', async () => {
    await financeiroPage.clicarNovaTransacao();
    
    await financeiroPage.preencherModalTransacao({
      tipo: 'receita',
      categoria: '1',
      descricao: 'Transação para salvar',
      valor: '1000,00',
      dataVencimento: '2026-12-31'
    });
    
    await financeiroPage.salvarTransacao();
    await financeiroPage.verificarModalFechado();
  });
});
