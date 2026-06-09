import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class AgendaPage extends BasePage {
  // Locators
  readonly btnNovoEvento: Locator;
  readonly cardFiltrosAgenda: Locator;
  readonly inputBuscaAgenda: Locator;
  readonly selectTipoAgenda: Locator;
  readonly selectStatusAgenda: Locator;
  readonly cardTabelaEventos: Locator;
  readonly modalEvento: Locator;
  readonly modalTitulo: Locator;
  readonly inputTituloModal: Locator;
  readonly selectTecnicoModal: Locator;
  readonly selectClienteModal: Locator;
  readonly inputDataInicioModal: Locator;
  readonly inputDataFimModal: Locator;
  readonly selectTipoEventoModal: Locator;
  readonly inputCorModal: Locator;
  readonly inputEnderecoModal: Locator;
  readonly textareaObservacoesModal: Locator;
  readonly btnCancelarModal: Locator;
  readonly btnSalvarModal: Locator;

  constructor(page: Page) {
    super(page);
    this.btnNovoEvento = page.getByTestId('btn-novo-evento');
    this.cardFiltrosAgenda = page.getByTestId('card-filtros-agenda');
    this.inputBuscaAgenda = page.getByTestId('input-busca-agenda');
    this.selectTipoAgenda = page.getByTestId('select-tipo-agenda');
    this.selectStatusAgenda = page.getByTestId('select-status-agenda');
    this.cardTabelaEventos = page.getByTestId('card-tabela-eventos');
    this.modalEvento = page.getByTestId('modal-evento');
    this.modalTitulo = page.getByTestId('modal-titulo');
    this.inputTituloModal = page.getByTestId('input-titulo-modal');
    this.selectTecnicoModal = page.getByTestId('select-tecnico-modal');
    this.selectClienteModal = page.getByTestId('select-cliente-modal');
    this.inputDataInicioModal = page.getByTestId('input-data-inicio-modal');
    this.inputDataFimModal = page.getByTestId('input-data-fim-modal');
    this.selectTipoEventoModal = page.getByTestId('select-tipo-evento-modal');
    this.inputCorModal = page.getByTestId('input-cor-modal');
    this.inputEnderecoModal = page.getByTestId('input-endereco-modal');
    this.textareaObservacoesModal = page.getByTestId('textarea-observacoes-modal');
    this.btnCancelarModal = page.getByTestId('btn-cancelar-modal');
    this.btnSalvarModal = page.getByTestId('btn-salvar-modal');
  }

  async abrirPagina() {
    await this.goto('/agenda');
  }

  async clicarNovoEvento() {
    await this.btnNovoEvento.click();
  }

  async preencherFiltroBusca(valor: string) {
    await this.inputBuscaAgenda.fill(valor);
  }

  async selecionarTipoFiltro(tipo: string) {
    await this.selectTipoAgenda.selectOption(tipo);
  }

  async selecionarStatusFiltro(status: string) {
    await this.selectStatusAgenda.selectOption(status);
  }

  async preencherModalEvento(dados: {
    titulo: string;
    tecnico: string;
    cliente?: string;
    dataInicio: string;
    dataFim: string;
    tipoEvento: string;
    cor?: string;
    endereco?: string;
    observacoes?: string;
  }) {
    await this.inputTituloModal.fill(dados.titulo);
    await this.selectTecnicoModal.selectOption(dados.tecnico);
    await this.page.waitForTimeout(300);
    
    if (dados.cliente) {
      await this.selectClienteModal.selectOption(dados.cliente);
    }
    
    await this.inputDataInicioModal.fill(dados.dataInicio);
    await this.inputDataFimModal.fill(dados.dataFim);
    await this.selectTipoEventoModal.selectOption(dados.tipoEvento);
    
    if (dados.cor) {
      await this.inputCorModal.fill(dados.cor);
    }
    
    if (dados.endereco) {
      await this.inputEnderecoModal.fill(dados.endereco);
    }
    
    if (dados.observacoes) {
      await this.textareaObservacoesModal.fill(dados.observacoes);
    }
  }

  async salvarEvento() {
    await this.btnSalvarModal.click();
    await this.esperarCarregamento();
  }

  async cancelarModal() {
    await this.btnCancelarModal.click();
  }

  async verificarModalAberto() {
    await expect(this.modalEvento).toBeVisible();
  }

  async verificarModalFechado() {
    await expect(this.modalEvento).not.toBeVisible();
  }

  async verificarTabelaVisivel() {
    await expect(this.cardTabelaEventos).toBeVisible();
  }
}
