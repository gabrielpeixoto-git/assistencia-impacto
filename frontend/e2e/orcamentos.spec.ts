import { test, expect } from '@playwright/test';

test.describe('Orçamentos', () => {
  test.beforeEach(async ({ page }) => {
    // Fazer login antes de cada teste
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*dashboard/);
    
    // Navegar para página de orçamentos
    await page.click('text=Orçamentos');
    await page.waitForURL(/.*orcamentos/);
  });

  test('deve exibir página de orçamentos', async ({ page }) => {
    await expect(page.locator('text=Orçamentos')).toBeVisible();
    await expect(page.locator('text=Gerencie os orçamentos do sistema')).toBeVisible();
  });

  test('deve abrir modal para criar novo orçamento', async ({ page }) => {
    await page.click('button:has-text("Novo Orçamento")');
    
    await expect(page.locator('text=Novo Orçamento')).toBeVisible();
    await expect(page.locator('text=Informações Básicas')).toBeVisible();
  });

  test('deve criar orçamento com dados válidos', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Novo Orçamento")');
    
    // Selecionar cliente
    const clienteSelect = page.locator('#cliente-orcamento');
    await clienteSelect.click();
    await page.waitForTimeout(500);
    
    // Selecionar primeiro cliente disponível
    const firstOption = clienteSelect.locator('option').nth(1);
    if (await firstOption.count() > 0) {
      await clienteSelect.selectOption(await firstOption.getAttribute('value') || '');
    }
    
    // Preencher título
    await page.fill('#titulo-orcamento', 'Orçamento de Teste E2E');
    
    // Preencher descrição
    await page.fill('#descricao-orcamento', 'Descrição do orçamento de teste E2E');
    
    // Selecionar tipo de cálculo automático
    await page.selectOption('#tipo-calculo-orcamento', 'automatico');
    
    // Salvar orçamento
    await page.click('button:has-text("Salvar")');
    
    // Aguardar sucesso
    await expect(page.locator('text=criado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
  });

  test('deve validar campos obrigatórios ao criar orçamento', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Novo Orçamento")');
    
    // Tentar salvar sem preencher campos
    await page.click('button:has-text("Salvar")');
    
    // Verificar alerta de validação
    await expect(page.locator('text=Preencha os campos obrigatórios').or(page.locator('text=obrigatórios'))).toBeVisible({ timeout: 5000 });
  });

  test('deve buscar orçamentos por título', async ({ page }) => {
    // Preencher campo de busca
    await page.fill('input[placeholder*="Buscar"]', 'Teste');
    
    // Aguardar resultados
    await page.waitForTimeout(1000);
    
    // Verificar se tabela está visível
    await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
  });

  test('deve filtrar orçamentos por status', async ({ page }) => {
    // Selecionar filtro de status
    const statusSelect = page.locator('select').filter({ hasText: 'Todos os Status' });
    await statusSelect.click();
    await page.waitForTimeout(500);
    
    // Selecionar status "Rascunho"
    await statusSelect.selectOption('rascunho');
    
    // Aguardar resultados
    await page.waitForTimeout(1000);
    
    // Verificar se tabela está visível
    await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
  });

  test('deve editar orçamento existente', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de editar do primeiro orçamento
    const editButton = page.locator('button').filter({ hasText: /Editar/ }).first();
    if (await editButton.isVisible({ timeout: 5000 })) {
      await editButton.click();
      
      // Verificar se modal de edição abriu
      await expect(page.locator('text=Editar Orçamento')).toBeVisible();
      
      // Modificar título
      await page.fill('#titulo-orcamento', 'Orçamento Editado E2E');
      
      // Salvar
      await page.click('button:has-text("Salvar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=atualizado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('deve deletar orçamento com confirmação', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de deletar do primeiro orçamento
    const deleteButton = page.locator('button').filter({ hasText: /Deletar/ }).first();
    if (await deleteButton.isVisible({ timeout: 5000 })) {
      await deleteButton.click();
      
      // Verificar se modal de confirmação abriu
      await expect(page.locator('text=Confirmar').or(page.locator('text=Tem certeza'))).toBeVisible();
      
      // Confirmar deleção
      await page.click('button:has-text("Confirmar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=removido com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });
});
