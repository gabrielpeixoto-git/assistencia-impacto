"""Testes da máquina de estados das Ordens de Serviço."""
import pytest
from httpx import AsyncClient


# ================================================================
# HELPERS — copie o padrão exato de test_ordens_servico.py
# ================================================================

async def criar_os_para_teste(client, auth_headers):
    """Cria uma OS de teste e retorna o ID."""
    # Criar cliente primeiro
    cliente_resp = await client.post("/api/clientes", json={
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "11988888888",
        "tipo_cliente": "residencial"
    }, headers=auth_headers)
    assert cliente_resp.status_code == 201, f"Falha ao criar cliente: {cliente_resp.text}"
    cliente_id = cliente_resp.json()["id"]
    
    # Criar categoria de serviço
    categoria_data = {
        "nome": "Instalação de Ar Condicionado",
        "descricao": "Serviços de instalação de ar condicionado",
        "ativo": True,
        "icone": "snowflake",
        "cor": "#3B82F6"
    }
    categoria_resp = await client.post("/api/categorias-servico", json=categoria_data, headers=auth_headers)
    assert categoria_resp.status_code == 201, f"Falha ao criar categoria: {categoria_resp.text}"
    categoria_id = categoria_resp.json()["id"]
    
    # Criar OS
    os_resp = await client.post("/api/ordens-servico", json={
        "cliente_id": cliente_id,
        "tipo_servico_id": categoria_id,
        "titulo": "Instalação de Ar Condicionado",
        "descricao": "Instalação de ar condicionado split 12000 BTUs na sala",
        "valor_estimado": 1500.00
    }, headers=auth_headers)
    assert os_resp.status_code == 201, f"Falha ao criar OS: {os_resp.text}"
    return os_resp.json()["id"]


# ================================================================
# TESTES
# ================================================================

@pytest.mark.asyncio
async def test_transicao_valida_pendente_para_confirmada(client: AsyncClient, auth_headers: dict):
    """Testa transição de status pendente → confirmada."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "confirmada"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "confirmada"


@pytest.mark.asyncio
async def test_transicao_invalida_pendente_para_concluida(client: AsyncClient, auth_headers: dict):
    """Não pode ir direto de pendente para concluída."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "concluida"},
        headers=auth_headers
    )
    assert response.status_code == 409, f"Deveria ser 409, got: {response.text}"


@pytest.mark.asyncio
async def test_cancelar_sem_motivo(client: AsyncClient, auth_headers: dict):
    """Cancelar sem motivo deve retornar 400."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "cancelada"},  # sem motivo_cancelamento
        headers=auth_headers
    )
    assert response.status_code == 400, f"Deveria ser 400, got: {response.text}"


@pytest.mark.asyncio
async def test_cancelar_com_motivo(client: AsyncClient, auth_headers: dict):
    """Cancelar com motivo deve funcionar."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "cancelada", "motivo": "Cliente desistiu"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "cancelada"


@pytest.mark.asyncio
async def test_concluir_registra_data_conclusao(client: AsyncClient, auth_headers: dict):
    """Concluir OS deve registrar data_conclusao."""
    os_id = await criar_os_para_teste(client, auth_headers)
    
    # pendente → confirmada → em_andamento → concluida
    await client.patch(f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "confirmada"}, headers=auth_headers)
    await client.patch(f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "em_andamento"}, headers=auth_headers)
    
    response = await client.patch(
        f"/api/ordens-servico/{os_id}/status",
        json={"novo_status": "concluida"},
        headers=auth_headers
    )
    assert response.status_code == 200, f"Erro: {response.text}"
    data = response.json()
    assert data["status"] == "concluida"
    assert data.get("data_conclusao") is not None
