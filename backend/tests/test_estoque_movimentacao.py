"""Testes de movimentação de estoque."""
import pytest
from httpx import AsyncClient


async def criar_item_para_teste(client, auth_headers):
    """Cria um item de estoque de teste."""
    # Criar categoria primeiro
    cat_resp = await client.post("/api/estoque/categorias", json={
        "nome": "Materiais Elétricos",
        "cor": "#3B82F6",
        "icone": "zap"
    }, headers=auth_headers)
    assert cat_resp.status_code in [200, 201], f"Falha categoria: {cat_resp.text}"
    
    cat_data = cat_resp.json()
    categoria_id = cat_data.get("id") or cat_data.get("dados", {}).get("id")
    assert categoria_id is not None, f"ID da categoria não encontrado em: {cat_data}"
    
    # Criar item
    item_resp = await client.post("/api/estoque/itens", json={
        "nome": "Cabo Flexível 2.5mm",
        "sku": "CAB-025",
        "categoria_id": categoria_id,
        "unidade": "metro",
        "preco_custo": 5.50,
        "preco_venda": 8.00,
        "custo_unitario": 5.50,
        "estoque_minimo": 100,
        "estoque_maximo": 500
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
        "/api/estoque/movimentacoes",
        json={"item_estoque_id": item_id, "tipo_movimentacao": "entrada", "quantidade": 10, "custo_unitario": 5.50, "observacoes": "Compra teste"},
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
    await client.post("/api/estoque/movimentacoes",
        json={"item_estoque_id": item_id, "tipo_movimentacao": "entrada", "quantidade": 20, "custo_unitario": 5.50},
        headers=auth_headers)
    
    # Depois retirar
    response = await client.post(
        "/api/estoque/movimentacoes",
        json={"item_estoque_id": item_id, "tipo_movimentacao": "saida", "quantidade": 5, "custo_unitario": 5.50},
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
        "/api/estoque/movimentacoes",
        json={"item_estoque_id": item_id, "tipo_movimentacao": "saida", "quantidade": 999, "custo_unitario": 5.50},
        headers=auth_headers
    )
    assert response.status_code == 400, f"Deveria ser 400, got: {response.text}"


@pytest.mark.asyncio
async def test_movimentacao_ajuste(client: AsyncClient, auth_headers: dict):
    """Ajuste deve definir o estoque diretamente."""
    item_id = await criar_item_para_teste(client, auth_headers)
    
    response = await client.post(
        "/api/estoque/movimentacoes",
        json={"item_estoque_id": item_id, "tipo_movimentacao": "ajuste", "quantidade": 30, "custo_unitario": 5.50},
        headers=auth_headers
    )
    assert response.status_code in [200, 201], f"Erro: {response.text}"
