from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import secrets
import string
import uuid

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha plana corresponde ao hash."""
    return pwd_context.verify(senha_plana, senha_hash)


def hash_senha(senha: str) -> str:
    """Gera hash da senha."""
    # Truncar senha se exceder 72 bytes (limite do bcrypt)
    if len(senha.encode('utf-8')) > 72:
        senha = senha[:72]
    return pwd_context.hash(senha)


def criar_token_acesso(dados: dict) -> str:
    """Cria token de acesso JWT."""
    para_adicionar = {
        "exp": datetime.now(UTC) + timedelta(minutes=settings.expiracao_token_acesso_minutos),
        "iat": datetime.now(UTC),
        "type": "access",
        "jti": str(uuid.uuid4())
    }
    dados_atualizados = dados.copy()
    dados_atualizados.update(para_adicionar)
    return jwt.encode(dados_atualizados, settings.chave_secreta, algorithm=settings.algoritmo)


def criar_token_refresh(dados: dict) -> str:
    """Cria token de refresh JWT."""
    para_adicionar = {
        "exp": datetime.now(UTC) + timedelta(days=settings.expiracao_refresh_token_dias),
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    dados_atualizados = dados.copy()
    dados_atualizados.update(para_adicionar)
    return jwt.encode(dados_atualizados, settings.chave_secreta, algorithm=settings.algoritmo)


def verificar_token(token: str) -> Optional[dict]:
    """Verifica e decodifica token JWT."""
    try:
        payload = jwt.decode(token, settings.chave_secreta, algorithms=[settings.algoritmo])
        return payload
    except JWTError:
        return None


def gerar_token_consulta() -> str:
    """Gera um token único para consulta de OS pelo cliente."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(12))
