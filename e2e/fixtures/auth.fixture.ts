import { test as base, Page, BrowserContext } from '@playwright/test';
import { LoginPage } from '@pages/login.page';

type AuthFixtures = {
  adminPage: Page;
  tecnicoPage: Page;
  gerentePage: Page;
  visualizadorPage: Page;
  loginAs: (perfil: 'admin' | 'tecnico' | 'gerente' | 'visualizador') => Promise<Page>;
};

export const test = base.extend<AuthFixtures>({
  // Página pré-autenticada como admin (reutiliza storageState)
  adminPage: async ({ page }, use) => {
    await use(page);
  },

  // loginAs: cria contexto isolado e faz login com as credenciais do perfil
  loginAs: async ({ browser }, use) => {
    const loginAs = async (perfil: string): Promise<Page> => {
      const credenciais = {
        admin: { email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! },
        tecnico: { email: process.env.TECNICO_EMAIL!, senha: process.env.TECNICO_SENHA! },
        gerente: { email: process.env.GERENTE_EMAIL!, senha: process.env.GERENTE_SENHA! },
        visualizador: { email: process.env.VISUALIZADOR_EMAIL!, senha: process.env.VISUALIZADOR_SENHA! },
      };
      const ctx = await browser.newContext();
      const page = await ctx.newPage();
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(credenciais[perfil as keyof typeof credenciais]);
      await page.waitForURL('**/dashboard');
      return page;
    };
    await use(loginAs);
  },
});
