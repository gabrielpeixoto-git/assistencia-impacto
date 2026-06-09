import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

interface Credenciais { email: string; senha: string; }

export class LoginPage extends BasePage {
  readonly campoEmail = this.page.getByTestId('login-email');
  readonly campoSenha = this.page.getByTestId('login-senha');
  readonly botaoEntrar = this.page.getByTestId('login-botao-entrar');

  async goto() {
    await this.page.goto('/login');
    await expect(this.botaoEntrar).toBeVisible();
  }

  async login({ email, senha }: Credenciais) {
    await this.campoEmail.fill(email);
    await this.campoSenha.fill(senha);
    await this.botaoEntrar.click();
  }

  async loginComSucesso(credenciais: Credenciais) {
    await this.login(credenciais);
    await expect(this.page).toHaveURL(/.*\/$/, { timeout: 15_000 });
  }

  async loginComFalha(credenciais: Credenciais) {
    await this.login(credenciais);
    await expect(this.page.locator('text=erro').or(this.page.locator('text=Erro'))).toBeVisible({ timeout: 5000 });
  }
}
