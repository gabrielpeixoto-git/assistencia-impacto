import pytest


@pytest.mark.asyncio
async def test_listar_usuarios(client, auth_headers):
    """Testa listagem de usuários (apenas admin)."""
    
    response = await client.get("/api/usuarios/", headers=auth_headers)
    assert response.status_code == 200
    usuarios = response.json()
    assert isinstance(usuarios, list)
    assert len(usuarios) >= 1  # Pelo menos o usuário criado no fixture


@pytest.mark.asyncio
async def test_listar_usuarios_sem_autenticacao(client):
    """Testa que listar usuários requer autenticação."""
    response = await client.get("/api/usuarios/")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_obter_usuario_atual(client, auth_headers):
    """Testa obtenção do usuário autenticado."""

    response = await client.get("/api/usuarios/eu", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["email"] is not None
    assert data["nome_completo"] == "Admin Teste"
    assert "id" in data


@pytest.mark.asyncio
async def test_obter_usuario_atual_sem_autenticacao(client):
    """Testa que obter usuário atual requer autenticação."""
    response = await client.get("/api/usuarios/eu")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_obter_usuario_por_id(client, auth_headers):
    """Testa obtenção de usuário por ID (apenas admin)."""
    
    # Primeiro obter o usuário atual para pegar o ID
    eu_response = await client.get("/api/usuarios/eu", headers=auth_headers)
    usuario_id = eu_response.json()["id"]
    
    # Obter usuário por ID
    response = await client.get(f"/api/usuarios/{usuario_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == usuario_id
    assert data["email"] is not None


@pytest.mark.asyncio
async def test_obter_usuario_inexistente(client, auth_headers):
    """Testa obtenção de usuário inexistente."""
    
    response = await client.get("/api/usuarios/id-inexistente", headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_criar_usuario(client, auth_headers):
    """Testa criação de usuário (apenas admin)."""
    
    novo_usuario_data = {
        "email": "novo@example.com",
        "senha": "Senha123!",
        "nome_completo": "Novo Usuário",
        "telefone": "11988888888",
        "perfil": "tecnico"
    }
    
    response = await client.post("/api/usuarios/", json=novo_usuario_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == novo_usuario_data["email"]
    assert data["nome_completo"] == novo_usuario_data["nome_completo"]
    assert data["perfil"] == novo_usuario_data["perfil"]
    assert "id" in data
    assert "senha" not in data  # Senha não deve ser retornada


@pytest.mark.asyncio
async def test_criar_usuario_sem_autenticacao(client):
    """Testa que criar usuário requer autenticação."""
    usuario_data = {
        "email": "teste@example.com",
        "senha": "Senha123!",
        "nome_completo": "Teste",
        "perfil": "tecnico"
    }
    response = await client.post("/api/usuarios/", json=usuario_data)
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_atualizar_usuario(client, auth_headers):
    """Testa atualização de usuário (apenas admin)."""
    
    # Primeiro criar um usuário
    novo_usuario_data = {
        "email": "para-atualizar@example.com",
        "senha": "Senha123!",
        "nome_completo": "Para Atualizar",
        "telefone": "11977777777",
        "perfil": "tecnico"
    }
    
    criar_response = await client.post("/api/usuarios/", json=novo_usuario_data, headers=auth_headers)
    usuario_id = criar_response.json()["id"]
    
    # Atualizar usuário
    update_data = {
        "nome_completo": "Nome Atualizado",
        "telefone": "11966666666",
        "perfil": "gerente"
    }
    
    response = await client.patch(f"/api/usuarios/{usuario_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["nome_completo"] == "Nome Atualizado"
    assert data["telefone"] == "11966666666"
    assert data["perfil"] == "gerente"


@pytest.mark.asyncio
async def test_atualizar_usuario_inexistente(client, auth_headers):
    """Testa atualização de usuário inexistente."""
    
    update_data = {"nome_completo": "Teste"}
    response = await client.patch("/api/usuarios/id-inexistente", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_atualizar_usuario_sem_autenticacao(client):
    """Testa que atualizar usuário requer autenticação."""
    update_data = {"nome_completo": "Teste"}
    response = await client.patch("/api/usuarios/algum-id", json=update_data)
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_deletar_usuario(client, auth_headers):
    """Testa deleção de usuário (apenas admin)."""
    
    # Criar usuário para deletar
    novo_usuario_data = {
        "email": "para-deletar@example.com",
        "senha": "Senha123!",
        "nome_completo": "Para Deletar",
        "telefone": "11955555555",
        "perfil": "tecnico"
    }
    
    criar_response = await client.post("/api/usuarios/", json=novo_usuario_data, headers=auth_headers)
    usuario_id = criar_response.json()["id"]
    
    # Deletar usuário
    response = await client.delete(f"/api/usuarios/{usuario_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verificar que foi deletado
    verificar_response = await client.get(f"/api/usuarios/{usuario_id}", headers=auth_headers)
    assert verificar_response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_usuario_inexistente(client, auth_headers):
    """Testa deleção de usuário inexistente."""
    
    response = await client.delete("/api/usuarios/id-inexistente", headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deletar_usuario_sem_autenticacao(client):
    """Testa que deletar usuário requer autenticação."""
    response = await client.delete("/api/usuarios/algum-id")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_criar_usuario_email_duplicado(client, auth_headers):
    """Testa criação de usuário com email duplicado."""
    
    # Obter o email do usuário atual
    eu_response = await client.get("/api/usuarios/eu", headers=auth_headers)
    email_existente = eu_response.json()["email"]
    
    # Tentar criar usuário com email já existente
    usuario_data = {
        "email": email_existente,
        "senha": "OutraSenha123!",
        "nome_completo": "Outro Usuário",
        "perfil": "tecnico"
    }
    
    response = await client.post("/api/usuarios/", json=usuario_data, headers=auth_headers)
    # Deve retornar erro (400, 409 ou 422)
    assert response.status_code in [400, 409, 422]


@pytest.mark.asyncio
async def test_listar_usuarios_com_paginacao(client, auth_headers):
    """Testa listagem de usuários com paginação."""
    response = await client.get("/api/usuarios/?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200
    usuarios = response.json()
    assert isinstance(usuarios, list)


@pytest.mark.asyncio
async def test_atualizar_usuario_com_senha(client, auth_headers):
    """Testa atualização de usuário incluindo senha."""
    # Criar usuário
    novo_usuario_data = {
        "email": "senha-test@example.com",
        "senha": "Senha123!",
        "nome_completo": "Teste Senha",
        "telefone": "11944444444",
        "perfil": "tecnico"
    }
    criar_response = await client.post("/api/usuarios/", json=novo_usuario_data, headers=auth_headers)
    usuario_id = criar_response.json()["id"]
    
    # Atualizar com senha
    update_data = {
        "nome_completo": "Nome Atualizado",
        "senha": "NovaSenha456!"
    }
    response = await client.patch(f"/api/usuarios/{usuario_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nome_completo"] == "Nome Atualizado"
