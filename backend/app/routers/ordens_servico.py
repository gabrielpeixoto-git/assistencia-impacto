from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from app.database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets

limiter = Limiter(key_func=get_remote_address)
from app.schemas.ordem_servico import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    ItemOrdemServicoCreate, FotoOrdemServicoCreate, ChecklistOrdemServicoCreate
)
from app.models.ordem_servico import (
    OrdemServico, ItemOrdemServico, FotoOrdemServico, ChecklistOrdemServico, StatusOS
)
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from app.models.log_auditoria import LogAuditoria
from datetime import datetime, UTC
from loguru import logger
from app.websocket.manager import manager

router = APIRouter(prefix="/api/ordens-servico", tags=["ordens-servico"])


# Máquina de estados para transições de status
TRANSICOES_VALIDAS = {
    "pendente": ["confirmada", "cancelada"],
    "confirmada": ["em_andamento", "cancelada"],
    "em_andamento": ["concluida", "aguardando", "cancelada"],
    "aguardando": ["em_andamento", "cancelada"],
    "concluida": [],  # estado final
    "cancelada": [],  # estado final
}


def gerar_numero_os():
    """Gera um número de OS único."""
    from datetime import datetime
    ano = datetime.now().year
    mes = datetime.now().month
    return f"OS{ano}{mes:02d}"


@router.get("")
async def listar_ordens_servico(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = None,
    prioridade: str = None,
    cliente_id: str = None,
    tecnico_id: str = None,
    busca: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as ordens de serviço com filtros opcionais."""
    query = select(OrdemServico)
    
    if status:
        query = query.where(OrdemServico.status == status)
    
    if prioridade:
        query = query.where(OrdemServico.prioridade == prioridade)
    
    if cliente_id:
        query = query.where(OrdemServico.cliente_id == cliente_id)
    
    if tecnico_id:
        query = query.where(OrdemServico.tecnico_id == tecnico_id)
    
    if busca:
        query = query.where(
            or_(
                OrdemServico.titulo.ilike(f"%{busca}%"),
                OrdemServico.descricao.ilike(f"%{busca}%")
            )
        )
    
    query = query.order_by(OrdemServico.criado_em.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    ordens = result.scalars().all()
    
    # Converter manualmente para dicionários para controlar a serialização
    result_list = [
        {
            "id": os.id,
            "numero_os": os.numero_os,
            "titulo": os.titulo,
            "descricao": os.descricao,
            "status": os.status.value if os.status else None,
            "prioridade": os.prioridade.value if os.prioridade else None,
            "cliente_id": os.cliente_id,
            "tecnico_id": os.tecnico_id,
            "tipo_servico_id": os.tipo_servico_id,
            "valor_estimado": os.valor_estimado,
            "valor_final": os.valor_final,
            "data_agendada": os.data_agendada.isoformat() if os.data_agendada else None,
            "criado_em": os.criado_em.isoformat() if os.criado_em else None,
        }
        for os in ordens
    ]
    return result_list


@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def obter_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém uma ordem de serviço específica por ID."""
    query = select(OrdemServico).where(OrdemServico.id == os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    return os


@router.post("", response_model=OrdemServicoResponse, status_code=201)
@limiter.limit("20/minute")
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova ordem de serviço."""
    try:
        # Gerar número de OS único
        numero_os = gerar_numero_os()
        
        # Verificar se já existe OS com este número
        query = select(OrdemServico).where(OrdemServico.numero_os == numero_os)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            # Adicionar sufixo se já existir
            contador = 1
            while True:
                numero_os = f"{gerar_numero_os()}-{contador}"
                query = select(OrdemServico).where(OrdemServico.numero_os == numero_os)
                result = await db.execute(query)
                if not result.scalar_one_or_none():
                    break
                contador += 1
        
        os = OrdemServico(
            **os_data.model_dump(),
            numero_os=numero_os,
            criado_por=current_user.id,
            token_acesso_publico=secrets.token_urlsafe(32)
        )
        
        db.add(os)
        await db.commit()
        await db.refresh(os)
        
        # Enviar notificação WebSocket
        await manager.send_personal_message({
            "type": "os_criada",
            "data": {
                "id": os.id,
                "numero_os": os.numero_os,
                "cliente_id": os.cliente_id,
                "tecnico_id": os.tecnico_id,
                "titulo": os.titulo,
                "status": os.status,
                "prioridade": os.prioridade,
                "criado_em": os.criado_em.isoformat()
            }
        }, current_user.id)
        
        logger.info(f"Ordem de serviço {os.numero_os} (ID: {os.id}) criada por {current_user.email}")
        return os
    except Exception as e:
        logger.error(f"Erro ao criar ordem de serviço: {str(e)}")
        raise


@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_ordem_servico(
    os_id: str,
    os_data: OrdemServicoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza uma ordem de serviço existente."""
    try:
        query = select(OrdemServico).where(OrdemServico.id == os_id)
        result = await db.execute(query)
        os = result.scalar_one_or_none()
        
        if not os:
            logger.warning(f"Ordem de serviço {os_id} não encontrada para atualização por {current_user.email}")
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
        
        update_data = os_data.model_dump(exclude_unset=True)
        
        # Se status mudou para concluída, registrar data de conclusão
        if "status" in update_data and update_data["status"] == "concluida":
            update_data["data_conclusao"] = datetime.now(UTC)
        
        for field, value in update_data.items():
            setattr(os, field, value)
        
        await db.commit()
        await db.refresh(os)
        
        logger.info(f"Ordem de serviço {os.numero_os} (ID: {os_id}) atualizada por {current_user.email}")
        return os
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ordem de serviço {os_id}: {str(e)}")
        raise


@router.delete("/{os_id}", status_code=204)
async def deletar_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta uma ordem de serviço (hard delete)."""
    try:
        query = select(OrdemServico).where(OrdemServico.id == os_id)
        result = await db.execute(query)
        os = result.scalar_one_or_none()

        if not os:
            logger.warning(f"Ordem de serviço {os_id} não encontrada para deleção por {current_user.email}")
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        await db.delete(os)
        await db.commit()

        logger.info(f"Ordem de serviço {os.numero_os} (ID: {os_id}) deletada por {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar ordem de serviço {os_id}: {str(e)}")
        raise


@router.patch("/{os_id}/status", response_model=OrdemServicoResponse)
async def alterar_status_os(
    os_id: str,
    novo_status: str = Body(..., embed=True),
    motivo: str = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Altera o status de uma ordem de serviço com validação de transições."""
    try:
        query = select(OrdemServico).where(OrdemServico.id == os_id)
        result = await db.execute(query)
        os = result.scalar_one_or_none()

        if not os:
            raise HTTPException(status_code=404, detail="OS não encontrada")

        status_atual = os.status.value
        if novo_status not in TRANSICOES_VALIDAS.get(status_atual, []):
            raise HTTPException(
                status_code=409,
                detail=f"Transição inválida: {status_atual} → {novo_status}. Permitidas: {TRANSICOES_VALIDAS[status_atual]}"
            )

        if novo_status == "cancelada" and not motivo:
            raise HTTPException(status_code=400, detail="Motivo de cancelamento obrigatório")

        os.status = StatusOS(novo_status)
        if novo_status == "concluida":
            os.data_conclusao = datetime.now(UTC)
        if novo_status == "em_andamento" and not os.hora_inicio:
            os.hora_inicio = datetime.now(UTC).strftime("%H:%M")

        # Log de auditoria
        import json
        log = LogAuditoria(
            usuario_id=current_user.id,
            acao=f"status_os_alterado: {status_atual} → {novo_status}",
            tipo_entidade="ordem_servico",
            id_entidade=os_id,
            alteracoes=json.dumps({"status_anterior": status_atual, "status_novo": novo_status, "motivo": motivo})
        )
        db.add(log)
        await db.commit()
        await db.refresh(os)

        logger.info(f"OS {os.numero_os} (ID: {os_id}) status alterado de {status_atual} para {novo_status} por {current_user.email}")
        return os
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar status da OS {os_id}: {str(e)}")
        raise


@router.post("/{os_id}/itens", response_model=dict, status_code=201)
async def adicionar_item_ordem_servico(
    os_id: str,
    item_data: ItemOrdemServicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Adiciona um item a uma ordem de serviço."""
    # Verificar se a OS existe
    query = select(OrdemServico).where(OrdemServico.id == os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    # Calcular custo total
    custo_total = item_data.quantidade * item_data.custo_unitario
    
    item = ItemOrdemServico(
        ordem_servico_id=os_id,
        **item_data.model_dump(),
        custo_total=custo_total
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return {"id": item.id, "mensagem": "Item adicionado com sucesso"}


@router.get("/{os_id}/itens", response_model=List[dict])
async def listar_itens_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os itens de uma ordem de serviço."""
    query = select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os_id)
    result = await db.execute(query)
    itens = result.scalars().all()
    
    return [
        {
            "id": i.id,
            "item_estoque_id": i.item_estoque_id,
            "descricao": i.descricao,
            "quantidade": i.quantidade,
            "unidade": i.unidade,
            "custo_unitario": i.custo_unitario,
            "custo_total": i.custo_total,
            "compra_externa": i.compra_externa,
            "criado_em": i.criado_em
        }
        for i in itens
    ]


@router.post("/{os_id}/fotos", response_model=dict, status_code=201)
async def adicionar_foto_ordem_servico(
    os_id: str,
    foto_data: FotoOrdemServicoCreate,
    url_arquivo: str = Query(..., description="URL do arquivo de foto"),
    url_miniatura: str = Query(None, description="URL da miniatura"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Adiciona uma foto a uma ordem de serviço."""
    # Verificar se a OS existe
    query = select(OrdemServico).where(OrdemServico.id == os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    foto = FotoOrdemServico(
        ordem_servico_id=os_id,
        enviado_por=current_user.id,
        url_arquivo=url_arquivo,
        url_miniatura=url_miniatura,
        **foto_data.model_dump()
    )
    
    db.add(foto)
    await db.commit()
    await db.refresh(foto)
    
    return {"id": foto.id, "mensagem": "Foto adicionada com sucesso"}


@router.get("/{os_id}/fotos", response_model=List[dict])
async def listar_fotos_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as fotos de uma ordem de serviço."""
    query = select(FotoOrdemServico).where(FotoOrdemServico.ordem_servico_id == os_id)
    result = await db.execute(query)
    fotos = result.scalars().all()
    
    return [
        {
            "id": f.id,
            "enviado_por": f.enviado_por,
            "url_arquivo": f.url_arquivo,
            "url_miniatura": f.url_miniatura,
            "legenda": f.legenda,
            "tipo_foto": f.tipo_foto,
            "tirada_em": f.tirada_em,
            "criada_em": f.criada_em
        }
        for f in fotos
    ]


@router.post("/{os_id}/checklist", response_model=dict, status_code=201)
async def adicionar_checklist_ordem_servico(
    os_id: str,
    checklist_data: ChecklistOrdemServicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Adiciona um item de checklist a uma ordem de serviço."""
    # Verificar se a OS existe
    query = select(OrdemServico).where(OrdemServico.id == os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    checklist = ChecklistOrdemServico(
        ordem_servico_id=os_id,
        **checklist_data.model_dump()
    )
    
    db.add(checklist)
    await db.commit()
    await db.refresh(checklist)
    
    return {"id": checklist.id, "mensagem": "Item de checklist adicionado com sucesso"}


@router.get("/{os_id}/checklist", response_model=List[dict])
async def listar_checklist_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os itens de checklist de uma ordem de serviço."""
    query = select(ChecklistOrdemServico).where(ChecklistOrdemServico.ordem_servico_id == os_id)
    result = await db.execute(query)
    checklist = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "descricao": c.descricao,
            "concluido": c.concluido,
            "concluido_em": c.concluido_em,
            "concluido_por": c.concluido_por
        }
        for c in checklist
    ]


@router.put("/{os_id}/checklist/{checklist_id}", response_model=dict)
async def marcar_checklist_concluido(
    os_id: str,
    checklist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Marca um item de checklist como concluído."""
    query = select(ChecklistOrdemServico).where(
        and_(
            ChecklistOrdemServico.id == checklist_id,
            ChecklistOrdemServico.ordem_servico_id == os_id
        )
    )
    result = await db.execute(query)
    checklist = result.scalar_one_or_none()
    
    if not checklist:
        raise HTTPException(status_code=404, detail="Item de checklist não encontrado")
    
    checklist.concluido = True
    checklist.concluido_em = datetime.now(UTC)
    checklist.concluido_por = current_user.id
    
    await db.commit()
    
    return {"mensagem": "Checklist marcado como concluído"}


@router.get("/{os_id}/pdf")
async def gerar_pdf_ordem_servico(
    os_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Gera PDF da ordem de serviço."""
    from fastapi.responses import Response
    from app.services.pdf_service import gerar_pdf_ordem_servico
    
    # Gerar PDF usando a nova função que retorna bytes
    pdf_bytes = await gerar_pdf_ordem_servico(os_id, db)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ordem_servico.pdf"}
    )
