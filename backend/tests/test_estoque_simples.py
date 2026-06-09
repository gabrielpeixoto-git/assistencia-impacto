import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_listar_categorias_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de categorias de estoque."""
    response = await client.get(
        "/api/estoque/categorias",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_criar_categoria_estoque(client: AsyncClient, auth_headers: dict):
    """Testa criação de nova categoria de estoque."""
    categoria_data = {
        "nome": "Elétrica",
        "cor": "#3B82F6",
        "icone": "zap"
    }
    
    response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_criar_categoria_estoque_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar categoria sem autenticação."""
    categoria_data = {
        "nome": "Hidráulica",
        "cor": "#10B981",
        "icone": "droplet"
    }
    
    response = await client.post("/api/estoque/categorias", json=categoria_data)
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_listar_itens_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de itens de estoque."""
    response = await client.get(
        "/api/estoque/itens",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_item_estoque_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter item inexistente."""
    response = await client.get(
        "/api/estoque/itens/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404
