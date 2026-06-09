import { test, expect } from '@playwright/test';
import { ClientesPage } from '../../pages/clientes.page';
import { DataFactory } from '../../helpers/data-factory';
import { LoginPage } from '../../pages/login.page';

test.describe('Clientes — CRUD Completo', () => {
  let clientesPage: ClientesPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginComSucesso({ email: process.env.ADMIN_EMAIL!, senha: process.env.ADMIN_SENHA! });
    clientesPage = new ClientesPage(page);
  });

  test('CLIENTES: criar novo cliente com sucesso', async ({ page }) => {
    await clientesPage.goto();
    await clientesPage.verificarCarregado();

    await clientesPage.clicarNovoCliente();

    const clienteData = DataFactory.gerarCliente();
    await clientesPage.preencherFormularioCliente(clienteData);
    await clientesPage.salvarCliente();

    // Esperar modal fechar
    await expect(clientesPage.modalNovoCliente).not.toBeVisible({ timeout: 10000 });

    await clientesPage.buscarCliente(clienteData.nome);
    await clientesPage.verificarClienteNaTabela(clienteData.nome);
  });

  test('CLIENTES: buscar cliente por nome', async ({ page }) => {
    await clientesPage.goto();
    await clientesPage.verificarCarregado();

    await clientesPage.buscarCliente('Teste');
    await expect(clientesPage.campoBusca).toHaveValue('Teste');
  });

  test('CLIENTES: editar cliente existente', async ({ page }) => {
    await clientesPage.goto();
    await clientesPage.verificarCarregado();

    // Criar cliente para editar
    await clientesPage.clicarNovoCliente();

    const clienteData = DataFactory.gerarCliente();
    await clientesPage.preencherFormularioCliente(clienteData);
    await clientesPage.salvarCliente();

    // Esperar modal fechar
    await expect(clientesPage.modalNovoCliente).not.toBeVisible({ timeout: 10000 });

    // Buscar cliente criado
    await clientesPage.buscarCliente(clienteData.nome);

    // Verificar que o cliente está na tabela antes de editar
    await clientesPage.verificarClienteNaTabela(clienteData.nome);

    // Editar cliente
    await clientesPage.clicarEditarCliente(clienteData.nome);

    const novoNome = 'Cliente Editado';
    await clientesPage.preencherFormularioCliente({ nome: novoNome });
    await clientesPage.salvarCliente();

    // Esperar modal fechar
    await expect(clientesPage.modalNovoCliente).not.toBeVisible({ timeout: 10000 });

    await clientesPage.buscarCliente(novoNome);
    await clientesPage.verificarClienteNaTabela(novoNome);
  });

  test('CLIENTES: excluir cliente', async ({ page }) => {
    await clientesPage.goto();
    await clientesPage.verificarCarregado();

    // Criar cliente para excluir
    await clientesPage.clicarNovoCliente();

    const clienteData = DataFactory.gerarCliente();
    await clientesPage.preencherFormularioCliente(clienteData);
    await clientesPage.salvarCliente();

    // Esperar modal fechar
    await expect(clientesPage.modalNovoCliente).not.toBeVisible({ timeout: 10000 });

    // Buscar cliente criado
    await clientesPage.buscarCliente(clienteData.nome);

    // Verificar que o cliente está na tabela antes de excluir
    await clientesPage.verificarClienteNaTabela(clienteData.nome);

    // Excluir cliente
    await clientesPage.clicarExcluirCliente(clienteData.nome);

    // Refresh da página para garantir que a tabela seja atualizada
    await page.reload();
    await clientesPage.verificarCarregado();

    // Verificar que o cliente não está mais na tabela
    await expect(page.locator(`text=${clienteData.nome}`)).not.toBeVisible();
  });
});
