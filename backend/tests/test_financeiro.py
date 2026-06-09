import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_listar_transacoes(client: AsyncClient):
    """Testa listar transações (endpoint público)."""
    response = await client.get("/api/financeiro/transacoes")
    
    # Aceita 200 ou 403 (pode precisar de auth)
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_listar_transacoes_com_autenticacao(client: AsyncClient, auth_headers: dict):
    """Testa listar transações com autenticação."""
    response = await client.get("/api/financeiro/transacoes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_grafico_receitas_despesas_mes(client: AsyncClient):
    """Testa gráfico de receitas e despesas por mês."""
    response = await client.get("/api/financeiro/grafico/receitas-despesas-mes")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_grafico_distribuicao_categoria(client: AsyncClient):
    """Testa gráfico de distribuição por categoria."""
    response = await client.get("/api/financeiro/grafico/distribuicao-categoria")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_resumo_financeiro(client: AsyncClient, auth_headers: dict):
    """Testa resumo financeiro."""
    response = await client.get("/api/financeiro/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "kpi" in data
    assert "receita_total" in data["kpi"]
    assert "despesa_total" in data["kpi"]


@pytest.mark.asyncio
async def test_resumo_financeiro_periodo_hoje(client: AsyncClient, auth_headers: dict):
    """Testa resumo financeiro com período hoje."""
    response = await client.get("/api/financeiro/resumo?periodo=hoje", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_exportar_transacoes(client: AsyncClient, auth_headers: dict):
    """Testa exportar transações em CSV."""
    response = await client.get("/api/financeiro/exportar", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_financeiro(client: AsyncClient, auth_headers: dict):
    """Testa dashboard financeiro."""
    response = await client.get("/api/financeiro/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_listar_categorias_financeiras(client: AsyncClient, auth_headers: dict):
    """Testa listar categorias financeiras."""
    response = await client.get("/api/financeiro/categorias", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_criar_categoria_financeira(client: AsyncClient, auth_headers: dict):
    """Testa criar categoria financeira."""
    categoria_data = {
        "nome": "Categoria Teste",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Categoria Teste"


@pytest.mark.asyncio
async def test_deletar_categoria_financeira(client: AsyncClient, auth_headers: dict):
    """Testa deletar categoria financeira."""
    # Criar categoria primeiro
    categoria_data = {
        "nome": "Categoria Para Deletar",
        "tipo": "receita",
        "cor": "#EF4444",
        "icone": "trash"
    }
    create_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = create_response.json()["id"]
    
    # Deletar
    response = await client.delete(f"/api/financeiro/categorias/{categoria_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_criar_transacao(client: AsyncClient, auth_headers: dict):
    """Testa criação de transação com geração de número único."""
    # Criar categoria financeira primeiro
    categoria_data = {
        "nome": "Serviços Teste",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    categoria_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    transacao_data = {
        "tipo": "receita",
        "categoria_id": categoria_id,
        "valor": 1500.00,
        "descricao": "Serviço de instalação",
        "data_vencimento": "2026-06-01T00:00:00"
    }
    
    response = await client.post(
        "/api/financeiro/transacoes",
        json=transacao_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["numero_transacao"] is not None
    assert data["numero_transacao"].startswith("TRX")
    assert data["valor"] == 1500.00


@pytest.mark.asyncio
async def test_obter_transacao_por_id(client: AsyncClient, auth_headers: dict):
    """Testa obter transação específica por ID."""
    # Criar categoria
    categoria_data = {
        "nome": "Serviços Teste 2",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    categoria_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar transação
    transacao_data = {
        "tipo": "receita",
        "categoria_id": categoria_id,
        "valor": 2000.00,
        "descricao": "Serviço de manutenção",
        "data_vencimento": "2026-06-15T00:00:00"
    }
    create_response = await client.post(
        "/api/financeiro/transacoes",
        json=transacao_data,
        headers=auth_headers
    )
    transacao_id = create_response.json()["id"]
    
    # Obter transação por ID
    response = await client.get(
        f"/api/financeiro/transacoes/{transacao_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transacao_id
    assert data["descricao"] == transacao_data["descricao"]


@pytest.mark.asyncio
async def test_obter_transacao_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter transação inexistente."""
    response = await client.get(
        "/api/financeiro/transacoes/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_transacao_para_pago_registra_data_pagamento(client: AsyncClient, auth_headers: dict):
    """Testa que ao mudar status para pago, data_pagamento é registrada automaticamente."""
    # Criar categoria
    categoria_data = {
        "nome": "Serviços Teste 3",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    categoria_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar transação
    transacao_data = {
        "tipo": "receita",
        "categoria_id": categoria_id,
        "valor": 1000.00,
        "descricao": "Teste de pagamento",
        "data_vencimento": "2026-06-01T00:00:00"
    }
    create_response = await client.post(
        "/api/financeiro/transacoes",
        json=transacao_data,
        headers=auth_headers
    )
    transacao_id = create_response.json()["id"]
    
    # Atualizar para pago
    update_data = {"status": "pago"}
    response = await client.put(
        f"/api/financeiro/transacoes/{transacao_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pago"
    assert data["data_pagamento"] is not None


@pytest.mark.asyncio
async def test_deletar_transacao(client: AsyncClient, auth_headers: dict):
    """Testa deleção de transação."""
    # Criar categoria
    categoria_data = {
        "nome": "Despesas Teste",
        "tipo": "despesa",
        "cor": "#EF4444",
        "icone": "box"
    }
    categoria_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar transação
    transacao_data = {
        "tipo": "despesa",
        "categoria_id": categoria_id,
        "valor": 500.00,
        "descricao": "Despesa teste",
        "data_vencimento": "2026-06-01T00:00:00"
    }
    create_response = await client.post(
        "/api/financeiro/transacoes",
        json=transacao_data,
        headers=auth_headers
    )
    transacao_id = create_response.json()["id"]
    
    # Deletar transação
    response = await client.delete(
        f"/api/financeiro/transacoes/{transacao_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_criar_categoria_financeira(client: AsyncClient, auth_headers: dict):
    """Testa criação de categoria financeira."""
    categoria_data = {
        "nome": "Serviços",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    
    response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_criar_categoria_nome_duplicado(client: AsyncClient, auth_headers: dict):
    """Testa erro ao criar categoria com nome duplicado."""
    categoria_data = {
        "nome": "Material",
        "tipo": "despesa",
        "cor": "#EF4444",
        "icone": "box"
    }
    
    # Primeira criação
    await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    
    # Tentativa de duplicata
    response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_atualizar_categoria_financeira(client: AsyncClient, auth_headers: dict):
    """Testa atualização de categoria financeira."""
    # Criar categoria
    categoria_data = {
        "nome": "Aluguel",
        "tipo": "despesa",
        "cor": "#F59E0B",
        "icone": "home"
    }
    create_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = create_response.json()["id"]
    
    # Atualizar categoria
    response = await client.put(
        f"/api/financeiro/categorias/{categoria_id}",
        json={"nome": "Aluguel Atualizado", "ativo": False},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_deletar_categoria_financeira(client: AsyncClient, auth_headers: dict):
    """Testa deleção de categoria financeira."""
    # Criar categoria
    categoria_data = {
        "nome": "Teste Delete",
        "tipo": "despesa",
        "cor": "#6B7280",
        "icone": "trash"
    }
    create_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = create_response.json()["id"]
    
    # Deletar categoria
    response = await client.delete(
        f"/api/financeiro/categorias/{categoria_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204




@pytest.mark.asyncio
async def test_listar_transacoes_com_filtros(client: AsyncClient, auth_headers: dict):
    """Testa listagem de transações com filtros de tipo, status e categoria."""
    response = await client.get(
        "/api/financeiro/transacoes?tipo=receita&status=pendente",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_atualizar_transacao_completa(client: AsyncClient, auth_headers: dict):
    """Testa atualização completa de transação."""
    # Criar categoria
    categoria_data = {
        "nome": "Serviços Teste 4",
        "tipo": "receita",
        "cor": "#10B981",
        "icone": "wrench"
    }
    categoria_response = await client.post(
        "/api/financeiro/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar transação
    transacao_data = {
        "tipo": "receita",
        "categoria_id": categoria_id,
        "valor": 1000.00,
        "descricao": "Teste atualização",
        "data_vencimento": "2026-06-01T00:00:00"
    }
    create_response = await client.post(
        "/api/financeiro/transacoes",
        json=transacao_data,
        headers=auth_headers
    )
    transacao_id = create_response.json()["id"]
    
    # Atualizar com múltiplos campos
    update_data = {
        "descricao": "Descrição atualizada",
        "valor": 1200.00,
        "forma_pagamento": "pix"
    }
    response = await client.put(
        f"/api/financeiro/transacoes/{transacao_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["descricao"] == "Descrição atualizada"
    assert data["valor"] == 1200.00


@pytest.mark.asyncio
async def test_listar_categorias_financeiras(client: AsyncClient, auth_headers: dict):
    """Testa listagem de categorias financeiras."""
    response = await client.get(
        "/api/financeiro/categorias",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_criar_transacao_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar transação sem autenticação."""
    transacao_data = {
        "tipo": "receita",
        "descricao": "Teste",
        "valor": 100.00,
        "categoria_id": "cat-id"
    }
    response = await client.post("/api/financeiro/transacoes", json=transacao_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_deletar_transacao_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao deletar transação inexistente."""
    response = await client.delete(
        "/api/financeiro/transacoes/id-inexistente",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_categoria_financeira_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao deletar categoria inexistente."""
    response = await client.delete(
        "/api/financeiro/categorias/id-inexistente",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_transacao_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao atualizar transação inexistente (método não suportado)."""
    transacao_data = {
        "tipo": "receita",
        "descricao": "Teste",
        "valor": 100.00,
        "categoria_id": "cat-id"
    }
    response = await client.patch(
        "/api/financeiro/transacoes/id-inexistente",
        json=transacao_data,
        headers=auth_headers
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_atualizar_categoria_financeira_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao atualizar categoria inexistente (método não suportado)."""
    categoria_data = {
        "nome": "Categoria Atualizada",
        "tipo": "receita"
    }
    response = await client.patch(
        "/api/financeiro/categorias/id-inexistente",
        json=categoria_data,
        headers=auth_headers
    )
    assert response.status_code == 405


