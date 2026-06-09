from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.orcamento import StatusOrcamento, TipoCalculoOrcamento


class OrcamentoBase(BaseModel):
    cliente_id: str
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: str
    valido_ate: Optional[datetime] = None
    condicoes_pagamento: Optional[str] = None
    garantia: Optional[str] = None
    tipo_calculo: TipoCalculoOrcamento = TipoCalculoOrcamento.AUTOMATICO
    tipo_desconto: Optional[str] = None
    valor_desconto: float = 0.0
    taxa_imposto: float = 0.0
    valor_total_manual: float = 0.0


class OrcamentoCreate(OrcamentoBase):
    observacoes_internas: Optional[str] = None
    subtotal: float = 0.0
    total: float = 0.0


class OrcamentoUpdate(BaseModel):
    status: Optional[StatusOrcamento] = None
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    observacoes_internas: Optional[str] = None
    valido_ate: Optional[datetime] = None
    condicoes_pagamento: Optional[str] = None
    garantia: Optional[str] = None
    tipo_calculo: Optional[TipoCalculoOrcamento] = None
    tipo_desconto: Optional[str] = None
    valor_desconto: Optional[float] = None
    taxa_imposto: Optional[float] = None
    valor_total_manual: Optional[float] = None
    subtotal: Optional[float] = None
    total: Optional[float] = None


class OrcamentoResponse(OrcamentoBase):
    id: str
    numero_orcamento: str
    criado_por: str
    status: StatusOrcamento
    observacoes_internas: Optional[str]
    subtotal: float
    tipo_desconto: Optional[str]
    valor_desconto: float
    taxa_imposto: float
    valor_total_manual: float
    total: float
    url_pdf: Optional[str]
    convertido_para_os_id: Optional[str]
    enviado_em: Optional[datetime]
    visualizado_em: Optional[datetime]
    aprovado_em: Optional[datetime]
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemOrcamentoCreate(BaseModel):
    item_estoque_id: Optional[str] = None
    descricao: str
    quantidade: float
    unidade: str
    preco_unitario: float
    ordem: int = 0
