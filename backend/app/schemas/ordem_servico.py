from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.ordem_servico import StatusOS, PrioridadeOS, StatusPagamento, FormaPagamento, TipoFoto


class OrdemServicoBase(BaseModel):
    cliente_id: str
    tecnico_id: Optional[str] = None
    tipo_servico_id: str
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: str = Field(..., min_length=10, max_length=5000)
    prioridade: PrioridadeOS = PrioridadeOS.NORMAL
    data_agendada: Optional[datetime] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    endereco_id: Optional[str] = None
    valor_estimado: float = Field(..., ge=0)
    forma_pagamento: Optional[FormaPagamento] = None
    emitir_nota: bool = False


class OrdemServicoCreate(OrdemServicoBase):
    observacoes_internas: Optional[str] = None


class OrdemServicoUpdate(BaseModel):
    cliente_id: Optional[str] = None
    tecnico_id: Optional[str] = None
    tipo_servico_id: Optional[str] = None
    status: Optional[StatusOS] = None
    prioridade: Optional[PrioridadeOS] = None
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    observacoes_internas: Optional[str] = None
    data_agendada: Optional[datetime] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    endereco_id: Optional[str] = None
    valor_estimado: Optional[float] = None
    valor_final: Optional[float] = None
    status_pagamento: Optional[StatusPagamento] = None
    forma_pagamento: Optional[FormaPagamento] = None
    emitir_nota: Optional[bool] = None


class OrdemServicoResponse(OrdemServicoBase):
    id: str
    numero_os: str
    status: StatusOS
    observacoes_internas: Optional[str]
    data_conclusao: Optional[datetime]
    duracao_minutos: Optional[int]
    valor_final: float
    status_pagamento: StatusPagamento
    url_assinatura_cliente: Optional[str]
    criado_por: str
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemOrdemServicoCreate(BaseModel):
    item_estoque_id: Optional[str] = None
    descricao: str = Field(..., min_length=3, max_length=500)
    quantidade: float = Field(..., gt=0)
    unidade: str = Field(..., min_length=1, max_length=20)
    custo_unitario: float = Field(..., ge=0)
    compra_externa: bool = False


class FotoOrdemServicoCreate(BaseModel):
    legenda: Optional[str] = None
    tipo_foto: TipoFoto = TipoFoto.OUTRO
    tirada_em: Optional[datetime] = None


class ChecklistOrdemServicoCreate(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=500)
