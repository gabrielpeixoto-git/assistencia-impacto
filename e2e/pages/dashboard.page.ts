import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class DashboardPage extends BasePage {
  readonly titulo = this.page.getByRole('heading', { name: /dashboard|visão geral/i });
  readonly statCardReceita = this.page.locator('[data-testid="stat-card-receita"]');
  readonly statCardOS = this.page.locator('[data-testid="stat-card-os"]');
  readonly statCardClientes = this.page.locator('[data-testid="stat-card-clientes"]');
  readonly statCardOrcamentos = this.page.locator('[data-testid="stat-card-orcamentos"]');
  readonly graficoReceita = this.page.locator('[data-testid="grafico-receita"]');
  readonly graficoStatusOS = this.page.locator('[data-testid="grafico-status-os"]');
  readonly tabelaRecentes = this.page.locator('[data-testid="tabela-os-recentes"]');

  async goto() {
    await this.page.goto('/');
    await this.esperarCarregamento();
  }

  async verificarCarregado() {
    await expect(this.titulo).toBeVisible({ timeout: 20000 });
  }

  async obterValorStatCard(statCard: string) {
    const card = this.page.locator(`[data-testid="stat-card-${statCard}"]`);
    await expect(card).toBeVisible();
    const valor = await card.locator('[data-testid="stat-card-valor"]').textContent();
    return valor;
  }

  async clicarEmOSRecente(numero: number) {
    const linhas = this.tabelaRecentes.locator('tbody tr');
    await linhas.nth(numero - 1).click();
  }
}
