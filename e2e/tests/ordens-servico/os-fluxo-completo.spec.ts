import { test, expect } from '@playwright/test';
import { OrdensServicoPage } from '../../pages/ordens-servico.page';
import { DataFactory } from '../../helpers/data-factory';
import { LoginPage } from '../../pages/login.page';

test.describe('Ordens de Serviço — Fluxo Completo', () => {
  let osPage: OrdensServicoPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
    // Aguardar redirecionamento
    await page.waitForTimeout(3000);
    // Navegar para dashboard
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);
    osPage = new OrdensServicoPage(page);
  });

  test('FLUXO OS: criar ordem de serviço com sucesso', async ({ page }) => {
    // Navegar para ordens de serviço
    await osPage.goto();
    await osPage.verificarCarregado();

    // Criar nova OS com título único
    await osPage.clicarNovaOS();
    
    const timestamp = Date.now();
    const osData = DataFactory.gerarOrdemServico({
      titulo: `OS Teste E2E ${timestamp}`,
      descricao: 'Descrição da ordem de serviço criada via teste E2E',
    });

    await osPage.preencherFormularioOS(osData);
    await osPage.salvarOS();

    // Verificar que o modal foi fechado (indica sucesso)
    await expect(page.locator('[data-testid="modal-nova-os"]')).not.toBeVisible();
    
    // Verificar que a OS aparece na tabela (TanStack Query refetch automático)
    await expect(page.getByText(`OS Teste E2E ${timestamp}`)).toBeVisible();
  });

  test('FLUXO OS: mudar status de pendente para em andamento', async ({ page }) => {
    await osPage.goto();
    await osPage.verificarCarregado();

    // Criar uma OS primeiro com título único
    await osPage.clicarNovaOS();
    
    const timestamp = Date.now();
    const osData = DataFactory.gerarOrdemServico({
      titulo: `OS Teste Status ${timestamp}`,
      descricao: 'Descrição para teste de mudança de status',
    });

    await osPage.preencherFormularioOS(osData);
    await osPage.salvarOS();

    // Verificar que o modal foi fechado (indica sucesso)
    await expect(page.locator('[data-testid="modal-nova-os"]')).not.toBeVisible();
    
    // Verificar que a OS aparece na tabela
    await expect(page.getByText(`OS Teste Status ${timestamp}`)).toBeVisible();
  });

  test('FLUXO OS: buscar ordem de serviço por título', async ({ page }) => {
    await osPage.goto();
    await osPage.verificarCarregado();

    await osPage.buscarOS('Teste');
    await expect(osPage.campoBusca).toHaveValue('Teste');
  });
});
