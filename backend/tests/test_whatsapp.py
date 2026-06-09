"""Testes básicos do router de WhatsApp."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_endpoint_whatsapp_status_requer_autenticacao(client: AsyncClient):
    """Endpoint /status requer autenticação."""
    response = await client.get("/api/whatsapp/status")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_endpoint_whatsapp_status_com_autenticacao(client: AsyncClient, auth_headers: dict):
    """Endpoint /status retorna resposta com autenticação."""
    response = await client.get("/api/whatsapp/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "ativo" in data
    assert "configurado" in data


@pytest.mark.asyncio
async def test_endpoint_enviar_orcamento_requer_autenticacao(client: AsyncClient):
    """Endpoint /enviar-orcamento requer autenticação."""
    response = await client.post("/api/whatsapp/enviar-orcamento", json={"orcamento_id": "test-id"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_endpoint_enviar_orcamento_orcamento_nao_encontrado(client: AsyncClient, auth_headers: dict):
    """Endpoint /enviar-orcamento retorna 404 para orçamento inexistente."""
    response = await client.post(
        "/api/whatsapp/enviar-orcamento",
        json={"orcamento_id": "id-inexistente"},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_confirmar_os_requer_autenticacao(client: AsyncClient):
    """Endpoint /confirmar-os requer autenticação."""
    response = await client.post("/api/whatsapp/confirmar-os", json={"os_id": "test-id"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_endpoint_confirmar_os_os_nao_encontrada(client: AsyncClient, auth_headers: dict):
    """Endpoint /confirmar-os retorna 404 para OS inexistente."""
    response = await client.post(
        "/api/whatsapp/confirmar-os",
        json={"os_id": "id-inexistente"},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_concluir_os_requer_autenticacao(client: AsyncClient):
    """Endpoint /concluir-os requer autenticação."""
    response = await client.post("/api/whatsapp/concluir-os", json={"os_id": "test-id"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_endpoint_concluir_os_os_nao_encontrada(client: AsyncClient, auth_headers: dict):
    """Endpoint /concluir-os retorna 404 para OS inexistente."""
    response = await client.post(
        "/api/whatsapp/concluir-os",
        json={"os_id": "id-inexistente"},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_lembrete_pagamento_requer_autenticacao(client: AsyncClient):
    """Endpoint /lembrete-pagamento requer autenticação."""
    response = await client.post("/api/whatsapp/lembrete-pagamento", json={"transacao_id": "test-id"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_endpoint_lembrete_pagamento_transacao_nao_encontrada(client: AsyncClient, auth_headers: dict):
    """Endpoint /lembrete-pagamento retorna 404 para transação inexistente."""
    response = await client.post(
        "/api/whatsapp/lembrete-pagamento",
        json={"transacao_id": "id-inexistente"},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_enviar_orcamento_whatsapp_sucesso(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Testa envio de orçamento via WhatsApp com sucesso."""
    from app.models.cliente import Cliente
    from app.models.orcamento import Orcamento
    from app.models.usuario import Usuario
    from sqlalchemy import select
    import uuid

    # Buscar usuário criado pela fixture
    result = await db_session.execute(select(Usuario).where(Usuario.email == "admin@teste.com"))
    usuario = result.scalar_one_or_none()

    # Criar cliente com WhatsApp
    cliente = Cliente(
        id=str(uuid.uuid4()),
        nome="João Silva",
        email="joao@example.com",
        telefone="11999999999",
        whatsapp="5511999999999",
        tipo_cliente="residencial",
        criado_por=usuario.id
    )
    db_session.add(cliente)

    # Criar orçamento
    orcamento = Orcamento(
        id=str(uuid.uuid4()),
        cliente_id=cliente.id,
        criado_por=usuario.id,
        numero_orcamento="ORC001",
        titulo="Orçamento Teste",
        descricao="Descrição teste",
        total=1000.0
    )
    db_session.add(orcamento)
    await db_session.commit()

    with patch('app.routers.whatsapp.WhatsAppService.enviar_orcamento_whatsapp', new_callable=AsyncMock) as mock_envio:
        mock_envio.return_value = True

        response = await client.post(
            "/api/whatsapp/enviar-orcamento",
            json={"orcamento_id": orcamento.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data


@pytest.mark.asyncio
async def test_enviar_orcamento_whatsapp_sem_whatsapp(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Testa erro ao enviar orçamento para cliente sem WhatsApp."""
    from app.models.cliente import Cliente
    from app.models.orcamento import Orcamento
    from app.models.usuario import Usuario
    from sqlalchemy import select
    import uuid

    # Buscar usuário criado pela fixture
    result = await db_session.execute(select(Usuario).where(Usuario.email == "admin@teste.com"))
    usuario = result.scalar_one_or_none()

    # Criar cliente SEM WhatsApp
    cliente = Cliente(
        id=str(uuid.uuid4()),
        nome="Maria Santos",
        email="maria@example.com",
        telefone="11888888888",
        whatsapp=None,
        tipo_cliente="residencial",
        criado_por=usuario.id
    )
    db_session.add(cliente)

    # Criar orçamento
    orcamento = Orcamento(
        id=str(uuid.uuid4()),
        cliente_id=cliente.id,
        criado_por=usuario.id,
        numero_orcamento="ORC002",
        titulo="Orçamento Teste",
        descricao="Descrição teste",
        total=1500.0
    )
    db_session.add(orcamento)
    await db_session.commit()

    response = await client.post(
        "/api/whatsapp/enviar-orcamento",
        json={"orcamento_id": orcamento.id},
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_confirmar_os_whatsapp_sucesso(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Testa confirmação de OS via WhatsApp com sucesso."""
    from app.models.cliente import Cliente
    from app.models.ordem_servico import OrdemServico
    from app.models.usuario import Usuario
    from app.models.categoria_servico import CategoriaServico
    from sqlalchemy import select
    import uuid

    # Buscar usuário criado pela fixture
    result = await db_session.execute(select(Usuario).where(Usuario.email == "admin@teste.com"))
    usuario = result.scalar_one_or_none()

    # Criar categoria de serviço
    categoria = CategoriaServico(
        id=str(uuid.uuid4()),
        nome="Reparo",
        descricao="Serviços de reparo",
        icone="wrench",
        cor="#6C63FF"
    )
    db_session.add(categoria)

    # Criar cliente com WhatsApp
    cliente = Cliente(
        id=str(uuid.uuid4()),
        nome="Pedro Oliveira",
        email="pedro@example.com",
        telefone="11777777777",
        whatsapp="5511777777777",
        tipo_cliente="residencial",
        logradouro="Rua Teste",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        criado_por=usuario.id
    )
    db_session.add(cliente)

    # Criar técnico
    tecnico = Usuario(
        id=str(uuid.uuid4()),
        email="tecnico@example.com",
        senha_hash="hash",
        nome_completo="Técnico Teste",
        perfil="tecnico",
        ativo=True
    )
    db_session.add(tecnico)

    # Criar OS
    os_data = OrdemServico(
        id=str(uuid.uuid4()),
        cliente_id=cliente.id,
        tecnico_id=tecnico.id,
        tipo_servico_id=categoria.id,
        numero_os="OS001",
        titulo="Serviço Teste",
        descricao="Descrição teste",
        data_agendada=None,
        status="confirmada",
        criado_por=usuario.id
    )
    db_session.add(os_data)
    await db_session.commit()

    with patch('app.routers.whatsapp.WhatsAppService.enviar_confirmacao_os_whatsapp', new_callable=AsyncMock) as mock_envio:
        mock_envio.return_value = True

        response = await client.post(
            "/api/whatsapp/confirmar-os",
            json={"os_id": os_data.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data


@pytest.mark.asyncio
async def test_concluir_os_whatsapp_sucesso(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Testa envio de OS concluída via WhatsApp com sucesso."""
    from app.models.cliente import Cliente
    from app.models.ordem_servico import OrdemServico
    from app.models.usuario import Usuario
    from app.models.categoria_servico import CategoriaServico
    from sqlalchemy import select
    import uuid

    # Buscar usuário criado pela fixture
    result = await db_session.execute(select(Usuario).where(Usuario.email == "admin@teste.com"))
    usuario = result.scalar_one_or_none()

    # Criar categoria de serviço
    categoria = CategoriaServico(
        id=str(uuid.uuid4()),
        nome="Instalação",
        descricao="Serviços de instalação",
        icone="tool",
        cor="#FF6C63"
    )
    db_session.add(categoria)

    # Criar cliente com WhatsApp
    cliente = Cliente(
        id=str(uuid.uuid4()),
        nome="Ana Costa",
        email="ana@example.com",
        telefone="11666666666",
        whatsapp="5511666666666",
        tipo_cliente="residencial",
        criado_por=usuario.id
    )
    db_session.add(cliente)

    # Criar técnico
    tecnico = Usuario(
        id=str(uuid.uuid4()),
        email="tecnico2@example.com",
        senha_hash="hash",
        nome_completo="Técnico Teste 2",
        perfil="tecnico",
        ativo=True
    )
    db_session.add(tecnico)

    # Criar OS
    os_data = OrdemServico(
        id=str(uuid.uuid4()),
        cliente_id=cliente.id,
        tecnico_id=tecnico.id,
        tipo_servico_id=categoria.id,
        numero_os="OS002",
        titulo="Serviço Teste 2",
        descricao="Descrição teste 2",
        valor_estimado=500.0,
        valor_final=500.0,
        status="concluida",
        token_acesso_publico="token123",
        criado_por=usuario.id
    )
    db_session.add(os_data)
    await db_session.commit()

    with patch('app.routers.whatsapp.WhatsAppService.enviar_mensagem', new_callable=AsyncMock) as mock_envio:
        mock_envio.return_value = True

        response = await client.post(
            "/api/whatsapp/concluir-os",
            json={"os_id": os_data.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data


@pytest.mark.asyncio
async def test_lembrete_pagamento_whatsapp_sucesso(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Testa envio de lembrete de pagamento via WhatsApp com sucesso."""
    from app.models.cliente import Cliente
    from app.models.financeiro import Transacao
    from app.models.usuario import Usuario
    from sqlalchemy import select
    import uuid
    from datetime import date

    # Buscar usuário criado pela fixture
    result = await db_session.execute(select(Usuario).where(Usuario.email == "admin@teste.com"))
    usuario = result.scalar_one_or_none()

    # Criar categoria financeira
    from app.models.financeiro import CategoriaFinanceira
    categoria_fin = CategoriaFinanceira(
        id=str(uuid.uuid4()),
        nome="Serviços",
        tipo="receita",
        cor="#6C63FF",
        icone="dollar-sign"
    )
    db_session.add(categoria_fin)

    # Criar cliente com WhatsApp
    cliente = Cliente(
        id=str(uuid.uuid4()),
        nome="Carlos Lima",
        email="carlos@example.com",
        telefone="11555555555",
        whatsapp="5511555555555",
        tipo_cliente="residencial",
        criado_por=usuario.id
    )
    db_session.add(cliente)

    # Criar transação
    transacao = Transacao(
        id=str(uuid.uuid4()),
        numero_transacao="TRX001",
        categoria_id=categoria_fin.id,
        cliente_id=cliente.id,
        tipo="receita",
        valor=1000.0,
        descricao="Serviço realizado",
        data_vencimento=date(2026, 12, 31),
        status="pendente",
        criado_por=usuario.id
    )
    db_session.add(transacao)
    await db_session.commit()

    with patch('app.routers.whatsapp.WhatsAppService.enviar_mensagem', new_callable=AsyncMock) as mock_envio:
        mock_envio.return_value = True

        response = await client.post(
            "/api/whatsapp/lembrete-pagamento",
            json={"transacao_id": transacao.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data
