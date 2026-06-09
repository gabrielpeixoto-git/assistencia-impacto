# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: portal.spec.ts >> Portal Público do Cliente >> portal é responsivo em mobile
- Location: specs\portal.spec.ts:32:7

# Error details

```
Error: Login falhou
```

# Test source

```ts
  1   | ﻿/**
  2   |  * Helper para criar/limpar dados de teste via API REST diretamente.
  3   |  * Usado nos beforeEach/afterEach dos testes para garantir estado limpo.
  4   |  */
  5   | 
  6   | const API_URL = process.env.API_URL || 'http://localhost:8000/api';
  7   | 
  8   | let adminToken: string | null = null;
  9   | 
  10  | async function getAdminToken(): Promise<string> {
  11  |   if (adminToken) return adminToken;
  12  | 
  13  |   const response = await fetch(`${API_URL}/auth/login`, {
  14  |     method: 'POST',
  15  |     headers: { 'Content-Type': 'application/json' },
  16  |     body: JSON.stringify({
  17  |       email: process.env.ADMIN_EMAIL || 'admin@assistenciaimpacto.com.br',
  18  |       senha: process.env.ADMIN_SENHA || 'Admin@123',
  19  |     }),
  20  |   });
  21  | 
  22  |   if (!response.ok) {
> 23  |     throw new Error('Login falhou');
      |           ^ Error: Login falhou
  24  |   }
  25  | 
  26  |   const data = await response.json();
  27  |   adminToken = data.access_token;
  28  |   return adminToken!;
  29  | }
  30  | 
  31  | async function apiPost<T>(endpoint: string, body: object): Promise<T> {
  32  |   const token = await getAdminToken();
  33  |   const response = await fetch(`${API_URL}${endpoint}`, {
  34  |     method: 'POST',
  35  |     headers: {
  36  |       'Content-Type': 'application/json',
  37  |       'Authorization': `Bearer ${token}`,
  38  |     },
  39  |     body: JSON.stringify(body),
  40  |   });
  41  | 
  42  |   if (!response.ok) {
  43  |     const text = await response.text();
  44  |     throw new Error(`POST ${endpoint} falhou: ${text}`);
  45  |   }
  46  | 
  47  |   return response.json();
  48  | }
  49  | 
  50  | async function apiGet<T>(endpoint: string): Promise<T> {
  51  |   const token = await getAdminToken();
  52  |   const response = await fetch(`${API_URL}${endpoint}`, {
  53  |     headers: { 'Authorization': `Bearer ${token}` },
  54  |   });
  55  | 
  56  |   if (!response.ok) {
  57  |     throw new Error(`GET ${endpoint} falhou`);
  58  |   }
  59  | 
  60  |   return response.json();
  61  | }
  62  | 
  63  | // ── Factories de dados para E2E ────────────────────────
  64  | 
  65  | export async function criarTransacao(overrides: Partial<{
  66  |   tipo: 'receita' | 'despesa';
  67  |   descricao: string;
  68  |   valor: number;
  69  |   status: string;
  70  | }> = {}) {
  71  |   // Busca ou cria categoria primeiro
  72  |   const categorias = await apiGet<any>('/financeiro/categorias');
  73  |   const categoria_id = categorias[0]?.id;
  74  | 
  75  |   return apiPost<any>('/financeiro/transacoes', {
  76  |     tipo: 'receita',
  77  |     descricao: 'Transação de teste E2E',
  78  |     valor: 150000, // R$ 1.500,00 em centavos
  79  |     status: 'pendente',
  80  |     data_vencimento: new Date(Date.now() + 30 * 86400000).toISOString(),
  81  |     categoria_id,
  82  |     ...overrides,
  83  |   });
  84  | }
  85  | 
  86  | export async function criarEvento(tecnico_id: string, overrides: Partial<{
  87  |   titulo: string;
  88  |   data_hora_inicio: string;
  89  |   data_hora_fim: string;
  90  |   tipo_evento: string;
  91  | }> = {}) {
  92  |   const amanha = new Date(Date.now() + 86400000);
  93  |   const inicio = new Date(amanha.setHours(10, 0, 0, 0)).toISOString();
  94  |   const fim = new Date(amanha.setHours(11, 0, 0, 0)).toISOString();
  95  | 
  96  |   return apiPost<any>('/agenda', {
  97  |     titulo: 'Evento de teste E2E',
  98  |     tecnico_id,
  99  |     data_hora_inicio: inicio,
  100 |     data_hora_fim: fim,
  101 |     tipo_evento: 'servico',
  102 |     ...overrides,
  103 |   });
  104 | }
  105 | 
  106 | export async function criarNotificacao(usuario_id: string) {
  107 |   return apiPost<any>('/notificacoes', {
  108 |     usuario_id,
  109 |     titulo: 'Notificação de teste E2E',
  110 |     corpo: 'Esta é uma notificação criada para teste automatizado.',
  111 |     tipo: 'info',
  112 |   });
  113 | }
  114 | 
  115 | export async function buscarUsuarioPorEmail(email: string) {
  116 |   const resultado = await apiGet<any>('/usuarios/');
  117 |   return resultado.find((u: any) => u.email === email);
  118 | }
  119 | 
  120 | export async function resetarDadosTeste() {
  121 |   // Limpa apenas dados criados pelos testes (marcados com tag e2e_test=true)
  122 |   // Implementar endpoint específico no backend se necessário
  123 |   adminToken = null; // Força novo login
```