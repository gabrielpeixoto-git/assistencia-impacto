import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_criar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa criação de novo orçamento."""
    # Criar cliente primeiro
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Instalação",
        "descricao": "Orçamento para instalação de ar condicionado",
        "subtotal": 1500.00,
        "total": 1500.00
    }
    
    response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == orcamento_data["titulo"]
    assert data["cliente_id"] == cliente_id
    assert data["numero_orcamento"] is not None
    assert data["status"] == "rascunho"


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
async def test_listar_orcamentos(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de orçamentos."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Manutenção",
        "descricao": "Orçamento para manutenção elétrica",
        "subtotal": 800.00,
        "total": 800.00
    }
    await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    
    # Listar orçamentos
    response = await client.get(
        "/api/orcamentos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_listar_orcamentos_com_busca(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de orçamentos com filtro de busca."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Pintura",
        "descricao": "Orçamento para pintura de paredes",
        "subtotal": 2000.00,
        "total": 2000.00
    }
    await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    
    # Buscar por título
    response = await client.get(
        "/api/orcamentos?busca=Pintura",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_obter_orcamento_por_id(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa obter orçamento específico por ID."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Hidráulica",
        "descricao": "Orçamento para conserto hidráulico",
        "subtotal": 500.00,
        "total": 500.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Obter orçamento por ID
    response = await client.get(
        f"/api/orcamentos/{orcamento_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == orcamento_id
    assert data["titulo"] == orcamento_data["titulo"]


@pytest.mark.asyncio
async def test_obter_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao obter orçamento inexistente."""
    response = await client.get(
        "/api/orcamentos/id-inexistente",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa atualização de orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Marcenaria",
        "descricao": "Orçamento para armário embutido",
        "subtotal": 3000.00,
        "total": 3000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Atualizar orçamento
    update_data = {
        "titulo": "Orçamento de Marcenaria Atualizado",
        "total": 3500.00
    }
    response = await client.put(
        f"/api/orcamentos/{orcamento_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Orçamento de Marcenaria Atualizado"


@pytest.mark.asyncio
async def test_deletar_orcamento_rascunho(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa deleção de orçamento em rascunho."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Jardinagem",
        "descricao": "Orçamento para poda de árvores",
        "subtotal": 600.00,
        "total": 600.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Deletar orçamento
    response = await client.delete(
        f"/api/orcamentos/{orcamento_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_enviar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa envio de orçamento para cliente."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Elétrica",
        "descricao": "Orçamento para instalação elétrica",
        "subtotal": 1200.00,
        "total": 1200.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar orçamento
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_aprovar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa aprovação de orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Refrigeração",
        "descricao": "Orçamento para manutenção de ar condicionado",
        "subtotal": 900.00,
        "total": 900.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar orçamento primeiro
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Aprovar orçamento
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/aprovar",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_rejeitar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa rejeição de orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Vidraçaria",
        "descricao": "Orçamento para substituição de vidros",
        "subtotal": 700.00,
        "total": 700.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar orçamento primeiro
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Rejeitar orçamento
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/rejeitar",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_adicionar_item_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa adicionar item a orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento de Material",
        "descricao": "Orçamento para compra de materiais",
        "subtotal": 0.00,
        "total": 0.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Adicionar item
    item_data = {
        "descricao": "Cimento 50kg",
        "quantidade": 10,
        "unidade": "sacos",
        "preco_unitario": 35.00
    }
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/itens",
        json=item_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


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
    assert "pendentes" in data
    assert "rejeitados" in data
    assert "taxa_conversao" in data


@pytest.mark.asyncio
async def test_resumo_orcamentos_periodo_hoje(client: AsyncClient, auth_headers: dict):
    """Testa resumo de orçamentos com filtro de período hoje."""
    response = await client.get(
        "/api/orcamentos/resumo?periodo=hoje",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data


@pytest.mark.asyncio
async def test_resumo_orcamentos_periodo_customizado(client: AsyncClient, auth_headers: dict):
    """Testa resumo de orçamentos com período customizado."""
    from datetime import datetime, timedelta
    data_inicio = (datetime.now() - timedelta(days=7)).isoformat()
    data_fim = datetime.now().isoformat()
    
    response = await client.get(
        f"/api/orcamentos/resumo?data_inicio={data_inicio}&data_fim={data_fim}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data


@pytest.mark.asyncio
async def test_atualizar_orcamento_registra_datas_status(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa que ao mudar status, datas correspondentes são registradas."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Teste Status",
        "descricao": "Teste de mudança de status",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Atualizar para enviado
    response = await client.put(
        f"/api/orcamentos/{orcamento_id}",
        json={"status": "enviado"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "enviado"
    assert data["enviado_em"] is not None


@pytest.mark.asyncio
async def test_deletar_orcamento_nao_rascunho(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa erro ao tentar deletar orçamento não rascunho."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Não Rascunho",
        "descricao": "Teste de deleção",
        "subtotal": 500.00,
        "total": 500.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar orçamento (muda status para enviado)
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Tentar deletar orçamento não rascunho
    response = await client.delete(
        f"/api/orcamentos/{orcamento_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_converter_orcamento_em_os(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa conversão de orçamento aprovado em ordem de serviço."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar categoria de serviço (necessária para conversão)
    categoria_data = {
        "nome": "Teste Conversão",
        "descricao": "Categoria para teste",
        "ativo": True,
        "icone": "check",
        "cor": "#10B981"
    }
    categoria_response = await client.post(
        "/api/categorias-servico",
        json=categoria_data,
        headers=auth_headers
    )
    assert categoria_response.status_code == 201
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento para Converter",
        "descricao": "Orçamento que será convertido em OS",
        "subtotal": 2000.00,
        "total": 2000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar e aprovar orçamento
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    await client.post(
        f"/api/orcamentos/{orcamento_id}/aprovar",
        headers=auth_headers
    )
    
    # Converter em OS
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/converter",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "os_id" in data
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_converter_orcamento_nao_aprovado(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa erro ao converter orçamento não aprovado."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Não Aprovado",
        "descricao": "Não pode ser convertido",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Tentar converter sem aprovar
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/converter",
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_converter_orcamento_sem_categoria_servico(client: AsyncClient, auth_headers: dict, test_cliente_data: dict, db_session):
    """Testa erro ao converter orçamento quando não existe categoria de serviço."""
    from sqlalchemy import delete
    from app.models.categoria_servico import CategoriaServico
    
    # Deletar todas as categorias de serviço
    await db_session.execute(delete(CategoriaServico))
    await db_session.commit()
    
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Sem Categoria",
        "descricao": "Teste sem categoria",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar e aprovar
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    await client.post(
        f"/api/orcamentos/{orcamento_id}/aprovar",
        headers=auth_headers
    )
    
    # Tentar converter sem categoria
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/converter",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "categoria" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_aprovar_orcamento_nao_enviado(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa erro ao aprovar orçamento que não foi enviado."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Rascunho",
        "descricao": "Ainda não enviado",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Tentar aprovar sem enviar
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/aprovar",
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_enviar_orcamento_nao_rascunho(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa erro ao enviar orçamento que não está em rascunho."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Teste",
        "descricao": "Teste",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar uma vez
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Tentar enviar novamente (já não é rascunho)
    response = await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_listar_itens_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa listagem de itens de orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Teste Itens",
        "descricao": "Teste de listagem de itens",
        "subtotal": 1000.00,
        "total": 1000.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Listar itens
    response = await client.get(
        f"/api/orcamentos/{orcamento_id}/itens",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_itens_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa listagem de itens de orçamento inexistente retorna lista vazia."""
    response = await client.get(
        "/api/orcamentos/id-inexistente/itens",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_recusar_orcamento(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa recusa de orçamento."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Teste Recusar",
        "descricao": "Teste de recusa",
        "subtotal": 500.00,
        "total": 500.00
    }
    create_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = create_response.json()["id"]
    
    # Enviar orçamento
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Recusar orçamento
    response = await client.patch(
        f"/api/orcamentos/{orcamento_id}/recusar?motivo=Preço alto",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recusado"


@pytest.mark.asyncio
async def test_recusar_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa recusa de orçamento inexistente."""
    response = await client.patch(
        "/api/orcamentos/id-inexistente/recusar?motivo=Teste",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_recusar_orcamento_sem_motivo(client: AsyncClient, auth_headers: dict, test_cliente_data: dict):
    """Testa recusa de orçamento sem motivo retorna 422 (schema validation)."""
    # Criar cliente
    cliente_response = await client.post(
        "/api/clientes",
        json=test_cliente_data,
        headers=auth_headers
    )
    cliente_id = cliente_response.json()["id"]
    
    # Criar orçamento
    orcamento_data = {
        "cliente_id": cliente_id,
        "titulo": "Orçamento Teste",
        "descricao": "Teste de recusa sem motivo",
        "valor_estimado": 500.00
    }
    orcamento_response = await client.post(
        "/api/orcamentos",
        json=orcamento_data,
        headers=auth_headers
    )
    orcamento_id = orcamento_response.json()["id"]
    
    # Enviar orçamento
    await client.post(
        f"/api/orcamentos/{orcamento_id}/enviar",
        headers=auth_headers
    )
    
    # Recusar sem motivo
    response = await client.patch(
        f"/api/orcamentos/{orcamento_id}/recusar",
        headers=auth_headers
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_aprovar_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa aprovação de orçamento inexistente."""
    response = await client.post(
        "/api/orcamentos/id-inexistente/aprovar",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rejeitar_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa rejeição de orçamento inexistente."""
    response = await client.post(
        "/api/orcamentos/id-inexistente/rejeitar",
        json={"motivo": "Teste"},
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa deleção de orçamento inexistente."""
    response = await client.delete(
        "/api/orcamentos/id-inexistente",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_converter_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa conversão de orçamento inexistente."""
    response = await client.post(
        "/api/orcamentos/id-inexistente/converter",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_adicionar_item_orcamento_inexistente(client: AsyncClient, auth_headers: dict):
    """Testa adicionar item a orçamento inexistente retorna 422 (schema validation)."""
    item_data = {
        "descricao": "Item Teste",
        "quantidade": 1,
        "unidade": "un",
        "valor_unitario": 100.00
    }
    response = await client.post(
        "/api/orcamentos/id-inexistente/itens",
        json=item_data,
        headers=auth_headers
    )
    assert response.status_code == 422
