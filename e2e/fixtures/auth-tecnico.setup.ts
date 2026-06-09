import { test as setup, expect } from '@playwright/test';

setup('autenticar como técnico', async ({ page }) => {
  await page.goto(process.env.BASE_URL + '/login');
  
  // Preencher campos
  await page.getByTestId('login-email').fill(process.env.TECNICO_EMAIL!);
  await page.getByTestId('login-senha').fill(process.env.TECNICO_SENHA!);
  
  console.log('Email:', process.env.TECNICO_EMAIL);
  console.log('Senha preenchida');
  
  // Clicar no botão
  const botao = page.getByTestId('login-botao-entrar');
  await botao.click();
  console.log('Botão clicado');
  
  // Aguardar um pouco
  await page.waitForTimeout(3000);
  
  // Verificar URL atual
  const currentUrl = page.url();
  console.log('URL atual:', currentUrl);
  
  // Verificar se há erro de login
  const errorElement = page.locator('[data-testid="login-error"]');
  const isErrorVisible = await errorElement.isVisible().catch(() => false);
  if (isErrorVisible) {
    const errorText = await errorElement.textContent();
    console.log('Erro de login:', errorText);
  }
  
  await expect(page).toHaveURL(/.*\/$/, { timeout: 15000 });
  await page.context().storageState({ path: 'fixtures/.auth/tecnico.json' });
});
