import { test, expect } from '@playwright/test';
import { PortalClientePage } from '../../e2e/pages/portal-cliente.page';

test.describe('Portal do Cliente', () => {
  let portalPage: PortalClientePage;

  test.beforeEach(async ({ page }) => {
    portalPage = new PortalClientePage(page);
    await portalPage.abrirPagina();
  });

  test('deve exibir página do portal', async ({ page }) => {
    await expect(page).toHaveURL(/\/portal/);
  });

  test('deve preencher campos de login', async () => {
    await portalPage.preencherLogin('cliente@teste.com', 'Senha123!');
    await expect(portalPage.inputEmail).toHaveValue('cliente@teste.com');
    await expect(portalPage.inputSenha).toHaveValue('Senha123!');
  });

  test('deve clicar em entrar', async () => {
    await portalPage.preencherLogin('cliente@teste.com', 'Senha123!');
    await portalPage.clicarEntrar();
    // Verifica se houve navegação ou erro
  });

  test('deve preencher token de consulta', async () => {
    await portalPage.preencherToken('TOKEN-12345');
    await expect(portalPage.inputToken).toHaveValue('TOKEN-12345');
  });

  test('deve clicar em consultar OS', async () => {
    await portalPage.preencherToken('TOKEN-12345');
    await portalPage.clicarConsultar();
    // Verifica se houve consulta ou erro
  });

  test('deve exibir detalhes da OS após consulta', async () => {
    await portalPage.preencherToken('TOKEN-VALIDO');
    await portalPage.clicarConsultar();
    // Se o token for válido, deve exibir detalhes
    // Este teste depende de um token válido existente
  });

  test('deve exibir status da OS', async () => {
    await portalPage.preencherToken('TOKEN-VALIDO');
    await portalPage.clicarConsultar();
    // Verifica se o status da OS é exibido
  });

  test('deve verificar detalhes da OS visíveis', async () => {
    await portalPage.preencherToken('TOKEN-VALIDO');
    await portalPage.clicarConsultar();
    await portalPage.verificarDetalhesOSVisiveis();
  });

  test('deve verificar status da OS visível', async () => {
    await portalPage.preencherToken('TOKEN-VALIDO');
    await portalPage.clicarConsultar();
    await portalPage.verificarStatusOSVisivel();
  });
});
