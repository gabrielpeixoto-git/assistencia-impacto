import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class EquipePage extends BasePage {
  // Locators
  readonly btnNovoMembro: Locator;
  readonly cardFiltrosEquipe: Locator;
  readonly inputBuscaEquipe: Locator;
  readonly selectCargoEquipe: Locator;
  readonly selectStatusEquipe: Locator;
  readonly cardTabelaMembros: Locator;
  readonly modalMembro: Locator;
  readonly modalTitulo: Locator;
  readonly inputEmailModal: Locator;
  readonly inputNomeModal: Locator;
  readonly selectPerfilModal: Locator;
  readonly inputTelefoneModal: Locator;
  readonly inputSenhaModal: Locator;
  readonly inputConfirmarSenhaModal: Locator;
  readonly btnCancelarModal: Locator;
  readonly btnSalvarModal: Locator;

  constructor(page: Page) {
    super(page);
    this.btnNovoMembro = page.getByTestId('btn-novo-membro');
    this.cardFiltrosEquipe = page.getByTestId('card-filtros-equipe');
    this.inputBuscaEquipe = page.getByTestId('input-busca-equipe');
    this.selectCargoEquipe = page.getByTestId('select-cargo-equipe');
    this.selectStatusEquipe = page.getByTestId('select-status-equipe');
    this.cardTabelaMembros = page.getByTestId('card-tabela-membros');
    this.modalMembro = page.getByTestId('modal-membro');
    this.modalTitulo = page.getByTestId('modal-titulo');
    this.inputEmailModal = page.getByTestId('input-email-modal');
    this.inputNomeModal = page.getByTestId('input-nome-modal');
    this.selectPerfilModal = page.getByTestId('select-perfil-modal');
    this.inputTelefoneModal = page.getByTestId('input-telefone-modal');
    this.inputSenhaModal = page.getByTestId('input-senha-modal');
    this.inputConfirmarSenhaModal = page.getByTestId('input-confirmar-senha-modal');
    this.btnCancelarModal = page.getByTestId('btn-cancelar-modal');
    this.btnSalvarModal = page.getByTestId('btn-salvar-modal');
  }

  async abrirPagina() {
    await this.goto('/equipe');
  }

  async clicarNovoMembro() {
    await this.btnNovoMembro.click();
  }

  async preencherFiltroBusca(valor: string) {
    await this.inputBuscaEquipe.fill(valor);
  }

  async selecionarCargoFiltro(cargo: string) {
    await this.selectCargoEquipe.selectOption(cargo);
  }

  async selecionarStatusFiltro(status: string) {
    await this.selectStatusEquipe.selectOption(status);
  }

  async preencherModalMembro(dados: {
    email: string;
    nome: string;
    perfil: string;
    telefone?: string;
    senha?: string;
    confirmarSenha?: string;
  }) {
    await this.inputEmailModal.fill(dados.email);
    await this.inputNomeModal.fill(dados.nome);
    await this.selectPerfilModal.selectOption(dados.perfil);
    
    if (dados.telefone) {
      await this.inputTelefoneModal.fill(dados.telefone);
    }
    
    if (dados.senha) {
      await this.inputSenhaModal.fill(dados.senha);
    }
    
    if (dados.confirmarSenha) {
      await this.inputConfirmarSenhaModal.fill(dados.confirmarSenha);
    }
  }

  async salvarMembro() {
    await this.btnSalvarModal.click();
    await this.esperarCarregamento();
  }

  async cancelarModal() {
    await this.btnCancelarModal.click();
  }

  async verificarModalAberto() {
    await expect(this.modalMembro).toBeVisible();
  }

  async verificarModalFechado() {
    await expect(this.modalMembro).not.toBeVisible();
  }

  async verificarTabelaVisivel() {
    await expect(this.cardTabelaMembros).toBeVisible();
  }
}
