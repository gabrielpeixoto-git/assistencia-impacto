import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class FinanceiroPage extends BasePage {
  // Locators
  readonly btnNovaTransacao: Locator;
  readonly cardFiltros: Locator;
  readonly inputBusca: Locator;
  readonly selectTipo: Locator;
  readonly selectStatus: Locator;
  readonly cardTabelaTransacoes: Locator;
  readonly modalTransacao: Locator;
  readonly modalTitulo: Locator;
  readonly selectTipoModal: Locator;
  readonly selectCategoriaModal: Locator;
  readonly inputDescricaoModal: Locator;
  readonly inputValorModal: Locator;
  readonly inputDataVencimentoModal: Locator;
  readonly inputFormaPagamentoModal: Locator;
  readonly inputContaBancariaModal: Locator;
  readonly textareaObservacoesModal: Locator;
  readonly checkboxRecorrenteModal: Locator;
  readonly selectIntervaloRecorrenciaModal: Locator;
  readonly btnCancelarModal: Locator;
  readonly btnSalvarModal: Locator;

  constructor(page: Page) {
    super(page);
    this.btnNovaTransacao = page.getByTestId('btn-nova-transacao');
    this.cardFiltros = page.getByTestId('card-filtros');
    this.inputBusca = page.getByTestId('input-busca');
    this.selectTipo = page.getByTestId('select-tipo');
    this.selectStatus = page.getByTestId('select-status');
    this.cardTabelaTransacoes = page.getByTestId('card-tabela-transacoes');
    this.modalTransacao = page.getByTestId('modal-transacao');
    this.modalTitulo = page.getByTestId('modal-titulo');
    this.selectTipoModal = page.getByTestId('select-tipo-modal');
    this.selectCategoriaModal = page.getByTestId('select-categoria-modal');
    this.inputDescricaoModal = page.getByTestId('input-descricao-modal');
    this.inputValorModal = page.getByTestId('input-valor-modal');
    this.inputDataVencimentoModal = page.getByTestId('input-data-vencimento-modal');
    this.inputFormaPagamentoModal = page.getByTestId('input-forma-pagamento-modal');
    this.inputContaBancariaModal = page.getByTestId('input-conta-bancaria-modal');
    this.textareaObservacoesModal = page.getByTestId('textarea-observacoes-modal');
    this.checkboxRecorrenteModal = page.getByTestId('checkbox-recorrente-modal');
    this.selectIntervaloRecorrenciaModal = page.getByTestId('select-intervalo-recorrencia-modal');
    this.btnCancelarModal = page.getByTestId('btn-cancelar-modal');
    this.btnSalvarModal = page.getByTestId('btn-salvar-modal');
  }

  async abrirPagina() {
    await this.goto('/financeiro');
  }

  async clicarNovaTransacao() {
    await this.btnNovaTransacao.click();
  }

  async preencherFiltroBusca(valor: string) {
    await this.inputBusca.fill(valor);
  }

  async selecionarTipoFiltro(tipo: string) {
    await this.selectTipo.selectOption(tipo);
  }

  async selecionarStatusFiltro(status: string) {
    await this.selectStatus.selectOption(status);
  }

  async preencherModalTransacao(dados: {
    tipo: string;
    categoria: string;
    descricao: string;
    valor: string;
    dataVencimento: string;
    formaPagamento?: string;
    contaBancaria?: string;
    observacoes?: string;
    recorrente?: boolean;
    intervaloRecorrencia?: string;
  }) {
    await this.selectTipoModal.selectOption(dados.tipo);
    await this.page.waitForTimeout(300);
    await this.selectCategoriaModal.selectOption(dados.categoria);
    await this.inputDescricaoModal.fill(dados.descricao);
    await this.inputValorModal.fill(dados.valor);
    await this.inputDataVencimentoModal.fill(dados.dataVencimento);
    
    if (dados.formaPagamento) {
      await this.inputFormaPagamentoModal.fill(dados.formaPagamento);
    }
    
    if (dados.contaBancaria) {
      await this.inputContaBancariaModal.fill(dados.contaBancaria);
    }
    
    if (dados.observacoes) {
      await this.textareaObservacoesModal.fill(dados.observacoes);
    }
    
    if (dados.recorrente) {
      await this.checkboxRecorrenteModal.check();
      if (dados.intervaloRecorrencia) {
        await this.selectIntervaloRecorrenciaModal.selectOption(dados.intervaloRecorrencia);
      }
    }
  }

  async salvarTransacao() {
    await this.btnSalvarModal.click();
    await this.esperarCarregamento();
  }

  async cancelarModal() {
    await this.btnCancelarModal.click();
  }

  async verificarModalAberto() {
    await expect(this.modalTransacao).toBeVisible();
  }

  async verificarModalFechado() {
    await expect(this.modalTransacao).not.toBeVisible();
  }

  async verificarTabelaVisivel() {
    await expect(this.cardTabelaTransacoes).toBeVisible();
  }
}
