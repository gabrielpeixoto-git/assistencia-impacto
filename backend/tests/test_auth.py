import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_registrar_usuario(client: AsyncClient, test_user_data: dict):
    """Testa registro de novo usuário."""
    response = await client.post("/api/auth/registrar", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "mensagem" in data
    assert "usuario_id" in data


@pytest.mark.asyncio
async def test_registrar_email_duplicado(client: AsyncClient, test_user_data: dict):
    """Testa erro ao registrar usuário com email duplicado."""
    # Primeiro registro
    await client.post("/api/auth/registrar", json=test_user_data)
    
    # Tentativa de registro duplicado
    response = await client.post("/api/auth/registrar", json=test_user_data)
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient, test_user_data: dict):
    """Testa login com credenciais corretas."""
    # Registrar usuário primeiro
    await client.post("/api/auth/registrar", json=test_user_data)
    
    # Login
    login_data = {
        "email": test_user_data["email"],
        "senha": test_user_data["senha"]
    }
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_senha_incorreta(client: AsyncClient, test_user_data: dict):
    """Testa login com senha incorreta."""
    # Registrar usuário primeiro
    await client.post("/api/auth/registrar", json=test_user_data)
    
    # Login com senha incorreta
    login_data = {
        "email": test_user_data["email"],
        "senha": "SenhaErrada123!"
    }
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_obter_usuario_atual(client: AsyncClient, auth_headers: dict):
    """Testa obter usuário atual com token válido."""
    # Obter usuário atual
    response = await client.get(
        "/api/usuarios/eu",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "nome_completo" in data


@pytest.mark.asyncio
async def test_obter_usuario_sem_token(client: AsyncClient):
    """Testa obter usuário atual sem token."""
    response = await client.get("/api/usuarios/eu")
    
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_alterar_senha_senha_incorreta(client: AsyncClient, auth_headers: dict):
    """Testa alteração de senha com senha atual incorreta."""
    # Tentar alterar senha com senha incorreta
    alterar_senha_data = {
        "senha_atual": "SenhaIncorreta123!",
        "nova_senha": "NovaSenha123!",
        "confirmar_senha": "NovaSenha123!"
    }
    response = await client.put(
        "/api/auth/alterar-senha",
        json=alterar_senha_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token_invalido(client: AsyncClient):
    """Testa refresh com token inválido."""
    response = await client.post("/api/auth/refresh", json={"refresh_token": "token-invalido"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_endpoint(client: AsyncClient, admin_headers: dict):
    """Testa endpoint de logout."""
    # Fazer login para obter refresh_token
    login_response = await client.post("/api/auth/login", json={
        "email": "admin@teste.com",
        "senha": "Admin123!"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Fazer logout - o endpoint espera refresh_token no body
    response = await client.post(
        "/api/auth/logout",
        params={"refresh_token": refresh_token}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_encerrar_sessao_inexistente(client: AsyncClient, admin_headers: dict):
    """Testa encerrar sessão inexistente."""
    response = await client.delete("/api/auth/sessoes/sessao-inexistente", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_alterar_senha_senha_atual_incorreta(client: AsyncClient, auth_headers: dict):
    """Testa erro ao alterar senha com senha atual incorreta."""
    # Tentar alterar com senha incorreta
    alterar_senha_data = {
        "senha_atual": "SenhaErrada123!",
        "nova_senha": "NovaSenha123!",
        "confirmar_senha": "NovaSenha123!"
    }
    response = await client.put(
        "/api/auth/alterar-senha",
        json=alterar_senha_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_alterar_senha_confirmacao_diferente(client: AsyncClient, auth_headers: dict):
    """Testa erro ao alterar senha com confirmação diferente."""
    # Tentar alterar com confirmação diferente
    alterar_senha_data = {
        "senha_atual": "Senha123!",
        "nova_senha": "NovaSenha123!",
        "confirmar_senha": "SenhaDiferente123!"
    }
    response = await client.put(
        "/api/auth/alterar-senha",
        json=alterar_senha_data,
        headers=auth_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_listar_sessoes(client: AsyncClient, auth_headers: dict):
    """Testa listagem de sessões ativas do usuário."""
    # Listar sessões
    response = await client.get(
        "/api/auth/sessoes",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_encerrar_sessao(client: AsyncClient, auth_headers: dict, test_user_data: dict):
    """Testa encerramento de sessão específica."""
    # Registrar e fazer login
    await client.post("/api/auth/registrar", json=test_user_data)
    login_response = await client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "senha": test_user_data["senha"]
    })
    token = login_response.json()["access_token"]
    
    # Listar sessões para obter uma sessão_id
    sessoes_response = await client.get(
        "/api/auth/sessoes",
        headers={"Authorization": f"Bearer {token}"}
    )
    sessoes = sessoes_response.json()
    
    if len(sessoes) > 0:
        sessao_id = sessoes[0]["id"]
        
        # Encerrar sessão
        response = await client.delete(
            f"/api/auth/sessoes/{sessao_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_encerrar_sessao_inexistente(client: AsyncClient, admin_headers: dict):
    """Testa erro ao encerrar sessão inexistente."""
    # Tentar encerrar sessão inexistente
    response = await client.delete(
        "/api/auth/sessoes/sessao-inexistente",
        headers=admin_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_encerrar_outras_sessoes(client: AsyncClient, auth_headers: dict):
    """Testa encerramento de todas as outras sessões."""
    # Encerrar outras sessões
    response = await client.delete(
        "/api/auth/sessoes",
        headers=auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_listar_historico_acesso(client: AsyncClient, auth_headers: dict):
    """Testa listagem de histórico de acessos do usuário."""
    # Listar histórico
    response = await client.get(
        "/api/auth/historico-acesso",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
