from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class TipoTransacao(str, Enum):
    receita = "receita"
    despesa = "despesa"


class StatusTransacao(str, Enum):
    pendente = "pendente"
    pago = "pago"
    atrasado = "atrasado"
    cancelado = "cancelado"


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_transacao: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(SQLEnum(TipoTransacao), nullable=False)
    categoria_id: Mapped[str] = mapped_column(String(36), ForeignKey("categorias_financeiras.id"), nullable=False)
    
    ordem_servico_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=True)
    orcamento_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orcamentos.id"), nullable=True)
    cliente_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=True)
    fornecedor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_pagamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[StatusTransacao] = mapped_column(SQLEnum(StatusTransacao), default=StatusTransacao.pendente, nullable=False)
    forma_pagamento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    conta_bancaria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    url_comprovante: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    recorrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    intervalo_recorrencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class CategoriaFinanceira(Base):
    __tablename__ = "categorias_financeiras"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tipo: Mapped[TipoTransacao] = mapped_column(SQLEnum(TipoTransacao), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    icone: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
