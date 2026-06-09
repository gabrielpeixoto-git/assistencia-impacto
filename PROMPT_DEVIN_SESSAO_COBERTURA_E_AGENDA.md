# PROMPT DEVIN — VERIFICAÇÃO DE COBERTURA + CORREÇÃO AGENDA + E2E
## Assistência Impacto — Continuação Pós-Sessão de Testes
> Leia este prompt completo antes de executar qualquer comando.

---

## CONTEXTO DO PROJETO

Stack: FastAPI + PostgreSQL + Redis + Celery + React 18 + TypeScript + Docker Compose  
Localização: `c:\Projeto Impacto Soluções`  
Admin: `admin@assistenciaimpacto.com.br / Admin@123`  
App: `http://localhost` ou `http://localhost:5173`  
Banco: `assistencia_impacto`

A última sessão do Devin focou em aumentar a cobertura de testes de 83% → 87%, criando
testes para `whatsapp_service.py`, `email_service.py`, `auth_service.py` e o router
`whatsapp.py`. A sessão terminou com rate-limit antes da confirmação final.

---

## ═══ FASE 0 — PRÉ-CHECKS OBRIGATÓRIOS (execute antes de qualquer mudança) ═══

### 0.1 — Verificar estado dos containers
```bash
cd "c:\Projeto Impacto Soluções"
docker compose ps
```
Se houver containers stopped duplicados, limpe:
```bash
docker rm $(docker ps -aq --filter "status=exited") 2>nul
```
Se nenhum container estiver rodando, suba o ambiente:
```bash
docker compose up -d
```

### 0.2 — Confirmar cobertura atual (resultado real da sessão anterior)
```bash
cd "c:\Projeto Impacto Soluções\backend"
python -m pytest tests/ --cov=app --cov-report=term-missing -q 2>&1 | Select-String "TOTAL"
```
**Anote o percentual exato antes de qualquer mudança.**

### 0.3 — Identificar testes quebrados (se houver)
```bash
python -m pytest tests/ -q 2>&1 | Select-String "failed|error" | Select-Object -Last 10
```

### 0.4 — Verificar mocks do whatsapp_service (patch path correto)
```bash
python -m pytest tests/test_whatsapp_service.py -v --tb=short
```
Se falhar com erro de import ou patch, leia o arquivo real antes de corrigir:
```bash
cat backend/app/services/whatsapp_service.py
```
O patch path DEVE ser `app.services.whatsapp_service.httpx.AsyncClient`,
não `httpx.AsyncClient`. Corrija se necessário.

---

## ═══ FASE 1 — COMPLETAR COBERTURA ATÉ 87% (se ainda não atingido) ═══

> Execute esta fase SOMENTE se a Fase 0.2 mostrar cobertura abaixo de 87%.
> Se já estiver em 87%+, pule diretamente para a Fase 2.

### 1.1 — Identificar os arquivos com maior gap
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing -q 2>&1 | Select-String " [0-2][0-9]%"
```

### 1.2 — Estratégia: mockar routers com mais linhas descobertas

Os routers com maior volume de linhas não cobertas são:
- `app/routers/dashboard.py` (~93 linhas descobertas)
- `app/routers/clientes.py` (~94 linhas descobertas)
- `app/routers/financeiro.py` (~281 linhas descobertas)

**Para cada router, use a abordagem de mock de dependências:**
```python
"""Testes do router <nome> com mocking de dependências de banco."""
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import select

# Padrão correto para mockar queries do banco em testes de integração:
# Use db_session real (fixture do conftest.py) para criar dados,
# depois chame os endpoints via client (fixture do conftest.py).
# NÃO use MagicMock para o db em testes de integração — use a fixture real.
```

**REGRA CRÍTICA:** Leia o conftest.py antes de escrever qualquer teste novo:
```bash
cat backend/tests/conftest.py
```
Use apenas as fixtures existentes: `client`, `db_session`, `auth_headers`, 
`admin_headers`, `test_user_data`, `test_cliente_data`.

### 1.3 — Verificação após cada arquivo de teste novo
```bash
python -m pytest tests/test_<modulo>.py -v --tb=short
python -m pytest tests/ --cov=app -q 2>&1 | Select-String "TOTAL"
```

---

## ═══ FASE 2 — CORREÇÃO DO BUG DE TIMEZONE NA AGENDA ═══

> **Este é o bug mais crítico em produção.** Eventos criados sem timezone-aware
> são armazenados como UTC mas exibidos 3 horas antes do horário correto (BRT = UTC-3).

### 2.1 — Diagnóstico antes de qualquer mudança

Leia os arquivos afetados:
```bash
cat "c:\Projeto Impacto Soluções\backend\app\models\agenda.py"
cat "c:\Projeto Impacto Soluções\backend\app\routers\agenda.py"
cat "c:\Projeto Impacto Soluções\backend\seed.py"
```

Verifique o banco para ver como os datetimes estão armazenados:
```bash
docker compose exec banco psql -U postgres -d assistencia_impacto -c \
  "SELECT id, titulo, data_hora_inicio, data_hora_fim FROM agenda LIMIT 5;"
```

### 2.2 — Correção no backend (modelo e schemas)

**Arquivo: `backend/app/models/agenda.py`**

Substitua imports de `datetime` para usar timezone-aware:
```python
# ANTES (errado — naive datetime, armazenado como UTC silenciosamente)
from datetime import datetime
data_hora_inicio: Mapped[datetime] = mapped_column(DateTime)

# DEPOIS (correto — timezone-aware)
from datetime import datetime
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")
data_hora_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
data_hora_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

**Arquivo: `backend/app/routers/agenda.py`** (e qualquer service de agenda)

Ao receber datetimes do frontend (strings ISO), converta para BRT:
```python
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")

# Ao criar/atualizar evento:
if data_hora_inicio.tzinfo is None:
    data_hora_inicio = data_hora_inicio.replace(tzinfo=BRT)
```

### 2.3 — Reescrever seed.py com horários BRT corretos

Leia o seed.py atual:
```bash
cat "c:\Projeto Impacto Soluções\backend\seed.py" | head -200
```

Corrija os eventos de agenda para usar horários comerciais reais (BRT):
```python
from datetime import datetime
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")

# Eventos com horários comerciais BRT (8h-18h)
eventos = [
    {
        "titulo": "Manutenção Elétrica - João Silva",
        "data_hora_inicio": datetime(2025, 6, 10, 9, 0, tzinfo=BRT),
        "data_hora_fim": datetime(2025, 6, 10, 11, 0, tzinfo=BRT),
    },
    # ... outros eventos em horários .0 ou .30 (sem minutos estranhos como :47)
]
```

**REGRA:** Use apenas horários em :00 ou :30. Nada de :17, :43, :52.

### 2.4 — Correção no frontend (exibição BRT)

Leia o arquivo da página de agenda:
```bash
cat "c:\Projeto Impacto Soluções\frontend\src\pages\agenda\AgendaPage.tsx"
```

Ao exibir horários no FullCalendar ou em qualquer lugar, force timezone BRT:
```typescript
// Ao formatar horário para exibição
const formatarHorario = (dataISO: string): string => {
  return new Date(dataISO).toLocaleTimeString('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// No FullCalendar, configure o timezone:
<FullCalendar
  timeZone="America/Sao_Paulo"
  // ... outras props
/>
```

### 2.5 — Criar migração Alembic para a mudança de coluna

```bash
docker compose exec backend alembic revision --autogenerate -m "agenda_timezone_aware"
docker compose exec backend alembic upgrade head
```

Verifique que a migração gerada altera o tipo das colunas de `TIMESTAMP` para 
`TIMESTAMP WITH TIME ZONE`.

### 2.6 — Reseeding e verificação

```bash
# Limpar dados antigos de agenda
docker compose exec banco psql -U postgres -d assistencia_impacto -c \
  "TRUNCATE TABLE agenda CASCADE;"

# Rodar seed novamente
docker compose exec backend python seed.py

# Verificar que os horários estão corretos
docker compose exec banco psql -U postgres -d assistencia_impacto -c \
  "SELECT titulo, data_hora_inicio AT TIME ZONE 'America/Sao_Paulo' AS horario_brt FROM agenda LIMIT 5;"
```

O horário exibido deve ser entre 08:00 e 18:00 (horário comercial).

---

## ═══ FASE 3 — TESTES E2E PARA MÓDULOS SEM COBERTURA ═══

Os 5 módulos que precisam de E2E (testes de ponta a ponta via HTTP real):

### 3.1 — Dashboard (`tests/test_dashboard_e2e.py`)
```python
"""E2E tests para o módulo de Dashboard."""
# Endpoints: GET /api/dashboard/resumo
# Verificar: os_hoje, os_semana, receita_mes, os_por_status
```

### 3.2 — Financeiro (`tests/test_financeiro_e2e.py`)
```python
"""E2E tests para o módulo Financeiro."""
# Endpoints: GET /api/financeiro/resumo, POST /api/financeiro/transacoes,
#            PATCH /api/financeiro/transacoes/{id}/pagar
# Verificar: criação de transação receita/despesa, marcar como pago,
#            cálculo correto de saldo
```

### 3.3 — Estoque (`tests/test_estoque_e2e.py`)
```python
"""E2E tests para o módulo de Estoque."""
# Endpoints: POST /api/estoque, POST /api/estoque/{id}/movimentacoes,
#            GET /api/estoque/criticos
# Verificar: criação de item, movimentação entrada/saída,
#            alerta de estoque crítico quando abaixo do mínimo
```

### 3.4 — Orçamentos (`tests/test_orcamentos_e2e.py`)
```python
"""E2E tests para o módulo de Orçamentos."""
# Endpoints: POST /api/orcamentos, PATCH /api/orcamentos/{id}/enviar,
#            PATCH /api/orcamentos/{id}/aprovar
# Verificar: criação de orçamento, mudança de status, conversão em OS
```

### 3.5 — Notificações (`tests/test_notificacoes_e2e.py`)
```python
"""E2E tests para o módulo de Notificações."""
# Endpoints: GET /api/notificacoes, PATCH /api/notificacoes/{id}/ler,
#            PATCH /api/notificacoes/ler-todas
# Verificar: listagem, marcar como lida, marcar todas como lidas
```

**Para cada módulo, siga este padrão:**
1. Leia o router antes de escrever o teste
2. Crie os dados necessários via API (não direto no banco)
3. Verifique o envelope de resposta: `{"sucesso": true, "dados": {...}}`
4. Teste o caminho feliz E o caminho de erro (404 para entidade inexistente)

---

## ═══ FASE 4 — VERIFICAÇÃO FINAL ═══

### 4.1 — Rodar suite completa
```bash
cd "c:\Projeto Impacto Soluções\backend"
python -m pytest tests/ --cov=app --cov-report=term-missing -q
```

### 4.2 — Checklist de qualidade obrigatório

Antes de encerrar a sessão, confirme cada item:

- [ ] Cobertura total ≥ 87%
- [ ] Zero testes falhando (0 failed, 0 error)
- [ ] Eventos de agenda exibidos no horário correto (BRT, não UTC)
- [ ] Horários do seed em :00 ou :30
- [ ] `docker compose up` sobe sem erros
- [ ] Frontend acessível em `http://localhost:5173`
- [ ] Login funciona: `admin@assistenciaimpacto.com.br / Admin@123`
- [ ] Página de Agenda mostra eventos nos horários corretos
- [ ] Nenhuma exception não tratada nos logs do backend:
  ```bash
  docker compose logs backend --tail=50 | Select-String "ERROR\|CRITICAL\|Exception"
  ```

### 4.3 — Relatório final esperado

Ao finalizar, escreva um relatório com:
- Cobertura antes vs depois
- Número de testes antes vs depois
- Bug de timezone: status antes/depois
- Lista dos arquivos criados/modificados
- Qualquer problema encontrado e como foi resolvido

---

## ═══ REGRAS CRÍTICAS DESTA SESSÃO ═══

1. **Leia antes de editar** — sempre rode `cat arquivo.py` antes de modificar
2. **Backup antes de grandes mudanças** — especialmente seed.py e migração Alembic
3. **Não quebre testes que já passam** — rode o teste isolado antes de rodar a suite
4. **Patch path correto** — o caminho do mock deve ser onde o objeto É USADO, 
   não onde é definido: `app.routers.whatsapp.WhatsAppService`, não `app.services.whatsapp_service.WhatsAppService`
5. **Enum values** — use SEMPRE os valores em MAIÚSCULAS: `"CONFIRMADA"`, `"PENDENTE"`, 
   nunca `"confirmada"`, `"agendada"` (valor inválido — causou falha na sessão anterior)
6. **Não adicione testes de 401** — já temos muitos, não movem a cobertura
7. **Migration antes de seed** — sempre rode `alembic upgrade head` antes de `seed.py`
8. **Windows PowerShell** — use `Select-String` em vez de `grep`, `2>nul` em vez de `2>/dev/null`

---

## ORDEM DE EXECUÇÃO RECOMENDADA

```
Fase 0 (pré-checks) → 10 min
Fase 1 (coberta 87%, se necessário) → 30 min  
Fase 2 (timezone agenda) → 45 min
Fase 3 (E2E 5 módulos) → 60 min
Fase 4 (verificação final) → 15 min
Total estimado: ~2.5 horas
```

Se a cobertura já estiver em 87% na Fase 0, **pule a Fase 1 e vá direto para a Fase 2**.
