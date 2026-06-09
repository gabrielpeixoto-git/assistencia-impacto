import { test, expect } from '@playwright/test';
import { OrcamentosPage } from '../../pages/orcamentos.page';
import { DataFactory } from '../../helpers/data-factory';
import { LoginPage } from '../../pages/login.page';

test.describe('Orçamentos — Fluxo de Aprovação', () => {
  let orcamentosPage: OrcamentosPage;
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
    orcamentosPage = new OrcamentosPage(page);
  });

  test('FLUXO ORÇAMENTO: criar orçamento com sucesso', async ({ page }) => {
    // Navegar para orçamentos
    await orcamentosPage.goto();
    await orcamentosPage.verificarCarregado();

    // Criar novo orçamento
    await orcamentosPage.clicarNovoOrcamento();
    
    const orcamentoData = DataFactory.gerarOrcamento({
      descricao: 'Orçamento Teste E2E',
      itens: [
        { descricao: 'Serviço 1', quantidade: 2, valorUnitario: 100 },
        { descricao: 'Serviço 2', quantidade: 1, valorUnitario: 50 },
      ],
    });

    await orcamentosPage.preencherFormularioOrcamento(orcamentoData);
    await orcamentosPage.salvarOrcamento();

    // Verificar que o orçamento foi criado
    await orcamentosPage.buscarOrcamento(orcamentoData.descricao);
    await orcamentosPage.verificarOrcamentoNaTabela(orcamentoData.descricao);
  });

  test('FLUXO ORÇAMENTO: aprovar orçamento', async ({ page }) => {
    await orcamentosPage.goto();
    await orcamentosPage.verificarCarregado();

    // Criar orçamento para aprovar
    await orcamentosPage.clicarNovoOrcamento();
    
    const orcamentoData = DataFactory.gerarOrcamento({
      descricao: 'Orçamento para Aprovar',
      itens: [
        { descricao: 'Serviço Teste', quantidade: 1, valorUnitario: 100 },
      ],
    });

    await orcamentosPage.preencherFormularioOrcamento(orcamentoData);
    await orcamentosPage.salvarOrcamento();

    // Buscar orçamento criado
    await orcamentosPage.buscarOrcamento(orcamentoData.descricao);

    // Aprovar orçamento
    await orcamentosPage.aprovarOrcamento(orcamentoData.descricao);

    // Verificar que o status foi atualizado
    await expect(page.locator('text=Aprovado')).toBeVisible();
  });

  test('FLUXO ORÇAMENTO: rejeitar orçamento', async ({ page }) => {
    await orcamentosPage.goto();
    await orcamentosPage.verificarCarregado();

    // Criar orçamento para rejeitar
    await orcamentosPage.clicarNovoOrcamento();
    
    const orcamentoData = DataFactory.gerarOrcamento({
      descricao: 'Orçamento para Rejeitar',
      itens: [
        { descricao: 'Serviço Teste', quantidade: 1, valorUnitario: 100 },
      ],
    });

    await orcamentosPage.preencherFormularioOrcamento(orcamentoData);
    await orcamentosPage.salvarOrcamento();

    // Buscar orçamento criado
    await orcamentosPage.buscarOrcamento(orcamentoData.descricao);

    // Rejeitar orçamento
    await orcamentosPage.rejeitarOrcamento(orcamentoData.descricao);

    // Verificar que o status foi atualizado
    await expect(page.locator('text=Rejeitado')).toBeVisible();
  });

  test('FLUXO ORÇAMENTO: converter orçamento em OS', async ({ page }) => {
    await orcamentosPage.goto();
    await orcamentosPage.verificarCarregado();

    // Criar orçamento para converter
    await orcamentosPage.clicarNovoOrcamento();
    
    const orcamentoData = DataFactory.gerarOrcamento({
      descricao: 'Orçamento para Converter',
      itens: [
        { descricao: 'Serviço Teste', quantidade: 1, valorUnitario: 100 },
      ],
    });

    await orcamentosPage.preencherFormularioOrcamento(orcamentoData);
    await orcamentosPage.salvarOrcamento();

    // Buscar orçamento criado
    await orcamentosPage.buscarOrcamento(orcamentoData.descricao);

    // Aprovar orçamento primeiro (precisa estar aprovado para converter)
    await orcamentosPage.aprovarOrcamento(orcamentoData.descricao);

    // Buscar novamente após aprovar
    await orcamentosPage.buscarOrcamento(orcamentoData.descricao);

    // Converter para OS
    await orcamentosPage.converterParaOS(orcamentoData.descricao);

    // Verificar redirecionamento para ordens de serviço
    await expect(page).toHaveURL(/.*ordens-servico/, { timeout: 10000 });
  });
});
