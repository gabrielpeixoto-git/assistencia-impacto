import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class NotificacoesPage extends BasePage {
  // Locators
  readonly btnNotificacoes: Locator;
  readonly badgeNotificacoes: Locator;
  readonly dropdownNotificacoes: Locator;
  readonly btnMarcarTodasLidas: Locator;

  constructor(page: Page) {
    super(page);
    this.btnNotificacoes = page.getByTestId('btn-notificacoes');
    this.badgeNotificacoes = page.getByTestId('badge-notificacoes');
    this.dropdownNotificacoes = page.getByTestId('dropdown-notificacoes');
    this.btnMarcarTodasLidas = page.getByTestId('btn-marcar-todas-lidas');
  }

  async abrirMenuNotificacoes() {
    await this.btnNotificacoes.click();
    await this.page.waitForTimeout(300);
  }

  async verificarBadgeVisivel() {
    await expect(this.badgeNotificacoes).toBeVisible();
  }

  async verificarBadgeNaoVisivel() {
    await expect(this.badgeNotificacoes).not.toBeVisible();
  }

  async verificarDropdownAberto() {
    await expect(this.dropdownNotificacoes).toBeVisible();
  }

  async marcarTodasComoLidas() {
    await this.btnMarcarTodasLidas.click();
    await this.page.waitForTimeout(500);
  }

  async verificarDropdownFechado() {
    await expect(this.dropdownNotificacoes).not.toBeVisible();
  }
}
