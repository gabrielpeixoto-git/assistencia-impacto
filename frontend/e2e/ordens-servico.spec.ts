import { test, expect } from '@playwright/test';

test.describe('Ordens de Serviço', () => {
  test.beforeEach(async ({ page }) => {
    // Fazer login antes de cada teste
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*dashboard/);
    
    // Navegar para página de ordens de serviço
    await page.click('text=Ordens de Serviço');
    await page.waitForURL(/.*ordens-servico/);
  });

  test('deve exibir página de ordens de serviço', async ({ page }) => {
    await expect(page.locator('text=Ordens de Serviço').or(page.locator('text=Ordens'))).toBeVisible();
    await expect(page.locator('text=Gerencie as ordens de serviço')).toBeVisible();
  });

  test('deve abrir modal para criar nova ordem de serviço', async ({ page }) => {
    await page.click('button:has-text("Nova Ordem")');
    
    await expect(page.locator('text=Nova Ordem').or(page.locator('text=Nova Ordem de Serviço'))).toBeVisible();
    await expect(page.locator('text=Informações Básicas').or(page.locator('text=Dados da OS'))).toBeVisible();
  });

  test('deve criar ordem de serviço com dados válidos', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Nova Ordem")');
    
    // Selecionar cliente
    const clienteSelect = page.locator('select').filter({ hasText: /Cliente/ });
    await clienteSelect.click();
    await page.waitForTimeout(500);
    
    // Selecionar primeiro cliente disponível
    const firstOption = clienteSelect.locator('option').nth(1);
    if (await firstOption.count() > 0) {
      await clienteSelect.selectOption(await firstOption.getAttribute('value') || '');
    }
    
    // Preencher título
    const tituloInput = page.locator('input[name="titulo"]').or(page.locator('input[placeholder*="Título"]'));
    await tituloInput.fill('OS Teste E2E');
    
    // Preencher descrição
    const descricaoInput = page.locator('textarea[name="descricao"]').or(page.locator('textarea[placeholder*="Descrição"]'));
    await descricaoInput.fill('Descrição da ordem de serviço de teste E2E');
    
    // Selecionar categoria de serviço
    const categoriaSelect = page.locator('select').filter({ hasText: /Categoria/ });
    await categoriaSelect.click();
    await page.waitForTimeout(500);
    
    const firstCategoriaOption = categoriaSelect.locator('option').nth(1);
    if (await firstCategoriaOption.count() > 0) {
      await categoriaSelect.selectOption(await firstCategoriaOption.getAttribute('value') || '');
    }
    
    // Salvar ordem de serviço
    await page.click('button:has-text("Salvar")');
    
    // Aguardar sucesso
    await expect(page.locator('text=criado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
  });

  test('deve validar campos obrigatórios ao criar ordem de serviço', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Nova Ordem")');
    
    // Tentar salvar sem preencher campos
    await page.click('button:has-text("Salvar")');
    
    // Verificar alerta de validação
    await expect(page.locator('text=Preencha os campos obrigatórios').or(page.locator('text=obrigatórios'))).toBeVisible({ timeout: 5000 });
  });

  test('deve buscar ordens de serviço por título', async ({ page }) => {
    // Preencher campo de busca
    await page.fill('input[placeholder*="Buscar"]', 'Teste');
    
    // Aguardar resultados
    await page.waitForTimeout(1000);
    
    // Verificar se tabela está visível
    await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
  });

  test('deve filtrar ordens de serviço por status', async ({ page }) => {
    // Selecionar filtro de status
    const statusSelect = page.locator('select').filter({ hasText: /Todos/ }).or(
      page.locator('select').filter({ hasText: /Status/ })
    );
    
    if (await statusSelect.isVisible({ timeout: 3000 })) {
      await statusSelect.click();
      await page.waitForTimeout(500);
      
      // Selecionar status "Pendente"
      await statusSelect.selectOption('pendente');
      
      // Aguardar resultados
      await page.waitForTimeout(1000);
      
      // Verificar se tabela está visível
      await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
    }
  });

  test('deve editar ordem de serviço existente', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de editar da primeira ordem
    const editButton = page.locator('button').filter({ hasText: /Editar/ }).first();
    if (await editButton.isVisible({ timeout: 5000 })) {
      await editButton.click();
      
      // Verificar se modal de edição abriu
      await expect(page.locator('text=Editar Ordem').or(page.locator('text=Editar'))).toBeVisible();
      
      // Modificar título
      const tituloInput = page.locator('input[name="titulo"]').or(page.locator('input[placeholder*="Título"]'));
      await tituloInput.fill('OS Editada E2E');
      
      // Salvar
      await page.click('button:has-text("Salvar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=atualizado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('deve alterar status da ordem de serviço', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de alterar status da primeira ordem
    const statusButton = page.locator('button').filter({ hasText: /Iniciar/ }).or(
      page.locator('button').filter({ hasText: /Concluir/ })
    ).first();
    
    if (await statusButton.isVisible({ timeout: 5000 })) {
      await statusButton.click();
      
      // Aguardar atualização
      await page.waitForTimeout(1000);
      
      // Verificar se status foi alterado
      await expect(page.locator('text=Em andamento').or(page.locator('text=Concluída'))).toBeVisible();
    }
  });
});
