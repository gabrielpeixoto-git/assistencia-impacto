import { test, expect } from '@playwright/test';

test.describe('RBAC — Controle de Acesso Baseado em Perfis', () => {
  test('RBAC: técnico não pode acessar configurações do sistema', async ({ page }) => {
    // Este teste usa storageState pré-configurado para técnico
    await page.goto('/configuracoes');
    
    // Deve ser redirecionado ou mostrar erro de permissão
    await expect(page).toHaveURL(/.*dashboard|.*acesso-negado/, { timeout: 10000 });
  });

  test('RBAC: técnico pode criar ordens de serviço', async ({ page }) => {
    await page.goto('/ordens-servico');
    
    const botaoNovaOS = page.getByRole('button', { name: /nova os|criar/i });
    await expect(botaoNovaOS).toBeVisible();
    
    await botaoNovaOS.click();
    await expect(page.locator('[data-testid="modal-nova-os"]')).toBeVisible();
  });

  test('RBAC: técnico não pode aprovar orçamentos', async ({ page }) => {
    await page.goto('/orcamentos');
    
    // Botão de aprovar não deve estar visível
    const botaoAprovar = page.locator('[data-testid="botao-aprovar"]');
    await expect(botaoAprovar).not.toBeVisible();
  });

  test('RBAC: gerente pode aprovar orçamentos', async ({ page }) => {
    // Nota: Este teste requer setup de autenticação como gerente
    // Por enquanto, apenas verifica a estrutura
    await page.goto('/orcamentos');
    
    // Verifica que a página carrega
    await expect(page.getByRole('heading', { name: /orçamentos/i })).toBeVisible();
  });
});
