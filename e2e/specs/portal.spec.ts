import { test, expect } from '@playwright/test';
import { apiPost, getAdminToken } from '../helpers/api.helper';

test.describe('Portal Público do Cliente', () => {

  test('cliente acessa orçamento sem login', async ({ page }) => {
    // Criar orçamento de teste via API
    const orcamentoResponse = await apiPost('/api/orcamentos', {
      cliente_id: 'cliente-teste-id',
      titulo: 'Orçamento Teste Portal',
      descricao: 'Orçamento para teste do portal público',
      subtotal: 1000,
      total: 1000,
    }) as any;

    const orcamentoId = orcamentoResponse.id;
    const orcamentoToken = orcamentoResponse.token_acesso_publico;

    // Enviar orçamento para gerar token
    await apiPost(`/api/orcamentos/${orcamentoId}/enviar`, {});

    // Acessar orçamento via portal público (sem autenticação)
    await page.goto(`/portal/orcamento/${orcamentoToken}`);

    // Verificar que a página carregou
    await expect(page.locator('h1')).toContainText('Orçamento Teste Portal');
    await expect(page.locator('text=Orçamento #')).toBeVisible();
    await expect(page.locator('text=Itens do Orçamento')).toBeVisible();
    await expect(page.locator('text=Resumo Financeiro')).toBeVisible();
  });

  test('portal é responsivo em mobile', async ({ page }) => {
    // Criar orçamento de teste via API
    const orcamentoResponse = await apiPost('/api/orcamentos', {
      cliente_id: 'cliente-teste-id',
      titulo: 'Orçamento Teste Mobile',
      descricao: 'Orçamento para teste de responsividade',
      subtotal: 500,
      total: 500,
    }) as any;

    const orcamentoId = orcamentoResponse.id;
    const orcamentoToken = orcamentoResponse.token_acesso_publico;

    // Enviar orçamento para gerar token
    await apiPost(`/api/orcamentos/${orcamentoId}/enviar`, {});

    // Simular viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`/portal/orcamento/${orcamentoToken}`);

    // Verificar que o layout é responsivo
    await expect(page.locator('h1')).toContainText('Orçamento Teste Mobile');
    
    // Verificar que elementos estão visíveis em mobile
    await expect(page.locator('text=Resumo Financeiro')).toBeVisible();
    
    // Verificar que a tabela de itens tem scroll horizontal em mobile
    const tabelaItens = page.locator('table');
    await expect(tabelaItens).toBeVisible();
  });

});
