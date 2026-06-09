import { test, expect } from '@playwright/test';
import { OrdensServicoPage } from '../../pages/ordens-servico.page';
import { KanbanPage } from '../../pages/kanban.page';
import { LoginPage } from '../../pages/login.page';

test.describe('Kanban — Drag and Drop', () => {
  let osPage: OrdensServicoPage;
  let kanbanPage: KanbanPage;
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
    kanbanPage = new KanbanPage(page);
  });

  test('KANBAN: arrastar OS de pendente para em andamento', async ({ page }) => {
    await osPage.goto();
    await kanbanPage.verificarCarregado();

    const countAntes = await kanbanPage.contarCardsNaColuna('em-andamento');
    await kanbanPage.arrastarCard('pendente', 'em-andamento');
    const countDepois = await kanbanPage.contarCardsNaColuna('em-andamento');

    expect(countDepois).toBe(countAntes + 1);
  });

  test('KANBAN: arrastar OS de em andamento para concluída', async ({ page }) => {
    await osPage.goto();
    await kanbanPage.verificarCarregado();

    await kanbanPage.arrastarCard('em-andamento', 'concluida');
    await kanbanPage.verificarCardNaColuna('OS Teste', 'concluida');
  });

  test('KANBAN: clicar em card abre detalhes da OS', async ({ page }) => {
    await osPage.goto();
    await kanbanPage.verificarCarregado();

    await kanbanPage.clicarCard('OS Teste');

    // Verificar que modal ou página de detalhes foi aberta
    await expect(page.locator('[data-testid="modal-detalhes-os"], [data-testid="pagina-detalhes-os"]')).toBeVisible();
  });
});
