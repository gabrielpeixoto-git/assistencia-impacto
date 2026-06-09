# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: notificacoes.spec.ts >> Módulo Notificações - Dropdown e Leitura >> dropdown exibe lista de notificações
- Location: specs\notificacoes.spec.ts:53:7

# Error details

```
Error: Login falhou
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - generic [ref=e3]:
      - complementary [ref=e4]:
        - generic [ref=e5]:
          - generic [ref=e7]:
            - img [ref=e9]
            - heading "Assistência Impacto" [level=1] [ref=e12]
            - button [ref=e13] [cursor=pointer]:
              - img [ref=e14]
          - navigation [ref=e17]:
            - generic [ref=e18]:
              - paragraph [ref=e19]: VISÃO GERAL
              - link "Dashboard" [ref=e21] [cursor=pointer]:
                - /url: /
                - img [ref=e22]
                - generic [ref=e27]: Dashboard
            - generic [ref=e28]:
              - paragraph [ref=e29]: OPERAÇÕES
              - generic [ref=e30]:
                - link "Ordens de Serviço" [ref=e31] [cursor=pointer]:
                  - /url: /ordens-servico
                  - img [ref=e32]
                  - generic [ref=e35]: Ordens de Serviço
                - link "Orçamentos" [ref=e36] [cursor=pointer]:
                  - /url: /orcamentos
                  - img [ref=e37]
                  - generic [ref=e40]: Orçamentos
                - link "Agenda" [ref=e41] [cursor=pointer]:
                  - /url: /agenda
                  - img [ref=e42]
                  - generic [ref=e44]: Agenda
                - link "Clientes" [ref=e45] [cursor=pointer]:
                  - /url: /clientes
                  - img [ref=e46]
                  - generic [ref=e51]: Clientes
            - generic [ref=e52]:
              - paragraph [ref=e53]: FINANCEIRO
              - generic [ref=e54]:
                - link "Visão Financeira" [ref=e55] [cursor=pointer]:
                  - /url: /financeiro
                  - img [ref=e56]
                  - generic [ref=e58]: Visão Financeira
                - link "Transações" [ref=e59] [cursor=pointer]:
                  - /url: /transacoes
                  - img [ref=e60]
                  - generic [ref=e63]: Transações
            - generic [ref=e64]:
              - paragraph [ref=e65]: RECURSOS
              - generic [ref=e66]:
                - link "Estoque" [ref=e67] [cursor=pointer]:
                  - /url: /estoque
                  - img [ref=e68]
                  - generic [ref=e72]: Estoque
                - link "Equipe" [ref=e73] [cursor=pointer]:
                  - /url: /equipe
                  - img [ref=e74]
                  - generic [ref=e79]: Equipe
            - generic [ref=e80]:
              - paragraph [ref=e81]: ANÁLISE
              - link "Relatórios" [ref=e83] [cursor=pointer]:
                - /url: /relatorios
                - img [ref=e84]
                - generic [ref=e86]: Relatórios
            - generic [ref=e87]:
              - paragraph [ref=e88]: SISTEMA
              - link "Configurações" [ref=e90] [cursor=pointer]:
                - /url: /configuracoes
                - img [ref=e91]
                - generic [ref=e94]: Configurações
          - generic [ref=e95]:
            - generic [ref=e96]:
              - generic [ref=e98]: A
              - generic [ref=e99]:
                - paragraph [ref=e100]: Administrador
                - paragraph [ref=e101]: admin@assistenciaimpacto.com.br
            - button "Sair" [ref=e102] [cursor=pointer]:
              - img [ref=e103]
              - generic [ref=e106]: Sair
      - generic [ref=e107]:
        - banner [ref=e108]:
          - generic [ref=e110]:
            - img [ref=e111]
            - textbox "Buscar... (Cmd+K)" [ref=e114]
          - generic [ref=e115]:
            - button [ref=e117] [cursor=pointer]:
              - img [ref=e118]
            - button "Administrador" [ref=e123] [cursor=pointer]:
              - img [ref=e125]
              - generic [ref=e128]:
                - paragraph [ref=e129]: Administrador
                - img [ref=e130]
        - main [ref=e132]:
          - generic [ref=e134]:
            - generic [ref=e135]:
              - heading "Dashboard" [level=1] [ref=e136]
              - paragraph [ref=e137]: Visão geral do sistema
            - generic [ref=e138]:
              - generic [ref=e139]:
                - generic [ref=e140]:
                  - img [ref=e142]
                  - generic [ref=e145]:
                    - generic [ref=e146]: ↑
                    - generic [ref=e147]: 12%
                - generic [ref=e148]: "0"
                - generic [ref=e149]: OS Hoje
              - generic [ref=e150]:
                - generic [ref=e151]:
                  - img [ref=e153]
                  - generic [ref=e156]:
                    - generic [ref=e157]: ↑
                    - generic [ref=e158]: 8%
                - generic [ref=e159]: "0"
                - generic [ref=e160]: OS Semana
              - generic [ref=e161]:
                - generic [ref=e162]:
                  - img [ref=e164]
                  - generic [ref=e166]:
                    - generic [ref=e167]: ↑
                    - generic [ref=e168]: 15%
                - generic [ref=e169]: R$ 0,00
                - generic [ref=e170]: Receita Mensal
              - generic [ref=e171]:
                - generic [ref=e172]:
                  - img [ref=e174]
                  - generic [ref=e177]:
                    - generic [ref=e178]: ↑
                    - generic [ref=e179]: 10%
                - generic [ref=e180]: R$ 0,00
                - generic [ref=e181]: Lucro Mensal
            - generic [ref=e182]:
              - generic [ref=e183]:
                - img [ref=e186]
                - generic [ref=e190]: "0"
                - generic [ref=e191]: Clientes Ativos
              - generic [ref=e192]:
                - img [ref=e195]
                - generic [ref=e198]: "0"
                - generic [ref=e199]: Orçamentos Pendentes
              - generic [ref=e200]:
                - img [ref=e203]
                - generic [ref=e205]: "0"
                - generic [ref=e206]: Pagamentos Atrasados
              - generic [ref=e207]:
                - img [ref=e210]
                - generic [ref=e214]: "0"
                - generic [ref=e215]: Estoque Crítico
            - generic [ref=e216]:
              - heading "Receita Últimos 7 Dias" [level=2] [ref=e217]
              - img [ref=e220]:
                - generic [ref=e225]:
                  - generic [ref=e227]: 01/06
                  - generic [ref=e229]: 02/06
                  - generic [ref=e231]: 03/06
                  - generic [ref=e233]: 04/06
                - generic [ref=e235]:
                  - generic [ref=e237]: R$ 0
                  - generic [ref=e239]: R$ 1
                  - generic [ref=e241]: R$ 2
                  - generic [ref=e243]: R$ 3
                  - generic [ref=e245]: R$ 4
            - generic [ref=e246]:
              - heading "Ordens de Serviço por Status" [level=2] [ref=e247]
              - paragraph [ref=e248]: Sem dados disponíveis
            - generic [ref=e249]:
              - heading "Ordens de Serviço Recentes" [level=2] [ref=e250]
              - generic [ref=e251]: Nenhum registro encontrado
            - generic [ref=e252]:
              - heading "Agenda - Próximos Dias" [level=2] [ref=e253]
              - paragraph [ref=e254]: Nenhum evento agendado para os próximos dias
            - generic [ref=e255]:
              - heading "Top Clientes" [level=2] [ref=e256]
              - paragraph [ref=e257]: Nenhum cliente encontrado
    - region "Notifications alt+T"
  - generic [ref=e258]: R$ 0
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