from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class Perfil(str, Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    TECNICO = "tecnico"
    VISUALIZADOR = "visualizador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[Perfil] = mapped_column(SQLEnum(Perfil), default=Perfil.VISUALIZADOR, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cor: Mapped[str] = mapped_column(String(7), default="#6C63FF", nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
