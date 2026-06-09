from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario, Perfil
from app.models.sessao import Sessao
from app.models.historico_acesso import HistoricoAcesso
from app.schemas.usuario import UsuarioCreate, UsuarioLogin
from app.core.seguranca import hash_senha, verificar_senha, criar_token_acesso, criar_token_refresh, verificar_token
from app.core.excecoes import NaoAutorizadoException, ConflitoException
from redis.asyncio import Redis
from app.config import settings
import uuid


async def criar_usuario(db: AsyncSession, usuario_data: UsuarioCreate) -> Usuario:
    """Cria um novo usuário."""
    # Verificar se email já existe
    result = await db.execute(select(Usuario).where(Usuario.email == usuario_data.email))
    if result.scalar_one_or_none():
        raise ConflitoException("Email já cadastrado")
    
    usuario = Usuario(
        id=str(uuid.uuid4()),
        email=usuario_data.email,
        senha_hash=hash_senha(usuario_data.senha),
        nome_completo=usuario_data.nome_completo,
        perfil=usuario_data.perfil,
        telefone=usuario_data.telefone,
        ativo=True,
        verificado=False
    )
    
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    
    return usuario


async def autenticar_usuario(db: AsyncSession, login_data: UsuarioLogin, ip: str = None, user_agent: str = None) -> dict:
    """Autentica usuário e retorna tokens."""
    result = await db.execute(select(Usuario).where(Usuario.email == login_data.email))
    usuario = result.scalar_one_or_none()
    
    # Registrar tentativa de acesso
    status_acesso = "sucesso" if usuario and verificar_senha(login_data.senha, usuario.senha_hash) else "falha"
    historico = HistoricoAcesso(
        usuario_id=usuario.id if usuario else None,
        ip=ip,
        dispositivo=user_agent,
        status=status_acesso
    )
    db.add(historico)
    
    if not usuario or not verificar_senha(login_data.senha, usuario.senha_hash):
        await db.commit()
        raise NaoAutorizadoException("Email ou senha inválidos")
    
    if not usuario.ativo:
        await db.commit()
        raise NaoAutorizadoException("Usuário inativo")
    
    # Atualizar último login
    usuario.ultimo_login = datetime.now(UTC)
    
    # Criar tokens
    token_data = {
        "sub": usuario.id,
        "email": usuario.email,
        "perfil": usuario.perfil.value,
        "nome": usuario.nome_completo
    }
    
    access_token = criar_token_acesso(token_data)
    refresh_token = criar_token_refresh(token_data)
    
    # Criar sessão
    sessao = Sessao(
        usuario_id=usuario.id,
        refresh_token=refresh_token,
        dispositivo=user_agent,
        ip=ip,
        ativa=True
    )
    db.add(sessao)
    
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "nome_completo": usuario.nome_completo,
            "perfil": usuario.perfil.value
        }
    }


async def refresh_token(db: AsyncSession, refresh_token: str, redis: Redis) -> dict:
    """Renova token de acesso usando refresh token."""
    payload = verificar_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise NaoAutorizadoException("Refresh token inválido")
    
    # Verificar se refresh token está na blacklist
    blacklist_key = f"blacklist:refresh:{refresh_token}"
    if await redis.exists(blacklist_key):
        raise NaoAutorizadoException("Refresh token revogado")
    
    usuario_id = payload.get("sub")
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario or not usuario.ativo:
        raise NaoAutorizadoException("Usuário inválido ou inativo")
    
    # Criar novo access token
    token_data = {
        "sub": usuario.id,
        "email": usuario.email,
        "perfil": usuario.perfil.value,
        "nome": usuario.nome_completo
    }
    
    access_token = criar_token_acesso(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


async def logout(refresh_token: str, redis: Redis, db: AsyncSession = None) -> None:
    """Adiciona refresh token à blacklist e desativa sessão."""
    payload = verificar_token(refresh_token)
    
    if payload and payload.get("type") == "refresh":
        # Adicionar à blacklist com expiração igual ao tempo de vida do refresh token
        exp = payload.get("exp")
        if exp:
            ttl = int(exp) - int(datetime.now(UTC).timestamp())
            if ttl > 0:
                blacklist_key = f"blacklist:refresh:{refresh_token}"
                await redis.setex(blacklist_key, ttl, "1")
        
        # Desativar sessão no banco se db foi fornecido
        if db:
            from sqlalchemy import select
            from app.models.sessao import Sessao
            result = await db.execute(
                select(Sessao).where(Sessao.refresh_token == refresh_token)
            )
            sessao = result.scalar_one_or_none()
            if sessao:
                sessao.ativa = False
                await db.commit()


async def alterar_senha(db: AsyncSession, usuario: Usuario, senha_atual: str, nova_senha: str) -> None:
    """Altera a senha do usuário."""
    # Verificar senha atual
    if not verificar_senha(senha_atual, usuario.senha_hash):
        raise ValueError("Senha atual incorreta")
    
    # Atualizar senha
    usuario.senha_hash = hash_senha(nova_senha)
    usuario.atualizado_em = datetime.now(UTC)
    
    await db.commit()
    await db.refresh(usuario)
