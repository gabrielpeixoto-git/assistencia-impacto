from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.estoque import Unidade, TipoMovimentacao


class ItemEstoqueBase(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    nome: str = Field(..., min_length=3, max_length=255)
    categoria_id: str
    unidade: Unidade = Unidade.UNIDADE
    estoque_minimo: float = 0.0
    estoque_maximo: float = 0.0
    custo_unitario: float = Field(..., ge=0)
    preco_venda: float = Field(..., ge=0)
    percentual_markup: float = 0.0


class ItemEstoqueCreate(ItemEstoqueBase):
    descricao: Optional[str] = None
    fornecedor: Optional[str] = None
    codigo_fornecedor: Optional[str] = None
    codigo_barras: Optional[str] = None
    localizacao_estoque: Optional[str] = None


class ItemEstoqueUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=3, max_length=50)
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    categoria_id: Optional[str] = None
    unidade: Optional[Unidade] = None
    estoque_minimo: Optional[float] = None
    estoque_maximo: Optional[float] = None
    custo_unitario: Optional[float] = Field(None, ge=0)
    preco_venda: Optional[float] = Field(None, ge=0)
    percentual_markup: Optional[float] = None
    fornecedor: Optional[str] = None
    codigo_fornecedor: Optional[str] = None
    codigo_barras: Optional[str] = None
    localizacao_estoque: Optional[str] = None
    url_imagem: Optional[str] = None
    ativo: Optional[bool] = None


class ItemEstoqueResponse(ItemEstoqueBase):
    id: str
    descricao: Optional[str]
    estoque_atual: float
    fornecedor: Optional[str]
    codigo_fornecedor: Optional[str]
    url_imagem: Optional[str]
    codigo_barras: Optional[str]
    localizacao_estoque: Optional[str]
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class MovimentacaoEstoqueCreate(BaseModel):
    item_estoque_id: str
    tipo_movimentacao: TipoMovimentacao
    quantidade: float
    custo_unitario: float
    referencia_id: Optional[str] = None
    tipo_referencia: Optional[str] = None
    observacoes: Optional[str] = None


class CategoriaEstoqueCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    cor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    icone: str
    categoria_pai_id: Optional[str] = None
