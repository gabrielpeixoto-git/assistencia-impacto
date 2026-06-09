from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, UTC

from app.database import get_db
from app.models.notificacao import Notificacao, TipoNotificacao
from app.models.usuario import Usuario
from app.dependencies import get_usuario_atual, require_admin
from app.schemas.notificacao import NotificacaoCreate, NotificacaoResponse, NotificacaoUpdate

router = APIRouter(prefix="/notificacoes", tags=["notificações"])


@router.get("", response_model=List[NotificacaoResponse])
async def listar_notificacoes(
    apenas_nao_lidas: bool = False,
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Lista notificações do usuário autenticado."""
    query = select(Notificacao).where(Notificacao.usuario_id == usuario_atual.id)
    
    if apenas_nao_lidas:
        query = query.where(Notificacao.lida == False)
    
    query = query.order_by(Notificacao.criado_em.desc())
    
    result = await db.execute(query)
    notificacoes = result.scalars().all()
    
    return notificacoes


@router.post("", response_model=NotificacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_notificacao(
    notificacao_data: NotificacaoCreate,
    usuario_atual: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Cria uma nova notificação (apenas admin)."""
    notificacao = Notificacao(
        usuario_id=notificacao_data.usuario_id or usuario_atual.id,
        titulo=notificacao_data.titulo,
        corpo=notificacao_data.corpo,
        tipo=notificacao_data.tipo,
        url_acao=notificacao_data.url_acao,
        tipo_entidade=notificacao_data.tipo_entidade,
        id_entidade=notificacao_data.id_entidade
    )
    
    db.add(notificacao)
    await db.commit()
    await db.refresh(notificacao)
    
    return notificacao


@router.patch("/{notificacao_id}/marcar-lida")
async def marcar_notificacao_lida(
    notificacao_id: str,
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Marca uma notificação como lida."""
    result = await db.execute(
        select(Notificacao).where(
            and_(
                Notificacao.id == notificacao_id,
                Notificacao.usuario_id == usuario_atual.id
            )
        )
    )
    notificacao = result.scalar_one_or_none()
    
    if not notificacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    notificacao.lida = True
    notificacao.lida_em = datetime.now(UTC)
    
    await db.commit()
    
    return {"message": "Notificação marcada como lida"}


@router.patch("/marcar-todas-lidas")
async def marcar_todas_lidas(
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Marca todas as notificações do usuário como lidas."""
    result = await db.execute(
        select(Notificacao).where(
            and_(
                Notificacao.usuario_id == usuario_atual.id,
                Notificacao.lida == False
            )
        )
    )
    notificacoes = result.scalars().all()
    
    for notificacao in notificacoes:
        notificacao.lida = True
        notificacao.lida_em = datetime.now(UTC)
    
    await db.commit()
    
    return {"message": f"{len(notificacoes)} notificações marcadas como lidas"}


@router.delete("/{notificacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_notificacao(
    notificacao_id: str,
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Deleta uma notificação."""
    result = await db.execute(
        select(Notificacao).where(
            and_(
                Notificacao.id == notificacao_id,
                Notificacao.usuario_id == usuario_atual.id
            )
        )
    )
    notificacao = result.scalar_one_or_none()
    
    if not notificacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    await db.delete(notificacao)
    await db.commit()
    
    return None


@router.get("/nao-lidas")
async def contar_nao_lidas(
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Conta notificações não lidas do usuário."""
    result = await db.execute(
        select(Notificacao).where(
            and_(
                Notificacao.usuario_id == usuario_atual.id,
                Notificacao.lida == False
            )
        )
    )
    notificacoes = result.scalars().all()
    
    return {"quantidade": len(notificacoes)}
