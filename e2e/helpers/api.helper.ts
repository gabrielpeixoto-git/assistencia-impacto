/**
 * Helper para criar/limpar dados de teste via API REST diretamente.
 * Usado nos beforeEach/afterEach dos testes para garantir estado limpo.
 */

const API_URL = process.env.API_URL || 'http://localhost:8000/api';

let adminToken: string | null = null;

async function getAdminToken(): Promise<string> {
  if (adminToken) return adminToken;

  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br',
      senha: process.env.ADMIN_SENHA || 'Admin@123',
    }),
  });

  if (!response.ok) {
    throw new Error('Login falhou');
  }

  const data = await response.json();
  adminToken = data.access_token;
  return adminToken!;
}

async function apiPost<T>(endpoint: string, body: object): Promise<T> {
  const token = await getAdminToken();
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`POST ${endpoint} falhou: ${text}`);
  }

  return response.json();
}

async function apiGet<T>(endpoint: string): Promise<T> {
  const token = await getAdminToken();
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error(`GET ${endpoint} falhou`);
  }

  return response.json();
}

// ── Factories de dados para E2E ────────────────────────

export async function criarTransacao(overrides: Partial<{
  tipo: 'receita' | 'despesa';
  descricao: string;
  valor: number;
  status: string;
}> = {}) {
  // Busca ou cria categoria primeiro
  const categorias = await apiGet<any>('/financeiro/categorias');
  const categoria_id = categorias[0]?.id;

  return apiPost<any>('/financeiro/transacoes', {
    tipo: 'receita',
    descricao: 'Transação de teste E2E',
    valor: 150000, // R$ 1.500,00 em centavos
    status: 'pendente',
    data_vencimento: new Date(Date.now() + 30 * 86400000).toISOString(),
    categoria_id,
    ...overrides,
  });
}

export async function criarEvento(tecnico_id: string, overrides: Partial<{
  titulo: string;
  data_hora_inicio: string;
  data_hora_fim: string;
  tipo_evento: string;
}> = {}) {
  const amanha = new Date(Date.now() + 86400000);
  const inicio = new Date(amanha.setHours(10, 0, 0, 0)).toISOString();
  const fim = new Date(amanha.setHours(11, 0, 0, 0)).toISOString();

  return apiPost<any>('/agenda', {
    titulo: 'Evento de teste E2E',
    tecnico_id,
    data_hora_inicio: inicio,
    data_hora_fim: fim,
    tipo_evento: 'servico',
    ...overrides,
  });
}

export async function criarNotificacao(usuario_id: string) {
  return apiPost<any>('/notificacoes', {
    usuario_id,
    titulo: 'Notificação de teste E2E',
    corpo: 'Esta é uma notificação criada para teste automatizado.',
    tipo: 'info',
  });
}

export async function buscarUsuarioPorEmail(email: string) {
  const resultado = await apiGet<any>('/usuarios/');
  return resultado.find((u: any) => u.email === email);
}

export async function resetarDadosTeste() {
  // Limpa apenas dados criados pelos testes (marcados com tag e2e_test=true)
  // Implementar endpoint específico no backend se necessário
  adminToken = null; // Força novo login
}

export { apiPost, apiGet, getAdminToken };
