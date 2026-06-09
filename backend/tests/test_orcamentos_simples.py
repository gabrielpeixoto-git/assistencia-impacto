import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_listar_orcamentos(client: AsyncClient, auth_headers: dict):
    """Testa listagem de orçamentos."""
    response = await client.get(
        "/api/orcamentos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter orçamento inexistente."""
    response = await client.get(
        "/api/orcamentos/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_criar_orcamento_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar orçamento sem autenticação."""
    orcamento_data = {
        "cliente_id": "cliente-id",
        "titulo": "Teste",
        "descricao": "Descrição teste",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    
    response = await client.post("/api/orcamentos", json=orcamento_data)
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_resumo_orcamentos(client: AsyncClient, auth_headers: dict):
    """Testa endpoint de resumo de orçamentos."""
    response = await client.get(
        "/api/orcamentos/resumo?periodo=mes",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "aprovados" in data
