from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update
from app.database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
from app.schemas.estoque import (
    ItemEstoqueCreate, ItemEstoqueUpdate, ItemEstoqueResponse,
    MovimentacaoEstoqueCreate, CategoriaEstoqueCreate
)
from app.models.estoque import (
    ItemEstoque, MovimentacaoEstoque, CategoriaEstoque, TipoMovimentacao
)
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from app.models.log_auditoria import LogAuditoria
from datetime import datetime, UTC

router = APIRouter(prefix="/api/estoque", tags=["estoque"])


@router.get("/itens", response_model=List[ItemEstoqueResponse])
async def listar_itens_estoque(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    categoria_id: str = None,
    ativo: bool = None,
    busca: str = None,
    estoque_baixo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os itens de estoque com filtros opcionais."""
    query = select(ItemEstoque)
    
    if categoria_id:
        query = query.where(ItemEstoque.categoria_id == categoria_id)
    
    if ativo is not None:
        query = query.where(ItemEstoque.ativo == ativo)
    
    if busca:
        query = query.where(
            or_(
                ItemEstoque.nome.ilike(f"%{busca}%"),
                ItemEstoque.sku.ilike(f"%{busca}%")
            )
        )
    
    if estoque_baixo:
        query = query.where(ItemEstoque.estoque_atual <= ItemEstoque.estoque_minimo)
    
    query = query.order_by(ItemEstoque.nome).offset(skip).limit(limit)
    result = await db.execute(query)
    itens = result.scalars().all()
    
    return itens


@router.get("/itens/{item_id}", response_model=ItemEstoqueResponse)
async def obter_item_estoque(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém um item de estoque específico por ID."""
    query = select(ItemEstoque).where(ItemEstoque.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    
    return item


@router.post("/itens", response_model=ItemEstoqueResponse, status_code=201)
@limiter.limit("20/minute")
async def criar_item_estoque(
    item_data: ItemEstoqueCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria um novo item de estoque."""
    # Verificar se já existe item com este SKU (apenas itens ativos)
    query = select(ItemEstoque).where(
        ItemEstoque.sku == item_data.sku,
        ItemEstoque.ativo == True
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Item com este SKU já existe")
    
    item = ItemEstoque(
        **item_data.model_dump(),
        estoque_atual=0.0
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return item


@router.put("/itens/{item_id}", response_model=ItemEstoqueResponse)
async def atualizar_item_estoque(
    item_id: str,
    item_data: ItemEstoqueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza um item de estoque existente."""
    query = select(ItemEstoque).where(ItemEstoque.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    return item


@router.delete("/itens/{item_id}", status_code=204)
async def deletar_item_estoque(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta um item de estoque (soft delete)."""
    query = select(ItemEstoque).where(ItemEstoque.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    
    item.ativo = False
    await db.commit()
    
    return None


@router.post("/movimentacoes", response_model=dict, status_code=201)
async def criar_movimentacao_estoque(
    movimentacao_data: MovimentacaoEstoqueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova movimentação de estoque."""
    # Verificar se o item existe
    query = select(ItemEstoque).where(ItemEstoque.id == movimentacao_data.item_estoque_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    
    # Calcular custo total
    custo_total = movimentacao_data.quantidade * movimentacao_data.custo_unitario
    
    # Validar estoque suficiente para saída
    if movimentacao_data.tipo_movimentacao == TipoMovimentacao.SAIDA:
        if item.estoque_atual < movimentacao_data.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Estoque atual: {item.estoque_atual}, solicitado: {movimentacao_data.quantidade}"
            )
    
    movimentacao = MovimentacaoEstoque(
        **movimentacao_data.model_dump(),
        usuario_id=current_user.id,
        custo_total=custo_total
    )
    
    db.add(movimentacao)
    
    # Atualizar estoque do item
    if movimentacao_data.tipo_movimentacao == TipoMovimentacao.ENTRADA:
        item.estoque_atual += movimentacao_data.quantidade
    elif movimentacao_data.tipo_movimentacao == TipoMovimentacao.SAIDA:
        item.estoque_atual -= movimentacao_data.quantidade
    elif movimentacao_data.tipo_movimentacao == TipoMovimentacao.AJUSTE:
        item.estoque_atual = movimentacao_data.quantidade
    
    await db.commit()
    await db.refresh(movimentacao)
    
    return {"id": movimentacao.id, "mensagem": "Movimentação registrada com sucesso"}


@router.get("/movimentacoes", response_model=List[dict])
async def listar_movimentacoes_estoque(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    item_estoque_id: str = None,
    tipo_movimentacao: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as movimentações de estoque com filtros opcionais."""
    query = select(MovimentacaoEstoque)
    
    if item_estoque_id:
        query = query.where(MovimentacaoEstoque.item_estoque_id == item_estoque_id)
    
    if tipo_movimentacao:
        query = query.where(MovimentacaoEstoque.tipo_movimentacao == tipo_movimentacao)
    
    query = query.order_by(MovimentacaoEstoque.criado_em.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    movimentacoes = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "item_estoque_id": m.item_estoque_id,
            "usuario_id": m.usuario_id,
            "tipo_movimentacao": m.tipo_movimentacao,
            "quantidade": m.quantidade,
            "custo_unitario": m.custo_unitario,
            "custo_total": m.custo_total,
            "referencia_id": m.referencia_id,
            "tipo_referencia": m.tipo_referencia,
            "observacoes": m.observacoes,
            "criado_em": m.criado_em
        }
        for m in movimentacoes
    ]


@router.post("/itens/{item_id}/movimentar", response_model=dict)
async def movimentar_item_estoque(
    item_id: str,
    quantidade: int = Body(..., ge=1),
    tipo: str = Body(..., description="Tipo: entrada ou saida"),
    motivo: str = Body(..., description="Motivo da movimentação"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Movimenta item de estoque de forma atômica."""
    try:
        # Validar tipo
        if tipo not in ["entrada", "saida"]:
            raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'")

        # Transação atômica: SELECT FOR UPDATE para bloquear o item
        from sqlalchemy import text
        query = select(ItemEstoque).where(ItemEstoque.id == item_id).with_for_update()
        result = await db.execute(query)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item de estoque não encontrado")

        # Validação de estoque suficiente para saídas
        if tipo == "saida" and item.estoque_atual < quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Atual: {item.estoque_atual}, Solicitado: {quantidade}"
            )

        # Atualizar estoque
        if tipo == "entrada":
            item.estoque_atual += quantidade
            tipo_mov = TipoMovimentacao.ENTRADA
        else:
            item.estoque_atual -= quantidade
            tipo_mov = TipoMovimentacao.SAIDA

        # Criar registro de movimentação
        movimentacao = MovimentacaoEstoque(
            item_estoque_id=item_id,
            usuario_id=current_user.id,
            tipo_movimentacao=tipo_mov,
            quantidade=quantidade,
            custo_unitario=item.custo_unitario,
            custo_total=quantidade * item.custo_unitario,
            observacoes=motivo
        )
        db.add(movimentacao)

        # Log de auditoria
        log = LogAuditoria(
            usuario_id=current_user.id,
            acao=f"estoque_movimentado: {tipo}",
            tipo_entidade="item_estoque",
            id_entidade=item_id,
            alteracoes={
                "quantidade": quantidade,
                "tipo": tipo,
                "motivo": motivo,
                "estoque_anterior": item.estoque_atual - (quantidade if tipo == "entrada" else -quantidade),
                "estoque_novo": item.estoque_atual
            }
        )
        db.add(log)

        await db.commit()
        await db.refresh(item)

        return {
            "id": movimentacao.id,
            "item_id": item_id,
            "estoque_atual": item.estoque_atual,
            "tipo": tipo,
            "quantidade": quantidade,
            "mensagem": "Movimentação realizada com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao movimentar estoque: {str(e)}")


@router.get("/categorias", response_model=List[dict])
async def listar_categorias_estoque(
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as categorias de estoque."""
    query = select(CategoriaEstoque)
    
    if ativo is not None:
        query = query.where(CategoriaEstoque.ativo == ativo)
    
    query = query.order_by(CategoriaEstoque.nome)
    result = await db.execute(query)
    categorias = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cor": c.cor,
            "icone": c.icone,
            "categoria_pai_id": c.categoria_pai_id,
            "ativo": c.ativo
        }
        for c in categorias
    ]


@router.post("/categorias", response_model=dict, status_code=201)
async def criar_categoria_estoque(
    categoria_data: CategoriaEstoqueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova categoria de estoque."""
    # Verificar se já existe categoria com este nome
    query = select(CategoriaEstoque).where(CategoriaEstoque.nome == categoria_data.nome)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe")
    
    categoria = CategoriaEstoque(**categoria_data.model_dump())
    
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    
    return {"id": categoria.id, "mensagem": "Categoria criada com sucesso"}


@router.put("/categorias/{categoria_id}", response_model=dict)
async def atualizar_categoria_estoque(
    categoria_id: str,
    nome: str = None,
    cor: str = None,
    icone: str = None,
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza uma categoria de estoque."""
    query = select(CategoriaEstoque).where(CategoriaEstoque.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    if nome:
        categoria.nome = nome
    if cor:
        categoria.cor = cor
    if icone:
        categoria.icone = icone
    if ativo is not None:
        categoria.ativo = ativo
    
    await db.commit()
    
    return {"mensagem": "Categoria atualizada com sucesso"}


@router.delete("/categorias/{categoria_id}", status_code=204)
async def deletar_categoria_estoque(
    categoria_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta uma categoria de estoque."""
    query = select(CategoriaEstoque).where(CategoriaEstoque.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    await db.delete(categoria)
    await db.commit()
    
    return None


@router.get("/alertas", response_model=List[ItemEstoqueResponse])
async def listar_alertas_estoque(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista itens com estoque abaixo do mínimo."""
    from sqlalchemy import and_
    query = select(ItemEstoque).where(
        and_(
            ItemEstoque.ativo == True,
            ItemEstoque.estoque_atual <= ItemEstoque.estoque_minimo
        )
    )
    query = query.order_by(ItemEstoque.estoque_atual)
    result = await db.execute(query)
    itens = result.scalars().all()
    
    return itens
