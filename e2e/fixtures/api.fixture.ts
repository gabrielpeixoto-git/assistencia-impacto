import { test as base } from '@playwright/test';

type ApiFixtures = {
  apiToken: string;
  apiGet: (path: string, token?: string) => Promise<any>;
  apiPost: (path: string, body: object, token?: string) => Promise<any>;
  apiPatch: (path: string, body: object, token?: string) => Promise<any>;
  apiDelete: (path: string, token?: string) => Promise<any>;
  criarCliente: (dados?: Partial<any>) => Promise<any>;
  criarOrdemServico: (dados?: Partial<any>) => Promise<any>;
  criarOrcamento: (dados?: Partial<any>) => Promise<any>;
};

export const test = base.extend<ApiFixtures>({
  apiToken: async ({ request }, use) => {
    const resp = await request.post(`${process.env.API_URL}/auth/login`, {
      data: { email: process.env.ADMIN_EMAIL, senha: process.env.ADMIN_SENHA },
    });
    const json = await resp.json();
    await use(json.dados.access_token);
  },

  apiGet: async ({ request, apiToken }, use) => {
    const apiGet = async (path: string, token?: string) => {
      const resp = await request.get(`${process.env.API_URL}${path}`, {
        headers: { Authorization: `Bearer ${token || apiToken}` },
      });
      return resp.json();
    };
    await use(apiGet);
  },

  apiPost: async ({ request, apiToken }, use) => {
    const apiPost = async (path: string, body: object, token?: string) => {
      const resp = await request.post(`${process.env.API_URL}${path}`, {
        data: body,
        headers: { Authorization: `Bearer ${token || apiToken}` },
      });
      return resp.json();
    };
    await use(apiPost);
  },

  apiPatch: async ({ request, apiToken }, use) => {
    const apiPatch = async (path: string, body: object, token?: string) => {
      const resp = await request.patch(`${process.env.API_URL}${path}`, {
        data: body,
        headers: { Authorization: `Bearer ${token || apiToken}` },
      });
      return resp.json();
    };
    await use(apiPatch);
  },

  apiDelete: async ({ request, apiToken }, use) => {
    const apiDelete = async (path: string, token?: string) => {
      const resp = await request.delete(`${process.env.API_URL}${path}`, {
        headers: { Authorization: `Bearer ${token || apiToken}` },
      });
      return resp.json();
    };
    await use(apiDelete);
  },

  criarCliente: async ({ apiPost }, use) => {
    const criarCliente = (dados = {}) => apiPost('/clientes', {
      nome: 'Cliente Teste E2E',
      email: `teste.e2e.${Date.now()}@email.com`,
      telefone: '11999990000',
      tipo_cliente: 'residencial',
      tipo_documento: 'cpf',
      numero_documento: '12345678901',
      endereco: {
        logradouro: 'Rua de Teste', numero: '123',
        bairro: 'Centro', cidade: 'São Paulo', estado: 'SP', cep: '01001000',
      },
      ...dados,
    });
    await use(criarCliente);
  },

  criarOrdemServico: async ({ apiPost }, use) => {
    const criarOrdemServico = (dados = {}) => apiPost('/ordens-servico', {
      titulo: 'OS de Teste E2E',
      tipo_servico: 'eletrica',
      prioridade: 'normal',
      ...dados,
    });
    await use(criarOrdemServico);
  },

  criarOrcamento: async ({ apiPost }, use) => {
    const criarOrcamento = (dados = {}) => apiPost('/orcamentos', {
      titulo: 'Orçamento de Teste E2E',
      ...dados,
    });
    await use(criarOrcamento);
  },
});
