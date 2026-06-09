import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_verificar_disponibilidade_sem_conflito(client: AsyncClient, auth_headers: dict):
    """Testa verificação de disponibilidade sem conflito (horário livre)."""
    # Criar um técnico primeiro
    tecnico_data = {
        "email": "tecnico@teste.com",
        "senha": "Tecnico123!",
        "nome_completo": "Técnico Teste",
        "perfil": "tecnico"
    }
    await client.post("/api/auth/registrar", json=tecnico_data)
    
    login_response = await client.post("/api/auth/login", json={
        "email": "tecnico@teste.com",
        "senha": "Tecnico123!"
    })
    tecnico_id = login_response.json()["usuario"]["id"]
    
    # Verificar disponibilidade em horário futuro (deve estar livre)
    inicio = (datetime.now() + timedelta(days=1, hours=10)).isoformat()
    fim = (datetime.now() + timedelta(days=1, hours=11)).isoformat()
    
    response = await client.get(
        f"/api/agenda/disponibilidade?tecnico_id={tecnico_id}&inicio={inicio}&fim={fim}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] == True
    assert data["dados"]["disponivel"] == True
    assert len(data["dados"]["conflitos"]) == 0


@pytest.mark.asyncio
async def test_verificar_disponibilidade_com_conflito(client: AsyncClient, auth_headers: dict):
    """Testa verificação de disponibilidade com conflito (horário ocupado)."""
    # Criar técnico
    tecnico_data = {
        "email": "tecnico2@teste.com",
        "senha": "Tecnico123!",
        "nome_completo": "Técnico Teste 2",
        "perfil": "tecnico"
    }
    await client.post("/api/auth/registrar", json=tecnico_data)
    
    login_response = await client.post("/api/auth/login", json={
        "email": "tecnico2@teste.com",
        "senha": "Tecnico123!"
    })
    tecnico_id = login_response.json()["usuario"]["id"]
    
    # Criar um evento na agenda
    evento_inicio = datetime.now() + timedelta(days=2, hours=10)
    evento_fim = datetime.now() + timedelta(days=2, hours=11)
    
    evento_data = {
        "tecnico_id": tecnico_id,
        "titulo": "Serviço Teste",
        "data_hora_inicio": evento_inicio.isoformat(),
        "data_hora_fim": evento_fim.isoformat(),
        "tipo_evento": "servico",
        "status": "confirmado"
    }
    await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    
    # Verificar disponibilidade no mesmo horário (deve ter conflito)
    response = await client.get(
        f"/api/agenda/disponibilidade?tecnico_id={tecnico_id}&inicio={evento_inicio.isoformat()}&fim={evento_fim.isoformat()}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] == True
    assert data["dados"]["disponivel"] == False
    assert len(data["dados"]["conflitos"]) > 0


@pytest.mark.asyncio
async def test_mapa_rotas_dia(client: AsyncClient, auth_headers: dict):
    """Testa endpoint de mapa de rotas do dia."""
    # Criar técnico
    tecnico_data = {
        "email": "tecnico3@teste.com",
        "senha": "Tecnico123!",
        "nome_completo": "Técnico Teste 3",
        "perfil": "tecnico"
    }
    await client.post("/api/auth/registrar", json=tecnico_data)
    
    login_response = await client.post("/api/auth/login", json={
        "email": "tecnico3@teste.com",
        "senha": "Tecnico123!"
    })
    tecnico_id = login_response.json()["usuario"]["id"]
    
    # Criar evento com coordenadas
    data_evento = datetime.now() + timedelta(days=3)
    evento_data = {
        "tecnico_id": tecnico_id,
        "titulo": "Visita Técnica",
        "data_hora_inicio": data_evento.isoformat(),
        "data_hora_fim": (data_evento + timedelta(hours=1)).isoformat(),
        "tipo_evento": "servico",
        "status": "confirmado",
        "latitude": -23.5505,
        "longitude": -46.6333
    }
    await client.post("/api/agenda", json=evento_data, headers=auth_headers)
    
    # Buscar mapa de rotas
    data_str = data_evento.date().isoformat()
    response = await client.get(
        f"/api/agenda/mapa?tecnico_id={tecnico_id}&data={data_str}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sucesso"] == True
    assert "dados" in data
    assert "distancia_total_km" in data["dados"]
    assert "eventos" in data["dados"]
