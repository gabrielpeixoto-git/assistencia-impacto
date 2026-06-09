# PROMPT DEVIN AI — CONTINUAÇÃO DO PROJETO "ASSISTÊNCIA IMPACTO"
## LEIA TODO ESTE DOCUMENTO ANTES DE COMEÇAR QUALQUER AÇÃO

---

## CONTEXTO DO PROJETO

Você está continuando o desenvolvimento do sistema **"Assistência Impacto"** — um sistema web de gestão para empresa de manutenção residencial e comercial.

**O que já foi construído:**
- Stack completa: FastAPI + SQLAlchemy 2.0 + PostgreSQL 15 + Redis 7 + Celery 5 (backend)
- Stack completa: React 18 + TypeScript + Vite 5 + Tailwind CSS + shadcn/ui (frontend)
- 18 modelos de banco de dados com migrações Alembic
- 14 routers FastAPI com 80+ endpoints
- Todos os módulos frontend: Dashboard, Clientes, OS, Orçamentos, Agenda, Financeiro, Estoque, Equipe, Relatórios, Configurações, Portal Público
- Sistema de autenticação JWT completo com RBAC
- 199/199 testes pytest passando (87% cobertura)
- 19/19 testes E2E Playwright passando
- Docker Compose completo funcional

**O que AINDA PRECISA SER FEITO** (sua missão nesta sessão):

---

## REGRAS ABSOLUTAS — NUNCA VIOLE

1. **ZERO placeholders** — Cada linha de código deve ser implementação real e funcional
2. **ZERO TODOs** — Remova todos os comentários TODO/FIXME ao implementar
3. **NUNCA quebre** o que já está funcionando — rode os testes antes e depois de cada mudança
4. **TypeScript strict mode** — sem `any`, sem `@ts-ignore`
5. **Assíncrono no backend** — sem chamadas síncronas bloqueantes
6. **Português do Brasil** — todos os textos de UI, mensagens de erro, logs
7. **Após cada arquivo modificado** — rode os testes relacionados para confirmar que não quebrou nada
8. Execute `docker-compose up --build` ao final para confirmar que o sistema sobe sem erros

---

## FASE A — BACKEND: CORREÇÕES CRÍTICAS (COMECE AQUI)

### A1. `backend/app/database.py` — Tratamento de Erro de Conexão

Adicione tratamento robusto de erros na conexão com o banco:

```python
# Implementar:
# - try/except na criação do engine com log estruturado via loguru
# - Retry com backoff exponencial (3 tentativas, 1s / 2s / 4s)
# - Health check endpoint que verifica conexão real com SELECT 1
# - Context manager assíncrono para sessões com rollback automático em exceção
# - Evento on_startup que verifica conexão e falha com erro claro se DB indisponível
# - Log de cada tentativa de reconexão com loguru logger
```

### A2. `backend/app/websocket/gerenciador.py` — Autenticação WebSocket

Adicione autenticação JWT no handshake WebSocket:

```python
# Implementar:
# - Receber token JWT como query param: ws://host/ws/notificacoes?token=<jwt>
# - Validar token no momento da conexão usando a mesma função de segurança do HTTP
# - Rejeitar conexão com código 4001 se token inválido/expirado
# - Associar conexão ao usuario_id extraído do token
# - Apenas entregar notificações para o usuario_id correto (nunca broadcast sem filtro)
# - Limpar conexão do mapa de conexões ao desconectar
# - Log de conexão/desconexão com usuario_id e ip
```

### A3. `backend/app/routers/usuarios.py` — Lógica de Reset de Senha

Implemente o fluxo completo de recuperação de senha:

```python
# Implementar:
# - POST /api/auth/esqueci-senha:
#   * Buscar usuário por email (se não existir, retornar 200 mesmo assim — segurança)
#   * Gerar token UUID4 seguro com validade de 1 hora
#   * Armazenar no Redis: key="reset_senha:{token}" value=usuario_id ttl=3600
#   * Disparar task Celery: tarefas_email.enviar_reset_senha(email, token)
#   * Template do email: link = {URL_FRONTEND}/redefinir-senha?token={token}
# - POST /api/auth/redefinir-senha:
#   * Receber: token (str), nova_senha (str min 8 chars, 1 maiúscula, 1 número)
#   * Validar token no Redis (404 se não existir ou expirado)
#   * Atualizar senha_hash com bcrypt
#   * Deletar token do Redis (uso único)
#   * Retornar 200 com mensagem de sucesso
#   * Criar log de auditoria da ação
```

---

## FASE B — BACKEND: MÓDULO FINANCEIRO COMPLETO

Arquivo: `backend/app/routers/financeiro.py` e `backend/app/services/financeiro_service.py`

### B1. KPIs Financeiros Reais

```python
# GET /api/financeiro/resumo?periodo=mes
# Implementar cálculo real com SQLAlchemy queries assíncronas:
# - receita_total: SUM de transações tipo=receita, status=pago no período
# - despesa_total: SUM de transações tipo=despesa, status=pago no período  
# - lucro_liquido: receita_total - despesa_total
# - margem_lucro: (lucro_liquido / receita_total * 100) se receita > 0 else 0
# - contas_receber: SUM de transações tipo=receita, status=pendente
# - contas_pagar: SUM de transações tipo=despesa, status=pendente
# - pagamentos_atrasados: COUNT de transações status=atrasado
# - variacao_receita_mes_anterior: percentual de variação vs mesmo período anterior
#
# Período aceito via query param: hoje | semana | mes | trimestre | ano | personalizado
# Para personalizado: de=YYYY-MM-DD&ate=YYYY-MM-DD
```

### B2. Filtro por Período nas Listagens

```python
# GET /api/financeiro/transacoes
# Adicionar query params obrigatórios para filtro:
# - ?periodo=mes (hoje/semana/mes/trimestre/ano)
# - ?de=2025-01-01&ate=2025-12-31 (intervalo personalizado)
# - ?tipo=receita|despesa|todos
# - ?status=pendente|pago|atrasado|cancelado
# - ?categoria_id=UUID
# - ?cliente_id=UUID
# - Paginação padrão: ?pagina=1&por_pagina=20&ordenar_por=data_vencimento&ordem=desc
```

### B3. Exportação CSV

```python
# GET /api/financeiro/exportar?formato=csv&periodo=mes
# - Gerar CSV com: data, tipo, categoria, descrição, valor, status, forma_pagamento, cliente
# - Retornar como StreamingResponse com Content-Disposition: attachment
# - Encoding UTF-8 com BOM para compatibilidade com Excel brasileiro
# - Formatar valores como R$ X.XXX,XX no CSV
# - Nome do arquivo: transacoes_{periodo}_{data_hoje}.csv
```

### B4. Validação de Permissão RBAC nas Transações

```python
# Aplicar verificação de perfil em cada endpoint:
# - Criar/Editar transação: somente admin e gerente
# - Marcar como pago: somente admin e gerente  
# - Deletar transação: somente admin
# - Visualizar: todos os perfis autenticados
# Usar o decorator de permissão já existente em core/permissoes.py
```

### B5. Vincular Transação a uma OS

```python
# POST /api/financeiro/transacoes
# Quando ordem_servico_id for fornecido:
# - Verificar se a OS existe e pertence ao cliente informado
# - Preencher automaticamente: cliente_id, descrição padrão "OS #{numero_os}"
# - Atualizar status_pagamento na OS quando transação for marcada como paga
# - Criar log de auditoria com referência cruzada OS ↔ Transação
```

---

## FASE C — BACKEND: MÓDULO AGENDA COMPLETO

Arquivo: `backend/app/routers/agenda.py` e `backend/app/services/agenda_service.py`

### C1. Detecção de Conflitos de Agendamento

```python
# GET /api/agenda/disponibilidade?tecnico_id=UUID&inicio=ISO8601&fim=ISO8601
# Implementar:
# - Query que busca todos os eventos do técnico que se sobreponham ao intervalo
# - Sobreposição: inicio_existente < fim_novo AND fim_existente > inicio_novo
# - Retornar: { disponivel: bool, conflitos: [{ id, titulo, inicio, fim }] }
#
# Ao criar/editar agendamento:
# - Chamar verificação de disponibilidade automaticamente
# - Se houver conflito: retornar 409 Conflict com lista de conflitos
# - Permitir override com ?forcar=true (somente admin/gerente)
```

### C2. Otimização de Rota no Mapa

```python
# GET /api/agenda/mapa?tecnico_id=UUID&data=YYYY-MM-DD
# Retornar todos os eventos do dia com coordenadas:
# {
#   "eventos": [
#     {
#       "id": UUID, "titulo": str, "hora_inicio": str, "hora_fim": str,
#       "endereco": str, "latitude": float, "longitude": float,
#       "status": str, "cliente": { "nome": str, "telefone": str }
#     }
#   ],
#   "total_eventos": int,
#   "distancia_total_km": float  # calcular com fórmula haversine entre pontos em ordem
# }
# Ordenar eventos por data_hora_inicio
# Calcular distância total percorrida usando fórmula haversine entre coordenadas consecutivas
```

---

## FASE D — BACKEND: OUTROS MÓDULOS

### D1. `backend/app/routers/clientes.py` — Validação de CPF/CNPJ

```python
# Implementar função de validação real (não apenas formato):
# CPF: algoritmo dos dois dígitos verificadores
# CNPJ: algoritmo dos dois dígitos verificadores
# Adicionar validator Pydantic v2 no schema ClienteCreate:
#   @field_validator('numero_documento')
#   def validar_documento(cls, v, info):
#       tipo = info.data.get('tipo_documento')
#       if tipo == 'cpf': validar_cpf(v)
#       elif tipo == 'cnpj': validar_cnpj(v)
#       return v
# Retornar 422 com mensagem clara se inválido: "CPF inválido" / "CNPJ inválido"
```

### D2. `backend/app/routers/clientes.py` — Busca por Endereço/CEP

```python
# GET /api/clientes/buscar-endereco?cep=01310100
# - Chamar API ViaCEP: https://viacep.com.br/ws/{cep}/json/
# - Retornar campos mapeados para o schema de endereço do sistema
# - Cache Redis por 24h (CEPs não mudam frequentemente)
# - Fallback gracioso se ViaCEP indisponível: retornar 503 com mensagem clara
```

### D3. `backend/app/routers/ordens_servico.py` — Lógica de Atualização de Status

```python
# PATCH /api/ordens-servico/{id}/status
# Implementar máquina de estados com transições válidas:
# pendente → confirmada, cancelada
# confirmada → em_andamento, cancelada
# em_andamento → concluida, aguardando, cancelada
# aguardando → em_andamento, cancelada
# concluida → (nenhuma transição permitida)
# cancelada → (nenhuma transição permitida)
#
# Ao transitar para cada status:
# - concluida: registrar data_conclusao = now(), disparar notificação ao cliente via WhatsApp
# - em_andamento: registrar hora_inicio real
# - cancelada: exigir campo motivo_cancelamento (obrigatório)
# - Criar entrada no log_auditoria com status_anterior e status_novo
# - Disparar notificação WebSocket para o técnico responsável
```

### D4. `backend/app/routers/orcamentos.py` — Lógica de Aprovação/Rejeição

```python
# PATCH /api/orcamentos/{id}/aprovar (requer token público OU autenticação)
# PATCH /api/orcamentos/{id}/recusar (requer token público OU autenticação)
#
# Ao aprovar:
# - Verificar que status atual é 'enviado' ou 'visualizado'
# - Atualizar: status='aprovado', aprovado_em=now()
# - Criar notificação WebSocket para admin/gerente
# - Disparar WhatsApp: "Seu orçamento #{numero} foi aprovado pelo cliente!"
#
# Ao recusar:
# - Receber campo motivo_recusa (obrigatório)
# - Atualizar: status='recusado'
# - Criar notificação WebSocket para admin/gerente
#
# GET /api/portal/orcamentos/{token} (SEM autenticação JWT)
# - Token único e seguro gerado ao enviar orçamento, armazenado no registro
# - Retornar dados completos do orçamento para exibição no portal
# - Verificar se token é válido e orçamento não expirou (valido_ate)
```

### D5. `backend/app/routers/dashboard.py` — Busca Real de Dados

```python
# GET /api/dashboard/resumo
# Implementar todas as queries reais:
#
# os_hoje: COUNT OS com data_agendada = today()
# os_semana: COUNT OS com data_agendada entre início e fim da semana atual
# receita_mes: SUM transações tipo=receita status=pago no mês atual
# despesas_mes: SUM transações tipo=despesa status=pago no mês atual
# lucro_mes: receita_mes - despesas_mes
# orcamentos_pendentes: COUNT orçamentos status IN ('enviado', 'visualizado')
# pagamentos_atrasados: COUNT transações status='atrasado'
# itens_estoque_critico: COUNT itens onde estoque_atual <= estoque_minimo
#
# os_por_status: GROUP BY status, COUNT(*), para gráfico de rosca
# grafico_receita: últimos 12 meses, receita e despesa por mês (para gráfico de área)
# top_clientes: TOP 5 clientes por soma de receita no mês, com nome e valor
# top_tecnicos: TOP 5 técnicos por quantidade de OS concluídas no mês
# os_recentes: últimas 5 OS criadas com JOIN cliente e técnico
# agenda_proximos_dias: próximos 7 dias de agendamentos com técnico e cliente
#
# Cache Redis com TTL de 5 minutos para não sobrecarregar o banco
```

### D6. `backend/app/routers/estoque.py` — Lógica de Movimentação

```python
# POST /api/estoque/{id}/movimentacoes
# Implementar com transação de banco atômica:
# - tipo_movimentacao: entrada | saida | ajuste | compra | uso_os
# - Para 'saida' e 'uso_os': verificar se estoque_atual >= quantidade (400 se insuficiente)
# - Para 'entrada' e 'compra': apenas adicionar
# - Para 'ajuste': pode ser positivo ou negativo, definir estoque_atual diretamente
# - Após movimentação: atualizar estoque_atual no ItemEstoque atomicamente
# - Registrar MovimentacaoEstoque com todos os campos
# - Se estoque_atual <= estoque_minimo após movimentação: criar notificação de alerta
# - Retornar ItemEstoque atualizado com estoque_atual novo
```

---

## FASE E — FRONTEND: FUNCIONALIDADES PENDENTES

### E1. `frontend/src/pages/configuracoes/ConfiguracoesPage.tsx` — Exportação de Dados

```typescript
// Botão "Exportar todos os dados (JSON)" — implementar funcionalidade real:
// 1. Chamar GET /api/admin/exportar-dados (criar este endpoint no backend)
// 2. Backend retorna JSON comprimido com todos os dados do sistema
// 3. Frontend faz download automático: dados_assistencia_impacto_{data}.json
// 4. Mostrar progress bar durante exportação (pode demorar)
// 5. Toast de sucesso com nome do arquivo ao concluir
//
// Endpoint backend necessário: GET /api/admin/exportar-dados (somente admin)
// - Exportar: clientes, ordens_servico, orcamentos, transacoes, estoque
// - Formato: { versao: "1.0", exportado_em: ISO8601, dados: { ... } }
// - Usar StreamingResponse para arquivos grandes
```

### E2. `frontend/src/pages/configuracoes/ConfiguracoesPage.tsx` — Limpar Cache

```typescript
// Botão "Limpar cache do sistema" — implementar funcionalidade real:
// 1. Chamar POST /api/admin/limpar-cache (criar este endpoint no backend)
// 2. Backend: redis.flushdb() no banco de cache (somente admin)
// 3. Frontend: queryClient.clear() para limpar cache TanStack Query
// 4. Toast de sucesso: "Cache limpo com sucesso!"
// 5. Recarregar dados do dashboard automaticamente após limpar
```

---

## FASE F — TESTES E2E PLAYWRIGHT: CENÁRIOS AVANÇADOS

**Diretório:** `e2e/specs/`

Implemente os seguintes arquivos de teste com cenários completos e reais (não mocks):

### F1. `e2e/specs/financeiro-avancado.spec.ts`

```typescript
// Cobrir:
// 1. KPIs corretos: verificar que receita total, despesa, lucro e margem batem com os dados seed
// 2. Seletor de período: mudar para "Este Mês" → dados atualizam, mudar para "Este Ano" → dados atualizam
// 3. Gráfico de barras: verificar que SVG/canvas do Recharts está presente e visível
// 4. Gráfico de rosca de categorias: verificar que está presente e visível
// 5. Alertas de pagamentos atrasados: verificar seção de alertas com dados seed
// 6. Marcar como pago: clicar "Marcar como Pago" em transação pendente → status muda para "Pago"
// 7. Paginação: avançar para página 2 → URL muda, dados mudam
// 8. Filtro por tipo: filtrar "Apenas Receitas" → somente receitas aparecem na tabela
// 9. Exportar CSV: clicar exportar → download inicia (verificar download via Playwright)
// 10. Criar nova transação: preencher formulário completo → transação aparece na lista
```

### F2. `e2e/specs/agenda-avancada.spec.ts`

```typescript
// Cobrir:
// 1. Navegação de visões: clicar "Dia" → muda visão; "Semana" → muda; "Mês" → muda
// 2. Cores dos eventos: verificar que eventos têm cores CSS distintas por tipo
// 3. Clicar em evento: painel lateral de detalhes abre com nome, hora, técnico
// 4. Criar evento: clicar em slot vazio → form desliza → preencher → evento aparece
// 5. Detecção de conflito: criar evento em horário ocupado → mensagem de conflito aparece
// 6. Filtro de técnico: selecionar "João Silva" → apenas eventos do João aparecem
// 7. Aba de mapa: clicar aba "Mapa" → mapa Leaflet renderiza com marcadores
// 8. Navegação de data: clicar "Próximo" → avança para próxima semana/mês
```

### F3. `e2e/specs/equipe-avancada.spec.ts`

```typescript
// Cobrir:
// 1. Cards de técnicos: verificar que cards têm nome, avatar, badge de perfil
// 2. Métricas de desempenho: OS no mês, avaliação média aparecem com valores numéricos
// 3. Status de técnico: verificar badge "disponível" / "ocupado" / "offline"
// 4. Detalhe do técnico: clicar no card → navega para página de detalhe
// 5. Gráfico de OS por mês: gráfico Recharts visível na página de detalhe
// 6. Histórico de OS: tabela de OS atribuídas ao técnico visível
// 7. Editar técnico: clicar editar → form abre com dados preenchidos → salvar → sucesso
// 8. Criar novo usuário (admin): preencher form completo → usuário aparece na lista
```

### F4. `e2e/specs/notificacoes-websocket.spec.ts`

```typescript
// Cobrir:
// 1. Badge inicial: após login, verificar badge no sino com número de não lidas
// 2. Dropdown de notificações: clicar sino → lista de notificações abre
// 3. Marcar como lida: clicar em notificação → badge decremente
// 4. Marcar todas como lidas: botão "Marcar todas" → badge some
// 5. Página completa: navegar para /notificacoes → lista paginada visível
// 6. WebSocket em tempo real: 
//    - Fazer ação que gera notificação (mudar status de OS via API direta)
//    - Verificar que toast Sonner aparece sem recarregar a página
//    - Verificar que badge incrementa automaticamente
// 7. Tipos de notificação: verificar ícones/cores distintas para info/aviso/erro/sucesso
```

### F5. `e2e/specs/portal-publico-avancado.spec.ts`

```typescript
// Cobrir:
// 1. Aprovação de orçamento:
//    - Criar orçamento via API, buscar token gerado
//    - Acessar /portal/orcamento/{token} sem autenticação
//    - Verificar dados do orçamento visíveis (itens, valores, cliente)
//    - Clicar "Aprovar Orçamento" → animação de sucesso → status atualiza
// 2. Solicitar alterações:
//    - Clicar "Solicitar Alterações" → campo de texto aparece → enviar mensagem
// 3. Token expirado/inválido:
//    - Acessar /portal/orcamento/token-invalido → página de erro amigável
// 4. Rastreamento de OS:
//    - Acessar /portal/os/{token} sem autenticação
//    - Verificar stepper visual de progresso (pendente → em andamento → concluída)
//    - Verificar dados do técnico e endereço visíveis
// 5. Galeria de fotos:
//    - OS com fotos: verificar galeria grid visível no portal
//    - Clicar foto → lightbox abre
// 6. Seção de avaliação:
//    - OS concluída: formulário de avaliação de 1-5 estrelas visível
//    - Enviar avaliação → confirmação exibida
// 7. Mobile-first: verificar que layout é responsivo em viewport 375x667
```

---

## FASE G — BACKEND: ENDPOINTS DE SUPORTE AO PORTAL PÚBLICO

Estes endpoints são necessários para os testes E2E do portal:

```python
# Criar router: backend/app/routers/portal.py
# Montar no main.py: app.include_router(portal_router, prefix="/portal")
# TODOS os endpoints abaixo são PÚBLICOS (sem JWT)

# GET /portal/orcamentos/{token}
# - Buscar orçamento pelo campo token_portal (gerar UUID4 ao enviar)
# - Verificar se token existe: 404 se não
# - Verificar se não expirou (valido_ate): 410 Gone se expirado
# - Registrar visualização: atualizar visualizado_em se ainda não foi
# - Retornar dados completos sem informações sensíveis da empresa interna

# POST /portal/orcamentos/{token}/aprovar
# - Validações acima +
# - Verificar status é 'enviado' ou 'visualizado': 409 se já aprovado
# - Atualizar status='aprovado', aprovado_em=now()
# - Notificar admin via WebSocket

# POST /portal/orcamentos/{token}/solicitar-alteracao
# - Body: { mensagem: str }
# - Criar notificação para admin com a mensagem do cliente

# GET /portal/ordens-servico/{token}
# - Buscar OS pelo campo token_portal
# - Retornar: status, tecnico (nome, telefone), endereço, fotos, checklist (sem dados internos)

# POST /portal/ordens-servico/{token}/avaliar
# - Body: { nota: int (1-5), comentario: str }
# - Salvar avaliação na OS
# - Criar entrada de auditoria
```

---

## FASE H — VERIFICAÇÃO FINAL E GARANTIA DE QUALIDADE

### H1. Remover Todos os TODOs Restantes

Após implementar tudo acima, execute:

```bash
grep -r "TODO\|FIXME\|HACK\|XXX" backend/app/ --include="*.py"
grep -r "TODO\|FIXME" frontend/src/ --include="*.ts" --include="*.tsx"
```

**Resultado esperado: zero ocorrências.** Se encontrar algum, implementar a funcionalidade.

### H2. Executar Suite de Testes

```bash
# Backend
cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing
# Meta: manter ≥ 87% de cobertura, 100% dos testes passando

# E2E
npx playwright test --reporter=html
# Meta: 100% dos testes passando (incluindo os novos da Fase F)
```

### H3. Verificar Docker Compose

```bash
docker-compose down -v
docker-compose up --build -d
sleep 30
curl http://localhost/api/health  # deve retornar 200
curl http://localhost             # deve retornar frontend React
docker-compose exec backend python seed.py  # popular dados iniciais
```

### H4. Verificar Sem Erros no Console

Abrir browser em localhost, inspecionar console:
- Zero erros JavaScript
- Zero warnings TypeScript em build
- Zero erros de rede 4xx/5xx durante navegação normal

---

## DADOS CONTEXTUAIS IMPORTANTES

**Usuários seed existentes:**
- admin@assistenciaimpacto.com.br / Admin@123 (perfil: admin)
- joao@assistenciaimpacto.com.br / Tecnico@123 (perfil: tecnico)
- maria@assistenciaimpacto.com.br / Tecnico@123 (perfil: tecnico)
- carlos@assistenciaimpacto.com.br / Tecnico@123 (perfil: tecnico)

**Paleta de cores do tema (usar consistentemente):**
- Fundo: #0A0B0F | Superfície: #111318 | Elevado: #1A1D27
- Primário: #6C63FF (violeta) | Secundário: #00D4FF (ciano)
- Sucesso: #10B981 | Aviso: #F59E0B | Erro: #EF4444
- Glassmorphism: `backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl`

**Padrão de resposta da API (manter consistente):**
```json
{ "sucesso": true, "dados": {}, "mensagem": "...", "meta": { "pagina": 1, "total": 0 } }
```

**Formatações brasileiras:**
- Datas: DD/MM/AAAA
- Moeda: R$ X.XXX,XX
- Telefone: (XX) XXXXX-XXXX
- CPF: XXX.XXX.XXX-XX | CNPJ: XX.XXX.XXX/XXXX-XX

---

## ORDEM DE EXECUÇÃO — SIGA EXATAMENTE ESTA SEQUÊNCIA

```
1. Ler todos os arquivos relevantes antes de editar qualquer um
2. Fase A: database.py → websocket → usuarios (crítico: segurança)
3. Rodar: pytest tests/test_auth.py -v (confirmar que não quebrou auth)
4. Fase B: financeiro_service.py → financeiro router completo
5. Rodar: pytest tests/test_financeiro.py -v
6. Fase C: agenda_service.py → agenda router completo
7. Rodar: pytest tests/test_agenda.py -v
8. Fase D: clientes → ordens_servico → orcamentos → dashboard → estoque
9. Rodar: pytest tests/ -v (suite completa)
10. Fase E: ConfiguracoesPage.tsx (frontend)
11. Fase G: portal.py router (backend, necessário para testes E2E)
12. Fase F: todos os 5 arquivos de teste E2E
13. Rodar: npx playwright test
14. Fase H: verificação final completa
15. docker-compose up --build → confirmar tudo funcional
```

---

## CRITÉRIO DE CONCLUSÃO

O projeto está concluído quando:
- [ ] `grep -r "TODO" backend/app/` retorna **zero resultados**
- [ ] `pytest tests/ -v` mostra **199+ testes, 100% passando**
- [ ] `npx playwright test` mostra **24+ testes E2E, 100% passando**
- [ ] `docker-compose up --build` sobe **sem nenhum erro**
- [ ] Browser em `localhost` → **zero erros no console**
- [ ] Login com admin@assistenciaimpacto.com.br funciona e **dashboard exibe dados reais**
- [ ] Portal público `localhost/portal/orcamento/{token}` acessível **sem login**

**Quando tudo acima estiver verde, o projeto "Assistência Impacto" está completo e pronto para produção.**
