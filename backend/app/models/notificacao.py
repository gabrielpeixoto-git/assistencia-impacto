from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class TipoNotificacao(str, Enum):
    INFO = "info"
    SUCESSO = "sucesso"
    AVISO = "aviso"
    ERRO = "erro"
    LEMBRETE = "lembrete"


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo: Mapped[str] = mapped_column(Text, nullable=False)
    
    tipo: Mapped[TipoNotificacao] = mapped_column(SQLEnum(TipoNotificacao), default=TipoNotificacao.INFO, nullable=False)
    tipo_entidade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    id_entidade: Mapped[str | None] = mapped_column(String(36), nullable=True)
    
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    url_acao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
