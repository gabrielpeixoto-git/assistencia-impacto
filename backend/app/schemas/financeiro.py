from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.financeiro import TipoTransacao, StatusTransacao


class TransacaoBase(BaseModel):
    tipo: TipoTransacao
    categoria_id: str
    descricao: str = Field(..., min_length=3, max_length=255)
    valor: float = Field(..., gt=0)
    data_vencimento: datetime
    forma_pagamento: Optional[str] = None
    conta_bancaria: Optional[str] = None


class TransacaoCreate(TransacaoBase):
    ordem_servico_id: Optional[str] = None
    orcamento_id: Optional[str] = None
    cliente_id: Optional[str] = None
    fornecedor_id: Optional[str] = None
    observacoes: Optional[str] = None
    recorrente: bool = False
    intervalo_recorrencia: Optional[str] = None


class TransacaoUpdate(BaseModel):
    tipo: Optional[TipoTransacao] = None
    categoria_id: Optional[str] = None
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    valor: Optional[float] = Field(None, gt=0)
    data_vencimento: Optional[datetime] = None
    status: Optional[StatusTransacao] = None
    data_pagamento: Optional[datetime] = None
    forma_pagamento: Optional[str] = None
    conta_bancaria: Optional[str] = None
    url_comprovante: Optional[str] = None
    cliente_id: Optional[str] = None
    fornecedor_id: Optional[str] = None
    observacoes: Optional[str] = None
    recorrente: Optional[bool] = None
    intervalo_recorrencia: Optional[str] = None


class TransacaoResponse(TransacaoBase):
    id: str
    numero_transacao: str
    status: StatusTransacao
    ordem_servico_id: Optional[str]
    orcamento_id: Optional[str]
    cliente_id: Optional[str]
    fornecedor_id: Optional[str]
    data_pagamento: Optional[datetime]
    url_comprovante: Optional[str]
    recorrente: bool
    intervalo_recorrencia: Optional[str]
    observacoes: Optional[str]
    criado_por: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoriaFinanceiraCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    tipo: TipoTransacao
    cor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    icone: str
