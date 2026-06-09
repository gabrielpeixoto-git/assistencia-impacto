"""Testes unitários do Auth Service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import (
    criar_usuario,
    autenticar_usuario,
    refresh_token,
    logout,
    alterar_senha
)
from app.models.usuario import Usuario, Perfil
from app.schemas.usuario import UsuarioCreate, UsuarioLogin
from app.core.excecoes import NaoAutorizadoException, ConflitoException
from datetime import datetime, UTC


@pytest.mark.asyncio
async def test_criar_usuario_email_duplicado():
    """Testa erro ao criar usuário com email duplicado."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()  # Email já existe
    mock_db.execute = AsyncMock(return_value=mock_result)

    usuario_data = UsuarioCreate(
        email="teste@example.com",
        senha="Senha123!",
        nome_completo="Teste User",
        perfil=Perfil.TECNICO,
        telefone="11999999999"
    )

    with pytest.raises(ConflitoException) as exc_info:
        await criar_usuario(mock_db, usuario_data)
    
    assert "Email já cadastrado" in str(exc_info.value)


@pytest.mark.asyncio
async def test_autenticar_usuario_inativo():
    """Testa erro ao autenticar usuário inativo."""
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock usuário inativo
    mock_usuario = MagicMock()
    mock_usuario.id = "user-123"
    mock_usuario.ativo = False
    mock_usuario.senha_hash = "hash_valido"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    login_data = UsuarioLogin(
        email="teste@example.com",
        senha="Senha123!"
    )

    with patch('app.services.auth_service.verificar_senha', return_value=True):
        with pytest.raises(NaoAutorizadoException) as exc_info:
            await autenticar_usuario(mock_db, login_data)
        
        assert "Usuário inativo" in str(exc_info.value)


@pytest.mark.asyncio
async def test_refresh_token_blacklist():
    """Testa erro ao usar refresh token na blacklist."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_redis = AsyncMock()
    
    # Mock token válido
    mock_payload = {"sub": "user-123", "type": "refresh", "exp": 9999999999}
    
    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        mock_redis.exists = AsyncMock(return_value=1)  # Token na blacklist
        
        with pytest.raises(NaoAutorizadoException) as exc_info:
            await refresh_token(mock_db, "revoked_token", mock_redis)
        
        assert "Refresh token revogado" in str(exc_info.value)


@pytest.mark.asyncio
async def test_refresh_token_usuario_inativo():
    """Testa erro ao renovar token de usuário inativo."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_redis = AsyncMock()
    
    # Mock token válido
    mock_payload = {"sub": "user-123", "type": "refresh"}
    
    # Mock usuário inativo
    mock_usuario = MagicMock()
    mock_usuario.ativo = False
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        mock_redis.exists = AsyncMock(return_value=0)  # Token não na blacklist
        
        with pytest.raises(NaoAutorizadoException) as exc_info:
            await refresh_token(mock_db, "valid_token", mock_redis)
        
        assert "Usuário inválido ou inativo" in str(exc_info.value)


@pytest.mark.asyncio
async def test_logout_com_db():
    """Testa logout com desativação de sessão no banco."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_redis = AsyncMock()
    
    # Mock token válido com expiração
    exp_timestamp = int(datetime.now(UTC).timestamp()) + 3600
    mock_payload = {"sub": "user-123", "type": "refresh", "exp": exp_timestamp}
    
    # Mock sessão existente
    mock_sessao = MagicMock()
    mock_sessao.ativa = True
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_sessao
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        await logout("valid_token", mock_redis, mock_db)
        
        # Verifica que sessão foi desativada
        assert mock_sessao.ativa is False
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_logout_sem_db():
    """Testa logout sem fornecer banco de dados (apenas blacklist)."""
    mock_redis = AsyncMock()
    
    # Mock token válido com expiração
    exp_timestamp = int(datetime.now(UTC).timestamp()) + 3600
    mock_payload = {"sub": "user-123", "type": "refresh", "exp": exp_timestamp}

    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        await logout("valid_token", mock_redis, None)
        
        # Verifica que token foi adicionado à blacklist
        mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_logout_token_expirado():
    """Testa logout com token já expirado (não adiciona à blacklist)."""
    mock_redis = AsyncMock()
    
    # Mock token expirado
    exp_timestamp = int(datetime.now(UTC).timestamp()) - 3600
    mock_payload = {"sub": "user-123", "type": "refresh", "exp": exp_timestamp}

    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        await logout("expired_token", mock_redis, None)
        
        # Verifica que NÃO adicionou à blacklist (ttl <= 0)
        mock_redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_alterar_senha_sucesso():
    """Testa alteração de senha com sucesso."""
    mock_db = AsyncMock(spec=AsyncSession)
    
    mock_usuario = MagicMock()
    mock_usuario.senha_hash = "hash_antigo"
    
    with patch('app.services.auth_service.verificar_senha', return_value=True), \
         patch('app.services.auth_service.hash_senha', return_value="hash_novo"):
        
        await alterar_senha(mock_db, mock_usuario, "senha_antiga", "nova_senha")
        
        # Verifica que senha foi atualizada
        assert mock_usuario.senha_hash == "hash_novo"
        assert mock_usuario.atualizado_em is not None
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_alterar_senha_incorreta():
    """Testa erro ao alterar senha com senha atual incorreta."""
    mock_db = AsyncMock(spec=AsyncSession)
    
    mock_usuario = MagicMock()
    mock_usuario.senha_hash = "hash_valido"

    with patch('app.services.auth_service.verificar_senha', return_value=False):
        with pytest.raises(ValueError) as exc_info:
            await alterar_senha(mock_db, mock_usuario, "senha_errada", "nova_senha")
        
        assert "Senha atual incorreta" in str(exc_info.value)


@pytest.mark.asyncio
async def test_refresh_token_tipo_invalido():
    """Testa erro ao usar token que não é do tipo refresh."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_redis = AsyncMock()
    
    # Mock token access (não refresh)
    mock_payload = {"sub": "user-123", "type": "access"}

    with patch('app.services.auth_service.verificar_token', return_value=mock_payload):
        with pytest.raises(NaoAutorizadoException) as exc_info:
            await refresh_token(mock_db, "access_token", mock_redis)
        
        assert "Refresh token inválido" in str(exc_info.value)


@pytest.mark.asyncio
async def test_refresh_token_payload_vazio():
    """Testa erro quando payload do token é vazio."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_redis = AsyncMock()

    with patch('app.services.auth_service.verificar_token', return_value=None):
        with pytest.raises(NaoAutorizadoException) as exc_info:
            await refresh_token(mock_db, "invalid_token", mock_redis)
        
        assert "Refresh token inválido" in str(exc_info.value)
