# Testes E2E - Assistência Impacto

Suite de testes End-to-End usando Playwright para o sistema Assistência Impacto.

## Estrutura

```
e2e/
├── fixtures/           # Fixtures do Playwright (autenticação, API, banco)
├── helpers/            # Helpers customizados (data-factory, wait, assertions)
├── pages/              # Page Objects (POM)
├── tests/              # Specs de teste
│   ├── smoke/         # Smoke tests (verificação de saúde)
│   ├── auth/          # Testes de autenticação
│   ├── clientes/      # Testes de clientes
│   ├── ordens-servico/# Testes de ordens de serviço
│   ├── orcamentos/    # Testes de orçamentos
│   ├── dashboard/     # Testes do dashboard
│   ├── kanban/        # Testes do kanban
│   ├── estoque/       # Testes de estoque
│   └── rbac/          # Testes de RBAC
├── reports/            # Relatórios de teste
├── playwright.config.ts
├── package.json
└── .env.test          # Variáveis de ambiente para testes
```

## Pré-requisitos

- Node.js 20+
- Docker e Docker Compose (para backend e banco de dados)
- Backend e frontend rodando

## Configuração

1. Instalar dependências:
```bash
cd e2e
npm install
```

2. Configurar variáveis de ambiente em `.env.test`:
```env
BASE_URL=http://localhost:5173
API_URL=http://localhost:8000/api
ADMIN_EMAIL=admin@assistenciaimpacto.com.br
ADMIN_SENHA=Admin@123
TECNICO_EMAIL=joao@assistenciaimpacto.com.br
TECNICO_SENHA=Tecnico@123
```

## Executar Testes

### Smoke Tests (verificação rápida)
```bash
npm run test:smoke
```

### Todos os testes
```bash
npm test
```

### Testes específicos
```bash
npx playwright test tests/auth/login.spec.ts
```

### Com UI do Playwright
```bash
npm run test:ui
```

### Modo headed (com janela do navegador)
```bash
npm run test:headed
```

### Modo debug
```bash
npm run test:debug
```

## Page Objects

Os Page Objects encapsulam a interação com as páginas da aplicação:

- `LoginPage`: Página de login
- `DashboardPage`: Dashboard principal
- `ClientesPage`: Gestão de clientes
- `OrdensServicoPage`: Gestão de ordens de serviço
- `OrcamentosPage`: Gestão de orçamentos
- `KanbanPage`: Kanban de ordens de serviço

## Fixtures

Fixtures disponíveis:

- `loginAs`: Função para login com diferentes perfis
- `apiToken`: Token de acesso para API
- `apiGet`, `apiPost`, `apiPatch`, `apiDelete`: Métodos para requisições HTTP
- `criarCliente`, `criarOrdemServico`, `criarOrcamento`: Criação de dados de teste via API

## Helpers

- `DataFactory`: Gera dados de teste consistentes
- `WaitHelpers`: Métodos para espera de elementos e estados
- `Assertions`: Métodos customizados para assertions

## Relatórios

Após executar os testes, os relatórios são gerados em:

- HTML: `reports/html/index.html`
- JSON: `reports/results.json`

Para abrir o relatório HTML:
```bash
npx playwright show-report reports/html
```

## CI/CD

Os testes são configurados para rodar no GitHub Actions (ver `.github/workflows/e2e.yml`).

## Boas Práticas

1. Use Page Objects para encapsular interações de página
2. Use `data-testid` para seletores estáveis
3. Mantenha testes independentes (cada teste deve poder rodar isolado)
4. Use helpers para lógica comum
5. Evite sleeps fixos - use espera explícita de elementos
6. Limpe dados de teste após cada teste (via API ou fixtures)
