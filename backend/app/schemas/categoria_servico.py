from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CategoriaServicoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    icone: str = Field(..., min_length=1, max_length=50)
    cor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    duracao_padrao_minutos: int = Field(default=60, ge=1)
    preco_minimo: float = Field(default=0.0, ge=0)
    preco_maximo: float = Field(default=0.0, ge=0)
    categoria_pai_id: Optional[str] = None


class CategoriaServicoCreate(CategoriaServicoBase):
    pass


class CategoriaServicoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    icone: Optional[str] = Field(None, min_length=1, max_length=50)
    cor: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    duracao_padrao_minutos: Optional[int] = Field(None, ge=1)
    preco_minimo: Optional[float] = Field(None, ge=0)
    preco_maximo: Optional[float] = Field(None, ge=0)
    ativo: Optional[bool] = None


class CategoriaServicoResponse(CategoriaServicoBase):
    id: str
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
