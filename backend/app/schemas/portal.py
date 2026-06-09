from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.models.orcamento import StatusOrcamento
from app.models.ordem_servico import StatusOS, PrioridadeOS, StatusPagamento


class OrcamentoPublicoResponse(BaseModel):
    """Resposta de orçamento para visualização pública (cliente)"""
    id: str
    numero_orcamento: str
    titulo: str
    descricao: str
    status: StatusOrcamento
    valido_ate: Optional[datetime]
    subtotal: float
    tipo_desconto: Optional[str]
    valor_desconto: float
    taxa_imposto: float
    total: float
    condicoes_pagamento: Optional[str]
    garantia: Optional[str]
    url_pdf: Optional[str]
    enviado_em: Optional[datetime]
    visualizado_em: Optional[datetime]
    aprovado_em: Optional[datetime]
    criado_em: datetime
    
    # Informações do cliente (limitadas)
    cliente_nome: str
    cliente_email: str
    
    model_config = ConfigDict(from_attributes=True)


class ItemOrcamentoPublicoResponse(BaseModel):
    """Item de orçamento para visualização pública"""
    descricao: str
    quantidade: float
    unidade: str
    preco_unitario: float
    preco_total: float
    ordem: int
    
    model_config = ConfigDict(from_attributes=True)


class OSPublicaResponse(BaseModel):
    """Resposta de OS para visualização pública (cliente)"""
    id: str
    numero_os: str
    titulo: str
    descricao: str
    status: StatusOS
    prioridade: PrioridadeOS
    data_agendada: Optional[datetime]
    hora_inicio: Optional[str]
    hora_fim: Optional[str]
    data_conclusao: Optional[datetime]
    duracao_minutos: Optional[int]
    valor_estimado: float
    valor_final: float
    status_pagamento: StatusPagamento
    forma_pagamento: Optional[str]
    criado_em: datetime
    atualizado_em: datetime
    
    # Informações do cliente (limitadas)
    cliente_nome: str
    cliente_email: str
    
    # Informações do técnico (se atribuído)
    tecnico_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ItemOSPublicoResponse(BaseModel):
    """Item de OS para visualização pública"""
    descricao: str
    quantidade: float
    unidade: str
    custo_unitario: float
    custo_total: float
    
    model_config = ConfigDict(from_attributes=True)


class FotoOSPublicoResponse(BaseModel):
    """Foto de OS para visualização pública"""
    url_arquivo: str
    url_miniatura: Optional[str]
    legenda: Optional[str]
    tipo_foto: str
    tirada_em: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class ChecklistOSPublicoResponse(BaseModel):
    """Checklist de OS para visualização pública"""
    descricao: str
    concluido: bool
    concluido_em: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class AvaliacaoCreate(BaseModel):
    """Schema para criação de avaliação de serviço"""
    nota: int = Field(..., ge=1, le=5, description="Nota de 1 a 5")
    comentario: Optional[str] = Field(None, max_length=1000, description="Comentário opcional")


class AvaliacaoResponse(BaseModel):
    """Resposta de avaliação"""
    id: str
    ordem_servico_id: str
    nota: int
    comentario: Optional[str]
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AcaoOrcamentoResponse(BaseModel):
    """Resposta de ação em orçamento (aprovar/rejeitar)"""
    mensagem: str
    status: StatusOrcamento
