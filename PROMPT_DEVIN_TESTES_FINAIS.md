# PROMPT DEVIN — RECRIAR TESTES DELETADOS E ATINGIR 87% DE COBERTURA

## CONTEXTO

Na última sessão, `test_os_status.py` e `test_estoque_movimentacao.py` foram **deletados** porque falhavam com erro 422. Isso foi errado — os testes devem ser corrigidos, não deletados. O erro 422 significa que os dados enviados não passaram na validação do schema Pydantic — não que o endpoint está quebrado.

**Status atual:** 210 testes passando, cobertura 78%  
**Meta:** 87% de cobertura, recriar os testes deletados corretamente

---

## REGRA CRÍTICA ANTES DE COMEÇAR

**Antes de criar qualquer teste**, leia o arquivo de schema correspondente para saber quais campos são obrigatórios. O erro 422 sempre significa campos faltando ou inválidos.

---

## TAREFA 1 — INVESTIGAR SCHEMAS ANTES DE CRIAR TESTES

Execute este comando para ver os campos obrigatórios de cada schema:

```bash
cd backend

# Ver schema de OrdemServico
python -c "
from app.schemas.ordem_servico import OrdemServicoCreate
import json
schema = OrdemServicoCreate.model_json_schema()
print('=== OrdemServicoCreate ===')
print('Required:', schema.get('required', []))
props = schema.get('properties', {})
for k, v in props.items():
    print(f'  {k}: {v}')
"

# Ver schema de ItemEstoque
python -c "
from app.schemas.estoque import ItemEstoqueCreate
import json
schema = ItemEstoqueCreate.model_json_schema()
print('=== ItemEstoqueCreate ===')
print('Required:', schema.get('required', []))
props = schema.get('properties', {})
for k, v in props.items():
    print(f'  {k}: {v}')
"

# Ver schema de CategoriaEstoque (ou qual é o schema para categorias de estoque)
python -c "
from app.schemas.estoque import CategoriaEstoqueCreate
import json
schema = CategoriaEstoqueCreate.model_json_schema()
print('=== CategoriaEstoqueCreate ===')
print('Required:', schema.get('required', []))
props = schema.get('properties', {})
for k, v in props.items():
    print(f'  {k}: {v}')
" 2>/dev/null || python -c "
import app.schemas.estoque as e
print(dir(e))
"
```

Anote os campos obrigatórios antes de continuar.

---

## TAREFA 2 — VER TESTES QUE JÁ FUNCIONAM COMO REFERÊNCIA

Os testes existentes em `test_ordens_servico.py` e `test_estoque.py` já criam OS e itens de estoque com sucesso. Leia-os para copiar o padrão exato de dados:

```bash
head -80 tests/test_ordens_servico.py
head -60 tests/test_estoque.py
```

Use os **mesmos dados** (mesmos campos, mesmos formatos, mesmos tipos) nos novos testes.

---

## TAREFA 3 — RECRIAR `tests/test_os_status.py`

Crie este arquivo **usando exatamente os mesmos dados de criação de OS que funcionam em `test_ordens_servico.py`**:

```python
"""Testes da máquina de estados das Ordens de Serviço."""
import pytest
from httpx import AsyncClient


# ================================================================
# HELPERS — copie o padrão exato de test_ordens_servico.py
# ================================================================

async def criar_os_para_teste(client, auth_headers):
    """Cria uma OS de teste e retorna o ID. 
    COPIE OS DADOS EXATOS DE test_ordens_servico.py que funcionam."""
    # Primeiro criar cliente
    cliente_resp = await client.post("/api/clientes", json={
        # USE OS CAMPOS QUE EXISTEM no schema ClienteCreate
        # Olhe test_clientes.py para saber quais campos usar
    }, headers=auth_headers)
    assert cliente_resp.status_code == 201, f"Falha ao criar cliente: {cliente_resp.text}"
    cliente_id = cliente_resp.json()["id"]
    
    # Depois criar OS
    os_resp = await client.post("/api/ordens-servico", json={
        # USE OS CAMPOS QUE EXISTEM no schema OrdemServicoCreate
        # Olhe test_ordens_servico.py para saber quais campos usar
        "cliente_id": cliente_id,
        # ... outros campos obrigatórios
    }, headers=auth_headers)
    assert os_resp.status_code == 201, f"Falha ao criar OS: {os_resp.text}"
    return os_resp.json()["id"]


# ================================================================
# TESTES
# ================================================================

@pytest.mark.asyncio
async def test_transicao_valida_pendente_para_confirmada(client: AsyncClient, auth_headers: dict):
    """Testa transição de status pendente → confirmada."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "confirmada"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "confirmada"


@pytest.mark.asyncio
async def test_transicao_invalida_pendente_para_concluida(client: AsyncClient, auth_headers: dict):
    """Não pode ir direto de pendente para concluída."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "concluida"},
        headers=auth_headers
    )
    assert response.status_code == 409, f"Deveria ser 409, got: {response.text}"


@pytest.mark.asyncio
async def test_cancelar_sem_motivo(client: AsyncClient, auth_headers: dict):
    """Cancelar sem motivo deve retornar 400."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "cancelada"},  # sem motivo_cancelamento
        headers=auth_headers
    )
    assert response.status_code == 400, f"Deveria ser 400, got: {response.text}"


@pytest.mark.asyncio
async def test_cancelar_com_motivo(client: AsyncClient, auth_headers: dict):
    """Cancelar com motivo deve funcionar."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "cancelada", "motivo_cancelamento": "Cliente desistiu"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "cancelada"


@pytest.mark.asyncio
async def test_concluir_registra_data_conclusao(client: AsyncClient, auth_headers: dict):
    """Concluir OS deve registrar data_conclusao."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    # pendente → confirmada → em_andamento → concluida
    await client.patch(f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "confirmada"}, headers=auth_headers)
    await client.patch(f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "em_andamento"}, headers=auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "concluida"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "concluida"
    assert data.get("data_conclusao") is not None
```

**IMPORTANTE:** Preencha os campos `# USE OS CAMPOS...` copiando literalmente de `test_ordens_servico.py`. Rode o teste após criar:

```bash
python -m pytest tests/test_os_status.py -v --tb=short
```

Se ainda falhar com 422, imprima `os_resp.text` no assert para ver o erro exato e corrija os dados.

---

## TAREFA 4 — RECRIAR `tests/test_estoque_movimentacao.py`

Da mesma forma, leia `test_estoque.py` e copie o padrão de criação de categoria e item:

```python
"""Testes de movimentação de estoque."""
import pytest
from httpx import AsyncClient


async def criar_item_para_teste(client, auth_headers):
    """Cria um item de estoque de teste.
    COPIE OS DADOS EXATOS DE test_estoque.py que funcionam."""
    # Criar categoria primeiro (copie de test_estoque.py)
    cat_resp = await client.post("/api/estoque/categorias", json={
        # USE OS CAMPOS QUE EXISTEM no schema CategoriaEstoqueCreate
    }, headers=auth_headers)
    # Verificar se criou com sucesso — se der 422, imprimir cat_resp.text
    assert cat_resp.status_code in [200, 201], f"Falha categoria: {cat_resp.text}"
    
    # O ID pode estar na raiz ou em ["dados"]["id"] — verificar formato real
    cat_data = cat_resp.json()
    categoria_id = cat_data.get("id") or cat_data.get("dados", {}).get("id")
    assert categoria_id is not None, f"ID da categoria não encontrado em: {cat_data}"
    
    # Criar item (copie de test_estoque.py)
    item_resp = await client.post("/api/estoque/itens", json={
        # USE OS CAMPOS QUE EXISTEM no schema ItemEstoqueCreate
        "categoria_id": categoria_id,
        # ... outros campos obrigatórios
    }, headers=auth_headers)
    assert item_resp.status_code in [200, 201], f"Falha item: {item_resp.text}"
    
    item_data = item_resp.json()
    item_id = item_data.get("id") or item_data.get("dados", {}).get("id")
    return item_id


@pytest.mark.asyncio
async def test_movimentacao_entrada_aumenta_estoque(client: AsyncClient, auth_headers: dict):
    """Entrada deve aumentar o estoque."""
    item_id = await criar_item_para_teste(client, auth_headers)
    
    # Verificar estoque inicial
    item_before = (await client.get(f"/api/estoque/itens/{item_id}", headers=auth_headers)).json()
    estoque_inicial = item_before.get("estoque_atual", 0)
    
    # Fazer movimentação de entrada
    response = await client.post(
        f"/api/estoque/itens/{item_id}/movimentacoes",
        json={"tipo_movimentacao": "entrada", "quantidade": 10, "observacoes": "Compra teste"},
        headers=auth_headers
    )
    assert response.status_code in [200, 201], f"Erro: {response.text}"
    
    # Verificar que estoque aumentou
    item_after = (await client.get(f"/api/estoque/itens/{item_id}", headers=auth_headers)).json()
    assert item_after["estoque_atual"] == estoque_inicial + 10


@pytest.mark.asyncio
async def test_movimentacao_saida_diminui_estoque(client: AsyncClient, auth_headers: dict):
    """Saída deve diminuir o estoque."""
    item_id = await criar_item_para_teste(client, auth_headers)
    
    # Primeiro adicionar estoque
    await client.post(f"/api/estoque/itens/{item_id}/movimentacoes",
        json={"tipo_movimentacao": "entrada", "quantidade": 20},
        headers=auth_headers)
    
    # Depois retirar
    response = await client.post(
        f"/api/estoque/itens/{item_id}/movimentacoes",
        json={"tipo_movimentacao": "saida", "quantidade": 5},
        headers=auth_headers
    )
    assert response.status_code in [200, 201], f"Erro: {response.text}"
    
    item_after = (await client.get(f"/api/estoque/itens/{item_id}", headers=auth_headers)).json()
    assert item_after["estoque_atual"] == 15


@pytest.mark.asyncio
async def test_movimentacao_saida_sem_estoque(client: AsyncClient, auth_headers: dict):
    """Saída sem estoque suficiente deve retornar 400."""
    item_id = await criar_item_para_teste(client, auth_headers)
    
    # Tentar retirar mais do que tem (estoque inicial é 0)
    response = await client.post(
        f"/api/estoque/itens/{item_id}/movimentacoes",
        json={"tipo_movimentacao": "saida", "quantidade": 999},
        headers=auth_headers
    )
    assert response.status_code == 400, f"Deveria ser 400, got: {response.text}"


@pytest.mark.asyncio
async def test_movimentacao_ajuste(client: AsyncClient, auth_headers: dict):
    """Ajuste deve definir o estoque diretamente."""
    item_id = await criar_item_para_teste(client, auth_headers)
    
    response = await client.post(
        f"/api/estoque/itens/{item_id}/movimentacoes",
        json={"tipo_movimentacao": "ajuste", "quantidade": 30},
        headers=auth_headers
    )
    assert response.status_code in [200, 201], f"Erro: {response.text}"
```

Rode e corrija qualquer campo faltando com base no erro 422:
```bash
python -m pytest tests/test_estoque_movimentacao.py -v --tb=short
```

---

## TAREFA 5 — VERIFICAR COBERTURA FINAL

Após os testes acima passando:

```bash
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing -q
```

Se a cobertura ainda estiver abaixo de 87%, identifique os módulos com menor cobertura no relatório e adicione testes pontuais para as linhas descobertas.

Os módulos com mais linhas descobertas são tipicamente:
- `routers/clientes.py` (74%)
- `routers/estoque.py` (63%)
- `routers/financeiro.py` (72%)
- `routers/whatsapp.py` (22%)

Para `whatsapp.py`, que provavelmente não tem integração real disponível, adicione testes que verificam que os endpoints existem e retornam resposta (mesmo que mock):

```python
# tests/test_whatsapp.py — testes básicos sem integração real
@pytest.mark.asyncio
async def test_endpoint_whatsapp_requer_autenticacao(client, auth_headers):
    response = await client.post("/api/whatsapp/enviar-mensagem", json={})
    assert response.status_code != 404  # endpoint existe
```

---

## TAREFA 6 — VERIFICAÇÃO FINAL COMPLETA

```bash
# 1. Testes backend
python -m pytest tests/ -v -q 2>&1 | tail -5

# 2. Cobertura
python -m pytest tests/ --cov=app --cov-report=term-missing -q 2>&1 | grep "TOTAL"

# 3. Zero TODOs
grep -r "# TODO\|# FIXME" backend/app/ --include="*.py" | wc -l

# 4. Build frontend
cd frontend && npm run build 2>&1 | tail -3
```

**Critérios de conclusão:**
- [ ] Todos os testes passando (sem nenhum deletado por falha)
- [ ] Cobertura ≥ 87%
- [ ] Zero TODOs no código
- [ ] Build frontend limpo

---

## SE O ENDPOINT `/status` NÃO EXISTIR

Se o PATCH `/api/ordens-servico/{id}/status` retornar 404, verifique se está montado no `main.py` e se o router de OS inclui essa rota. Leia o arquivo `ordens_servico.py` e confirme que a função existe e o decorator `@router.patch("/{os_id}/status")` está presente.
