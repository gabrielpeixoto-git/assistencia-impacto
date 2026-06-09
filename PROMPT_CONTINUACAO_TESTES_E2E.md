# PROMPT DE CONTINUAÇÃO — TESTES E2E MÓDULOS CRÍTICOS
## Assistência Impacto — Fase de Qualidade

> Cole este prompt no Windsurf em modo Plan para continuar o projeto a partir dos testes E2E.

---

```
Você é um engenheiro de software sênior full-stack, especialista em qualidade de software,
testes automatizados e arquitetura de sistemas. Você está continuando o desenvolvimento do
sistema "Assistência Impacto" — um sistema web de gestão para empresa de manutenção
residencial e comercial.

O sistema já foi construído nas Fases 1 a 5 conforme o prompt original. Agora você vai
implementar a Fase de Qualidade: testes E2E completos para os 5 módulos críticos que ainda
não têm cobertura.

═══════════════════════════════════════════════════════
CONTEXTO DO PROJETO EXISTENTE
═══════════════════════════════════════════════════════

Stack já implementada:
- Backend: FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + Celery
- Frontend: React 18 + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query
- Infra: Docker Compose (banco, redis, backend, worker, frontend, nginx)
- Auth: JWT com refresh token, RBAC (admin, gerente, tecnico, visualizador)

Módulos já existentes (com testes básicos):
✅ Autenticação (login, logout, refresh, permissões)
✅ Dashboard (carregamento de KPIs, gráficos)
✅ Clientes (CRUD completo)
✅ Ordens de Serviço (Kanban, CRUD, fotos, checklist, assinatura)
✅ Orçamentos (construtor, PDF, aprovação pública)
✅ Estoque (CRUD, movimentações, alertas)

Módulos SEM cobertura E2E (objetivo desta fase):
❌ Financeiro
❌ Agenda
❌ Equipe
❌ Notificações
❌ Portal Público do Cliente

═══════════════════════════════════════════════════════
STACK DE TESTES — USE EXATAMENTE ESTA
═══════════════════════════════════════════════════════

TESTES E2E (Frontend + Integração):
- Playwright (framework principal de E2E)
  * @playwright/test (runner nativo)
  * playwright-testing-library (queries semânticas)
  * @faker-js/faker (dados de teste dinâmicos)
  * Modo: Chromium (principal) + Firefox (smoke)

TESTES DE INTEGRAÇÃO (Backend):
- pytest + pytest-asyncio (testes assíncronos)
- httpx (cliente HTTP nos testes de API)
- pytest-postgresql (banco isolado por teste)
- factory-boy (factories de dados de teste)
- faker (dados falsos em português)
- freezegun (controle de data/hora nos testes)

BANCO DE TESTES:
- PostgreSQL separado (test_assistencia_impacto)
- Redis separado (DB 1, não DB 0)
- Fixtures com rollback automático por teste
- Seeds mínimos: admin + 1 técnico + dados base por módulo

COBERTURA:
- Backend: pytest-cov (meta: 85%+ nos módulos testados)
- Frontend: Playwright coverage (meta: fluxos críticos 100%)

═══════════════════════════════════════════════════════
ESTRUTURA DE ARQUIVOS A CRIAR
═══════════════════════════════════════════════════════

assistencia-impacto/
├── backend/
│   └── tests/
│       ├── conftest.py                    # já existe — ATUALIZAR
│       ├── factories/
│       │   ├── __init__.py
│       │   ├── financeiro_factory.py      # CRIAR
│       │   ├── agenda_factory.py          # CRIAR
│       │   └── equipe_factory.py          # CRIAR
│       ├── integration/
│       │   ├── test_financeiro.py         # CRIAR — testes de integração
│       │   ├── test_agenda.py             # CRIAR
│       │   ├── test_equipe.py             # CRIAR
│       │   └── test_notificacoes.py       # CRIAR
│       └── unit/
│           ├── test_financeiro_service.py # CRIAR — testes unitários de serviço
│           ├── test_agenda_service.py     # CRIAR
│           └── test_notificacao_service.py# CRIAR
│
├── e2e/
│   ├── playwright.config.ts               # CRIAR
│   ├── fixtures/
│   │   ├── auth.fixture.ts                # já existe — ATUALIZAR
│   │   ├── financeiro.fixture.ts          # CRIAR
│   │   ├── agenda.fixture.ts              # CRIAR
│   │   ├── equipe.fixture.ts              # CRIAR
│   │   ├── notificacoes.fixture.ts        # CRIAR
│   │   └── portal.fixture.ts              # CRIAR
│   ├── pages/                             # Page Object Models
│   │   ├── FinanceiroPage.ts              # CRIAR
│   │   ├── AgendaPage.ts                  # CRIAR
│   │   ├── EquipePage.ts                  # CRIAR
│   │   ├── NotificacoesPage.ts            # CRIAR
│   │   └── PortalClientePage.ts           # CRIAR
│   └── specs/
│       ├── financeiro/
│       │   ├── visao-geral.spec.ts        # CRIAR
│       │   ├── transacoes.spec.ts         # CRIAR
│       │   ├── contas-receber.spec.ts     # CRIAR
│       │   └── contas-pagar.spec.ts       # CRIAR
│       ├── agenda/
│       │   ├── calendario.spec.ts         # CRIAR
│       │   ├── agendamento.spec.ts        # CRIAR
│       │   ├── conflitos.spec.ts          # CRIAR
│       │   └── mapa-rotas.spec.ts         # CRIAR
│       ├── equipe/
│       │   ├── listagem-tecnicos.spec.ts  # CRIAR
│       │   ├── desempenho.spec.ts         # CRIAR
│       │   └── gestao-usuarios.spec.ts    # CRIAR
│       ├── notificacoes/
│       │   ├── tempo-real.spec.ts         # CRIAR
│       │   ├── leitura.spec.ts            # CRIAR
│       │   └── triggers.spec.ts           # CRIAR
│       └── portal/
│           ├── aprovacao-orcamento.spec.ts# CRIAR
│           ├── rastreamento-os.spec.ts    # CRIAR
│           └── avaliacao.spec.ts          # CRIAR

═══════════════════════════════════════════════════════
MÓDULO 1: TESTES E2E — FINANCEIRO (CRÍTICO)
═══════════════════════════════════════════════════════

CONTEXTO DE DOMÍNIO:
O módulo financeiro controla receitas, despesas, fluxo de caixa, contas a receber e pagar.
Erros aqui causam impacto direto no negócio (dinheiro). Cobertura máxima obrigatória.

CENÁRIOS DE TESTE — visao-geral.spec.ts:
1. Dashboard financeiro carrega com KPIs corretos
   - Receita do mês corresponde à soma das transações do período
   - Despesas do mês calculadas corretamente
   - Lucro = Receita - Despesas (validar cálculo)
   - Margem de lucro em percentual correta
2. Seletor de período funciona corretamente
   - Semana: filtrar apenas a semana atual
   - Mês: filtrar mês atual (padrão)
   - Trimestre: últimos 3 meses
   - Ano: ano fiscal atual
   - Período personalizado: seletor de data de/até
3. Gráficos renderizam sem erros com dados reais
   - Recharts não lança erro de console
   - Tooltips mostram valores formatados em R$ X.XXX,XX
4. Alertas de pagamentos atrasados aparecem quando há atrasos
5. Exportação de dados: botão CSV gera arquivo válido

CENÁRIOS — transacoes.spec.ts:
1. CRUD completo de transação de receita:
   - Criar receita vinculada a uma OS existente
   - Verificar que o total do dashboard atualiza imediatamente
   - Editar valor e categoria
   - Soft delete com confirmação
2. CRUD completo de transação de despesa:
   - Criar despesa com upload de comprovante (PDF ou imagem)
   - Verificar validação: valor não pode ser negativo
   - Verificar formatação automática R$ no campo de valor
3. Marcar pagamento como pago:
   - Transação pendente → clicar "Marcar como Pago"
   - Modal de confirmação com data de pagamento (default hoje)
   - Verificar que status muda e KPI atualiza
4. Filtros da tabela de transações:
   - Filtrar por tipo (receita/despesa)
   - Filtrar por status (pendente/pago/atrasado)
   - Filtrar por categoria
   - Filtrar por período de/até
   - Combinar múltiplos filtros
5. Paginação funciona corretamente (20 itens por página padrão)

CENÁRIOS — contas-receber.spec.ts:
1. Lista contas a receber com prazo correto
2. Destaque visual em contas vencidas (cor vermelha/badge "Atrasado")
3. Botão "Enviar Lembrete WhatsApp" dispara tarefa Celery
   - Verificar que endpoint POST /api/whatsapp/lembrete-pagamento é chamado
   - Toast de confirmação aparece
4. Ordenação por data de vencimento (mais antigas primeiro)
5. Filtro por cliente específico

CENÁRIOS — contas-pagar.spec.ts:
1. Lista contas a pagar ordenada por vencimento
2. Criar nova despesa recorrente (mensal)
3. Verificar que despesa recorrente aparece nos próximos meses
4. Exportar relatório de contas a pagar (CSV/Excel)

TESTES DE INTEGRAÇÃO BACKEND — test_financeiro.py:
```python
# Testar todos estes cenários via HTTP:
# POST /api/financeiro/transacoes → criar receita vinculada a OS
# GET /api/financeiro/resumo?periodo=mes → validar cálculo correto
# PATCH /api/financeiro/transacoes/{id}/pagar → marcar como pago
# GET /api/financeiro/atrasados → retornar apenas atrasados
# GET /api/financeiro/fluxo-caixa?meses=3 → dados mensais corretos
# GET /api/financeiro/exportar?formato=csv → CSV válido gerado
# Testar RBAC: visualizador não pode criar/editar transações
# Testar isolamento: técnico só vê transações das suas OS
```

═══════════════════════════════════════════════════════
MÓDULO 2: TESTES E2E — AGENDA (CRÍTICO)
═══════════════════════════════════════════════════════

CONTEXTO DE DOMÍNIO:
A agenda é o hub operacional diário. Técnicos dependem dela para saber onde estar.
Conflitos de horário causam falhas no serviço ao cliente. Zero tolerância a bugs.

CENÁRIOS — calendario.spec.ts:
1. Calendário carrega na visão Semana por padrão
2. Navegar entre visões: Dia / Semana / Mês / Agenda
3. Eventos aparecem com a cor correta do técnico
4. Clicar em evento abre painel lateral com detalhes completos
5. Eventos de OS aparecem com número da OS no título
6. Filtrar por técnico: selecionar "João Silva" → mostrar apenas eventos dele
7. Filtrar por "Todos os técnicos" → mostrar todos com cores diferentes

CENÁRIOS — agendamento.spec.ts:
1. Criar novo agendamento clicando em slot vazio do calendário
   - Formulário pré-preenche data/hora do slot clicado
   - Selecionar técnico, cliente e tipo de evento
   - Salvar → evento aparece no calendário imediatamente
2. Criar agendamento vinculado a uma OS existente
   - Busca autocomplete de OS no formulário
   - Ao vincular, título da OS preenche automaticamente
3. Editar agendamento existente:
   - Clicar no evento → painel lateral → botão Editar
   - Alterar hora de fim → salvar → calendário atualiza
4. Arrastar evento para reagendar (drag & drop):
   - Arrastar de terça para quarta
   - Verificar que data/hora atualiza via API
   - Verificar toast de confirmação
5. Deletar agendamento com confirmação

CENÁRIOS — conflitos.spec.ts:
1. Detectar conflito ao criar agendamento sobreposto:
   - Técnico A tem compromisso das 14h às 16h
   - Criar novo para técnico A das 15h às 17h
   - Sistema exibe alerta visual de conflito (não bloqueia, apenas avisa)
2. Verificar endpoint GET /api/agenda/disponibilidade retorna conflitos corretamente
3. Badge de conflito no card do evento quando há sobreposição

CENÁRIOS — mapa-rotas.spec.ts:
1. Aba de Mapa carrega com marcadores dos eventos do dia
2. Marcadores mostram número de sequência (1, 2, 3...)
3. Botão "Otimizar Rota" reordena os marcadores por distância
4. Clicar em marcador mostra popup com info do agendamento
5. Localização atual do técnico aparece como marcador especial (se geolocation permitido)

TESTES INTEGRAÇÃO — test_agenda.py:
```python
# POST /api/agenda → criar evento e verificar no banco
# GET /api/agenda/tecnico/{id} → retornar apenas eventos do técnico
# GET /api/agenda/disponibilidade?tecnico_id&inicio&fim → verificar conflito
# PATCH /api/agenda/{id} → atualizar data hora (simular drag & drop)
# DELETE /api/agenda/{id} → soft delete
# GET /api/agenda/mapa → retornar coordenadas dos eventos do dia
# Testar RBAC: técnico só altera próprios agendamentos
# Testar: evento vinculado a OS atualiza status da OS ao concluir
```

═══════════════════════════════════════════════════════
MÓDULO 3: TESTES E2E — EQUIPE (CRÍTICO)
═══════════════════════════════════════════════════════

CONTEXTO DE DOMÍNIO:
Gestão de usuários e técnicos. Permissões erradas são falhas de segurança.
Métricas de desempenho alimentam decisões de gestão.

CENÁRIOS — listagem-tecnicos.spec.ts:
1. Página carrega com cards de todos os técnicos
2. Card mostra: avatar/iniciais, nome, badge de perfil, status (disponível/ocupado/offline)
3. Métricas do card: OS este mês, avaliação média (estrelas), receita gerada
4. Status "ocupado" aparece quando técnico tem OS em_andamento no momento
5. Busca por nome filtra os cards em tempo real (debounce 300ms)

CENÁRIOS — desempenho.spec.ts:
1. Clicar em técnico abre página de detalhe
2. Gráfico de OS por mês (últimos 6 meses) renderiza corretamente
3. Métricas de eficiência: tempo médio de conclusão de OS
4. Histórico de OS atribuídas com paginação
5. Visão da agenda semanal do técnico embutida na página
6. Botão "Ver Agenda Completa" navega para Agenda filtrada pelo técnico

CENÁRIOS — gestao-usuarios.spec.ts:
1. RBAC: apenas admin vê botão "Gerenciar Usuários"
2. Criar novo usuário técnico:
   - Preencher nome, e-mail, senha, perfil=tecnico
   - Salvar → usuário aparece na lista
   - Login com novo usuário funciona
3. Editar perfil de usuário (gerente → técnico)
4. Resetar senha de usuário: admin define nova senha
5. Desativar usuário: usuário desativado não consegue fazer login
   - Tentar login → retorna 401 com mensagem "Conta desativada"
6. Proteção de tela: visualizador tenta acessar /equipe/gestao → redirect 403

TESTES INTEGRAÇÃO — test_equipe.py:
```python
# GET /api/equipe → listar técnicos com métricas
# GET /api/equipe/{id}/desempenho → estatísticas corretas por período
# POST /api/usuarios → criar usuário (apenas admin)
# PATCH /api/usuarios/{id} → atualizar perfil
# PATCH /api/usuarios/{id}/desativar → soft delete
# POST /api/auth/login com usuário desativado → 401
# Testar RBAC completo: gerente não acessa POST/PATCH de usuários
# Testar: técnico acessa apenas seus próprios dados de desempenho
```

═══════════════════════════════════════════════════════
MÓDULO 4: TESTES E2E — NOTIFICAÇÕES (IMPORTANTE)
═══════════════════════════════════════════════════════

CONTEXTO DE DOMÍNIO:
Notificações em tempo real são o canal de comunicação interno.
WebSocket deve ser confiável; notificações não lidas impactam UX.

CENÁRIOS — tempo-real.spec.ts:
1. Conexão WebSocket estabelecida ao fazer login
   - Verificar que /ws/notificacoes conecta com sucesso
   - Badge no sino mostra "0" inicialmente
2. Receber notificação em tempo real:
   - Usuário A (admin) cria uma OS e atribui para técnico B
   - Página do técnico B recebe notificação instantânea (usar 2 contextos Playwright)
   - Badge do sino atualiza de "0" para "1"
   - Toast aparece com título da notificação
3. Reconexão automática após queda de rede:
   - Simular queda de conexão (page.route para bloquear WS)
   - Verificar que tenta reconectar em até 5 segundos
4. Múltiplas notificações: badge mostra "99+" quando há mais de 99

CENÁRIOS — leitura.spec.ts:
1. Clicar no sino abre dropdown com lista de notificações
2. Notificações não lidas destacadas visualmente (fundo diferente)
3. Clicar em notificação individual → marcar como lida + navegar para entidade relacionada
   - Notificação de OS → navega para /ordens-servico/{id}
   - Notificação de orçamento → navega para /orcamentos/{id}
4. Botão "Marcar todas como lidas" funciona e badge zera
5. Página completa /notificacoes com paginação
6. Filtro por tipo: info / sucesso / aviso / erro / lembrete

CENÁRIOS — triggers.spec.ts:
1. OS atribuída para técnico gera notificação para o técnico
2. Orçamento aprovado pelo cliente gera notificação para o criador do orçamento
3. Estoque abaixo do mínimo gera notificação para admin e gerente
4. Job de verificação de pagamentos atrasados (simular com freezegun):
   - Criar transação com vencimento ontem
   - Executar a tarefa Celery manualmente via API de teste
   - Verificar que notificação de atraso foi criada
5. Notificação de OS concluída envia WhatsApp (mock da Evolution API)

TESTES INTEGRAÇÃO — test_notificacoes.py:
```python
# GET /api/notificacoes → lista paginada do usuário
# PATCH /api/notificacoes/{id}/ler → marcar como lida
# PATCH /api/notificacoes/ler-todas → marcar todas
# Testar isolamento: usuário A não vê notificações do usuário B
# Testar criação automática ao mudar status de OS
# Testar job Celery de pagamentos atrasados (com mock de data)
# WebSocket: conectar, enviar notificação via serviço, verificar recebimento
```

═══════════════════════════════════════════════════════
MÓDULO 5: TESTES E2E — PORTAL PÚBLICO DO CLIENTE
═══════════════════════════════════════════════════════

CONTEXTO DE DOMÍNIO:
O portal é a face pública do sistema. Clientes acessam sem login.
Segurança de token é crítica (tokens não devem ser adivinháveis ou reusáveis).

CENÁRIOS — aprovacao-orcamento.spec.ts:
1. Acessar /portal/orcamento/{token_valido} → exibe orçamento completo
   - Logo e nome da empresa visíveis
   - Nome do cliente, data, validade exibidos
   - Tabela de itens com quantidades e valores
   - Total em destaque (formato R$ X.XXX,XX)
2. Clicar "Aprovar Orçamento":
   - Animação de sucesso (confetti ou checkmark animado)
   - Status do orçamento muda para "aprovado" no backend
   - Notificação criada para o admin/criador do orçamento
   - Botão de aprovação desaparece (não pode aprovar duas vezes)
3. Clicar "Solicitar Alterações":
   - Modal com textarea para mensagem
   - Enviar → status muda para histórico interno de comentários
4. Token expirado: acessar com token antigo → página de "Orçamento expirado"
5. Token inválido: UUID inexistente → 404 com página amigável
6. Orçamento já aprovado: botão de aprovar não aparece, exibe "✅ Aprovado em DD/MM/AAAA"

CENÁRIOS — rastreamento-os.spec.ts:
1. Acessar /portal/os/{token_valido} → página de rastreamento
   - Progresso visual por etapas: Recebida → Confirmada → Em Andamento → Concluída
   - Etapa atual destacada com animação
2. Informações exibidas: número OS, data, endereço, técnico (nome), descrição
3. Status em tempo real: quando técnico muda status de "confirmada" para "em_andamento",
   página do portal atualiza automaticamente (polling a cada 30s ou WebSocket público)
4. Galeria de fotos "depois" visível quando OS concluída
5. Token inválido/expirado → página amigável com contato da empresa

CENÁRIOS — avaliacao.spec.ts:
1. OS concluída exibe seção de avaliação
2. Selecionar nota de 1 a 5 estrelas (interação visual)
3. Campo de comentário opcional
4. Submeter avaliação → feedback de sucesso
5. Não pode avaliar duas vezes: seção de avaliação desaparece após submit
6. Avaliação salva atualiza campo "avaliacao" do cliente no banco

TESTES INTEGRAÇÃO — test_portal.py:
```python
# GET /api/portal/orcamento/{token} → sem autenticação
# PATCH /api/portal/orcamento/{token}/aprovar → sem autenticação
# GET /api/portal/os/{token} → sem autenticação
# POST /api/portal/os/{token}/avaliar → sem autenticação
# Testar: token expirado retorna 410 Gone
# Testar: token inválido retorna 404
# Testar: aprovar duas vezes retorna 409 Conflict
# Testar: CORS permite acesso de qualquer origem (portal é público)
# Testar: dados sensíveis NÃO aparecem (ex: observações_internas, custo)
```

═══════════════════════════════════════════════════════
CONFIGURAÇÃO DO PLAYWRIGHT
═══════════════════════════════════════════════════════

Criar e2e/playwright.config.ts com:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  fullyParallel: false,  // serializado para evitar conflitos no banco de teste
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
  },
  projects: [
    // Setup: criar dados de teste
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    // Testes autenticados (admin)
    {
      name: 'admin-chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    // Testes autenticados (técnico)
    {
      name: 'tecnico-chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/tecnico.json',
      },
      dependencies: ['setup'],
    },
    // Portal público (sem autenticação)
    {
      name: 'portal-chromium',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /portal\/.*/,
      dependencies: ['setup'],
    },
    // Smoke test em Firefox (apenas cenários críticos)
    {
      name: 'firefox-smoke',
      use: { ...devices['Desktop Firefox'] },
      testMatch: /.*\.smoke\.ts/,
    },
  ],
  webServer: {
    command: 'docker-compose -f docker-compose.test.yml up --wait',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

═══════════════════════════════════════════════════════
PADRÃO DE PAGE OBJECT MODEL — IMPLEMENTAR EM TODOS
═══════════════════════════════════════════════════════

Cada arquivo em e2e/pages/ deve seguir este padrão:

```typescript
// e2e/pages/FinanceiroPage.ts — EXEMPLO DO PADRÃO
import { Page, Locator, expect } from '@playwright/test';

export class FinanceiroPage {
  readonly page: Page;

  // Locators nomeados semanticamente
  readonly kpiReceita: Locator;
  readonly kpiDespesas: Locator;
  readonly kpiLucro: Locator;
  readonly seletorPeriodo: Locator;
  readonly tabelaTransacoes: Locator;
  readonly botaoNovaTransacao: Locator;
  readonly alertaAtrasados: Locator;

  constructor(page: Page) {
    this.page = page;
    // Usar data-testid como seletor principal (mais robusto)
    this.kpiReceita = page.getByTestId('kpi-receita');
    this.kpiDespesas = page.getByTestId('kpi-despesas');
    this.kpiLucro = page.getByTestId('kpi-lucro');
    this.seletorPeriodo = page.getByTestId('seletor-periodo');
    this.tabelaTransacoes = page.getByTestId('tabela-transacoes');
    this.botaoNovaTransacao = page.getByTestId('btn-nova-transacao');
    this.alertaAtrasados = page.getByTestId('alerta-atrasados');
  }

  async navegar() {
    await this.page.goto('/financeiro');
    await expect(this.kpiReceita).toBeVisible();
  }

  async selecionarPeriodo(periodo: 'semana' | 'mes' | 'trimestre' | 'ano') {
    await this.seletorPeriodo.click();
    await this.page.getByRole('option', { name: periodo }).click();
    await this.page.waitForLoadState('networkidle');
  }

  async criarTransacao(dados: {
    tipo: 'receita' | 'despesa';
    descricao: string;
    valor: number;
    categoria: string;
  }) {
    await this.botaoNovaTransacao.click();
    await this.page.getByTestId(`toggle-${dados.tipo}`).click();
    await this.page.getByTestId('input-descricao').fill(dados.descricao);
    await this.page.getByTestId('input-valor').fill(dados.valor.toString());
    await this.page.getByTestId('select-categoria').selectOption(dados.categoria);
    await this.page.getByTestId('btn-salvar').click();
    await expect(this.page.getByText('Transação criada com sucesso')).toBeVisible();
  }

  async obterValorKPI(tipo: 'receita' | 'despesas' | 'lucro'): Promise<number> {
    const locator = this.page.getByTestId(`kpi-${tipo}`).getByTestId('valor-numerico');
    const texto = await locator.textContent();
    // Converter "R$ 1.234,56" para 1234.56
    return parseFloat(texto!.replace('R$', '').replace('.', '').replace(',', '.').trim());
  }
}
```

IMPORTANTE: Ao implementar os Page Objects, use data-testid nos componentes React.
Adicionar data-testid em todos os elementos interativos dos módulos:
- Financeiro: todos os KPIs, botões, filtros, linhas da tabela
- Agenda: botões de visão, slots do calendário, painel lateral
- Equipe: cards de técnico, métricas, formulários de usuário
- Notificações: sino, badge, itens da lista, botões de leitura
- Portal: botões de aprovação, estrelas de avaliação, seções de status

═══════════════════════════════════════════════════════
FACTORIES DE DADOS DE TESTE (BACKEND)
═══════════════════════════════════════════════════════

Criar factories com factory-boy para cada módulo:

```python
# backend/tests/factories/financeiro_factory.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from app.models.financeiro import Transacao, CategoriaFinanceira

fake = Faker('pt_BR')

class CategoriaFinanceiraFactory(SQLAlchemyModelFactory):
    class Meta:
        model = CategoriaFinanceira
        sqlalchemy_session_persistence = 'commit'

    nome = factory.LazyFunction(lambda: fake.word())
    tipo = factory.Iterator(['receita', 'despesa'])
    cor = factory.LazyFunction(lambda: fake.hex_color())
    icone = 'dollar-sign'
    ativo = True

class TransacaoFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Transacao
        sqlalchemy_session_persistence = 'commit'

    tipo = factory.Iterator(['receita', 'despesa'])
    descricao = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    valor = factory.LazyFunction(lambda: fake.random_int(min=5000, max=500000))  # centavos
    data_vencimento = factory.LazyFunction(lambda: fake.future_date())
    status = 'pendente'
    forma_pagamento = factory.Iterator(['pix', 'dinheiro', 'cartao_credito'])

    @factory.post_generation
    def categoria(self, create, extracted, **kwargs):
        if extracted:
            self.categoria_id = extracted.id
        else:
            cat = CategoriaFinanceiraFactory(tipo=self.tipo)
            self.categoria_id = cat.id
```

Criar factories similares para:
- AgendaFactory (com técnico, cliente, OS vinculados)
- EquipeFactory (UsuarioFactory com perfil técnico e métricas)
- NotificacaoFactory (vários tipos)

═══════════════════════════════════════════════════════
ADICIONAIS NECESSÁRIOS NO CÓDIGO EXISTENTE
═══════════════════════════════════════════════════════

Para que os testes funcionem, os seguintes ajustes são necessários:

1. BACKEND — Adicionar endpoints de teste (apenas em ambiente de teste):
```python
# Disponível somente quando ENVIRONMENT=test
@router.post("/test/reset-db")     # Limpar e re-seed banco de teste
@router.post("/test/run-celery-task/{nome}")  # Disparar task Celery manualmente
@router.post("/test/advance-time")  # Avançar data/hora (para testar agendamentos)
```

2. FRONTEND — Adicionar data-testid em todos os componentes dos módulos testados:
- FinanceiroPage.tsx: data-testid em KPIs, filtros, tabela, botões
- AgendaPage.tsx: data-testid nos botões de visão e no container do FullCalendar
- EquipePage.tsx: data-testid nos cards e métricas
- TopBar.tsx: data-testid no sino, badge, dropdown de notificações
- Portal pages: data-testid em todos os elementos interativos

3. DOCKER — Criar docker-compose.test.yml:
```yaml
# Igual ao docker-compose.yml mas com:
# - Banco separado (test_assistencia_impacto)
# - Redis DB 1
# - ENVIRONMENT=test
# - Seed automático ao iniciar
# - Porta diferente (5174 para não colidir com dev)
```

═══════════════════════════════════════════════════════
SCRIPT DE CI/CD — GITHUB ACTIONS
═══════════════════════════════════════════════════════

Criar .github/workflows/testes.yml:

```yaml
name: Testes Automáticos

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  testes-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_assistencia_impacto
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov=backend/app --cov-report=xml -v
      - uses: codecov/codecov-action@v4

  testes-e2e:
    runs-on: ubuntu-latest
    needs: testes-backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
        working-directory: e2e
      - run: npx playwright install --with-deps chromium
      - run: docker-compose -f docker-compose.test.yml up -d --wait
      - run: npx playwright test
        working-directory: e2e
        env:
          CI: true
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: e2e/playwright-report/
```

═══════════════════════════════════════════════════════
ORDEM DE IMPLEMENTAÇÃO
═══════════════════════════════════════════════════════

Execute nesta sequência exata:

Etapa 1 — Infraestrutura de Testes:
1. Criar docker-compose.test.yml com banco e redis isolados
2. Atualizar conftest.py do backend com fixtures assíncronas e rollback por teste
3. Criar todas as factories (financeiro, agenda, equipe)
4. Criar playwright.config.ts com todos os projetos
5. Criar auth.setup.ts (login admin + técnico, salvar storage state)

Etapa 2 — data-testid no Frontend:
6. Adicionar data-testid em FinanceiroPage.tsx e componentes relacionados
7. Adicionar data-testid em AgendaPage.tsx
8. Adicionar data-testid em EquipePage.tsx
9. Adicionar data-testid em TopBar.tsx (notificações)
10. Adicionar data-testid nos componentes do Portal

Etapa 3 — Page Objects:
11. Criar FinanceiroPage.ts (POM)
12. Criar AgendaPage.ts (POM)
13. Criar EquipePage.ts (POM)
14. Criar NotificacoesPage.ts (POM)
15. Criar PortalClientePage.ts (POM)

Etapa 4 — Testes de Integração Backend:
16. Implementar test_financeiro.py (todos os endpoints)
17. Implementar test_agenda.py (todos os endpoints)
18. Implementar test_equipe.py (todos os endpoints + RBAC)
19. Implementar test_notificacoes.py (incluindo WebSocket)
20. Implementar test_portal.py (sem autenticação, edge cases de token)

Etapa 5 — Testes E2E Frontend:
21. Implementar specs de Financeiro (4 arquivos)
22. Implementar specs de Agenda (4 arquivos)
23. Implementar specs de Equipe (3 arquivos)
24. Implementar specs de Notificações (3 arquivos)
25. Implementar specs de Portal (3 arquivos)

Etapa 6 — CI/CD e Documentação:
26. Criar .github/workflows/testes.yml
27. Executar todos os testes e corrigir falhas encontradas
28. Atualizar README.md com seção "Como Executar os Testes"

═══════════════════════════════════════════════════════
REQUISITOS DE QUALIDADE DOS TESTES
═══════════════════════════════════════════════════════

Cada teste deve:
- Ser independente: nenhum teste depende do estado deixado por outro
- Ter dados próprios: usar factories para criar dados antes de cada teste
- Usar await/async corretamente: sem race conditions
- Ter assertions claras: mensagem de erro explica o que falhou
- Limpar após si: teardown automático via fixtures

Naming convention:
- test_deve_[acao]_quando_[condicao] (backend)
- describe('[Módulo]') > it('deve [ação] quando [condição]') (frontend E2E)

Metas de cobertura ao finalizar esta fase:
- Backend Financeiro: ≥ 90% cobertura de linhas
- Backend Agenda: ≥ 85% cobertura de linhas
- Backend Equipe: ≥ 85% cobertura de linhas
- Backend Notificações: ≥ 80% cobertura de linhas
- E2E: 100% dos fluxos críticos (criação, edição, aprovação, pagamento)
- RBAC: 100% das rotas protegidas testadas com perfil sem permissão

Ao finalizar, execute:
  cd backend && pytest tests/ -v --cov --cov-report=html
  cd e2e && npx playwright test --reporter=html

E verifique que TODOS os testes passam antes de considerar esta fase concluída.
```

---

## PROMPTS DE REFINAMENTO (use se travar em alguma etapa)

**Se travar na configuração do Playwright:**
```
Configure o Playwright para o projeto Assistência Impacto. 
Crie o playwright.config.ts com projetos separados para admin, técnico 
e portal público. Implemente o auth.setup.ts que faz login com cada perfil 
e salva o storageState. Use a URL base http://localhost:5173.
```

**Se travar nos testes do Financeiro:**
```
Implemente os testes E2E completos do módulo Financeiro.
Crie o FinanceiroPage.ts (Page Object Model) e todos os specs:
visao-geral.spec.ts, transacoes.spec.ts, contas-receber.spec.ts.
Cada spec deve ter fixtures próprias usando a API de reset do banco de teste.
```

**Se travar nos testes de WebSocket (Notificações):**
```
Implemente os testes E2E de notificações em tempo real com Playwright.
Use dois contextos de browser simultaneamente para simular o admin criando
uma OS e o técnico recebendo a notificação via WebSocket. 
Arquivo: e2e/specs/notificacoes/tempo-real.spec.ts
```

**Se travar no Portal Público:**
```
Implemente os testes E2E do portal público do cliente.
O portal não usa autenticação — apenas tokens UUID nas URLs.
Teste: aprovação de orçamento, rastreamento de OS com polling de status,
e envio de avaliação após conclusão. Inclua edge cases de token inválido/expirado.
```

**Para executar e verificar:**
```
Execute a suite completa de testes e corrija todas as falhas encontradas.
Backend: cd backend && pytest tests/ -v --tb=short
E2E: cd e2e && npx playwright test --headed (para ver visualmente)
Gere o relatório HTML e mostre quais testes passaram/falharam.
```
