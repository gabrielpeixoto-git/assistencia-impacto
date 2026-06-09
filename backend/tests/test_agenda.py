import pytest
from datetime import datetime, timedelta
from app.models.agenda import Agenda, TipoEvento, StatusEvento


@pytest.mark.asyncio
async def test_listar_agenda_vazia(client, auth_headers):
    """Testa listagem de agenda vazia."""
    response = await client.get("/api/agenda", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_criar_evento_agenda(client, auth_headers):
    """Testa criação de evento na agenda."""
    evento_data = {
        "titulo": "Visita Técnica",
        "descricao": "Instalação de ar condicionado",
        "data_hora_inicio": (datetime.now() + timedelta(days=1)).isoformat(),
        "data_hora_fim": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    response = await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == evento_data["titulo"]
    assert data["tipo_evento"] == "servico"
    assert "id" in data


@pytest.mark.asyncio
async def test_obter_evento_agenda(client, auth_headers):
    """Testa obtenção de evento específico."""
    evento_data = {
        "titulo": "Manutenção",
        "descricao": "Manutenção preventiva",
        "data_hora_inicio": (datetime.now() + timedelta(days=2)).isoformat(),
        "data_hora_fim": (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
        "tipo_evento": "manutencao",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    criar_response = await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    evento_id = criar_response.json()["id"]
    
    # Obter evento
    response = await client.get(f"/api/agenda/{evento_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == evento_id
    assert data["titulo"] == evento_data["titulo"]


@pytest.mark.asyncio
async def test_obter_evento_inexistente(client, auth_headers):
    """Testa obtenção de evento inexistente."""
    response = await client.get("/api/agenda/id-inexistente", headers=auth_headers)
    assert response.status_code == 404
    # Verificar se a resposta contém a mensagem de erro
    if response.headers.get("content-type", "").startswith("application/json"):
        assert "não encontrado" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_atualizar_evento_agenda(client, auth_headers):
    """Testa atualização de evento."""
    evento_data = {
        "titulo": "Visita Original",
        "descricao": "Descrição original",
        "data_hora_inicio": (datetime.now() + timedelta(days=3)).isoformat(),
        "data_hora_fim": (datetime.now() + timedelta(days=3, hours=2)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    criar_response = await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    evento_id = criar_response.json()["id"]
    
    # Atualizar evento
    update_data = {
        "titulo": "Visita Atualizada",
        "status": "confirmado"
    }
    
    response = await client.put(f"/api/agenda/{evento_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Visita Atualizada"
    assert data["status"] == "confirmado"


@pytest.mark.asyncio
async def test_deletar_evento_agenda(client, auth_headers):
    """Testa deleção de evento."""
    evento_data = {
        "titulo": "Evento para deletar",
        "descricao": "Será deletado",
        "data_hora_inicio": (datetime.now() + timedelta(days=4)).isoformat(),
        "data_hora_fim": (datetime.now() + timedelta(days=4, hours=1)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    criar_response = await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    evento_id = criar_response.json()["id"]
    
    # Deletar evento
    response = await client.delete(f"/api/agenda/{evento_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verificar que foi deletado
    verificar_response = await client.get(f"/api/agenda/{evento_id}", headers=auth_headers)
    assert verificar_response.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_status_evento(client, auth_headers):
    """Testa atualização de status de evento."""
    evento_data = {
        "titulo": "Evento de teste",
        "descricao": "Teste de status",
        "data_hora_inicio": (datetime.now() + timedelta(days=5)).isoformat(),
        "data_hora_fim": (datetime.now() + timedelta(days=5, hours=1)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    criar_response = await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    evento_id = criar_response.json()["id"]
    
    # Atualizar status
    status_data = {"status": "concluido"}
    response = await client.put(f"/api/agenda/{evento_id}/status", json=status_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "concluido"


@pytest.mark.asyncio
async def test_listar_eventos_mes(client, auth_headers):
    """Testa listagem de eventos de um mês específico."""
    hoje = datetime.now()
    evento_data = {
        "titulo": "Evento do mês",
        "descricao": "Evento deste mês",
        "data_hora_inicio": hoje.isoformat(),
        "data_hora_fim": (hoje + timedelta(hours=2)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "test-tecnico-id"
    }
    
    await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    
    # Listar eventos do mês atual
    response = await client.get(f"/api/agenda/calendario/{hoje.year}/{hoje.month}", headers=auth_headers)
    assert response.status_code == 200
    eventos = response.json()
    assert len(eventos) >= 1


@pytest.mark.asyncio
async def test_listar_agenda_com_filtros(client, auth_headers):
    """Testa listagem de agenda com filtros."""
    hoje = datetime.now()
    evento_data = {
        "titulo": "Evento filtrado",
        "descricao": "Teste de filtros",
        "data_hora_inicio": hoje.isoformat(),
        "data_hora_fim": (hoje + timedelta(hours=2)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "cliente-filtro-id",
        "tecnico_id": "tecnico-filtro-id"
    }
    
    await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    
    # Filtrar por tecnico_id
    response = await client.get("/api/agenda?tecnico_id=tecnico-filtro-id", headers=auth_headers)
    assert response.status_code == 200
    
    # Filtrar por cliente_id
    response = await client.get("/api/agenda?cliente_id=cliente-filtro-id", headers=auth_headers)
    assert response.status_code == 200
    
    # Filtrar por tipo_evento
    response = await client.get("/api/agenda?tipo_evento=servico", headers=auth_headers)
    assert response.status_code == 200
    
    # Filtrar por status
    response = await client.get("/api/agenda?status=agendado", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_atualizar_status_evento_inexistente(client, auth_headers):
    """Testa atualização de status de evento inexistente."""
    status_data = {"status": "concluido"}
    response = await client.put("/api/agenda/id-inexistente/status", json=status_data, headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_evento_inexistente(client, auth_headers):
    """Testa deleção de evento inexistente."""
    response = await client.delete("/api/agenda/id-inexistente", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_eventos_mes_com_tecnico(client, auth_headers):
    """Testa listagem de eventos do mês com filtro de técnico."""
    hoje = datetime.now()
    evento_data = {
        "titulo": "Evento tecnico",
        "descricao": "Evento com técnico específico",
        "data_hora_inicio": hoje.isoformat(),
        "data_hora_fim": (hoje + timedelta(hours=2)).isoformat(),
        "tipo_evento": "servico",
        "status": "agendado",
        "cliente_id": "test-cliente-id",
        "tecnico_id": "tecnico-especifico-id"
    }
    
    await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    
    # Listar eventos do mês com filtro de tecnico
    response = await client.get(f"/api/agenda/calendario/{hoje.year}/{hoje.month}?tecnico_id=tecnico-especifico-id", headers=auth_headers)
    assert response.status_code == 200
    eventos = response.json()
    assert isinstance(eventos, list)
