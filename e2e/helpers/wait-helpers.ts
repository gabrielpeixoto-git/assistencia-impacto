import { Page, Locator } from '@playwright/test';

/**
 * Helpers para espera de elementos e estados
 */
export class WaitHelpers {
  /**
   * Espera até que um elemento esteja visível e estável
   */
  static async esperarElementoVisivel(page: Page, selector: string, timeout = 10000): Promise<void> {
    await page.waitForSelector(selector, { state: 'visible', timeout });
  }

  /**
   * Espera até que um elemento esteja oculto
   */
  static async esperarElementoOculto(page: Page, selector: string, timeout = 10000): Promise<void> {
    await page.waitForSelector(selector, { state: 'hidden', timeout });
  }

  /**
   * Espera até que um elemento esteja anexado ao DOM
   */
  static async esperarElementoAnexado(page: Page, selector: string, timeout = 10000): Promise<void> {
    await page.waitForSelector(selector, { state: 'attached', timeout });
  }

  /**
   * Espera até que a rede esteja ociosa (sem requisições pendentes)
   */
  static async esperarRedeOciosa(page: Page, timeout = 30000): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Espera até que o DOM esteja carregado
   */
  static async esperarDOMCarregado(page: Page, timeout = 30000): Promise<void> {
    await page.waitForLoadState('domcontentloaded', { timeout });
  }

  /**
   * Espera até que um loader/skeleton desapareça
   */
  static async esperarLoaderDesaparecer(page: Page, timeout = 10000): Promise<void> {
    await page.waitForSelector('[data-testid="skeleton-loader"], .animate-pulse', { state: 'hidden', timeout }).catch(() => {
      // Se não encontrar loader, continua normalmente
    });
  }

  /**
   * Espera até que um toast de sucesso apareça
   */
  static async esperarToastSucesso(page: Page, timeout = 5000): Promise<void> {
    await page.waitForSelector('[data-testid="toast-success"], .bg-green-500', { state: 'visible', timeout });
  }

  /**
   * Espera até que um toast de erro apareça
   */
  static async esperarToastErro(page: Page, timeout = 5000): Promise<void> {
    await page.waitForSelector('[data-testid="toast-error"], .bg-red-500', { state: 'visible', timeout });
  }

  /**
   * Espera um tempo fixo (último recurso)
   */
  static async esperar(ms: number): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Espera até que o locator esteja visível
   */
  static async esperarLocatorVisivel(locator: Locator, timeout = 10000): Promise<void> {
    await locator.waitFor({ state: 'visible', timeout });
  }

  /**
   * Espera até que o locator esteja oculto
   */
  static async esperarLocatorOculto(locator: Locator, timeout = 10000): Promise<void> {
    await locator.waitFor({ state: 'hidden', timeout });
  }
}
