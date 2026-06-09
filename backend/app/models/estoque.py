from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid


class Unidade(str, Enum):
    UNIDADE = "unidade"
    METRO = "metro"
    LITRO = "litro"
    KG = "kg"
    CAIXA = "caixa"
    ROLO = "rolo"
    PAR = "par"


class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    COMPRA = "compra"
    USO_OS = "uso_os"


class ItemEstoque(Base):
    __tablename__ = "itens_estoque"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    categoria_id: Mapped[str] = mapped_column(String(36), ForeignKey("categorias_estoque.id"), nullable=False)
    
    unidade: Mapped[Unidade] = mapped_column(SQLEnum(Unidade), default=Unidade.UNIDADE, nullable=False)
    
    estoque_atual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estoque_minimo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estoque_maximo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    custo_unitario: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    preco_venda: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentual_markup: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    fornecedor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    codigo_fornecedor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    url_imagem: Mapped[str | None] = mapped_column(String(500), nullable=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(50), nullable=True)
    localizacao_estoque: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_estoque_id: Mapped[str] = mapped_column(String(36), ForeignKey("itens_estoque.id"), nullable=False)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    
    tipo_movimentacao: Mapped[TipoMovimentacao] = mapped_column(SQLEnum(TipoMovimentacao), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    custo_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    custo_total: Mapped[float] = mapped_column(Float, nullable=False)
    
    referencia_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tipo_referencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class CategoriaEstoque(Base):
    __tablename__ = "categorias_estoque"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    icone: Mapped[str] = mapped_column(String(50), nullable=False)
    categoria_pai_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categorias_estoque.id"), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
