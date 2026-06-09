import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  async goto(path: string) {
    await this.page.goto(path);
    await this.esperarCarregamento();
  }

  async esperarCarregamento() {
    await this.page.waitForSelector('[data-testid="skeleton-loader"]', {
      state: 'hidden', timeout: 15_000
    }).catch(() => {});
    await this.page.waitForTimeout(300);
  }

  async esperarToast(tipo: 'sucesso' | 'erro' | 'aviso') {
    const seletores = {
      sucesso: '[data-sonner-toast][data-type="success"]',
      erro: '[data-sonner-toast][data-type="error"]',
      aviso: '[data-sonner-toast][data-type="warning"]',
    };
    await expect(this.page.locator(seletores[tipo])).toBeVisible({ timeout: 10_000 });
  }

  async confirmarDialog() {
    // Aguardar o modal de confirmação aparecer com timeout maior
    const modal = this.page.locator('[data-testid="modal-confirmacao"]');
    await modal.waitFor({ state: 'visible', timeout: 10000 });
    
    // Clicar no botão de confirmar usando data-testid específico
    await this.page.locator('[data-testid="botao-confirmar-modal"]').click();
    await this.page.waitForTimeout(2000); // Aguardar exclusão ser processada
    await this.esperarCarregamento();
  }

  async selecionarOpcao(label: string, opcao: string) {
    await this.page.getByLabel(label).click();
    await this.page.getByRole('option', { name: opcao }).click();
  }

  async selecionarCustomOpcao(selector: string, opcao: string) {
    // Clicar no botão do CustomSelect para abrir o dropdown
    await this.page.locator(selector).click();
    await this.page.waitForTimeout(500);
    
    // Se opcao for '1', selecionar a primeira opção disponível
    if (opcao === '1') {
      const dropdown = this.page.locator('[data-testid="custom-select-dropdown"]');
      await dropdown.locator('div').first().click();
    } else {
      // Clicar na opção desejada no dropdown - usar data-testid
      const dropdown = this.page.locator('[data-testid="custom-select-dropdown"]');
      await dropdown.getByText(opcao).click();
    }
    await this.page.waitForTimeout(300);
  }

  async preencherCampo(label: string, valor: string) {
    const campo = this.page.getByLabel(label);
    await campo.clear();
    await campo.fill(valor);
  }

  async verificarErroValidacao(mensagem: string) {
    await expect(this.page.getByText(mensagem)).toBeVisible();
  }

  async capturarEvidencia(nome: string) {
    await this.page.screenshot({
      path: `reports/evidencias/${nome}-${Date.now()}.png`,
      fullPage: true,
    });
  }
}
