import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_validacao_cpf_valido(client: AsyncClient, auth_headers: dict):
    """Testa criação de cliente com CPF válido."""
    cliente_data = {
        "nome": "Cliente CPF Válido",
        "email": "cliente_cpf@teste.com",
        "telefone": "11988888888",
        "tipo_documento": "cpf",
        "numero_documento": "529.982.247-25",  # CPF válido
        "tipo_cliente": "residencial"
    }
    
    response = await client.post("/api/clientes", json=cliente_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["numero_documento"] == "529.982.247-25"


@pytest.mark.asyncio
async def test_validacao_cpf_invalido(client: AsyncClient, auth_headers: dict):
    """Testa criação de cliente com CPF inválido."""
    cliente_data = {
        "nome": "Cliente CPF Inválido",
        "email": "cliente_cpf_invalido@teste.com",
        "telefone": "11988888888",
        "tipo_documento": "cpf",
        "numero_documento": "111.111.111-11",  # CPF inválido
        "tipo_cliente": "residencial"
    }
    
    response = await client.post("/api/clientes", json=cliente_data, headers=auth_headers)
    
    assert response.status_code == 422
    data = response.json()
    assert "CPF inválido" in str(data)


@pytest.mark.asyncio
async def test_validacao_cnpj_valido(client: AsyncClient, auth_headers: dict):
    """Testa criação de cliente com CNPJ válido."""
    cliente_data = {
        "nome": "Empresa CNPJ Válido",
        "email": "empresa@teste.com",
        "telefone": "11988888888",
        "tipo_documento": "cnpj",
        "numero_documento": "11.444.777/0001-61",  # CNPJ válido
        "tipo_cliente": "comercial"
    }
    
    response = await client.post("/api/clientes", json=cliente_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["numero_documento"] == "11.444.777/0001-61"


@pytest.mark.asyncio
async def test_validacao_cnpj_invalido(client: AsyncClient, auth_headers: dict):
    """Testa criação de cliente com CNPJ inválido."""
    cliente_data = {
        "nome": "Empresa CNPJ Inválido",
        "email": "empresa_invalida@teste.com",
        "telefone": "11988888888",
        "tipo_documento": "cnpj",
        "numero_documento": "11.111.111/1111-11",  # CNPJ inválido
        "tipo_cliente": "comercial"
    }
    
    response = await client.post("/api/clientes", json=cliente_data, headers=auth_headers)
    
    assert response.status_code == 422
    data = response.json()
    assert "CNPJ inválido" in str(data)
