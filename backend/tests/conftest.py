import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Definir variável de ambiente para desabilitar rate limiting nos testes
os.environ["TESTING"] = "true"

from app.main import app
from app.database import Base, get_db
from app.models.usuario import Usuario
from app.models import Perfil
from app.core.seguranca import hash_senha

# Engine SQLite para testes (banco em memória, sem conflitos)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestAsyncSession = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Cria e destrói as tabelas para cada teste."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # drop primeiro para evitar conflitos de schema
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de banco de dados para uso direto nos testes."""
    async with TestAsyncSession() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP de teste com banco de dados isolado."""
    
    async def override_get_db():
        async with TestAsyncSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.exists = AsyncMock(return_value=False)

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient) -> dict:
    """Headers de autenticação para usuário comum (admin)."""
    # Registrar usuário via API (cada teste tem banco limpo, sem conflito)
    register_data = {
        "email": "admin@teste.com",
        "senha": "Admin123!",
        "nome_completo": "Admin Teste",
        "perfil": "admin"
    }
    reg_response = await client.post("/api/auth/registrar", json=register_data)
    assert reg_response.status_code == 201, f"Falha ao registrar: {reg_response.text}"

    login_response = await client.post("/api/auth/login", json={
        "email": "admin@teste.com",
        "senha": "Admin123!"
    })
    assert login_response.status_code == 200, f"Falha no login: {login_response.text}"
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_headers(auth_headers: dict) -> dict:
    """Alias para auth_headers — compatibilidade com testes antigos."""
    return auth_headers


@pytest_asyncio.fixture(scope="function")
def test_user_data() -> dict:
    """Dados de usuário para testes."""
    return {
        "email": "teste@example.com",
        "senha": "Senha123!",
        "nome_completo": "Usuário Teste",
        "perfil": "admin"
    }


@pytest_asyncio.fixture(scope="function")
def test_cliente_data() -> dict:
    """Dados de cliente para testes."""
    return {
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "11988888888",
        "tipo_cliente": "residencial"
    }
