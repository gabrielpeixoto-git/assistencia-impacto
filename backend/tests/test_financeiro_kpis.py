import pytest
from httpx import AsyncClient
from datetime import datetime, date, timedelta


@pytest.mark.asyncio
async def test_resumo_financeiro_retorna_kpis(client: AsyncClient, auth_headers: dict):
    """Testa endpoint de resumo financeiro com KPIs reais."""
    response = await client.get("/api/financeiro/resumo", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "periodo" in data
    assert "kpi" in data
    assert "receita_total" in data["kpi"]
    assert "despesa_total" in data["kpi"]
    assert "lucro_liquido" in data["kpi"]
    assert "margem_lucro" in data["kpi"]
    assert "contas_receber" in data["kpi"]
    assert "contas_pagar" in data["kpi"]


@pytest.mark.asyncio
async def test_resumo_financeiro_periodo_semana(client: AsyncClient, auth_headers: dict):
    """Testa filtro de período semana no resumo financeiro."""
    response = await client.get(
        "/api/financeiro/resumo?periodo=semana",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["periodo"]["tipo"] == "semana"
    assert "kpi" in data


@pytest.mark.asyncio
async def test_exportar_transacoes_csv(client: AsyncClient, auth_headers: dict):
    """Testa exportação de transações em formato CSV."""
    response = await client.get(
        "/api/financeiro/exportar?formato=csv",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8-sig"
    assert "Content-Disposition" in response.headers


@pytest.mark.asyncio
async def test_exportar_csv_formato_correto(client: AsyncClient, auth_headers: dict):
    """Testa se o CSV exportado tem o formato correto com BOM UTF-8."""
    response = await client.get(
        "/api/financeiro/exportar?formato=csv",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8-sig"
    content = response.text
    # Verificar cabeçalho CSV
    assert "Data" in content
    assert "Tipo" in content
    assert "Valor (R$)" in content
