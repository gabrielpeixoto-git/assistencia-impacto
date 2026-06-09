import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_criar_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa criação de nova ordem de serviço."""
    # Criar cliente primeiro
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar categoria de serviço
    categoria_data = {
        "nome": "Instalação de Ar Condicionado",
        "descricao": "Serviços de instalação de ar condicionado",
        "ativo": True,
        "icone": "snowflake",
        "cor": "#3B82F6"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Instalação de Ar Condicionado",
        "descricao": "Instalação de ar condicionado split 12000 BTUs na sala",
        "valor_estimado": 1500.00
    }
    
    response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == os_data["titulo"]
    assert data["cliente_id"] == cliente_id
    assert data["numero_os"] is not None


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


@pytest.mark.asyncio
async def test_listar_ordens_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de ordens de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Manutenção",
        "descricao": "Serviços de manutenção",
        "ativo": True,
        "icone": "wrench",
        "cor": "#F59E0B"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Manutenção Elétrica",
        "descricao": "Manutenção do sistema elétrico",
        "valor_estimado": 800.00
    }
    await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    
    # Listar ordens de serviço
    response = await client.get(
        "/api/ordens-servico",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_listar_ordens_servico_com_busca(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de ordens de serviço com filtro de busca."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Hidráulica",
        "descricao": "Serviços hidráulicos",
        "ativo": True,
        "icone": "droplet",
        "cor": "#EF4444"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Conserto de Torneira",
        "descricao": "Conserto de torneira vazando na cozinha",
        "valor_estimado": 200.00
    }
    await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    
    # Buscar por título
    response = await client.get(
        "/api/ordens-servico?busca=Torneira",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_ordem_servico_por_id(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa obter ordem de serviço específica por ID."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Pintura",
        "descricao": "Serviços de pintura",
        "ativo": True,
        "icone": "palette",
        "cor": "#FBBF24"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Pintura de Parede",
        "descricao": "Pintura da parede da sala",
        "valor_estimado": 1200.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Obter ordem de serviço por ID
    response = await client.get(
        f"/api/ordens-servico/{os_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == os_id
    assert data["titulo"] == os_data["titulo"]


@pytest.mark.asyncio
async def test_obter_ordem_servico_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter ordem de serviço inexistente."""
    response = await client.get(
        "/api/ordens-servico/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa atualização de ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Marcenaria",
        "descricao": "Serviços de marcenaria",
        "ativo": True,
        "icone": "hammer",
        "cor": "#8B5CF6"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Construção de Armário",
        "descricao": "Construção de armário embutido",
        "valor_estimado": 3000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Atualizar ordem de serviço
    update_data = {
        "titulo": "Construção de Armário Atualizado",
        "status": "em_andamento",
        "valor_estimado": 3500.00
    }
    response = await client.put(
        f"/api/ordens-servico/{os_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Construção de Armário Atualizado"
    assert data["status"] == "em_andamento"


@pytest.mark.asyncio
async def test_deletar_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa deleção de ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Jardinagem",
        "descricao": "Serviços de jardinagem",
        "ativo": True,
        "icone": "leaf",
        "cor": "#10B981"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Poda de Árvores",
        "descricao": "Poda de árvores no quintal",
        "valor_estimado": 500.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Deletar ordem de serviço
    response = await client.delete(
        f"/api/ordens-servico/{os_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_adicionar_item_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa adicionar item a ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Elétrica",
        "descricao": "Serviços elétricos",
        "ativo": True,
        "icone": "zap",
        "cor": "#6366F1"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Instalação de Tomada",
        "descricao": "Instalação de tomadas adicionais",
        "valor_estimado": 300.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar item
    item_data = {
        "ordem_servico_id": os_id,
        "descricao": "Cabo elétrico 2.5mm",
        "quantidade": 10,
        "unidade": "metros",
        "custo_unitario": 5.00
    }
    response = await client.post(
        f"/api/ordens-servico/{os_id}/itens",
        json=item_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_adicionar_checklist_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa adicionar checklist a ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Refrigeração",
        "descricao": "Serviços de refrigeração",
        "ativo": True,
        "icone": "snowflake",
        "cor": "#06B6D4"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201, f"Erro ao criar categoria: {categoria_response.status_code} - {categoria_response.text}"
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Manutenção de Geladeira",
        "descricao": "Manutenção preventiva de geladeira",
        "valor_estimado": 400.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar checklist
    checklist_data = {
        "ordem_servico_id": os_id,
        "descricao": "Verificar nível de gás refrigerante"
    }
    response = await client.post(
        f"/api/ordens-servico/{os_id}/checklist",
        json=checklist_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_ordens_servico_com_filtros(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de ordens de serviço com filtros de status e prioridade."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Filtros",
        "descricao": "Categoria para teste de filtros",
        "ativo": True,
        "icone": "filter",
        "cor": "#8B5CF6"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço com status específico
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Filtro",
        "descricao": "Teste de filtros",
        "valor_estimado": 1000.00,
        "status": "pendente",
        "prioridade": "alta"
    }
    await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    
    # Filtrar por status
    response = await client.get(
        "/api/ordens-servico?status=pendente",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_atualizar_os_para_concluida_registra_data_conclusao(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa que ao mudar status para concluida, data_conclusao é registrada."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Conclusão",
        "descricao": "Categoria para teste de conclusão",
        "ativo": True,
        "icone": "check-circle",
        "cor": "#10B981"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Conclusão",
        "descricao": "Teste de conclusão",
        "valor_estimado": 1500.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Atualizar para concluida
    update_data = {"status": "concluida"}
    response = await client.put(
        f"/api/ordens-servico/{os_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "concluida"
    assert data["data_conclusao"] is not None


@pytest.mark.asyncio
async def test_listar_itens_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de itens de uma ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Itens",
        "descricao": "Categoria para teste de itens",
        "ativo": True,
        "icone": "list",
        "cor": "#6366F1"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Itens",
        "descricao": "Teste de itens",
        "valor_estimado": 1000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar item
    item_data = {
        "ordem_servico_id": os_id,
        "descricao": "Material teste",
        "quantidade": 5,
        "unidade": "un",
        "custo_unitario": 10.00
    }
    await client.post(
        f"/api/ordens-servico/{os_id}/itens",
        json=item_data,
        headers=auth_headers
    )
    
    # Listar itens
    response = await client.get(
        f"/api/ordens-servico/{os_id}/itens",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_adicionar_foto_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa adicionar foto a ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Fotos",
        "descricao": "Categoria para teste de fotos",
        "ativo": True,
        "icone": "camera",
        "cor": "#F59E0B"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Fotos",
        "descricao": "Teste de fotos",
        "valor_estimado": 1000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar foto
    foto_data = {
        "legenda": "Foto do serviço",
        "tipo_foto": "antes"
    }
    response = await client.post(
        f"/api/ordens-servico/{os_id}/fotos?url_arquivo=http://example.com/foto.jpg",
        json=foto_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_fotos_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de fotos de uma ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Listar Fotos",
        "descricao": "Categoria para teste de listar fotos",
        "ativo": True,
        "icone": "image",
        "cor": "#EC4899"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Listar Fotos",
        "descricao": "Teste de listar fotos",
        "valor_estimado": 1000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar foto
    foto_data = {
        "legenda": "Foto teste",
        "tipo_foto": "antes"
    }
    await client.post(
        f"/api/ordens-servico/{os_id}/fotos?url_arquivo=http://example.com/foto.jpg",
        json=foto_data,
        headers=auth_headers
    )
    
    # Listar fotos
    response = await client.get(
        f"/api/ordens-servico/{os_id}/fotos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_checklist_ordem_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de checklist de uma ordem de serviço."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Listar Checklist",
        "descricao": "Categoria para teste de listar checklist",
        "ativo": True,
        "icone": "check-square",
        "cor": "#14B8A6"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Listar Checklist",
        "descricao": "Teste de listar checklist",
        "valor_estimado": 1000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar checklist
    checklist_data = {
        "ordem_servico_id": os_id,
        "descricao": "Item de checklist teste"
    }
    await client.post(
        f"/api/ordens-servico/{os_id}/checklist",
        json=checklist_data,
        headers=auth_headers
    )
    
    # Listar checklist
    response = await client.get(
        f"/api/ordens-servico/{os_id}/checklist",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_marcar_checklist_concluido(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa marcar item de checklist como concluído."""
    # Criar cliente e categoria
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    categoria_data = {
        "nome": "Teste Marcar Checklist",
        "descricao": "Categoria para teste de marcar checklist",
        "ativo": True,
        "icone": "check",
        "cor": "#22C55E"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    categoria_id = categoria_response.json()["id"]
    
    # Criar ordem de serviço
    os_data = {
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "OS Teste Marcar Checklist",
        "descricao": "Teste de marcar checklist",
        "valor_estimado": 1000.00
    }
    create_response = await client.post(
        "/api/ordens-servico",
        json=os_data,
        headers=auth_headers
    )
    os_id = create_response.json()["id"]
    
    # Adicionar checklist
    checklist_data = {
        "ordem_servico_id": os_id,
        "descricao": "Item para marcar como concluído"
    }
    checklist_response = await client.post(
        f"/api/ordens-servico/{os_id}/checklist",
        json=checklist_data,
        headers=auth_headers
    )
    checklist_id = checklist_response.json()["id"]
    
    # Marcar como concluído
    response = await client.put(
        f"/api/ordens-servico/{os_id}/checklist/{checklist_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_listar_itens_ordem_servico_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa listagem de itens de ordem de serviço inexistente retorna lista vazia."""
    response = await client.get(
        "/api/ordens-servico/id-inexistente/itens",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_fotos_ordem_servico_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa listagem de fotos de ordem de serviço inexistente retorna lista vazia."""
    response = await client.get(
        "/api/ordens-servico/id-inexistente/fotos",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_checklist_ordem_servico_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa listagem de checklist de ordem de serviço inexistente retorna lista vazia."""
    response = await client.get(
        "/api/ordens-servico/id-inexistente/checklist",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_marcar_checklist_concluido_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa marcar checklist inexistente como concluído retorna 404."""
    response = await client.put(
        "/api/ordens-servico/os-id/checklist/checklist-id",
        headers=auth_headers
    )
    assert response.status_code == 404


