import { test, expect } from '@playwright/test';
import { EquipePage } from '../../e2e/pages/equipe.page';

test.describe('Equipe', () => {
  let equipePage: EquipePage;

  test.beforeEach(async ({ page }) => {
    equipePage = new EquipePage(page);
    await equipePage.abrirPagina();
  });

  test('deve exibir página de equipe', async () => {
    await expect(equipePage.cardTabelaMembros).toBeVisible();
  });

  test('deve abrir modal de novo membro', async () => {
    await equipePage.clicarNovoMembro();
    await equipePage.verificarModalAberto();
    await expect(equipePage.modalTitulo).toContainText('Novo Membro');
  });

  test('deve fechar modal ao clicar em cancelar', async () => {
    await equipePage.clicarNovoMembro();
    await equipePage.verificarModalAberto();
    await equipePage.cancelarModal();
    await equipePage.verificarModalFechado();
  });

  test('deve preencher filtro de busca', async () => {
    await equipePage.preencherFiltroBusca('joão');
    await expect(equipePage.inputBuscaEquipe).toHaveValue('joão');
  });

  test('deve selecionar filtro de cargo', async () => {
    await equipePage.selecionarCargoFiltro('tecnico');
    await expect(equipePage.selectCargoEquipe).toHaveValue('tecnico');
  });

  test('deve selecionar filtro de status', async () => {
    await equipePage.selecionarStatusFiltro('ativo');
    await expect(equipePage.selectStatusEquipe).toHaveValue('ativo');
  });

  test('deve preencher modal de membro', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'novo.membro@exemplo.com',
      nome: 'Novo Membro E2E',
      perfil: 'tecnico',
      telefone: '11999999999',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await expect(equipePage.inputEmailModal).toHaveValue('novo.membro@exemplo.com');
  });

  test('deve criar membro sem telefone', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'sem.telefone@exemplo.com',
      nome: 'Membro Sem Telefone',
      perfil: 'assistente',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await expect(equipePage.inputNomeModal).toHaveValue('Membro Sem Telefone');
  });

  test('deve salvar membro', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'membro.salvar@exemplo.com',
      nome: 'Membro Para Salvar',
      perfil: 'gerente',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await equipePage.salvarMembro();
    await equipePage.verificarModalFechado();
  });

  test('deve criar técnico', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'tecnico.novo@exemplo.com',
      nome: 'Técnico Novo',
      perfil: 'tecnico',
      telefone: '11888888888',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await expect(equipePage.selectPerfilModal).toHaveValue('tecnico');
  });

  test('deve criar gerente', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'gerente.novo@exemplo.com',
      nome: 'Gerente Novo',
      perfil: 'gerente',
      telefone: '11777777777',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await expect(equipePage.selectPerfilModal).toHaveValue('gerente');
  });

  test('deve criar administrador', async () => {
    await equipePage.clicarNovoMembro();
    
    await equipePage.preencherModalMembro({
      email: 'admin.novo@exemplo.com',
      nome: 'Admin Novo',
      perfil: 'admin',
      telefone: '11666666666',
      senha: 'Senha123!',
      confirmarSenha: 'Senha123!'
    });
    
    await expect(equipePage.selectPerfilModal).toHaveValue('admin');
  });
});
