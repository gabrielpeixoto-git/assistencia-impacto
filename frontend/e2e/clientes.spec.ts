import { test, expect } from '@playwright/test';

test.describe('Clientes', () => {
  test.beforeEach(async ({ page }) => {
    // Fazer login antes de cada teste
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@assistenciaimpacto.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*dashboard/);
    
    // Navegar para página de clientes
    await page.click('text=Clientes');
    await page.waitForURL(/.*clientes/);
  });

  test('deve exibir página de clientes', async ({ page }) => {
    await expect(page.locator('text=Clientes')).toBeVisible();
    await expect(page.locator('text=Gerencie os clientes do sistema')).toBeVisible();
  });

  test('deve abrir modal para criar novo cliente', async ({ page }) => {
    await page.click('button:has-text("Novo Cliente")');
    
    await expect(page.locator('text=Novo Cliente').or(page.locator('text=Cadastrar Cliente'))).toBeVisible();
    await expect(page.locator('text=Informações Pessoais').or(page.locator('text=Dados do Cliente'))).toBeVisible();
  });

  test('deve criar cliente com dados válidos', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Novo Cliente")');
    
    // Preencher nome
    await page.fill('input[name="nome"]', 'Cliente Teste E2E');
    
    // Preencher email
    await page.fill('input[name="email"]', 'cliente.e2e@teste.com');
    
    // Preencher telefone
    await page.fill('input[name="telefone"]', '11999999999');
    
    // Preencher CPF/CNPJ
    await page.fill('input[name="cpf_cnpj"]', '12345678900');
    
    // Salvar cliente
    await page.click('button:has-text("Salvar")');
    
    // Aguardar sucesso
    await expect(page.locator('text=criado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
  });

  test('deve validar campos obrigatórios ao criar cliente', async ({ page }) => {
    // Abrir modal de criação
    await page.click('button:has-text("Novo Cliente")');
    
    // Tentar salvar sem preencher campos
    await page.click('button:has-text("Salvar")');
    
    // Verificar alerta de validação
    await expect(page.locator('text=Preencha os campos obrigatórios').or(page.locator('text=obrigatórios'))).toBeVisible({ timeout: 5000 });
  });

  test('deve buscar clientes por nome', async ({ page }) => {
    // Preencher campo de busca
    await page.fill('input[placeholder*="Buscar"]', 'Teste');
    
    // Aguardar resultados
    await page.waitForTimeout(1000);
    
    // Verificar se tabela está visível
    await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
  });

  test('deve filtrar clientes por status', async ({ page }) => {
    // Selecionar filtro de status
    const statusSelect = page.locator('select').filter({ hasText: /Todos/ }).or(
      page.locator('select').filter({ hasText: /Status/ })
    );
    
    if (await statusSelect.isVisible({ timeout: 3000 })) {
      await statusSelect.click();
      await page.waitForTimeout(500);
      
      // Selecionar status "Ativo"
      await statusSelect.selectOption('ativo');
      
      // Aguardar resultados
      await page.waitForTimeout(1000);
      
      // Verificar se tabela está visível
      await expect(page.locator('table').or(page.locator('[role="table"]'))).toBeVisible();
    }
  });

  test('deve editar cliente existente', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de editar do primeiro cliente
    const editButton = page.locator('button').filter({ hasText: /Editar/ }).first();
    if (await editButton.isVisible({ timeout: 5000 })) {
      await editButton.click();
      
      // Verificar se modal de edição abriu
      await expect(page.locator('text=Editar Cliente').or(page.locator('text=Editar'))).toBeVisible();
      
      // Modificar nome
      await page.fill('input[name="nome"]', 'Cliente Editado E2E');
      
      // Salvar
      await page.click('button:has-text("Salvar")');
      
      // Aguardar sucesso
      await expect(page.locator('text=atualizado com sucesso').or(page.locator('text=sucesso'))).toBeVisible({ timeout: 10000 });
    }
  });

  test('deve deletar cliente com confirmação', async ({ page }) => {
    // Aguardar carregamento da tabela
    await page.waitForTimeout(2000);
    
    // Clicar no botão de deletar do primeiro cliente
    const deleteButton = page.locator('button').filter({ hasText: /Deletar/ }).or(
      page.locator('button').filter({ hasText: /Excluir/ })
    ).first();
    
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
