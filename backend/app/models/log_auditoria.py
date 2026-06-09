from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(100), nullable=False)
    
    tipo_entidade: Mapped[str] = mapped_column(String(50), nullable=False)
    id_entidade: Mapped[str] = mapped_column(String(36), nullable=False)
    alteracoes: Mapped[str] = mapped_column(Text, nullable=True)
    
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
