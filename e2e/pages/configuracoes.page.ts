import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ConfiguracoesPage extends BasePage {
  readonly titulo = this.page.getByRole('heading', { name: /configurações/i });
  readonly abaGeral = this.page.getByRole('button', { name: /geral/i });
  readonly abaSeguranca = this.page.getByRole('button', { name: /segurança/i });
  readonly abaSistema = this.page.getByRole('button', { name: /sistema/i });
  readonly abaNotificacoes = this.page.getByRole('button', { name: /notificações/i });
  readonly abaAparencia = this.page.getByRole('button', { name: /aparência/i });
  readonly botaoSalvar = this.page.getByRole('button', { name: /salvar/i });

  // Campos de alteração de senha
  readonly campoSenhaAtual = this.page.getByTestId('input-senha-atual');
  readonly campoNovaSenha = this.page.getByTestId('input-nova-senha');
  readonly campoConfirmarSenha = this.page.getByTestId('input-confirmar-senha');
  readonly botaoAlterarSenha = this.page.getByRole('button', { name: /alterar senha/i });

  // Sessões
  readonly listaSessoes = this.page.locator('[data-testid="lista-sessoes"]');
  readonly botaoEncerrarSessao = (sessaoId: string) => 
    this.page.locator(`[data-testid="btn-encerrar-sessao-${sessaoId}"]`);
  readonly botaoEncerrarTodasSessoes = this.page.getByTestId('btn-encerrar-todas-sessoes');

  async goto() {
    await this.page.goto('/configuracoes');
    await this.esperarCarregamento();
  }

  async verificarCarregado() {
    await expect(this.titulo).toBeVisible({ timeout: 10000 });
  }

  async clicarAba(aba: 'geral' | 'seguranca' | 'sistema' | 'notificacoes' | 'aparencia') {
    switch (aba) {
      case 'geral':
        await this.abaGeral.click();
        break;
      case 'seguranca':
        await this.abaSeguranca.click();
        break;
      case 'sistema':
        await this.abaSistema.click();
        break;
      case 'notificacoes':
        await this.abaNotificacoes.click();
        break;
      case 'aparencia':
        await this.abaAparencia.click();
        break;
    }
    await this.page.waitForTimeout(500);
  }

  async preencherAlteracaoSenha(senhaAtual: string, novaSenha: string, confirmarSenha: string) {
    await this.campoSenhaAtual.fill(senhaAtual);
    await this.campoNovaSenha.fill(novaSenha);
    await this.campoConfirmarSenha.fill(confirmarSenha);
  }

  async clicarAlterarSenha() {
    await this.botaoAlterarSenha.click();
  }

  async verificarSessoesVisiveis() {
    await expect(this.listaSessoes).toBeVisible({ timeout: 10000 });
  }

  async encerrarSessao(sessaoId: string) {
    await this.botaoEncerrarSessao(sessaoId).click();
  }

  async encerrarTodasSessoes() {
    await this.botaoEncerrarTodasSessoes.click();
  }

  async salvarConfiguracoes() {
    await this.botaoSalvar.click();
  }
}
