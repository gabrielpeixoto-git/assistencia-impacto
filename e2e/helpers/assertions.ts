import { Page, Locator, expect } from '@playwright/test';

/**
 * Helpers customizados para assertions
 */
export class Assertions {
  /**
   * Verifica se um elemento está visível
   */
  static async verificarVisivel(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toBeVisible();
  }

  /**
   * Verifica se um elemento está oculto
   */
  static async verificarOculto(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toBeHidden();
  }

  /**
   * Verifica se um elemento existe no DOM
   */
  static async verificarExiste(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveCount(1);
  }

  /**
   * Verifica se um elemento tem um texto específico
   */
  static async verificarTexto(locator: Locator, texto: string, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveText(texto);
  }

  /**
   * Verifica se um elemento contém um texto
   */
  static async verificarContemTexto(locator: Locator, texto: string, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toContainText(texto);
  }

  /**
   * Verifica se um elemento tem um atributo específico
   */
  static async verificarAtributo(locator: Locator, atributo: string, valor: string, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveAttribute(atributo, valor);
  }

  /**
   * Verifica se a URL atual corresponde a um padrão
   */
  static async verificarURL(page: Page, padrao: RegExp | string, mensagem?: string): Promise<void> {
    await expect(page, mensagem).toHaveURL(padrao);
  }

  /**
   * Verifica se um elemento está desabilitado
   */
  static async verificarDesabilitado(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toBeDisabled();
  }

  /**
   * Verifica se um elemento está habilitado
   */
  static async verificarHabilitado(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toBeEnabled();
  }

  /**
   * Verifica se um input tem um valor específico
   */
  static async verificarValor(locator: Locator, valor: string, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveValue(valor);
  }

  /**
   * Verifica se um checkbox está marcado
   */
  static async verificarMarcado(locator: Locator, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toBeChecked();
  }

  /**
   * Verifica se um elemento tem uma classe específica
   */
  static async verificarClasse(locator: Locator, classe: string, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveClass(new RegExp(classe));
  }

  /**
   * Verifica se o número de elementos corresponde ao esperado
   */
  static async verificarContagem(locator: Locator, count: number, mensagem?: string): Promise<void> {
    await expect(locator, mensagem).toHaveCount(count);
  }

  /**
   * Verifica se há um erro de validação visível
   */
  static async verificarErroValidacao(page: Page, mensagem?: string): Promise<void> {
    const erroLocator = page.locator('[data-testid="validation-error"], .text-destructive');
    await expect(erroLocator, mensagem || 'Erro de validação deveria estar visível').toBeVisible();
  }

  /**
   * Verifica se não há erros de validação visíveis
   */
  static async verificarSemErrosValidacao(page: Page, mensagem?: string): Promise<void> {
    const erroLocator = page.locator('[data-testid="validation-error"], .text-destructive');
    await expect(erroLocator, mensagem || 'Não deveria haver erros de validação').not.toBeVisible();
  }
}
