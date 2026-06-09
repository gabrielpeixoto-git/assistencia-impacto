"""Testes do router de Portal (endpoints públicos)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_visualizar_orcamento_token_invalido(client: AsyncClient):
    """Visualizar orçamento com token inválido retorna 404."""
    response = await client.get("/api/portal/orcamento/token-invalido")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_itens_orcamento_token_invalido(client: AsyncClient):
    """Listar itens de orçamento com token inválido retorna 404."""
    response = await client.get("/api/portal/orcamento/token-invalido/itens")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_aprovar_orcamento_token_invalido(client: AsyncClient):
    """Aprovar orçamento com token inválido retorna 404."""
    response = await client.post("/api/portal/orcamento/token-invalido/aprovar")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rejeitar_orcamento_token_invalido(client: AsyncClient):
    """Rejeitar orçamento com token inválido retorna 404."""
    response = await client.post("/api/portal/orcamento/token-invalido/rejeitar")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_visualizar_os_token_invalido(client: AsyncClient):
    """Visualizar OS com token inválido retorna 404."""
    response = await client.get("/api/portal/os/token-invalido")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_itens_os_token_invalido(client: AsyncClient):
    """Listar itens de OS com token inválido retorna 404."""
    response = await client.get("/api/portal/os/token-invalido/itens")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_fotos_os_token_invalido(client: AsyncClient):
    """Listar fotos de OS com token inválido retorna 404."""
    response = await client.get("/api/portal/os/token-invalido/fotos")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_listar_checklist_os_token_invalido(client: AsyncClient):
    """Listar checklist de OS com token inválido retorna 404."""
    response = await client.get("/api/portal/os/token-invalido/checklist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_avaliar_os_token_invalido(client: AsyncClient):
    """Avaliar OS com token inválido retorna 404."""
    response = await client.post(
        "/api/portal/os/token-invalido/avaliar",
        json={"nota": 5, "comentario": "Ótimo serviço"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_aprovar_orcamento_sem_dados(client: AsyncClient):
    """Aprovar orçamento sem dados retorna 404 (token inválido)."""
    response = await client.post("/api/portal/orcamento/token-invalido/aprovar", json={})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_avaliar_os_sem_dados(client: AsyncClient):
    """Avaliar OS sem dados retorna 422 (schema validation)."""
    response = await client.post("/api/portal/os/token-invalido/avaliar", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_avaliar_os_nota_invalida(client: AsyncClient):
    """Avaliar OS com nota inválida retorna 422 (schema validation)."""
    response = await client.post(
        "/api/portal/os/token-invalido/avaliar",
        json={"nota": 6, "comentario": "Nota acima do limite"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_avaliar_os_nota_negativa(client: AsyncClient):
    """Avaliar OS com nota negativa retorna 422 (schema validation)."""
    response = await client.post(
        "/api/portal/os/token-invalido/avaliar",
        json={"nota": -1, "comentario": "Nota negativa"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_orcamento_sem_dados(client: AsyncClient):
    """Rejeitar orçamento sem dados retorna 404 (token inválido)."""
    response = await client.post("/api/portal/orcamento/token-invalido/rejeitar", json={})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_aprovar_orcamento_com_motivo_vazio(client: AsyncClient):
    """Aprovar orçamento com motivo vazio retorna 404 (token inválido)."""
    response = await client.post(
        "/api/portal/orcamento/token-invalido/aprovar",
        json={"motivo": ""}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rejeitar_orcamento_com_motivo_vazio(client: AsyncClient):
    """Rejeitar orçamento com motivo vazio retorna 404 (token inválido)."""
    response = await client.post(
        "/api/portal/orcamento/token-invalido/rejeitar",
        json={"motivo": ""}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_avaliar_os_com_comentario_vazio(client: AsyncClient):
    """Avaliar OS com comentário vazio retorna 404 (token inválido)."""
    response = await client.post(
        "/api/portal/os/token-invalido/avaliar",
        json={"nota": 5, "comentario": ""}
    )
    assert response.status_code == 404
