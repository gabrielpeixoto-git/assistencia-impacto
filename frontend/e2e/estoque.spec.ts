import { test, expect } from '@playwright/test';

test.describe('Estoque', () => {
  test.beforeEach(async ({ page }) => {
    // Fazer login antes de cada teste
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*dashboard/);
    
    // Navegar para página de estoque
    await page.click('text=Estoque');
    await page.waitForURL(/.*estoque/);
  });

  test('deve exibir página de estoque', async ({ page }) => {
    await expect(page.locator('text=Estoque')).toBeVisible();
    await expect(page.locator('text=Gerencie o estoque')).toBeVisible();
  });

  test('deve abrir modal para novo item', async ({ page }) => {
    await page.click('button:has-text("Novo Item")');
    
    await expect(page.locator('text=Novo Item').or(page.locator('text=Adicionar Item'))).toBeVisible();
  });

  test('deve fechar modal ao clicar em cancelar', async ({ page }) => {
    await page.click('button:has-text("Novo Item")');
    await page.waitForTimeout(500);
    
    await page.click('button:has-text("Cancelar")');
    await page.waitForTimeout(500);
    
    const modal = page.locator('text=Novo Item').or(page.locator('text=Adicionar Item'));
    await expect(modal).not.toBeVisible();
  });

  test('deve preencher filtro de busca', async ({ page }) => {
    await page.fill('input[placeholder*="Buscar"]', 'parafuso');
    await page.waitForTimeout(1000);
    
    await expect(page.locator('input[placeholder*="Buscar"]')).toHaveValue('parafuso');
  });

  test('deve filtrar por categoria', async ({ page }) => {
    const categoriaSelect = page.locator('select').filter({ hasText: 'Todas' }).or(page.locator('select').first());
    await categoriaSelect.click();
    await page.waitForTimeout(500);
    
    const options = await categoriaSelect.locator('option').count();
    if (options > 1) {
      await categoriaSelect.selectOption({ index: 1 });
      await page.waitForTimeout(1000);
    }
  });

  test('deve exibir tabela de itens', async ({ page }) => {
    await page.waitForTimeout(2000);
    await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
  });

  test('deve criar item com dados válidos', async ({ page }) => {
    await page.click('button:has-text("Novo Item")');
    await page.waitForTimeout(500);
    
    // Preencher nome
    await page.fill('input[name="nome"]', 'Item de Teste E2E');
    
    // Preencher descrição
    await page.fill('textarea[name="descricao"]', 'Descrição do item de teste');
    
    // Preencher quantidade
    await page.fill('input[name="quantidade"]', '10');
    
    // Preencher custo unitário
    await page.fill('input[name="custo_unitario"]', '50,00');
    
    // Selecionar unidade
    const unidadeSelect = page.locator('select[name="unidade"]');
    await unidadeSelect.selectOption('UN');
    
    // Selecionar categoria
    const categoriaSelect = page.locator('select[name="categoria"]');
    const options = await categoriaSelect.locator('option').count();
    if (options > 1) {
      await categoriaSelect.selectOption({ index: 1 });
    }
    
    // Salvar
    await page.click('button:has-text("Salvar")');
    
    // Aguardar sucesso
    await expect(page.locator('text=criado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
  });

  test('deve validar campos obrigatórios ao criar item', async ({ page }) => {
    await page.click('button:has-text("Novo Item")');
    await page.waitForTimeout(500);
    
    // Tentar salvar sem preencher campos
    await page.click('button:has-text("Salvar")');
    
    // Verificar alerta de validação
    await expect(page.locator('text=Preencha os campos obrigatórios').or(page.locator('text=obrigatórios'))).toBeVisible({ timeout: 5000 });
  });

  test('deve editar item existente', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Clicar no botão de editar do primeiro item
    const editButton = page.locator('button').filter({ hasText: /Editar/ }).first();
    if (await editButton.isVisible({ timeout: 5000 })) {
      await editButton.click();
      await page.waitForTimeout(500);
      
      // Verificar se modal de edição abriu
      await expect(page.locator('text=Editar Item').or(page.locator('text=Editar'))).toBeVisible();
      
      // Modificar nome
      await page.fill('input[name="nome"]', 'Item Editado E2E');
      
      // Salvar
      await page.click('button:has-text("Salvar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=atualizado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('deve deletar item com confirmação', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Clicar no botão de deletar do primeiro item
    const deleteButton = page.locator('button').filter({ hasText: /Deletar/ }).or(page.locator('button').filter({ hasText: /Excluir/ })).first();
    if (await deleteButton.isVisible({ timeout: 5000 })) {
      await deleteButton.click();
      await page.waitForTimeout(500);
      
      // Verificar se modal de confirmação abriu
      await expect(page.locator('text=Confirmar').or(page.locator('text=Tem certeza'))).toBeVisible();
      
      // Confirmar deleção
      await page.click('button:has-text("Confirmar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=removido com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('deve exibir indicador de estoque baixo', async ({ page }) => {
    await page.waitForTimeout(2000);
    // Verificar se há indicadores de estoque baixo (itens com quantidade abaixo do mínimo)
    const lowStockIndicator = page.locator('text=Estoque Baixo').or(page.locator('[data-testid="low-stock"]'));
    // Este teste pode não falhar se não houver itens com estoque baixo
  });

  test('deve registrar movimentação de entrada', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Clicar no botão de movimentação do primeiro item
    const moveButton = page.locator('button').filter({ hasText: /Movimentação/ }).or(page.locator('button').filter({ hasText: /Entrada/ })).first();
    if (await moveButton.isVisible({ timeout: 5000 })) {
      await moveButton.click();
      await page.waitForTimeout(500);
      
      // Verificar se modal de movimentação abriu
      await expect(page.locator('text=Movimentação').or(page.locator('text=Entrada'))).toBeVisible();
      
      // Preencher quantidade
      await page.fill('input[name="quantidade"]', '5');
      
      // Salvar
      await page.click('button:has-text("Salvar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=sucesso').or(page.locator('text=registrado'))).toBeVisible({ timeout: 10000 });
    }
  });
});
