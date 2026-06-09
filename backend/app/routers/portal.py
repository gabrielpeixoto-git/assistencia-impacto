from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, UTC
import secrets
import uuid

limiter = Limiter(key_func=get_remote_address)

from app.schemas.portal import (
    OrcamentoPublicoResponse,
    ItemOrcamentoPublicoResponse,
    OSPublicaResponse,
    ItemOSPublicoResponse,
    FotoOSPublicoResponse,
    ChecklistOSPublicoResponse,
    AvaliacaoCreate,
    AvaliacaoResponse,
    AcaoOrcamentoResponse,
)

from app.models.orcamento import Orcamento, ItemOrcamento, StatusOrcamento
from app.models.ordem_servico import (
    OrdemServico,
    ItemOrdemServico,
    FotoOrdemServico,
    ChecklistOrdemServico,
    StatusOS,
)
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from loguru import logger

router = APIRouter(prefix="/api/portal", tags=["portal"])


@router.get("/orcamento/{token}", response_model=OrcamentoPublicoResponse)
@limiter.limit("10/minute")
async def visualizar_orcamento_publico(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Visualiza orçamento público via token de acesso.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    # Buscar informações do cliente
    result_cliente = await db.execute(
        select(Cliente).where(Cliente.id == orcamento.cliente_id)
    )
    cliente = result_cliente.scalar_one_or_none()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Marcar como visualizado se ainda não foi
    if orcamento.status == StatusOrcamento.ENVIADO and not orcamento.visualizado_em:
        orcamento.visualizado_em = datetime.now(UTC)
        orcamento.status = StatusOrcamento.VISUALIZADO
        await db.commit()

    # Construir resposta
    response_data = {
        **orcamento.__dict__,
        "cliente_nome": cliente.nome_completo,
        "cliente_email": cliente.email,
    }

    return OrcamentoPublicoResponse.model_validate(response_data)


@router.get("/orcamento/{token}/itens", response_model=List[ItemOrcamentoPublicoResponse])
@limiter.limit("10/minute")
async def listar_itens_orcamento_publico(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista itens de um orçamento público via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    result_itens = await db.execute(
        select(ItemOrcamento)
        .where(ItemOrcamento.orcamento_id == orcamento.id)
        .order_by(ItemOrcamento.ordem)
    )
    itens = result_itens.scalars().all()

    return [ItemOrcamentoPublicoResponse.model_validate(item) for item in itens]


@router.post("/orcamento/{token}/aprovar", response_model=AcaoOrcamentoResponse)
@limiter.limit("5/minute")
async def aprovar_orcamento_publico(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Aprova um orçamento público via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    if orcamento.status not in [StatusOrcamento.ENVIADO, StatusOrcamento.VISUALIZADO]:
        raise HTTPException(
            status_code=400,
            detail=f"Orçamento não pode ser aprovado no status {orcamento.status}",
        )

    orcamento.status = StatusOrcamento.APROVADO
    orcamento.aprovado_em = datetime.now(UTC)
    await db.commit()

    logger.info(f"Orçamento {orcamento.numero_orcamento} aprovado via token")

    return AcaoOrcamentoResponse(
        mensagem="Orçamento aprovado com sucesso",
        status=orcamento.status,
    )


@router.post("/orcamento/{token}/rejeitar", response_model=AcaoOrcamentoResponse)
@limiter.limit("5/minute")
async def rejeitar_orcamento_publico(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Rejeita um orçamento público via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    if orcamento.status not in [StatusOrcamento.ENVIADO, StatusOrcamento.VISUALIZADO]:
        raise HTTPException(
            status_code=400,
            detail=f"Orçamento não pode ser rejeitado no status {orcamento.status}",
        )

    orcamento.status = StatusOrcamento.RECUSADO
    await db.commit()

    logger.info(f"Orçamento {orcamento.numero_orcamento} rejeitado via token")

    return AcaoOrcamentoResponse(
        mensagem="Orçamento rejeitado com sucesso",
        status=orcamento.status,
    )


@router.get("/os/{token}", response_model=OSPublicaResponse)
@limiter.limit("10/minute")
async def visualizar_os_publica(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Visualiza ordem de serviço pública via token de acesso.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(OrdemServico).where(OrdemServico.token_acesso_publico == token)
    )
    os = result.scalar_one_or_none()

    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    # Buscar informações do cliente
    result_cliente = await db.execute(select(Cliente).where(Cliente.id == os.cliente_id))
    cliente = result_cliente.scalar_one_or_none()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar informações do técnico (se atribuído)
    tecnico_nome = None
    if os.tecnico_id:
        result_tecnico = await db.execute(
            select(Usuario).where(Usuario.id == os.tecnico_id)
        )
        tecnico = result_tecnico.scalar_one_or_none()
        if tecnico:
            tecnico_nome = tecnico.nome_completo

    # Construir resposta
    response_data = {
        **os.__dict__,
        "cliente_nome": cliente.nome_completo,
        "cliente_email": cliente.email,
        "tecnico_nome": tecnico_nome,
    }

    return OSPublicaResponse.model_validate(response_data)


@router.get("/os/{token}/itens", response_model=List[ItemOSPublicoResponse])
@limiter.limit("10/minute")
async def listar_itens_os_publica(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista itens de uma ordem de serviço pública via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(OrdemServico).where(OrdemServico.token_acesso_publico == token)
    )
    os = result.scalar_one_or_none()

    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    result_itens = await db.execute(
        select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os.id)
    )
    itens = result_itens.scalars().all()

    return [ItemOSPublicoResponse.model_validate(item) for item in itens]


@router.get("/os/{token}/fotos", response_model=List[FotoOSPublicoResponse])
@limiter.limit("10/minute")
async def listar_fotos_os_publica(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista fotos de uma ordem de serviço pública via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(OrdemServico).where(OrdemServico.token_acesso_publico == token)
    )
    os = result.scalar_one_or_none()

    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    result_fotos = await db.execute(
        select(FotoOrdemServico).where(FotoOrdemServico.ordem_servico_id == os.id)
    )
    fotos = result_fotos.scalars().all()

    return [FotoOSPublicoResponse.model_validate(foto) for foto in fotos]


@router.get("/os/{token}/checklist", response_model=List[ChecklistOSPublicoResponse])
@limiter.limit("10/minute")
async def listar_checklist_os_publica(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista checklist de uma ordem de serviço pública via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(OrdemServico).where(OrdemServico.token_acesso_publico == token)
    )
    os = result.scalar_one_or_none()

    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    result_checklist = await db.execute(
        select(ChecklistOrdemServico).where(
            ChecklistOrdemServico.ordem_servico_id == os.id
        )
    )
    checklist = result_checklist.scalars().all()

    return [ChecklistOSPublicoResponse.model_validate(item) for item in checklist]


@router.post("/os/{token}/avaliar", response_model=AvaliacaoResponse)
@limiter.limit("5/minute")
async def avaliar_os_publica(
    token: str,
    avaliacao: AvaliacaoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Avalia uma ordem de serviço pública via token.
    Endpoint público - não requer autenticação.
    """
    result = await db.execute(
        select(OrdemServico).where(OrdemServico.token_acesso_publico == token)
    )
    os = result.scalar_one_or_none()

    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    if os.status != StatusOS.CONCLUIDA:
        raise HTTPException(
            status_code=400,
            detail="Apenas ordens de serviço concluídas podem ser avaliadas",
        )

    # Verificar se já existe avaliação
    # Nota: Implementação futura - criar modelo de Avaliacao

    logger.info(f"OS {os.numero_os} avaliada com nota {avaliacao.nota} via token")

    # Placeholder - retornar resposta simulada
    return AvaliacaoResponse(
        id=str(uuid.uuid4()),
        ordem_servico_id=os.id,
        nota=avaliacao.nota,
        comentario=avaliacao.comentario,
        criado_em=datetime.now(UTC),
    )
