from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.dependencies import get_redis, get_usuario_atual
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, TokenResponse, AlterarSenhaRequest, SessaoAtiva, HistoricoAcesso, RefreshTokenRequest
from app.services.auth_service import criar_usuario, autenticar_usuario, refresh_token, logout, alterar_senha
from app.models.usuario import Usuario
from app.models.sessao import Sessao
from app.models.historico_acesso import HistoricoAcesso as HistoricoAcessoModel
from app.config import settings
from loguru import logger
from datetime import datetime
import uuid
import os
import traceback

# Desabilitar rate limiting em ambiente de teste
TESTING = os.getenv("TESTING", "false").lower() == "true"
if TESTING:
    limiter = None
else:
    limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


def rate_limit(limit_value):
    """Decorator condicional para rate limiting."""
    if TESTING:
        return lambda func: func
    return limiter.limit(limit_value)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: UsuarioLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Autentica usuário e retorna tokens de acesso e refresh."""
    try:
        # Capturar IP e User-Agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        resultado = await autenticar_usuario(db, login_data, ip=client_ip, user_agent=user_agent)
        logger.info(f"Usuário {login_data.email} autenticado com sucesso")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERRO NO LOGIN: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/refresh", response_model=dict, status_code=status.HTTP_200_OK)
async def refresh_endpoint(
    request_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Renova token de acesso usando refresh token."""
    try:
        resultado = await refresh_token(db, request_data.refresh_token, redis)
        return resultado
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível renovar o token"
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(
    refresh_token: str,
    redis: Redis = Depends(get_redis)
):
    """Revoga refresh token (logout)."""
    try:
        await logout(refresh_token, redis)
        logger.info("Logout realizado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise


@router.post("/registrar", status_code=status.HTTP_201_CREATED)
@rate_limit("3/minute")
async def registrar(
    usuario_data: UsuarioCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Registra um novo usuário (apenas se permitido nas configurações)."""
    if not settings.permitir_registro_publico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registro público não está habilitado. Entre em contato com o administrador."
        )
    
    try:
        usuario = await criar_usuario(db, usuario_data)
        logger.info(f"Usuário {usuario_data.email} criado com sucesso")
        return {
            "mensagem": "Usuário criado com sucesso",
            "usuario_id": usuario.id
        }
    except Exception as e:
        logger.error(f"Erro ao criar usuário {usuario_data.email}: {str(e)}")
        raise


@router.put("/alterar-senha", status_code=status.HTTP_200_OK)
async def alterar_senha_endpoint(
    senha_data: AlterarSenhaRequest,
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Altera a senha do usuário autenticado."""
    try:
        # Validar que as senhas coincidem
        senha_data.validate_senhas()
        
        await alterar_senha(db, current_user, senha_data.senha_atual, senha_data.nova_senha)
        logger.info(f"Senha alterada com sucesso para usuário {current_user.email}")
        return {"mensagem": "Senha alterada com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao alterar senha do usuário {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao alterar senha. Verifique sua senha atual."
        )


@router.get("/sessoes", response_model=list[SessaoAtiva])
async def listar_sessoes(
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas as sessões ativas do usuário."""
    result = await db.execute(
        select(Sessao).where(Sessao.usuario_id == current_user.id, Sessao.ativa == True)
    )
    sessoes = result.scalars().all()
    
    return [
        SessaoAtiva(
            id=sessao.id,
            dispositivo=sessao.dispositivo or "Dispositivo desconhecido",
            ip=sessao.ip or "IP desconhecido",
            data_ultimo_acesso=sessao.ultimo_acesso,
            eh_atual=False  # Seria necessário identificar a sessão atual via token
        )
        for sessao in sessoes
    ]


@router.delete("/sessoes/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def encerrar_sessao(
    sessao_id: str,
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Encerra uma sessão específica."""
    result = await db.execute(
        select(Sessao).where(
            Sessao.id == sessao_id,
            Sessao.usuario_id == current_user.id,
            Sessao.ativa == True
        )
    )
    sessao = result.scalar_one_or_none()
    
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    sessao.ativa = False
    await db.commit()
    logger.info(f"Sessão {sessao_id} encerrada pelo usuário {current_user.email}")


@router.delete("/sessoes", status_code=status.HTTP_204_NO_CONTENT)
async def encerrar_outras_sessoes(
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Encerra todas as outras sessões do usuário (exceto a atual)."""
    result = await db.execute(
        select(Sessao).where(
            Sessao.usuario_id == current_user.id,
            Sessao.ativa == True
        )
    )
    sessoes = result.scalars().all()
    
    # Encerrar todas (em um cenário real, identificaríamos a sessão atual para não encerrá-la)
    for sessao in sessoes:
        sessao.ativa = False
    
    await db.commit()
    logger.info(f"Todas as sessões encerradas pelo usuário {current_user.email}")


@router.get("/historico-acesso", response_model=list[HistoricoAcesso])
async def listar_historico_acesso(
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Lista o histórico de acessos do usuário (últimos 10 registros)."""
    result = await db.execute(
        select(HistoricoAcessoModel)
        .where(HistoricoAcessoModel.usuario_id == current_user.id)
        .order_by(HistoricoAcessoModel.criado_em.desc())
        .limit(10)
    )
    historicos = result.scalars().all()
    
    return [
        HistoricoAcesso(
            id=h.id,
            data_hora=h.criado_em,
            ip=h.ip or "IP desconhecido",
            dispositivo=h.dispositivo or "Dispositivo desconhecido",
            status=h.status
        )
        for h in historicos
    ]
