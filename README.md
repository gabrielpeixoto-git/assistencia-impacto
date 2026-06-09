<div align="center">

# ⚡ Assistência Impacto

**Sistema de Gestão Completo para Empresas de Manutenção Residencial e Comercial**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com)
[![License](https://img.shields.io/badge/Licença-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 📋 Visão Geral

O **Assistência Impacto** é uma plataforma web de gestão empresarial desenvolvida para empresas de
serviços de manutenção residencial e comercial. Com design dark futurístico e glassmorphism,
oferece uma experiência visual impressionante aliada a funcionalidades completas de gestão.

### ✨ Funcionalidades Principais

| Módulo | Descrição |
|--------|-----------|
| 📊 **Dashboard** | KPIs em tempo real, gráficos de receita/despesa, agenda dos próximos dias |
| 👥 **Clientes (CRM)** | Cadastro completo, histórico de OS, linha do tempo de atividades |
| 🔧 **Ordens de Serviço** | Kanban drag-and-drop, checklist, fotos antes/depois, assinatura digital |
| 📄 **Orçamentos** | Construtor visual com preview PDF em tempo real, aprovação online |
| 📅 **Agenda** | FullCalendar integrado, filtros por técnico, detecção de conflitos |
| 💰 **Financeiro** | Fluxo de caixa, contas a receber/pagar, alertas de inadimplência |
| 📦 **Estoque** | Controle de materiais, alertas de estoque mínimo, histórico de movimentações |
| 👷 **Equipe** | Gestão de técnicos, métricas de desempenho, agenda individual |
| 📈 **Relatórios** | Analytics completo, exportação PDF/CSV/Excel |
| 🔔 **Notificações** | Tempo real via WebSocket, push de eventos críticos |
| 💬 **WhatsApp** | Integração Evolution API, templates automáticos |
| 🌐 **Portal Cliente** | Aprovação de orçamentos e acompanhamento de OS via link público |

---

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.11+** + **FastAPI** (assíncrono)
- **SQLAlchemy 2.0** (ORM async) + **Alembic** (migrações)
- **PostgreSQL 15** (banco principal) + **Redis 7** (cache/broker)
- **Celery 5** (tarefas em background)
- **JWT** (autenticação) + **RBAC** (permissões por perfil)
- **ReportLab / WeasyPrint** (geração de PDFs)
- **WebSockets** (notificações em tempo real)

### Frontend
- **React 18** + **TypeScript** (strict mode) + **Vite 5**
- **Tailwind CSS** + **shadcn/ui** + **Framer Motion**
- **TanStack Query v5** + **TanStack Router**
- **FullCalendar** (agenda) + **Recharts** (gráficos) + **Leaflet** (mapas)
- **Zustand** (estado global) + **React Hook Form** + **Zod**

### Infraestrutura
- **Docker Compose** (stack completo em contêineres)
- **Nginx** (proxy reverso: `/api/` → backend, `/` → frontend)
- Acessível em `http://localhost` na porta 80

---

## 🚀 Instalação e Execução

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/assistencia-impacto.git
cd assistencia-impacto
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações reais
nano .env
```

> ⚠️ **Importante:** O `VITE_API_URL` deve ser `/api` (caminho relativo), não `http://backend:8000`.

### 3. Subir os containers

```bash
docker compose up --build -d
```

### 4. Rodar as migrações do banco de dados

```bash
docker compose exec backend alembic upgrade head
```

### 5. Popular o banco com dados iniciais (seed)

```bash
# Copiar e executar o script de seed
docker cp backend/seed.py assistencia-impacto-backend-1:/app/seed.py
docker compose exec backend python seed.py
```

### 6. Acessar o sistema

| Serviço | URL |
|---------|-----|
| 🌐 **Frontend** | http://localhost |
| 📡 **API Backend** | http://localhost/api |
| 📚 **Swagger Docs** | http://localhost/api/docs |
| 🔄 **ReDoc** | http://localhost/api/redoc |

### Credenciais padrão (após seed)

| Usuário | E-mail | Senha | Perfil |
|---------|--------|-------|--------|
| Administrador | `admin@assistenciaimpacto.com.br` | `admin123` | Admin |
| João Silva | `joao@assistenciaimpacto.com.br` | `tecnico123` | Técnico |
| Maria Santos | `maria@assistenciaimpacto.com.br` | `tecnico123` | Técnico |
| Carlos Oliveira | `carlos@assistenciaimpacto.com.br` | `tecnico123` | Técnico |

---

## 🏗️ Arquitetura

```
assistencia-impacto/
├── backend/                    # API FastAPI (Python)
│   ├── app/
│   │   ├── main.py             # Fábrica do app
│   │   ├── models/             # Modelos ORM (18 entidades)
│   │   ├── schemas/            # Schemas Pydantic v2
│   │   ├── routers/            # 14+ APIRouters (80+ endpoints)
│   │   ├── services/           # Regras de negócio
│   │   ├── tasks/              # Tarefas Celery
│   │   └── websocket/          # Gerenciador WebSocket
│   ├── alembic/                # Migrações do banco
│   └── seed.py                 # Script de dados iniciais
│
├── frontend/                   # SPA React + TypeScript
│   └── src/
│       ├── pages/              # 20+ páginas
│       ├── components/         # Componentes reutilizáveis
│       ├── hooks/              # Hooks customizados
│       └── store/              # Zustand stores
│
├── nginx/
│   └── nginx.conf              # Proxy reverso
│
├── docker-compose.yml          # Stack completa (dev)
├── docker-compose.prod.yml     # Stack produção
├── .env.example                # Template de variáveis de ambiente
└── README.md
```

### Serviços Docker

| Serviço | Imagem | Porta Interna | Descrição |
|---------|--------|---------------|-----------|
| `banco` | postgres:15-alpine | 5432 | Banco de dados principal |
| `redis` | redis:7-alpine | 6379 | Cache e broker do Celery |
| `backend` | ./backend | 8000 | API FastAPI |
| `worker` | ./backend | — | Worker Celery |
| `beat` | ./backend | — | Agendador Celery Beat |
| `frontend` | ./frontend | 5173 | Vite dev server |
| `nginx` | nginx:alpine | **80** | Proxy reverso (ponto de entrada) |

---

## 📡 API

A documentação interativa da API está disponível em:
- **Swagger UI:** `http://localhost/api/docs` 
- **ReDoc:** `http://localhost/api/redoc` 

### Autenticação

```bash
# Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@assistenciaimpacto.com.br", "senha": "admin123"}'

# Resposta: { "access_token": "...", "token_type": "bearer" }
```

---

## 🔒 Segurança

- Autenticação **JWT** com access token (15min) + refresh token (7 dias, httpOnly cookie)
- **RBAC** por perfil: `admin`, `gerente`, `tecnico`, `visualizador` 
- Rate limiting nos endpoints de autenticação
- Soft delete em entidades críticas
- Todos os uploads validados por tipo e tamanho
- Log de auditoria completo para mutações de dados

---

## 🎨 Design System

| Token | Valor | Uso |
|-------|-------|-----|
| `--bg-primary` | `#0A0B0F` | Fundo principal |
| `--bg-surface` | `#111318` | Cards e superfícies |
| `--accent-primary` | `#6C63FF` | Violeta elétrico — CTAs principais |
| `--accent-secondary` | `#00D4FF` | Ciano cyber — destaques |
| `--success` | `#10B981` | Sucesso, confirmado |
| `--warning` | `#F59E0B` | Aviso, pendente |
| `--danger` | `#EF4444` | Erro, cancelado |

---

## ⚠️ Comandos Importantes

```bash
# ✅ Subir containers (seguro)
docker compose up -d

# ✅ Ver logs em tempo real
docker compose logs -f backend
docker compose logs -f frontend

# ✅ Parar containers (mantém dados)
docker compose stop

# ✅ Reiniciar um serviço específico
docker compose restart backend

# ⛔ NUNCA EXECUTAR — apaga todos os dados do banco
# docker compose down -v
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch: `git checkout -b feature/minha-funcionalidade` 
3. Commit: `git commit -m 'feat: adicionar nova funcionalidade'` 
4. Push: `git push origin feature/minha-funcionalidade` 
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
Desenvolvido com ❤️ para a <strong>Assistência Impacto</strong>
</div>
