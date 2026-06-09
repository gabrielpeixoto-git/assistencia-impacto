from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class StatusOS(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    AGUARDANDO = "aguardando"


class PrioridadeOS(str, Enum):
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class StatusPagamento(str, Enum):
    PENDENTE = "pendente"
    PARCIAL = "parcial"
    PAGO = "pago"
    ATRASADO = "atrasado"


class FormaPagamento(str, Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    TRANSFERENCIA = "transferencia"
    BOLETO = "boleto"


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_os: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    cliente_id: Mapped[str] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=False)
    tecnico_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=True)
    status: Mapped[StatusOS] = mapped_column(SQLEnum(StatusOS), default=StatusOS.PENDENTE, nullable=False)
    prioridade: Mapped[PrioridadeOS] = mapped_column(SQLEnum(PrioridadeOS), default=PrioridadeOS.NORMAL, nullable=False)
    tipo_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("categorias_servico.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    observacoes_internas: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    data_agendada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hora_inicio: Mapped[str | None] = mapped_column(String(5), nullable=True)
    hora_fim: Mapped[str | None] = mapped_column(String(5), nullable=True)
    
    data_conclusao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duracao_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    endereco_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("enderecos_cliente.id"), nullable=True)
    
    valor_estimado: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_final: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    status_pagamento: Mapped[StatusPagamento] = mapped_column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE, nullable=False)
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(SQLEnum(FormaPagamento), nullable=True)
    
    emitir_nota: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    url_assinatura_cliente: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url_pdf: Mapped[str | None] = mapped_column(String(500), nullable=True)
    token_acesso_publico: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class ItemOrdemServico(Base):
    __tablename__ = "itens_ordem_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ordem_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=False)
    item_estoque_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("itens_estoque.id"), nullable=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    custo_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    custo_total: Mapped[float] = mapped_column(Float, nullable=False)
    compra_externa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class TipoFoto(str, Enum):
    ANTES = "antes"
    DURANTE = "durante"
    DEPOIS = "depois"
    PROBLEMA = "problema"
    OUTRO = "outro"


class FotoOrdemServico(Base):
    __tablename__ = "fotos_ordem_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ordem_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=False)
    enviado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    url_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    url_miniatura: Mapped[str | None] = mapped_column(String(500), nullable=True)
    legenda: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo_foto: Mapped[TipoFoto] = mapped_column(SQLEnum(TipoFoto), default=TipoFoto.OUTRO, nullable=False)
    tirada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ChecklistOrdemServico(Base):
    __tablename__ = "checklist_ordem_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ordem_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    concluido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    concluido_por: Mapped[str | None] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=True)
