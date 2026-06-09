import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_cliente(client: AsyncClient, auth_headers: dict):
    """Testa criação de novo cliente."""
    cliente_data = {
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "11988888888",
        "tipo": "residencial",
        "ativo": True
    }
    
    response = await client.post(
        "/api/clientes",
        json=cliente_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == cliente_data["nome"]
    assert data["email"] == cliente_data["email"]


@pytest.mark.asyncio
async def test_criar_cliente_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar cliente sem autenticação."""
    cliente_data = {
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "11988888888",
        "tipo": "residencial"
    }
    
    response = await client.post("/api/clientes", json=cliente_data)
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_listar_clientes(client: AsyncClient, auth_headers: dict):
    """Testa listagem de clientes."""
    response = await client.get(
        "/api/clientes",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_cliente_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter cliente inexistente."""
    response = await client.get(
        "/api/clientes/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404
