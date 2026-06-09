import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_dashboard_resumo(client, auth_headers):
    """Testa endpoint de resumo do dashboard."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estrutura do response
    assert "os_hoje" in data
    assert "os_semana" in data
    assert "receita_mes" in data
    assert "despesas_mes" in data
    assert "lucro_mes" in data
    assert "orcamentos_pendentes" in data
    assert "pagamentos_atrasados" in data
    assert "itens_estoque_critico" in data
    assert "os_por_status" in data
    assert "grafico_receita" in data
    assert "top_clientes" in data
    assert "top_tecnicos" in data
    assert "os_recentes" in data
    assert "agenda_proximos_dias" in data
    
    # Verificar tipos de dados
    assert isinstance(data["os_hoje"], int)
    assert isinstance(data["os_semana"], int)
    assert isinstance(data["receita_mes"], (int, float))
    assert isinstance(data["despesas_mes"], (int, float))
    assert isinstance(data["lucro_mes"], (int, float))
    assert isinstance(data["orcamentos_pendentes"], int)
    assert isinstance(data["pagamentos_atrasados"], int)
    assert isinstance(data["itens_estoque_critico"], int)
    assert isinstance(data["os_por_status"], list)
    assert isinstance(data["grafico_receita"], list)
    assert isinstance(data["top_clientes"], list)
    assert isinstance(data["top_tecnicos"], list)
    assert isinstance(data["os_recentes"], list)
    assert isinstance(data["agenda_proximos_dias"], list)


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_hoje(client, auth_headers):
    """Testa dashboard com filtro de período 'hoje'."""
    
    response = await client.get("/api/dashboard/resumo?periodo=hoje", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_semana(client, auth_headers):
    """Testa dashboard com filtro de período 'semana'."""
    
    response = await client.get("/api/dashboard/resumo?periodo=semana", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_mes(client, auth_headers):
    """Testa dashboard com filtro de período 'mes'."""
    
    response = await client.get("/api/dashboard/resumo?periodo=mes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_trimestre(client, auth_headers):
    """Testa dashboard com filtro de período 'trimestre'."""
    
    response = await client.get("/api/dashboard/resumo?periodo=trimestre", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_ano(client, auth_headers):
    """Testa dashboard com filtro de período 'ano'."""
    
    response = await client.get("/api/dashboard/resumo?periodo=ano", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_resumo_periodo_customizado(client, auth_headers):
    """Testa dashboard com filtro de período customizado."""
    
    data_inicio = datetime(2024, 1, 1).isoformat()
    data_fim = datetime(2024, 12, 31).isoformat()
    
    response = await client.get(
        f"/api/dashboard/resumo?data_inicio={data_inicio}&data_fim={data_fim}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "receita_mes" in data
    assert "grafico_receita" in data


@pytest.mark.asyncio
async def test_dashboard_sem_autenticacao(client):
    """Testa que dashboard requer autenticação."""
    response = await client.get("/api/dashboard/resumo")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_dashboard_grafico_receita_estrutura(client, auth_headers):
    """Testa estrutura do gráfico de receita."""
    
    response = await client.get("/api/dashboard/resumo?periodo=semana", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    grafico = data["grafico_receita"]
    assert isinstance(grafico, list)
    
    if len(grafico) > 0:
        item = grafico[0]
        assert "data" in item
        assert "valor" in item
        assert isinstance(item["valor"], (int, float))


@pytest.mark.asyncio
async def test_dashboard_os_por_status_estrutura(client, auth_headers):
    """Testa estrutura de OS por status."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    os_por_status = data["os_por_status"]
    assert isinstance(os_por_status, list)
    
    for item in os_por_status:
        assert "status" in item
        assert "quantidade" in item
        assert isinstance(item["quantidade"], int)


@pytest.mark.asyncio
async def test_dashboard_top_clientes_estrutura(client, auth_headers):
    """Testa estrutura de top clientes."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    top_clientes = data["top_clientes"]
    assert isinstance(top_clientes, list)
    
    for item in top_clientes:
        assert "id" in item
        assert "nome" in item
        assert "total" in item
        assert isinstance(item["total"], (int, float))


@pytest.mark.asyncio
async def test_dashboard_top_tecnicos_estrutura(client, auth_headers):
    """Testa estrutura de top técnicos."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    top_tecnicos = data["top_tecnicos"]
    assert isinstance(top_tecnicos, list)
    
    for item in top_tecnicos:
        assert "tecnico_id" in item
        assert "quantidade" in item
        assert isinstance(item["quantidade"], int)


@pytest.mark.asyncio
async def test_dashboard_os_recentes_estrutura(client, auth_headers):
    """Testa estrutura de OS recentes."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    os_recentes = data["os_recentes"]
    assert isinstance(os_recentes, list)
    
    for item in os_recentes:
        assert "id" in item
        assert "numero_os" in item
        assert "titulo" in item
        assert "status" in item
        assert "prioridade" in item


@pytest.mark.asyncio
async def test_dashboard_agenda_proximos_dias_estrutura(client, auth_headers):
    """Testa estrutura de agenda próximos dias."""
    
    response = await client.get("/api/dashboard/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    agenda = data["agenda_proximos_dias"]
    assert isinstance(agenda, list)
    
    for item in agenda:
        assert "id" in item
        assert "titulo" in item
        assert "data_hora_inicio" in item
        assert "data_hora_fim" in item
        assert "tipo_evento" in item
        assert "status" in item
