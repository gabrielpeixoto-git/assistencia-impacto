import pytest
from httpx import AsyncClient


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
async def test_listar_categorias_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de categorias de estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Ferramentas",
        "cor": "#F59E0B",
        "icone": "wrench"
    }
    await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    
    # Listar categorias
    response = await client.get(
        "/api/estoque/categorias",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_criar_item_estoque(client: AsyncClient, auth_headers: dict):
    """Testa criação de novo item de estoque."""
    # Criar categoria primeiro
    categoria_data = {
        "nome": "Materiais Elétricos",
        "cor": "#3B82F6",
        "icone": "zap"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Cabo Flexível 2.5mm",
        "sku": "CAB-025",
        "categoria_id": categoria_id,
        "unidade": "metro",
        "preco_custo": 5.50,
        "preco_venda": 8.00,
        "custo_unitario": 5.50,
        "estoque_minimo": 100,
        "estoque_maximo": 500
    }
    
    response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201, f"Erro ao criar item: {response.status_code} - {response.text}"
    data = response.json()
    assert data["nome"] == item_data["nome"]
    assert data["sku"] == item_data["sku"]
    assert data["estoque_atual"] == 0


@pytest.mark.asyncio
async def test_criar_item_estoque_sku_duplicado(client: AsyncClient, auth_headers: dict):
    """Testa erro ao criar item com SKU duplicado."""
    # Criar categoria
    categoria_data = {
        "nome": "Tubos",
        "cor": "#EF4444",
        "icone": "pipe"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar primeiro item
    item_data = {
        "nome": "Tubo PVC 100mm",
        "sku": "TUB-100",
        "categoria_id": categoria_id,
        "unidade": "metros",
        "preco_custo": 25.00,
        "preco_venda": 35.00,
        "estoque_minimo": 50,
        "estoque_maximo": 200
    }
    await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    
    # Tentar criar item com mesmo SKU
    response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_listar_itens_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de itens de estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Parafusos",
        "cor": "#8B5CF6",
        "icone": "hexagon"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Parafuso Sextavado 1/4\"",
        "sku": "PAR-025",
        "categoria_id": categoria_id,
        "unidade": "unidade",
        "preco_custo": 0.50,
        "preco_venda": 1.00,
        "custo_unitario": 0.50,
        "estoque_minimo": 100,
        "estoque_maximo": 1000
    }
    await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    
    # Listar itens
    response = await client.get(
        "/api/estoque/itens",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_itens_estoque_com_busca(client: AsyncClient, auth_headers: dict):
    """Testa listagem de itens com filtro de busca."""
    # Criar categoria
    categoria_data = {
        "nome": "Fios",
        "cor": "#EC4899",
        "icone": "cable"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Fio Cobre 4mm",
        "sku": "FIO-004",
        "categoria_id": categoria_id,
        "unidade": "metros",
        "preco_custo": 8.00,
        "preco_venda": 12.00,
        "custo_unitario": 8.00,
        "estoque_minimo": 200,
        "estoque_maximo": 800
    }
    await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    
    # Buscar por nome
    response = await client.get(
        "/api/estoque/itens?busca=Cobre",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_item_estoque_por_id(client: AsyncClient, auth_headers: dict):
    """Testa obter item de estoque específico por ID."""
    # Criar categoria
    categoria_data = {
        "nome": "Lâmpadas",
        "cor": "#FBBF24",
        "icone": "lightbulb"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Lâmpada LED 9W",
        "sku": "LAM-009",
        "categoria_id": categoria_id,
        "unidade": "unidade",
        "preco_custo": 8.00,
        "preco_venda": 15.00,
        "custo_unitario": 8.00,
        "estoque_minimo": 50,
        "estoque_maximo": 300
    }
    create_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Obter item por ID
    response = await client.get(
        f"/api/estoque/itens/{item_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["nome"] == item_data["nome"]


@pytest.mark.asyncio
async def test_obter_item_estoque_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter item inexistente."""
    response = await client.get(
        "/api/estoque/itens/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_item_estoque(client: AsyncClient, auth_headers: dict):
    """Testa atualização de item de estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Tintas",
        "cor": "#06B6D4",
        "icone": "paint-bucket"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Tinta Látex Branca 18L",
        "sku": "TIN-018",
        "categoria_id": categoria_id,
        "unidade": "caixa",
        "preco_custo": 120.00,
        "preco_venda": 180.00,
        "custo_unitario": 120.00,
        "estoque_minimo": 10,
        "estoque_maximo": 50
    }
    create_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Atualizar item
    update_data = {
        "nome": "Tinta Látex Branca 18L Premium",
        "preco_venda": 200.00
    }
    response = await client.put(
        f"/api/estoque/itens/{item_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Tinta Látex Branca 18L Premium"


@pytest.mark.asyncio
async def test_deletar_item_estoque(client: AsyncClient, auth_headers: dict):
    """Testa deleção (soft delete) de item de estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Adesivos",
        "cor": "#84CC16",
        "icone": "sticky-note"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Fita Crepe 19mm",
        "sku": "FIT-019",
        "categoria_id": categoria_id,
        "unidade": "rolo",
        "preco_custo": 2.00,
        "preco_venda": 4.00,
        "custo_unitario": 2.00,
        "estoque_minimo": 20,
        "estoque_maximo": 100
    }
    create_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Deletar item
    response = await client.delete(
        f"/api/estoque/itens/{item_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_criar_movimentacao_estoque_entrada(client: AsyncClient, auth_headers: dict):
    """Testa criação de movimentação de entrada no estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Conectores",
        "cor": "#6366F1",
        "icone": "plug"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Conector RJ45",
        "sku": "CON-RJ45",
        "categoria_id": categoria_id,
        "unidade": "unidade",
        "preco_custo": 1.50,
        "preco_venda": 3.00,
        "custo_unitario": 1.50,
        "estoque_minimo": 50,
        "estoque_maximo": 500
    }
    item_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = item_response.json()["id"]
    
    # Criar movimentação de entrada
    movimentacao_data = {
        "item_estoque_id": item_id,
        "tipo_movimentacao": "entrada",
        "quantidade": 100,
        "custo_unitario": 1.50
    }
    response = await client.post(
        "/api/estoque/movimentacoes",
        json=movimentacao_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    
    # Verificar se estoque foi atualizado
    item_response = await client.get(
        f"/api/estoque/itens/{item_id}",
        headers=auth_headers
    )
    assert item_response.json()["estoque_atual"] == 100


@pytest.mark.asyncio
async def test_criar_movimentacao_estoque_saida(client: AsyncClient, auth_headers: dict):
    """Testa criação de movimentação de saída no estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Arruelas",
        "cor": "#A855F7",
        "icone": "circle"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Criar item
    item_data = {
        "nome": "Arruela Lisa 1/2\"",
        "sku": "ARR-012",
        "categoria_id": categoria_id,
        "unidade": "unidade",
        "preco_custo": 0.10,
        "preco_venda": 0.25,
        "custo_unitario": 0.10,
        "estoque_minimo": 200,
        "estoque_maximo": 1000
    }
    item_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = item_response.json()["id"]
    
    # Criar movimentação de entrada primeiro
    movimentacao_entrada = {
        "item_estoque_id": item_id,
        "tipo_movimentacao": "entrada",
        "quantidade": 50,
        "custo_unitario": 0.10
    }
    await client.post(
        "/api/estoque/movimentacoes",
        json=movimentacao_entrada,
        headers=auth_headers
    )
    
    # Criar movimentação de saída
    movimentacao_saida = {
        "item_estoque_id": item_id,
        "tipo_movimentacao": "saida",
        "quantidade": 20,
        "custo_unitario": 0.10
    }
    response = await client.post(
        "/api/estoque/movimentacoes",
        json=movimentacao_saida,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    
    # Verificar se estoque foi atualizado
    item_response = await client.get(
        f"/api/estoque/itens/{item_id}",
        headers=auth_headers
    )
    assert item_response.json()["estoque_atual"] == 30


@pytest.mark.asyncio
async def test_listar_movimentacoes_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de movimentações de estoque."""
    # Criar categoria e item
    categoria_data = {
        "nome": "Porcas",
        "cor": "#F97316",
        "icone": "hexagon"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    item_data = {
        "nome": "Porca Sextavada 1/4\"",
        "sku": "POR-025",
        "categoria_id": categoria_id,
        "unidade": "unidade",
        "preco_custo": 0.30,
        "preco_venda": 0.60,
        "custo_unitario": 0.30,
        "estoque_minimo": 150,
        "estoque_maximo": 800
    }
    item_response = await client.post(
        "/api/estoque/itens",
        json=item_data,
        headers=auth_headers
    )
    item_id = item_response.json()["id"]
    
    # Criar movimentação
    movimentacao_data = {
        "item_estoque_id": item_id,
        "tipo_movimentacao": "entrada",
        "quantidade": 200,
        "custo_unitario": 0.30
    }
    await client.post(
        "/api/estoque/movimentacoes",
        json=movimentacao_data,
        headers=auth_headers
    )
    
    # Listar movimentações
    response = await client.get(
        "/api/estoque/movimentacoes",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_alertas_estoque(client: AsyncClient, auth_headers: dict):
    """Testa listagem de alertas de estoque."""
    response = await client.get(
        "/api/estoque/alertas",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_deletar_categoria_estoque(client: AsyncClient, auth_headers: dict):
    """Testa deleção de categoria de estoque."""
    # Criar categoria
    categoria_data = {
        "nome": "Categoria Teste Deletar",
        "cor": "#EF4444",
        "icone": "trash"
    }
    categoria_response = await client.post(
        "/api/estoque/categorias",
        json=categoria_data,
        headers=auth_headers
    )
    categoria_id = categoria_response.json()["id"]
    
    # Deletar categoria
    response = await client.delete(
        f"/api/estoque/categorias/{categoria_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_deletar_categoria_estoque_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa deleção de categoria inexistente."""
    response = await client.delete(
        "/api/estoque/categorias/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_item_estoque_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa deleção de item inexistente."""
    response = await client.delete(
        "/api/estoque/itens/id-inexistente",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_criar_movimentacao_estoque_sem_autenticacao(client: AsyncClient):
    """Testa erro ao criar movimentação sem autenticação."""
    movimentacao_data = {
        "item_id": "item-id",
        "tipo": "entrada",
        "quantidade": 10,
        "motivo": "Teste"
    }
    response = await client.post(
        "/api/estoque/movimentacoes",
        json=movimentacao_data
    )
    assert response.status_code == 401
