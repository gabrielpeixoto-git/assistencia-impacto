from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from app.database import get_db
from app.config import settings
from app.core.seguranca import verificar_token
from app.models.usuario import Usuario

security = HTTPBearer()


async def get_redis() -> Generator[Redis, None, None]:
    """Dependency para obter conexão Redis."""
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()


async def get_usuario_atual(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Usuario:
    """Dependency para obter usuário atual a partir do token JWT."""
    token = credentials.credentials
    payload = verificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # Buscar usuário no banco de dados
    query = select(Usuario).where(Usuario.id == usuario_id)
    result = await db.execute(query)
    usuario = result.scalar_one_or_none()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return usuario


async def require_admin(usuario_atual: Annotated[Usuario, Depends(get_usuario_atual)]) -> Usuario:
    """Dependency para verificar se usuário é admin."""
    if usuario_atual.perfil.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )
    return usuario_atual
