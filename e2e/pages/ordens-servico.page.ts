import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

interface OrdemServicoData {
  titulo: string;
  descricao: string;
  clienteId?: string;
  categoriaId?: string;
  prioridade?: string;
}

export class OrdensServicoPage extends BasePage {
  readonly titulo = this.page.getByRole('heading', { name: 'Ordens de Serviço' });
  readonly botaoNovaOS = this.page.locator('[data-testid="botao-nova-os"]');
  readonly campoBusca = this.page.getByPlaceholder(/buscar por número, título/i);
  readonly tabela = this.page.locator('[data-testid="tabela-os"]');
  readonly kanbanBoard = this.page.locator('[data-testid="kanban-board"]');
  readonly modalNovaOS = this.page.locator('[data-testid="modal-nova-os"]');

  async goto() {
    await this.page.goto('/ordens-servico');
    await this.esperarCarregamento();
  }

  async verificarCarregado() {
    await expect(this.titulo).toBeVisible({ timeout: 10000 });
  }

  async clicarNovaOS() {
    await this.botaoNovaOS.click();
    await expect(this.modalNovaOS).toBeVisible();
  }

  async preencherFormularioOS(data: OrdemServicoData) {
    // Selecionar primeiro cliente
    await this.page.locator('[data-testid="campo-cliente"]').selectOption({ index: 1 });
    
    // Selecionar primeira categoria
    await this.page.locator('[data-testid="campo-categoria"]').selectOption({ index: 1 });
    
    if (data.titulo) {
      await this.page.locator('[data-testid="campo-titulo"]').fill(data.titulo);
    }
    if (data.descricao) {
      await this.page.locator('[data-testid="campo-descricao"]').fill(data.descricao);
    }
    if (data.clienteId) {
      await this.selecionarCustomOpcao('[data-testid="campo-cliente"]', data.clienteId);
    }
    if (data.categoriaId) {
      await this.selecionarCustomOpcao('[data-testid="campo-categoria"]', data.categoriaId);
    }
    if (data.prioridade) {
      await this.selecionarCustomOpcao('[data-testid="campo-prioridade"]', data.prioridade);
    }
  }

  async selecionarOpcaoNativa(selector: string, valor: string) {
    await this.page.locator(selector).selectOption(valor);
  }

  async salvarOS() {
    // Clicar no botão Salvar para submeter o formulário
    await this.page.locator('[data-testid="botao-salvar-os"]').click();
    
    // Aguardar o modal fechar (indica sucesso)
    await expect(this.modalNovaOS).not.toBeVisible();
    
    // Aguardar a tabela atualizar (TanStack Query refetch automático)
    await this.esperarCarregamento();
  }

  async buscarOS(termo: string) {
    await this.campoBusca.fill(termo);
    await this.esperarCarregamento();
  }

  async verificarOSNaTabela(titulo: string) {
    await expect(this.tabela.getByText(titulo)).toBeVisible();
  }

  async clicarOS(titulo: string) {
    // Clicar no botão de editar da OS na tabela
    const osRow = this.tabela.locator('tr').filter({ hasText: titulo });
    await osRow.locator('[data-testid="botao-editar-os"]').click();
  }

  async mudarStatusOS(titulo: string, novoStatus: string) {
    await this.clicarOS(titulo);
    await this.selecionarOpcao('[data-testid="campo-status"]', novoStatus);
    await this.page.getByRole('button', { name: /atualizar|salvar/i }).click();
    await this.esperarCarregamento();
  }
}
