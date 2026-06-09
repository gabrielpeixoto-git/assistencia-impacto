import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_criar_cliente(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa criação de novo cliente."""
    response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201, f"Erro ao adicionar endereço: {response.status_code} - {response.text}"
    data = response.json()
    assert data["nome"] == test_cliente_data["nome"]
    assert data["email"] == test_cliente_data["email"]
    assert data["ativo"] == True


@pytest.mark.asyncio
async def test_criar_cliente_sem_autenticacao(client: AsyncClient, test_cliente_data: dict):
    """Testa erro ao criar cliente sem autenticação."""
    response = await client.post("/api/clientes", json=test_cliente_data)
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_listar_clientes(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de clientes."""
    # Criar cliente primeiro
    await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    
    # Listar clientes
    response = await client.get(
        "/api/clientes",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_listar_clientes_com_busca(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de clientes com filtro de busca."""
    # Criar cliente
    await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    
    # Buscar por nome
    response = await client.get(
        "/api/clientes?busca=Cliente",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_cliente_por_id(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa obter cliente específico por ID."""
    # Criar cliente
    create_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = create_response.json()["id"]
    
    # Obter cliente por ID
    response = await client.get(
        f"/api/clientes/{cliente_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente_id
    assert data["nome"] == test_cliente_data["nome"]


@pytest.mark.asyncio
async def test_obter_cliente_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter cliente inexistente."""
    response = await client.get(
        "/api/clientes/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_cliente(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa atualização de cliente."""
    # Criar cliente
    create_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = create_response.json()["id"]
    
    # Atualizar cliente
    update_data = {"nome": "Cliente Atualizado", "telefone": "11977777777"}
    response = await client.put(
        f"/api/clientes/{cliente_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Cliente Atualizado"
    assert data["telefone"] == "11977777777"


@pytest.mark.asyncio
async def test_deletar_cliente(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa deleção (soft delete) de cliente."""
    # Criar cliente
    create_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = create_response.json()["id"]
    
    # Deletar cliente
    response = await client.delete(
        f"/api/clientes/{cliente_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verificar se foi desativado
    get_response = await client.get(
        f"/api/clientes/{cliente_id}",
        headers=auth_headers
    )
    assert get_response.json()["ativo"] == False


@pytest.mark.asyncio
async def test_adicionar_endereco_cliente(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa adicionar endereço a cliente."""
    # Criar cliente
    create_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = create_response.json()["id"]
    
    # Adicionar endereço
    endereco_data = {
        "rotulo": "Casa",
        "logradouro": "Rua Teste",
        "numero": "123",
        "complemento": "Apto 1",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567",
        "padrao": True
    }
    response = await client.post(
        f"/api/clientes/{cliente_id}/enderecos",
        json=endereco_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201, f"Erro ao adicionar endereço: {response.status_code} - {response.text}"
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_enderecos_cliente(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de endereços de cliente."""
    # Criar cliente
    create_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = create_response.json()["id"]
    
    # Adicionar endereço
    endereco_data = {
        "rotulo": "Casa",
        "logradouro": "Rua Teste",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567",
        "padrao": True
    }
    await client.post(
        f"/api/clientes/{cliente_id}/enderecos",
        json=endereco_data,
        headers=auth_headers
    )
    
    # Listar endereços
    response = await client.get(
        f"/api/clientes/{cliente_id}/enderecos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_listar_enderecos_cliente_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa listagem de endereços de cliente inexistente retorna lista vazia."""
    response = await client.get(
        "/api/clientes/id-inexistente/enderecos",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_adicionar_endereco_cliente_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa adicionar endereço a cliente inexistente retorna 404."""
    endereco_data = {
        "rotulo": "Casa",
        "logradouro": "Rua Teste",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567",
        "padrao": True
    }
    response = await client.post(
        "/api/clientes/id-inexistente/enderecos",
        json=endereco_data,
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_cliente_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa deleção de cliente inexistente retorna 404."""
    response = await client.delete(
        "/api/clientes/id-inexistente",
        headers=auth_headers
    )
    assert response.status_code == 404
