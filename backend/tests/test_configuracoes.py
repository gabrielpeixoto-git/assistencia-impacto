import pytest


@pytest.mark.asyncio
async def test_obter_configuracoes(client, auth_headers):
    """Testa obtenção de configurações do sistema."""
    
    response = await client.get("/api/configuracoes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estrutura do response
    assert "nome_empresa" in data
    assert "cnpj_empresa" in data
    assert "telefone_empresa" in data
    assert "email_empresa" in data
    assert "endereco_empresa" in data
    assert "smtp_host" in data
    assert "smtp_porta" in data
    assert "smtp_usuario" in data
    assert "email_remetente" in data
    assert "nome_remetente" in data
    assert "evolution_api_url" in data
    assert "whatsapp_telefone" in data
    assert "viacep_api_url" in data
    assert "url_frontend" in data
    assert "ambiente" in data
    assert "permitir_registro_publico" in data
    assert "tamanho_maximo_upload_mb" in data
    assert "tipos_imagem_permitidos" in data
    
    # Verificar preferências de notificação
    assert "notif_nova_os" in data
    assert "notif_orcamento_aprovado" in data
    assert "notif_orcamento_rejeitado" in data
    assert "notif_agendamento_proximo" in data
    assert "notif_estoque_baixo" in data
    assert "notif_relatorio_semanal" in data
    assert "notif_canal_email" in data
    assert "notif_canal_sistema" in data
    assert "notif_frequencia" in data
    
    # Verificar preferências de aparência
    assert "tema_dark_mode" in data
    assert "tema_cor_primaria" in data
    assert "tema_densidade" in data
    
    # Verificar configurações regionais
    assert "regiao_moeda" in data
    assert "regiao_fuso_horario" in data
    assert "regiao_formato_data" in data
    assert "regiao_idioma" in data


@pytest.mark.asyncio
async def test_obter_configuracoes_sem_autenticacao(client):
    """Testa que obter configurações requer autenticação."""
    response = await client.get("/api/configuracoes")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_atualizar_configuracoes(client, auth_headers):
    """Testa atualização de configurações (requer admin)."""
    
    # O usuário criado é ADMIN, então deve ter permissão
    update_data = {
        "nome_empresa": "Nova Empresa Teste",
        "telefone_empresa": "11999999999",
        "email_empresa": "nova@empresa.com",
        "ambiente": "development",
        "permitir_registro_publico": True
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["nome_empresa"] == "Nova Empresa Teste"
    assert data["telefone_empresa"] == "11999999999"
    assert data["email_empresa"] == "nova@empresa.com"
    assert data["ambiente"] == "development"
    assert data["permitir_registro_publico"] is True


@pytest.mark.asyncio
async def test_atualizar_configuracoes_preferencias_notificacao(client, auth_headers):
    """Testa atualização de preferências de notificação."""
    
    update_data = {
        "notif_nova_os": False,
        "notif_orcamento_aprovado": True,
        "notif_orcamento_rejeitado": True,
        "notif_agendamento_proximo": True,
        "notif_estoque_baixo": False,
        "notif_relatorio_semanal": True,
        "notif_canal_email": True,
        "notif_canal_sistema": False,
        "notif_frequencia": "diario"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["notif_nova_os"] is False
    assert data["notif_orcamento_aprovado"] is True
    assert data["notif_orcamento_rejeitado"] is True
    assert data["notif_agendamento_proximo"] is True
    assert data["notif_estoque_baixo"] is False
    assert data["notif_relatorio_semanal"] is True
    assert data["notif_canal_email"] is True
    assert data["notif_canal_sistema"] is False
    assert data["notif_frequencia"] == "diario"


@pytest.mark.asyncio
async def test_atualizar_configuracoes_preferencias_aparencia(client, auth_headers):
    """Testa atualização de preferências de aparência."""
    
    update_data = {
        "tema_dark_mode": True,
        "tema_cor_primaria": "azul",
        "tema_densidade": "compacto"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["tema_dark_mode"] is True
    assert data["tema_cor_primaria"] == "azul"
    assert data["tema_densidade"] == "compacto"


@pytest.mark.asyncio
async def test_atualizar_configuracoes_regional(client, auth_headers):
    """Testa atualização de configurações regionais."""
    
    update_data = {
        "regiao_moeda": "USD",
        "regiao_fuso_horario": "America/New_York",
        "regiao_formato_data": "MM/DD/YYYY",
        "regiao_idioma": "en-US"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["regiao_moeda"] == "USD"
    assert data["regiao_fuso_horario"] == "America/New_York"
    assert data["regiao_formato_data"] == "MM/DD/YYYY"
    assert data["regiao_idioma"] == "en-US"


@pytest.mark.asyncio
async def test_atualizar_configuracoes_sem_autenticacao(client):
    """Testa que atualizar configurações requer autenticação."""
    update_data = {"nome_empresa": "Teste"}
    response = await client.put("/api/configuracoes", json=update_data)
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_atualizar_configuracoes_upload(client, auth_headers):
    """Testa atualização de configurações de upload."""
    
    update_data = {
        "tamanho_maximo_upload_mb": 10,
        "tipos_imagem_permitidos": "jpg,jpeg,png,webp"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["tamanho_maximo_upload_mb"] == 10
    assert data["tipos_imagem_permitidos"] == "jpg,jpeg,png,webp"


@pytest.mark.asyncio
async def test_atualizar_configuracoes_smtp(client, auth_headers):
    """Testa atualização de configurações SMTP (sem senha)."""
    
    update_data = {
        "smtp_host": "smtp.gmail.com",
        "smtp_porta": 587,
        "smtp_usuario": "teste@gmail.com",
        "email_remetente": "noreply@empresa.com",
        "nome_remetente": "Empresa Teste"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["smtp_host"] == "smtp.gmail.com"
    assert data["smtp_porta"] == 587
    assert data["smtp_usuario"] == "teste@gmail.com"
    assert data["email_remetente"] == "noreply@empresa.com"
    assert data["nome_remetente"] == "Empresa Teste"


@pytest.mark.asyncio
async def test_atualizar_configuracoes_whatsapp(client, auth_headers):
    """Testa atualização de configurações WhatsApp (sem API key)."""
    
    update_data = {
        "evolution_api_url": "http://localhost:3000",
        "whatsapp_telefone": "5511999999999"
    }
    
    response = await client.put("/api/configuracoes", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["evolution_api_url"] == "http://localhost:3000"
    assert data["whatsapp_telefone"] == "5511999999999"


@pytest.mark.asyncio
async def test_exportar_dados(client, auth_headers):
    """Testa exportação de dados do sistema (requer admin)."""
    response = await client.get("/api/configuracoes/exportar-dados", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_exportar_dados_sem_autenticacao(client):
    """Testa que exportar dados requer autenticação."""
    response = await client.get("/api/configuracoes/exportar-dados")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_limpar_cache(client, auth_headers):
    """Testa limpeza de cache (requer admin)."""
    response = await client.delete("/api/configuracoes/limpar-cache", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data


@pytest.mark.asyncio
async def test_limpar_cache_sem_autenticacao(client):
    """Testa que limpar cache requer autenticação."""
    response = await client.delete("/api/configuracoes/limpar-cache")
    assert response.status_code in [401, 403]
