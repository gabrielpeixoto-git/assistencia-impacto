from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.models.usuario import Perfil


class UsuarioBase(BaseModel):
    email: EmailStr
    nome_completo: str = Field(..., min_length=3, max_length=255)
    perfil: Perfil = Perfil.VISUALIZADOR
    telefone: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=255)
    perfil: Optional[Perfil] = None
    telefone: Optional[str] = None
    avatar_url: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: str
    avatar_url: Optional[str]
    telefone: Optional[str]
    cor: str
    ativo: bool
    verificado: bool
    ultimo_login: Optional[datetime]
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioLoginResponse(BaseModel):
    id: str
    email: EmailStr
    nome_completo: str
    perfil: Perfil


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UsuarioLoginResponse


class AlterarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., min_length=1)
    nova_senha: str = Field(..., min_length=8)
    confirmar_senha: str = Field(..., min_length=8)
    
    def validate_senhas(self):
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem")
        return self


class SessaoAtiva(BaseModel):
    id: str
    dispositivo: str
    ip: str
    data_ultimo_acesso: datetime
    eh_atual: bool = False


class HistoricoAcesso(BaseModel):
    id: str
    data_hora: datetime
    ip: str
    dispositivo: str
    status: str  # "sucesso" ou "falha"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class EsqueciSenhaRequest(BaseModel):
    """Schema para solicitação de recuperação de senha."""
    email: EmailStr


class RedefinirSenhaRequest(BaseModel):
    """Schema para redefinição de senha com token."""
    token: str = Field(..., min_length=1)
    nova_senha: str = Field(..., min_length=8, max_length=128)
    
    def validate_senha_complexidade(self):
        """Valida complexidade da senha (mínimo 8 chars, 1 maiúscula, 1 número)."""
        if len(self.nova_senha) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        if not any(c.isupper() for c in self.nova_senha):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not any(c.isdigit() for c in self.nova_senha):
            raise ValueError("A senha deve conter pelo menos um número")
        return self
