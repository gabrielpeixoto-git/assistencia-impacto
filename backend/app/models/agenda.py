from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import uuid


class TipoEvento(str, Enum):
    SERVICO = "servico"
    REUNIAO = "reuniao"
    MANUTENCAO = "manutencao"
    INDISPONIVEL = "indisponivel"
    OUTRO = "outro"


class StatusEvento(str, Enum):
    AGENDADO = "agendado"
    CONFIRMADO = "confirmado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Agenda(Base):
    __tablename__ = "agenda"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    ordem_servico_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=True)
    tecnico_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    cliente_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=True)
    
    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_hora_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    tipo_evento: Mapped[TipoEvento] = mapped_column(SQLEnum(TipoEvento), default=TipoEvento.SERVICO, nullable=False)
    status: Mapped[StatusEvento] = mapped_column(SQLEnum(StatusEvento), default=StatusEvento.AGENDADO, nullable=False)
    
    endereco: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cor: Mapped[str] = mapped_column(String(7), default="#6C63FF", nullable=False)
    
    id_evento_google_calendar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lembrete_enviado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    tecnico: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[tecnico_id], lazy="selectin")
    cliente: Mapped["Cliente"] = relationship("Cliente", foreign_keys=[cliente_id], lazy="selectin")
    
    @property
    def tecnico_nome(self) -> str | None:
        return self.tecnico.nome_completo if self.tecnico else None
    
    @property
    def cliente_nome(self) -> str | None:
        return self.cliente.nome if self.cliente else None
    
    @property
    def cor_tecnico(self) -> str:
        """Retorna a cor do técnico, ou a cor do evento se não tiver técnico"""
        return self.tecnico.cor if self.tecnico else self.cor
