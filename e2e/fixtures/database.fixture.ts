import { test as base } from '@playwright/test';

type DbFixtures = {
  limparDadosTeste: () => Promise<void>;
  seedDadosMinimos: () => Promise<{ clienteId: string; osId: string; orcamentoId: string }>;
};

export const test = base.extend<DbFixtures>({
  limparDadosTeste: async ({ request, apiToken }, use) => {
    const idsParaDeletar: Array<{ endpoint: string; id: string }> = [];
    // Registrar IDs criados durante o teste para deletar depois
    await use(async () => {
      for (const item of idsParaDeletar.reverse()) {
        await request.delete(`${process.env.API_URL}${item.endpoint}/${item.id}`, {
          headers: { Authorization: `Bearer ${apiToken}` },
        });
      }
    });
  },

  seedDadosMinimos: async ({ apiPost }, use) => {
    const seedDadosMinimos = async () => {
      const clienteResp = await apiPost('/clientes', {
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
      });
      const osResp = await apiPost('/ordens-servico', {
        cliente_id: clienteResp.dados.id,
        titulo: 'OS de Teste E2E',
        tipo_servico: 'eletrica',
        prioridade: 'normal',
      });
      const orcResp = await apiPost('/orcamentos', {
        cliente_id: clienteResp.dados.id,
        titulo: 'Orçamento de Teste E2E',
      });
      return { clienteId: clienteResp.dados.id, osId: osResp.dados.id, orcamentoId: orcResp.dados.id };
    };
    await use(seedDadosMinimos);
  },
});
