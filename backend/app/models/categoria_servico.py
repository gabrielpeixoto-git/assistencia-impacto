from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class CategoriaServico(Base):
    __tablename__ = "categorias_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    icone: Mapped[str] = mapped_column(String(50), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    duracao_padrao_minutos: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    preco_minimo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    preco_maximo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    categoria_pai_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categorias_servico.id"), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
