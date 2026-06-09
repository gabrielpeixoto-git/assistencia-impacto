from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class StatusOrcamento(str, Enum):
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    VISUALIZADO = "visualizado"
    APROVADO = "aprovado"
    RECUSADO = "recusado"
    EXPIRADO = "expirado"
    CONVERTIDO = "convertido"


class TipoCalculoOrcamento(str, Enum):
    AUTOMATICO = "automatico"
    MANUAL = "manual"


class Orcamento(Base):
    __tablename__ = "orcamentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_orcamento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    cliente_id: Mapped[str] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=False)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    status: Mapped[StatusOrcamento] = mapped_column(SQLEnum(StatusOrcamento), default=StatusOrcamento.RASCUNHO, nullable=False)
    
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    observacoes_internas: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    valido_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    tipo_calculo: Mapped[TipoCalculoOrcamento] = mapped_column(SQLEnum(TipoCalculoOrcamento, values_callable=lambda obj: [e.value for e in obj]), default=TipoCalculoOrcamento.AUTOMATICO, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tipo_desconto: Mapped[str | None] = mapped_column(String(10), nullable=True)
    valor_desconto: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    taxa_imposto: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_total_manual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    condicoes_pagamento: Mapped[str | None] = mapped_column(Text, nullable=True)
    garantia: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    url_pdf: Mapped[str | None] = mapped_column(String(500), nullable=True)
    token_acesso_publico: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    convertido_para_os_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=True)
    
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    visualizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class ItemOrcamento(Base):
    __tablename__ = "itens_orcamento"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    orcamento_id: Mapped[str] = mapped_column(String(36), ForeignKey("orcamentos.id"), nullable=False)
    item_estoque_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("itens_estoque.id"), nullable=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    preco_total: Mapped[float] = mapped_column(Float, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
