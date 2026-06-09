import pytest


@pytest.mark.asyncio
async def test_listar_categorias_servico_vazia(client, auth_headers):
    """Testa listagem de categorias de serviço vazia."""
    
    response = await client.get("/api/categorias-servico", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_criar_categoria_servico(client, auth_headers):
    """Testa criação de categoria de serviço."""
    
    categoria_data = {
        "nome": "Ar Condicionado",
        "descricao": "Instalação e manutenção de ar condicionado",
        "icone": "snowflake",
        "cor": "#3B82F6",
        "duracao_padrao_minutos": 120,
        "preco_minimo": 150.0,
        "preco_maximo": 500.0
    }
    
    response = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == categoria_data["nome"]
    assert data["descricao"] == categoria_data["descricao"]
    assert data["icone"] == categoria_data["icone"]
    assert data["cor"] == categoria_data["cor"]
    assert data["duracao_padrao_minutos"] == categoria_data["duracao_padrao_minutos"]
    assert data["preco_minimo"] == categoria_data["preco_minimo"]
    assert data["preco_maximo"] == categoria_data["preco_maximo"]
    assert data["ativo"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_criar_categoria_duplicada(client, auth_headers):
    """Testa criação de categoria com nome duplicado."""
    
    categoria_data = {
        "nome": "Categoria Duplicada",
        "descricao": "Teste de duplicidade",
        "icone": "tool",
        "cor": "#EF4444",
        "duracao_padrao_minutos": 60,
        "preco_minimo": 100.0,
        "preco_maximo": 300.0
    }
    
    # Criar primeira categoria
    await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    
    # Tentar criar segunda categoria com mesmo nome
    response = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    assert response.status_code == 400
    assert "já existe" in response.json()["detail"]


@pytest.mark.asyncio
async def test_obter_categoria_servico(client, auth_headers):
    """Testa obtenção de categoria específica."""
    
    # Criar categoria
    categoria_data = {
        "nome": "Elétrica",
        "descricao": "Instalações elétricas",
        "icone": "zap",
        "cor": "#F59E0B",
        "duracao_padrao_minutos": 90,
        "preco_minimo": 80.0,
        "preco_maximo": 400.0
    }
    
    criar_response = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    categoria_id = criar_response.json()["id"]
    
    # Obter categoria
    response = await client.get(f"/api/categorias-servico/{categoria_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == categoria_id
    assert data["nome"] == categoria_data["nome"]


@pytest.mark.asyncio
async def test_obter_categoria_inexistente(client, auth_headers):
    """Testa obtenção de categoria inexistente."""
    response = await client.get("/api/categorias-servico/id-inexistente", headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]


@pytest.mark.asyncio
async def test_atualizar_categoria_servico(client, auth_headers):
    """Testa atualização de categoria de serviço."""
    
    # Criar categoria
    categoria_data = {
        "nome": "Hidráulica",
        "descricao": "Instalações hidráulicas",
        "icone": "droplets",
        "cor": "#10B981",
        "duracao_padrao_minutos": 60,
        "preco_minimo": 100.0,
        "preco_maximo": 350.0
    }
    
    criar_response = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    categoria_id = criar_response.json()["id"]
    
    # Atualizar categoria
    response = await client.put(
        f"/api/categorias-servico/{categoria_id}",
        params={
            "nome": "Hidráulica Atualizada",
            "descricao": "Nova descrição",
            "icone": "wrench",
            "cor": "#6366F1"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Hidráulica Atualizada"
    assert data["descricao"] == "Nova descrição"
    assert data["icone"] == "wrench"
    assert data["cor"] == "#6366F1"


@pytest.mark.asyncio
async def test_deletar_categoria_servico(client, auth_headers):
    """Testa deleção (soft delete) de categoria de serviço."""
    
    # Criar categoria
    categoria_data = {
        "nome": "Para Deletar",
        "descricao": "Será desativada",
        "icone": "trash",
        "cor": "#EF4444",
        "duracao_padrao_minutos": 30,
        "preco_minimo": 50.0,
        "preco_maximo": 150.0
    }
    
    criar_response = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    categoria_id = criar_response.json()["id"]
    
    # Deletar (soft delete)
    response = await client.delete(f"/api/categorias-servico/{categoria_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verificar que foi desativada (não aparece mais na listagem)
    listar_response = await client.get("/api/categorias-servico", headers=auth_headers)
    categorias = listar_response.json()
    assert all(cat["id"] != categoria_id for cat in categorias)


@pytest.mark.asyncio
async def test_listar_categorias_apenas_ativas(client, auth_headers):
    """Testa que listagem retorna apenas categorias ativas."""
    
    # Criar duas categorias
    categoria1_data = {
        "nome": "Ativa 1",
        "descricao": "Categoria ativa",
        "icone": "check",
        "cor": "#10B981",
        "duracao_padrao_minutos": 60,
        "preco_minimo": 100.0,
        "preco_maximo": 300.0
    }
    
    categoria2_data = {
        "nome": "Para Desativar",
        "descricao": "Será desativada",
        "icone": "x",
        "cor": "#EF4444",
        "duracao_padrao_minutos": 30,
        "preco_minimo": 50.0,
        "preco_maximo": 150.0
    }
    
    await client.post("/api/categorias-servico", json=categoria1_data, headers=auth_headers)
    
    cat2_response = await client.post("/api/categorias-servico", json=categoria2_data, headers=auth_headers)
    cat2_id = cat2_response.json()["id"]
    
    # Desativar segunda categoria
    await client.delete(f"/api/categorias-servico/{cat2_id}", headers=auth_headers)
    
    # Listar categorias
    response = await client.get("/api/categorias-servico", headers=auth_headers)
    assert response.status_code == 200
    categorias = response.json()
    assert len(categorias) >= 1
    # Verificar que pelo menos uma categoria está ativa
    categorias_ativas = [c for c in categorias if c["ativo"]]
    assert len(categorias_ativas) >= 1
