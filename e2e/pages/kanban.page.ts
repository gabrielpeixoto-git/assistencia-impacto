import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class KanbanPage extends BasePage {
  readonly board = this.page.locator('[data-testid="kanban-board"]');
  readonly colunaPendente = this.page.locator('[data-testid="kanban-coluna-pendente"]');
  readonly colunaEmAndamento = this.page.locator('[data-testid="kanban-coluna-em-andamento"]');
  readonly colunaConcluida = this.page.locator('[data-testid="kanban-coluna-concluida"]');
  readonly colunaCancelada = this.page.locator('[data-testid="kanban-coluna-cancelada"]');

  async verificarCarregado() {
    await expect(this.board).toBeVisible({ timeout: 10000 });
  }

  async contarCardsNaColuna(coluna: string): Promise<number> {
    const colunaLocator = this.page.locator(`[data-testid="kanban-coluna-${coluna}"]`);
    const cards = colunaLocator.locator('[data-testid="os-card"]');
    return await cards.count();
  }

  async arrastarCard(origem: string, destino: string, cardTexto?: string) {
    const colunaOrigem = this.page.locator(`[data-testid="kanban-coluna-${origem}"]`);
    const colunaDestino = this.page.locator(`[data-testid="kanban-coluna-${destino}"]`);
    
    let card = colunaOrigem.locator('[data-testid="os-card"]').first();
    if (cardTexto) {
      card = colunaOrigem.locator(`[data-testid="os-card"]:has-text("${cardTexto}")`);
    }
    
    await card.dragTo(colunaDestino);
  }

  async verificarCardNaColuna(texto: string, coluna: string) {
    const colunaLocator = this.page.locator(`[data-testid="kanban-coluna-${coluna}"]`);
    await expect(colunaLocator.locator(`[data-testid="os-card"]:has-text("${texto}")`)).toBeVisible();
  }

  async clicarCard(texto: string) {
    const card = this.board.locator(`[data-testid="os-card"]:has-text("${texto}")`);
    await card.click();
  }
}
