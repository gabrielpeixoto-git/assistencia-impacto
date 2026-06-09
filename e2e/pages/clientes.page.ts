import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

interface ClienteData {
  nome: string;
  email?: string;
  telefone?: string;
  endereco?: string;
}

export class ClientesPage extends BasePage {
  readonly titulo = this.page.getByRole('heading', { name: /clientes/i });
  readonly botaoNovoCliente = this.page.getByRole('button', { name: /novo cliente|adicionar/i });
  readonly campoBusca = this.page.getByPlaceholder(/buscar por nome, email/i);
  readonly tabela = this.page.locator('[data-testid="tabela-clientes"]');
  readonly modalNovoCliente = this.page.locator('[data-testid="modal-novo-cliente"]');

  async goto() {
    await this.page.goto('/clientes');
    await this.esperarCarregamento();
  }

  async verificarCarregado() {
    await expect(this.titulo).toBeVisible({ timeout: 10000 });
  }

  async clicarNovoCliente() {
    await this.botaoNovoCliente.click();
    await expect(this.modalNovoCliente).toBeVisible();
  }

  async preencherFormularioCliente(data: ClienteData) {
    if (data.nome) {
      await this.page.locator('[data-testid="campo-nome"]').fill(data.nome);
    }
    if (data.email) {
      await this.page.locator('[data-testid="campo-email"]').fill(data.email);
    }
    if (data.telefone) {
      await this.page.locator('[data-testid="campo-telefone"]').fill(data.telefone);
    }
    if (data.endereco) {
      await this.page.locator('[data-testid="campo-endereco"]').fill(data.endereco);
    }
  }

  async salvarCliente() {
    await this.page.getByRole('button', { name: /salvar/i }).click();
    await this.esperarCarregamento();
  }

  async buscarCliente(termo: string) {
    await this.campoBusca.fill(termo);
    await this.esperarCarregamento();
  }

  async verificarClienteNaTabela(nome: string) {
    await expect(this.tabela.locator(`text=${nome}`).first()).toBeVisible();
  }

  async clicarEditarCliente(nome: string) {
    const linha = this.tabela.locator(`tr:has-text("${nome}")`);
    await linha.locator('[data-testid="botao-editar"]').click();
  }

  async clicarExcluirCliente(nome: string) {
    const linha = this.tabela.locator(`tr:has-text("${nome}")`);
    await linha.locator('[data-testid="botao-excluir"]').click();
    // Esperar modal de confirmação aparecer
    await expect(this.page.locator('[data-testid="modal-confirmacao"]')).toBeVisible({ timeout: 5000 });
    await this.confirmarDialog();
  }
}
