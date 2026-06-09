from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.categoria_servico import CategoriaServicoCreate, CategoriaServicoResponse
from app.models.categoria_servico import CategoriaServico
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/categorias-servico", tags=["categorias-servico"])


@router.get("", response_model=List[CategoriaServicoResponse])
async def listar_categorias_servico(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as categorias de serviço."""
    query = select(CategoriaServico).where(CategoriaServico.ativo == True)
    result = await db.execute(query)
    categorias = result.scalars().all()
    return categorias


@router.post("", response_model=CategoriaServicoResponse, status_code=201)
async def criar_categoria_servico(
    categoria_data: CategoriaServicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova categoria de serviço."""
    # Verificar se já existe categoria com este nome
    query = select(CategoriaServico).where(CategoriaServico.nome == categoria_data.nome)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe")
    
    categoria = CategoriaServico(**categoria_data.model_dump())
    
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    
    return categoria


@router.get("/{categoria_id}", response_model=CategoriaServicoResponse)
async def obter_categoria_servico(
    categoria_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém uma categoria de serviço específica por ID."""
    query = select(CategoriaServico).where(CategoriaServico.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria de serviço não encontrada")
    
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaServicoResponse)
async def atualizar_categoria_servico(
    categoria_id: str,
    nome: str = None,
    descricao: str = None,
    icone: str = None,
    cor: str = None,
    duracao_padrao_minutos: int = None,
    preco_minimo: float = None,
    preco_maximo: float = None,
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza uma categoria de serviço."""
    query = select(CategoriaServico).where(CategoriaServico.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria de serviço não encontrada")
    
    if nome:
        categoria.nome = nome
    if descricao:
        categoria.descricao = descricao
    if icone:
        categoria.icone = icone
    if cor:
        categoria.cor = cor
    if duracao_padrao_minutos is not None:
        categoria.duracao_padrao_minutos = duracao_padrao_minutos
    if preco_minimo is not None:
        categoria.preco_minimo = preco_minimo
    if preco_maximo is not None:
        categoria.preco_maximo = preco_maximo
    if ativo is not None:
        categoria.ativo = ativo
    
    await db.commit()
    
    return categoria


@router.delete("/{categoria_id}", status_code=204)
async def deletar_categoria_servico(
    categoria_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta uma categoria de serviço (soft delete)."""
    query = select(CategoriaServico).where(CategoriaServico.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria de serviço não encontrada")
    
    categoria.ativo = False
    await db.commit()
    
    return None
