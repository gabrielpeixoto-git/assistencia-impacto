import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_listar_ordens_servico(client: AsyncClient, auth_headers: dict):
    """Testa listagem de ordens de serviço."""
    response = await client.get(
        "/api/ordens-servico",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_ordem_servico_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter ordem de serviço inexistente."""
    response = await client.get(
        "/api/ordens-servico/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_criar_ordem_servico_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar ordem de serviço sem autenticação."""
    os_data = {
        "cliente_id": "cliente-id",
        "tipo_servico_id": "categoria-id",
        "titulo": "Teste",
        "descricao": "Descrição teste",
        "valor_estimado": 1000.00
    }
    
    response = await client.post("/api/ordens-servico", json=os_data)
    
    assert response.status_code in [401, 403]
