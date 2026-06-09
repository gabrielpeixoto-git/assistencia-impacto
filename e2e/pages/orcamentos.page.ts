import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

interface OrcamentoData {
  clienteId?: string;
  descricao?: string;
  itens?: Array<{ descricao: string; quantidade: number; valorUnitario: number }>;
}

export class OrcamentosPage extends BasePage {
  readonly titulo = this.page.getByRole('heading', { name: /orçamentos/i });
  readonly botaoNovoOrcamento = this.page.getByRole('button', { name: /novo orçamento|criar/i });
  readonly campoBusca = this.page.getByPlaceholder(/buscar por número, título/i);
  readonly tabela = this.page.locator('[data-testid="tabela-orcamentos"]');
  readonly modalNovoOrcamento = this.page.locator('[data-testid="modal-novo-orcamento"]');

  async goto() {
    await this.page.goto('/orcamentos');
    await this.esperarCarregamento();
  }

  async verificarCarregado() {
    await expect(this.titulo).toBeVisible({ timeout: 10000 });
  }

  async clicarNovoOrcamento() {
    await this.botaoNovoOrcamento.click();
    await expect(this.modalNovoOrcamento).toBeVisible();
  }

  async preencherFormularioOrcamento(data: OrcamentoData) {
    if (data.clienteId) {
      await this.selecionarOpcao('[data-testid="campo-cliente"]', data.clienteId);
    }
    if (data.descricao) {
      await this.page.locator('[data-testid="campo-descricao"]').fill(data.descricao);
    }
    if (data.itens && data.itens.length > 0) {
      // Mudar para tipo de cálculo manual para não depender de itens de estoque
      await this.selecionarCustomOpcao('[data-testid="campo-tipo-calculo"]', 'Manual');
      await this.page.waitForTimeout(500);
      
      // Calcular o valor total dos itens
      const valorTotal = data.itens.reduce((sum, item) => sum + (item.quantidade * item.valorUnitario), 0);
      await this.page.locator('[data-testid="campo-valor-total-manual"]').fill(valorTotal.toString());
    }
  }


  async salvarOrcamento() {
    await this.page.getByRole('button', { name: /salvar/i }).click();
    await this.esperarCarregamento();
  }

  async buscarOrcamento(termo: string) {
    await this.campoBusca.fill(termo);
    await this.esperarCarregamento();
  }

  async verificarOrcamentoNaTabela(descricao: string) {
    await expect(this.tabela.locator(`text=${descricao}`)).toBeVisible();
  }

  async aprovarOrcamento(descricao: string) {
    const linha = this.tabela.locator('tr').filter({ hasText: descricao });
    await linha.locator('[data-testid="botao-aprovar"]').click();
    await this.confirmarDialog();
  }

  async rejeitarOrcamento(descricao: string) {
    const linha = this.tabela.locator('tr').filter({ hasText: descricao });
    await linha.locator('[data-testid="botao-rejeitar"]').click();
    await this.confirmarDialog();
  }

  async converterParaOS(descricao: string) {
    const linha = this.tabela.locator('tr').filter({ hasText: descricao });
    await linha.locator('[data-testid="botao-converter-os"]').click();
    await this.confirmarDialog();
  }
}
