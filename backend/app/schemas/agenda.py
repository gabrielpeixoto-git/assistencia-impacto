from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.agenda import TipoEvento, StatusEvento


class AgendaBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=255)
    tecnico_id: str
    cliente_id: Optional[str] = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    tipo_evento: TipoEvento = TipoEvento.SERVICO
    endereco: Optional[str] = None
    observacoes: Optional[str] = None
    cor: str = "#6C63FF"


class AgendaCreate(AgendaBase):
    ordem_servico_id: Optional[str] = None


class AgendaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    tecnico_id: Optional[str] = None
    cliente_id: Optional[str] = None
    data_hora_inicio: Optional[datetime] = None
    data_hora_fim: Optional[datetime] = None
    tipo_evento: Optional[TipoEvento] = None
    status: Optional[StatusEvento] = None
    endereco: Optional[str] = None
    observacoes: Optional[str] = None
    cor: Optional[str] = None


class AgendaStatusUpdate(BaseModel):
    status: StatusEvento


class AgendaResponse(AgendaBase):
    id: str
    ordem_servico_id: Optional[str]
    status: StatusEvento
    latitude: Optional[float]
    longitude: Optional[float]
    id_evento_google_calendar: Optional[str]
    lembrete_enviado: bool
    criado_em: datetime
    tecnico_nome: Optional[str] = None
    cliente_nome: Optional[str] = None
    cor_tecnico: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
