from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_
from app.database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets

limiter = Limiter(key_func=get_remote_address)
from app.schemas.orcamento import (
    OrcamentoCreate, OrcamentoUpdate, OrcamentoResponse, ItemOrcamentoCreate
)
from app.models.orcamento import Orcamento, ItemOrcamento, StatusOrcamento
from app.models.categoria_servico import CategoriaServico
from app.models.cliente import Cliente
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from app.services.email_service import EmailService
from app.services.whatsapp_service import WhatsAppService
from datetime import datetime, UTC
from loguru import logger
from app.websocket.manager import manager

router = APIRouter(prefix="/api/orcamentos", tags=["orcamentos"])


@router.get("/resumo", response_model=dict)
async def resumo_orcamentos(
    periodo: str = Query(None, description="Período: hoje, semana, mes, trimestre, ano"),
    data_inicio: datetime = Query(None, description="Data início para filtro customizado"),
    data_fim: datetime = Query(None, description="Data fim para filtro customizado"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Retorna resumo de orçamentos por status."""
    from datetime import datetime, timedelta
    
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    
    # Determinar período de filtro
    if data_inicio and data_fim:
        filtro_inicio = data_inicio
        filtro_fim = data_fim
    elif periodo == "hoje":
        filtro_inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "semana":
        filtro_inicio = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "mes":
        filtro_inicio = inicio_mes.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "trimestre":
        trimestre_atual = (hoje.month - 1) // 3
        inicio_trimestre = datetime(hoje.year, trimestre_atual * 3 + 1, 1)
        filtro_inicio = inicio_trimestre.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "ano":
        inicio_ano = datetime(hoje.year, 1, 1)
        filtro_inicio = inicio_ano.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Padrão: mês atual
        filtro_inicio = inicio_mes.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Total de orçamentos no período
    query_total = select(func.count(Orcamento.id)).where(
        and_(
            Orcamento.criado_em >= filtro_inicio,
            Orcamento.criado_em <= filtro_fim
        )
    )
    result_total = await db.execute(query_total)
    total = result_total.scalar() or 0
    
    # Orçamentos por status no período
    query_por_status = select(
        Orcamento.status,
        func.count(Orcamento.id)
    ).where(
        and_(
            Orcamento.criado_em >= filtro_inicio,
            Orcamento.criado_em <= filtro_fim
        )
    ).group_by(Orcamento.status)
    result_por_status = await db.execute(query_por_status)
    status_counts = {status: count for status, count in result_por_status.all()}
    
    aprovados = status_counts.get(StatusOrcamento.APROVADO, 0) + status_counts.get(StatusOrcamento.CONVERTIDO, 0)
    pendentes = status_counts.get(StatusOrcamento.ENVIADO, 0) + status_counts.get(StatusOrcamento.VISUALIZADO, 0)
    rejeitados = status_counts.get(StatusOrcamento.RECUSADO, 0)
    
    # Taxa de conversão
    taxa_conversao = 0
    if total > 0:
        taxa_conversao = (aprovados / total) * 100
    
    return {
        "total": total,
        "aprovados": aprovados,
        "pendentes": pendentes,
        "rejeitados": rejeitados,
        "taxa_conversao": round(taxa_conversao, 1)
    }


def gerar_numero_orcamento():
    """Gera um número de orçamento único."""
    from datetime import datetime
    ano = datetime.now().year
    mes = datetime.now().month
    return f"ORC{ano}{mes:02d}"


@router.get("", response_model=List[OrcamentoResponse])
async def listar_orcamentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = None,
    cliente_id: str = None,
    busca: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os orçamentos com filtros opcionais."""
    query = select(Orcamento)
    
    if status:
        query = query.where(Orcamento.status == status)
    
    if cliente_id:
        query = query.where(Orcamento.cliente_id == cliente_id)
    
    if busca:
        query = query.where(
            or_(
                Orcamento.titulo.ilike(f"%{busca}%"),
                Orcamento.descricao.ilike(f"%{busca}%")
            )
        )
    
    query = query.order_by(Orcamento.criado_em.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    orcamentos = result.scalars().all()
    
    return orcamentos


@router.get("/{orcamento_id}", response_model=OrcamentoResponse)
async def obter_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém um orçamento específico por ID."""
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    return orcamento

@router.post("", response_model=OrcamentoResponse, status_code=201)
async def criar_orcamento(
    orcamento_data: OrcamentoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria um novo orçamento."""
    try:
        logger.info(f"Criando orçamento. Dados recebidos: {orcamento_data.model_dump()}")
        
        # Gerar número de orçamento único
        numero_orcamento = gerar_numero_orcamento()
    
        # Verificar se já existe orçamento com este número
        query = select(Orcamento).where(Orcamento.numero_orcamento == numero_orcamento)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            # Adicionar sufixo se já existir
            contador = 1
            while True:
                numero_orcamento = f"{gerar_numero_orcamento()}-{contador}"
                query = select(Orcamento).where(Orcamento.numero_orcamento == numero_orcamento)
                result = await db.execute(query)
                if not result.scalar_one_or_none():
                    break
                contador += 1
    
        orcamento = Orcamento(
            **orcamento_data.model_dump(),
            numero_orcamento=numero_orcamento,
            criado_por=current_user.id
        )
    
        db.add(orcamento)
        await db.commit()
        await db.refresh(orcamento)
    
        # Enviar notificação WebSocket
        await manager.send_personal_message({
            "type": "orcamento_criado",
            "data": {
                "id": orcamento.id,
                "numero_orcamento": orcamento.numero_orcamento,
                "cliente_id": orcamento.cliente_id,
                "titulo": orcamento.titulo,
                "total": orcamento.total,
                "status": orcamento.status,
                "criado_em": orcamento.criado_em.isoformat()
            }
        }, current_user.id)
        
        logger.info(f"Orçamento criado com sucesso. ID: {orcamento.id}, Número: {orcamento.numero_orcamento}")
        return orcamento
    except Exception as e:
        logger.error(f"Erro ao criar orçamento: {e}")
        logger.error(f"Stack trace: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar orçamento: {str(e)}")


@router.put("/{orcamento_id}", response_model=OrcamentoResponse)
async def atualizar_orcamento(
    orcamento_id: str,
    orcamento_data: OrcamentoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza um orçamento existente."""
    try:
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()
        
        if not orcamento:
            logger.warning(f"Orçamento {orcamento_id} não encontrado para atualização por {current_user.email}")
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
        
        update_data = orcamento_data.model_dump(exclude_unset=True)
        
        # Registrar datas de mudança de status
        if "status" in update_data:
            if update_data["status"] == StatusOrcamento.ENVIADO and not orcamento.enviado_em:
                update_data["enviado_em"] = datetime.now(UTC)
            elif update_data["status"] == StatusOrcamento.VISUALIZADO and not orcamento.visualizado_em:
                update_data["visualizado_em"] = datetime.now(UTC)
            elif update_data["status"] == StatusOrcamento.APROVADO and not orcamento.aprovado_em:
                update_data["aprovado_em"] = datetime.now(UTC)
        
        for field, value in update_data.items():
            setattr(orcamento, field, value)
        
        await db.commit()
        await db.refresh(orcamento)
        
        logger.info(f"Orçamento {orcamento.numero_orcamento} (ID: {orcamento_id}) atualizado por {current_user.email}")
        return orcamento
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar orçamento {orcamento_id}: {str(e)}")
        raise


@router.delete("/{orcamento_id}", status_code=204)
async def deletar_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta um orçamento (soft delete)."""
    try:
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()
        
        if not orcamento:
            logger.warning(f"Orçamento {orcamento_id} não encontrado para deleção por {current_user.email}")
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
        
        # Só pode deletar se for rascunho
        if orcamento.status != StatusOrcamento.RASCUNHO:
            logger.warning(f"Tentativa de deletar orçamento {orcamento.numero_orcamento} não rascunho por {current_user.email}")
            raise HTTPException(
                status_code=400,
                detail="Só é possível deletar orçamentos em rascunho"
            )
        
        await db.delete(orcamento)
        await db.commit()
        
        logger.info(f"Orçamento {orcamento.numero_orcamento} (ID: {orcamento_id}) deletado por {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar orçamento {orcamento_id}: {str(e)}")
        raise


@router.patch("/{orcamento_id}/aprovar", response_model=OrcamentoResponse)
async def aprovar_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Aprova um orçamento."""
    try:
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()

        if not orcamento:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")

        # Verificar que status atual permite aprovação
        status_atual = orcamento.status.value
        if status_atual not in ["enviado", "visualizado"]:
            raise HTTPException(
                status_code=400,
                detail=f"Orçamento com status {status_atual} não pode ser aprovado"
            )

        orcamento.status = StatusOrcamento.APROVADO
        orcamento.aprovado_em = datetime.now(UTC)

        # Criar notificação WebSocket para admin/gerente
        await manager.send_personal_message({
            "type": "orcamento_aprovado",
            "data": {
                "id": orcamento.id,
                "numero_orcamento": orcamento.numero_orcamento,
                "cliente_id": orcamento.cliente_id,
                "aprovado_por": current_user.email
            }
        }, current_user.id)

        await db.commit()
        await db.refresh(orcamento)

        logger.info(f"Orçamento {orcamento.numero_orcamento} (ID: {orcamento_id}) aprovado por {current_user.email}")
        return orcamento
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao aprovar orçamento {orcamento_id}: {str(e)}")
        raise


@router.patch("/{orcamento_id}/recusar", response_model=OrcamentoResponse)
async def recusar_orcamento(
    orcamento_id: str,
    motivo: str = Query(..., description="Motivo da recusa"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Recusa um orçamento."""
    try:
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()

        if not orcamento:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")

        # Verificar que status atual permite recusa
        status_atual = orcamento.status.value
        if status_atual not in ["enviado", "visualizado"]:
            raise HTTPException(
                status_code=400,
                detail=f"Orçamento com status {status_atual} não pode ser recusado"
            )

        orcamento.status = StatusOrcamento.RECUSADO
        orcamento.recusado_em = datetime.now(UTC)
        orcamento.motivo_recusa = motivo

        # Criar notificação WebSocket para admin/gerente
        await manager.send_personal_message({
            "type": "orcamento_recusado",
            "data": {
                "id": orcamento.id,
                "numero_orcamento": orcamento.numero_orcamento,
                "cliente_id": orcamento.cliente_id,
                "recusado_por": current_user.email,
                "motivo": motivo
            }
        }, current_user.id)

        await db.commit()
        await db.refresh(orcamento)

        logger.info(f"Orçamento {orcamento.numero_orcamento} (ID: {orcamento_id}) recusado por {current_user.email}")
        return orcamento
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao recusar orçamento {orcamento_id}: {str(e)}")
        raise


@router.post("/{orcamento_id}/itens", response_model=dict, status_code=201)
async def adicionar_item_orcamento(
    orcamento_id: str,
    item_data: ItemOrcamentoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Adiciona um item a um orçamento."""
    # Verificar se o orçamento existe
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # Calcular preço total
    preco_total = item_data.quantidade * item_data.preco_unitario
    
    item = ItemOrcamento(
        orcamento_id=orcamento_id,
        **item_data.model_dump(),
        preco_total=preco_total
    )
    
    db.add(item)
    
    # Recalcular subtotal e total do orçamento
    await db.commit()
    await db.refresh(item)
    
    # Atualizar totais do orçamento
    query_itens = select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)
    result_itens = await db.execute(query_itens)
    itens = result_itens.scalars().all()
    
    subtotal = sum(i.preco_total for i in itens)
    orcamento.subtotal = subtotal
    orcamento.total = subtotal - orcamento.valor_desconto + (subtotal * orcamento.taxa_imposto / 100)
    
    await db.commit()
    
    return {"id": item.id, "mensagem": "Item adicionado com sucesso"}


@router.get("/{orcamento_id}/itens", response_model=List[dict])
async def listar_itens_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os itens de um orçamento."""
    query = select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)
    query = query.order_by(ItemOrcamento.ordem)
    result = await db.execute(query)
    itens = result.scalars().all()
    
    return [
        {
            "id": i.id,
            "item_estoque_id": i.item_estoque_id,
            "descricao": i.descricao,
            "quantidade": i.quantidade,
            "unidade": i.unidade,
            "preco_unitario": i.preco_unitario,
            "preco_total": i.preco_total,
            "ordem": i.ordem
        }
        for i in itens
    ]


@router.post("/{orcamento_id}/enviar", response_model=dict)
async def enviar_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Envia um orçamento para o cliente."""
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    if orcamento.status != StatusOrcamento.RASCUNHO:
        raise HTTPException(
            status_code=400,
            detail="Só é possível enviar orçamentos em rascunho"
        )
    
    # Buscar dados do cliente
    query_cliente = select(Cliente).where(Cliente.id == orcamento.cliente_id)
    result_cliente = await db.execute(query_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    orcamento.status = StatusOrcamento.ENVIADO
    orcamento.enviado_em = datetime.now(UTC)
    
    # Gerar token de acesso público para o portal do cliente
    if not orcamento.token_acesso_publico:
        orcamento.token_acesso_publico = secrets.token_urlsafe(32)
    
    await db.commit()
    
    # Enviar email se cliente tiver email
    if cliente.email:
        try:
            valido_ate_formatado = orcamento.valido_ate.strftime("%d/%m/%Y") if orcamento.valido_ate else "Não definido"
            EmailService.enviar_orcamento_email(
                destinatario=cliente.email,
                cliente_nome=cliente.nome,
                numero_orcamento=orcamento.numero_orcamento,
                valor_total=orcamento.total or 0,
                valido_ate=valido_ate_formatado,
                url_pdf=orcamento.url_pdf
            )
            logger.info(f"Email enviado para {cliente.email} sobre orçamento {orcamento.numero_orcamento}")
        except Exception as e:
            logger.error(f"Erro ao enviar email para cliente {cliente.email}: {e}")
    
    # Enviar WhatsApp se cliente tiver whatsapp
    if cliente.whatsapp:
        try:
            await WhatsAppService.enviar_orcamento_whatsapp(
                numero=cliente.whatsapp,
                cliente_nome=cliente.nome,
                numero_orcamento=orcamento.numero_orcamento,
                valor_total=orcamento.total or 0,
                url_pdf=orcamento.url_pdf
            )
            logger.info(f"WhatsApp enviado para {cliente.whatsapp} sobre orçamento {orcamento.numero_orcamento}")
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp para cliente {cliente.whatsapp}: {e}")
    
    return {"mensagem": "Orçamento enviado com sucesso"}


@router.post("/{orcamento_id}/aprovar", response_model=dict)
async def aprovar_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Aprova um orçamento."""
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    if orcamento.status not in [StatusOrcamento.ENVIADO, StatusOrcamento.VISUALIZADO]:
        raise HTTPException(
            status_code=400,
            detail="Só é possível aprovar orçamentos enviados ou visualizados"
        )
    
    orcamento.status = StatusOrcamento.APROVADO
    orcamento.aprovado_em = datetime.now(UTC)
    
    await db.commit()
    
    return {"mensagem": "Orçamento aprovado com sucesso"}


@router.post("/{orcamento_id}/rejeitar", response_model=dict)
async def rejeitar_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Rejeita um orçamento."""
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    if orcamento.status not in [StatusOrcamento.ENVIADO, StatusOrcamento.VISUALIZADO]:
        raise HTTPException(
            status_code=400,
            detail="Só é possível rejeitar orçamentos enviados ou visualizados"
        )
    
    orcamento.status = StatusOrcamento.RECUSADO
    
    await db.commit()
    
    return {"mensagem": "Orçamento rejeitado com sucesso"}


@router.post("/{orcamento_id}/converter", response_model=dict)
async def converter_orcamento_os(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Converte um orçamento aprovado em ordem de serviço."""
    query = select(Orcamento).where(Orcamento.id == orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    if orcamento.status != StatusOrcamento.APROVADO:
        raise HTTPException(
            status_code=400,
            detail="Só é possível converter orçamentos aprovados"
        )
    
    if orcamento.convertido_para_os_id:
        raise HTTPException(
            status_code=400,
            detail="Este orçamento já foi convertido em ordem de serviço"
        )
    
    # Criar ordem de serviço a partir do orçamento
    from app.models.ordem_servico import OrdemServico, StatusOS, PrioridadeOS
    from app.routers.ordens_servico import gerar_numero_os
    
    # Buscar primeira categoria de serviço como padrão
    query_categoria = select(CategoriaServico).limit(1)
    result_categoria = await db.execute(query_categoria)
    categoria_padrao = result_categoria.scalar_one_or_none()
    
    if not categoria_padrao:
        raise HTTPException(
            status_code=400,
            detail="Não existe categoria de serviço cadastrada. Crie uma categoria antes de converter orçamento em OS."
        )
    
    os = OrdemServico(
        numero_os=gerar_numero_os(),
        cliente_id=orcamento.cliente_id,
        tecnico_id=current_user.id,
        tipo_servico_id=categoria_padrao.id,
        titulo=orcamento.titulo,
        descricao=orcamento.descricao,
        observacoes_internas=orcamento.observacoes_internas,
        prioridade=PrioridadeOS.NORMAL,
        valor_estimado=orcamento.total,
        valor_final=orcamento.total,
        status=StatusOS.PENDENTE,
        criado_por=current_user.id
    )
    
    db.add(os)
    await db.commit()
    await db.refresh(os)
    
    # Atualizar orçamento
    orcamento.status = StatusOrcamento.CONVERTIDO
    orcamento.convertido_para_os_id = os.id
    
    await db.commit()
    
    return {"mensagem": "Orçamento convertido em ordem de serviço", "os_id": os.id}


@router.get("/{orcamento_id}/pdf")
async def gerar_pdf_orcamento(
    orcamento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Gera PDF do orçamento."""
    from fastapi.responses import Response
    from app.services.pdf_service import gerar_pdf_orcamento
    
    # Gerar PDF usando a nova função que retorna bytes
    pdf_bytes = await gerar_pdf_orcamento(orcamento_id, db)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=orcamento.pdf"}
    )
