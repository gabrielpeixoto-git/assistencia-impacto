import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class PortalClientePage extends BasePage {
  // Locators
  readonly inputEmail: Locator;
  readonly inputSenha: Locator;
  readonly btnEntrar: Locator;
  readonly inputToken: Locator;
  readonly btnConsultar: Locator;
  readonly cardDetalhesOS: Locator;
  readonly cardStatusOS: Locator;

  constructor(page: Page) {
    super(page);
    this.inputEmail = page.getByTestId('input-email-portal');
    this.inputSenha = page.getByTestId('input-senha-portal');
    this.btnEntrar = page.getByTestId('btn-entrar-portal');
    this.inputToken = page.getByTestId('input-token-consulta');
    this.btnConsultar = page.getByTestId('btn-consultar-os');
    this.cardDetalhesOS = page.getByTestId('card-detalhes-os');
    this.cardStatusOS = page.getByTestId('card-status-os');
  }

  async abrirPagina() {
    await this.goto('/portal');
  }

  async preencherLogin(email: string, senha: string) {
    await this.inputEmail.fill(email);
    await this.inputSenha.fill(senha);
  }

  async clicarEntrar() {
    await this.btnEntrar.click();
    await this.esperarCarregamento();
  }

  async preencherToken(token: string) {
    await this.inputToken.fill(token);
  }

  async clicarConsultar() {
    await this.btnConsultar.click();
    await this.esperarCarregamento();
  }

  async verificarDetalhesOSVisiveis() {
    await expect(this.cardDetalhesOS).toBeVisible();
  }

  async verificarStatusOSVisivel() {
    await expect(this.cardStatusOS).toBeVisible();
  }
}
