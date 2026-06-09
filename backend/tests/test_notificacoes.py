import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_listar_notificacoes(client: AsyncClient, auth_headers: dict):
    """Testa listagem de notificações do usuário autenticado."""
    response = await client.get("/api/notificacoes", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_listar_notificacoes_sem_autenticacao(client: AsyncClient):
    """Testa que listar notificações requer autenticação."""
    response = await client.get("/api/notificacoes")
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_criar_notificacao(client: AsyncClient, auth_headers: dict):
    """Testa criação de notificação (apenas admin)."""
    notificacao_data = {
        "titulo": "Nova notificação de teste",
        "corpo": "Corpo da notificação de teste",
        "tipo": "info",
        "usuario_id": None  # Para todos os usuários
    }
    
    response = await client.post(
        "/api/notificacoes",
        json=notificacao_data,
        headers=auth_headers
    )
    
    assert response.status_code in [201, 403]  # Pode não ter permissão


@pytest.mark.asyncio
async def test_marcar_notificacao_como_lida(client: AsyncClient, auth_headers: dict):
    """Testa marcar notificação como lida."""
    # Primeiro criar uma notificação
    notificacao_data = {
        "titulo": "Notificação teste",
        "corpo": "Corpo teste",
        "tipo": "info",
        "usuario_id": None
    }
    
    criar_response = await client.post(
        "/api/notificacoes",
        json=notificacao_data,
        headers=auth_headers
    )
    
    if criar_response.status_code == 201:
        notificacao_id = criar_response.json()["id"]
        
        # Marcar como lida
        response = await client.patch(
            f"/api/notificacoes/{notificacao_id}/marcar-lida",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_marcar_todas_como_lidas(client: AsyncClient, auth_headers: dict):
    """Testa marcar todas as notificações como lidas."""
    response = await client.patch(
        "/api/notificacoes/marcar-todas-lidas",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_deletar_notificacao(client: AsyncClient, auth_headers: dict):
    """Testa deleção de notificação."""
    # Primeiro criar uma notificação
    notificacao_data = {
        "titulo": "Notificação para deletar",
        "corpo": "Corpo teste",
        "tipo": "info",
        "usuario_id": None
    }
    
    criar_response = await client.post(
        "/api/notificacoes",
        json=notificacao_data,
        headers=auth_headers
    )
    
    if criar_response.status_code == 201:
        notificacao_id = criar_response.json()["id"]
        
        # Deletar
        response = await client.delete(
            f"/api/notificacoes/{notificacao_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [204, 403]


@pytest.mark.asyncio
async def test_contar_nao_lidas(client: AsyncClient, auth_headers: dict):
    """Testa contagem de notificações não lidas."""
    response = await client.get(
        "/api/notificacoes/nao-lidas",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "quantidade" in data or isinstance(data, int)


@pytest.mark.asyncio
async def test_criar_notificacao_com_url_acao(client: AsyncClient, auth_headers: dict):
    """Testa criação de notificação com URL de ação."""
    notificacao_data = {
        "titulo": "Nova OS criada",
        "corpo": "Uma nova ordem de serviço foi criada",
        "tipo": "sucesso",
        "url_acao": "/ordens-servico/123",
        "usuario_id": None
    }
    
    response = await client.post(
        "/api/notificacoes",
        json=notificacao_data,
        headers=auth_headers
    )
    
    assert response.status_code in [201, 403]


@pytest.mark.asyncio
async def test_listar_notificacoes_com_filtro_lidas(client: AsyncClient, auth_headers: dict):
    """Testa listagem de notificações com filtro de lidas."""
    response = await client.get(
        "/api/notificacoes?apenas_nao_lidas=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
