from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.notificacao import TipoNotificacao


class NotificacaoCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    corpo: str = Field(..., min_length=1)
    tipo: TipoNotificacao = TipoNotificacao.INFO
    usuario_id: Optional[str] = None
    url_acao: Optional[str] = Field(None, max_length=500)
    tipo_entidade: Optional[str] = Field(None, max_length=50)
    id_entidade: Optional[str] = Field(None, max_length=36)


class NotificacaoUpdate(BaseModel):
    lida: Optional[bool] = None


class NotificacaoResponse(BaseModel):
    id: str
    usuario_id: str
    titulo: str
    corpo: str
    tipo: TipoNotificacao
    tipo_entidade: Optional[str]
    id_entidade: Optional[str]
    lida: bool
    lida_em: Optional[datetime]
    url_acao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True
