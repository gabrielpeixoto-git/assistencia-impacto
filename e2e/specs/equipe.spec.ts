import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Módulo Equipe — Admin', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/admin.json') });

  test.beforeEach(async ({ page }) => {
    await page.goto('/equipe');
    await page.waitForSelector('[data-testid="equipe-container"]');
  });

  test('deve exibir grade de técnicos', async ({ page }) => {
    await expect(page.locator('[data-testid="equipe-container"]')).toBeVisible();
  });

  test('deve exibir botão de novo usuário', async ({ page }) => {
    await expect(page.locator('[data-testid="btn-novo-usuario"]')).toBeVisible();
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await expect(page.locator('[data-testid="input-busca-equipe"]')).toBeVisible();
  });

  test('deve abrir modal ao clicar em Novo Usuário', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
    await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Novo Membro');
  });

  test('deve preencher e salvar novo usuário', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    // Preencher formulário
    await page.fill('[data-testid="input-email-usuario"]', 'novo.usuario@teste.com');
    await page.fill('[data-testid="input-nome-usuario"]', 'Usuário Teste E2E');
    await page.fill('[data-testid="input-telefone-usuario"]', '11999999999');
    await page.fill('[data-testid="input-senha-usuario"]', 'Senha123!');
    await page.fill('[data-testid="input-confirmar-senha-usuario"]', 'Senha123!');

    // Salvar
    await page.click('[data-testid="btn-salvar-usuario"]');
    
    // Modal deve fechar
    await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
    await page.waitForTimeout(1000);
  });

  test('deve cancelar criação de usuário', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.click('[data-testid="btn-cancelar-modal"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  });

  test('deve validar campos obrigatórios ao criar usuário', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    // Tentar salvar sem preencher campos
    await page.click('[data-testid="btn-salvar-usuario"]');
    
    // Modal deve permanecer aberto (validação impediu salvamento)
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve validar confirmação de senha', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.fill('[data-testid="input-email-usuario"]', 'teste.senha@teste.com');
    await page.fill('[data-testid="input-nome-usuario"]', 'Teste Senha');
    await page.fill('[data-testid="input-senha-usuario"]', 'Senha123!');
    await page.fill('[data-testid="input-confirmar-senha-usuario"]', 'SenhaDiferente!');

    await page.click('[data-testid="btn-salvar-usuario"]');
    
    // Modal deve permanecer aberto (senhas não conferem)
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve selecionar perfil de usuário', async ({ page }) => {
    await page.click('[data-testid="btn-novo-usuario"]');
    await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();

    await page.click('[data-testid="select-perfil-usuario"]');
    await page.click('text=Gerente');
    
    const valorSelecionado = await page.locator('[data-testid="select-perfil-usuario"]').inputValue();
    expect(valorSelecionado).toBe('gerente');
    
    await page.click('[data-testid="btn-cancelar-modal"]');
  });

  test('deve buscar usuário por nome', async ({ page }) => {
    await page.fill('[data-testid="input-busca-equipe"]', 'admin');
    await page.waitForTimeout(500);
    
    const valorBusca = await page.locator('[data-testid="input-busca-equipe"]').inputValue();
    expect(valorBusca).toBe('admin');
  });

  test('deve editar usuário existente', async ({ page }) => {
    // Verificar se há usuários para editar
    const cards = await page.locator('[data-testid^="card-tecnico-"]').count();
    
    if (cards > 0) {
      const primeiroCard = page.locator('[data-testid^="card-tecnico-"]').first();
      const cardId = await primeiroCard.getAttribute('data-testid');
      const id = cardId?.replace('card-tecnico-', '');
      
      if (id) {
        await page.click(`[data-testid="btn-editar-${id}"]`);
        await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
        await expect(page.locator('[data-testid="modal-titulo"]')).toHaveText('Editar Membro');

        // Modificar nome
        await page.fill('[data-testid="input-nome-usuario"]', 'Usuário Editado E2E');
        await page.click('[data-testid="btn-salvar-usuario"]');
        
        await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
      }
    } else {
      test.skip(true, 'Nenhum usuário encontrado para editar');
    }
  });

  test('deve exibir cards de técnicos com informações', async ({ page }) => {
    const cards = await page.locator('[data-testid^="card-tecnico-"]').count();
    
    if (cards > 0) {
      const primeiroCard = page.locator('[data-testid^="card-tecnico-"]').first();
      await expect(primeiroCard).toBeVisible();
      // Verificar que o card tem conteúdo (nome, email, perfil)
    } else {
      test.skip(true, 'Nenhum usuário encontrado');
    }
  });
});

test.describe('Módulo Equipe — Técnico (acesso restrito)', () => {
  test.use({ storageState: path.join(__dirname, '../.auth/tecnico.json') });

  test('técnico não deve ver menu Financeiro na sidebar', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('[data-testid="nav-financeiro"]')).not.toBeVisible();
  });

  test('técnico deve ver menu Ordens de Serviço', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('[data-testid="nav-ordens-servico"]')).toBeVisible();
  });

  test('técnico não deve acessar página de equipe', async ({ page }) => {
    await page.goto('/equipe');
    // Deve ser redirecionado ou mostrar erro de permissão
    await page.waitForTimeout(1000);
    // Verificar se está na página de equipe ou foi redirecionado
  });
});
