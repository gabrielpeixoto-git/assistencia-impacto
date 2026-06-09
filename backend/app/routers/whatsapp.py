from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.services.whatsapp_service import WhatsAppService
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from app.models.orcamento import Orcamento
from app.models.ordem_servico import OrdemServico
from app.models.cliente import Cliente
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import re

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


class EnviarOrcamentoRequest(BaseModel):
    orcamento_id: str


class ConfirmarOSRequest(BaseModel):
    os_id: str


class ConcluirOSRequest(BaseModel):
    os_id: str
    link_avaliacao: Optional[str] = None


class LembretePagamentoRequest(BaseModel):
    transacao_id: str


@router.post("/enviar-orcamento")
async def enviar_orcamento_whatsapp(
    request: EnviarOrcamentoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Envia orçamento via WhatsApp ao cliente."""
    # Buscar orçamento
    query = select(Orcamento).where(Orcamento.id == request.orcamento_id)
    result = await db.execute(query)
    orcamento = result.scalar_one_or_none()
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # Buscar cliente
    query_cliente = select(Cliente).where(Cliente.id == orcamento.cliente_id)
    result_cliente = await db.execute(query_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if not cliente.whatsapp:
        raise HTTPException(status_code=400, detail="Cliente não tem WhatsApp cadastrado")
    
    # Formatar número para WhatsApp (remover caracteres não numéricos)
    numero_whatsapp = re.sub(r'\D', '', cliente.whatsapp)
    if not numero_whatsapp.startswith('55'):
        numero_whatsapp = f'55{numero_whatsapp}'
    
    # Gerar link do PDF se não existir
    url_pdf = orcamento.url_pdf
    if not url_pdf:
        from app.config import settings
        url_pdf = f"{settings.url_frontend}/orcamentos/{orcamento.id}"
    
    # Enviar mensagem
    sucesso = await WhatsAppService.enviar_orcamento_whatsapp(
        numero=numero_whatsapp,
        cliente_nome=cliente.nome.split()[0],
        numero_orcamento=orcamento.numero_orcamento,
        valor_total=orcamento.total or 0,
        url_pdf=url_pdf
    )
    
    if sucesso:
        logger.info(f"Orçamento {orcamento.numero_orcamento} enviado via WhatsApp para {cliente.whatsapp}")
        return {"mensagem": "Orçamento enviado com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar orçamento via WhatsApp")


@router.post("/confirmar-os")
async def confirmar_os_whatsapp(
    request: ConfirmarOSRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Envia confirmação de OS agendada via WhatsApp."""
    # Buscar OS
    query = select(OrdemServico).where(OrdemServico.id == request.os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    # Buscar cliente
    query_cliente = select(Cliente).where(Cliente.id == os.cliente_id)
    result_cliente = await db.execute(query_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if not cliente.whatsapp:
        raise HTTPException(status_code=400, detail="Cliente não tem WhatsApp cadastrado")
    
    # Buscar técnico
    query_tecnico = select(Usuario).where(Usuario.id == os.tecnico_id)
    result_tecnico = await db.execute(query_tecnico)
    tecnico = result_tecnico.scalar_one_or_none()
    
    # Formatar número para WhatsApp
    numero_whatsapp = re.sub(r'\D', '', cliente.whatsapp)
    if not numero_whatsapp.startswith('55'):
        numero_whatsapp = f'55{numero_whatsapp}'
    
    # Formatar data agendada
    data_formatada = ""
    if os.data_agendada:
        data_formatada = os.data_agendada.strftime('%d/%m/%Y às %H:%M')
    
    # Formatar endereço
    endereco = f"{cliente.logradouro}, {cliente.numero}"
    if cliente.bairro:
        endereco += f" - {cliente.bairro}"
    if cliente.cidade:
        endereco += f", {cliente.cidade}"
    
    # Enviar mensagem
    sucesso = await WhatsAppService.enviar_confirmacao_os_whatsapp(
        numero=numero_whatsapp,
        cliente_nome=cliente.nome.split()[0],
        numero_os=os.numero_os,
        data_agendada=data_formatada,
        endereco=endereco
    )
    
    if sucesso:
        logger.info(f"OS {os.numero_os} confirmada via WhatsApp para {cliente.whatsapp}")
        return {"mensagem": "Confirmação enviada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar confirmação via WhatsApp")


@router.post("/concluir-os")
async def concluir_os_whatsapp(
    request: ConcluirOSRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Envia mensagem de OS concluída via WhatsApp."""
    # Buscar OS
    query = select(OrdemServico).where(OrdemServico.id == request.os_id)
    result = await db.execute(query)
    os = result.scalar_one_or_none()
    
    if not os:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    
    # Buscar cliente
    query_cliente = select(Cliente).where(Cliente.id == os.cliente_id)
    result_cliente = await db.execute(query_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if not cliente.whatsapp:
        raise HTTPException(status_code=400, detail="Cliente não tem WhatsApp cadastrado")
    
    # Formatar número para WhatsApp
    numero_whatsapp = re.sub(r'\D', '', cliente.whatsapp)
    if not numero_whatsapp.startswith('55'):
        numero_whatsapp = f'55{numero_whatsapp}'
    
    # Gerar link de avaliação se não fornecido
    link_avaliacao = request.link_avaliacao
    if not link_avaliacao:
        from app.config import settings
        link_avaliacao = f"{settings.url_frontend}/avaliar-os/{os.token_acesso_publico}"
    
    # Enviar mensagem
    mensagem = f"""
✅ *Serviço Finalizado com Sucesso!*

Olá, {cliente.nome.split()[0]}! 👋

Sua ordem de serviço foi concluída:

🔧 *OS:* {os.numero_os}
📋 *Serviço:* {os.titulo}
💰 *Valor:* R$ {os.valor_final or os.valor_estimado:.2f}

Agradecemos pela confiança! Avalie nosso serviço: {link_avaliacao} ⭐

Atenciosamente,
*Assistência Impacto* ⚡
"""
    
    sucesso = await WhatsAppService.enviar_mensagem(numero_whatsapp, mensagem)
    
    if sucesso:
        logger.info(f"OS {os.numero_os} concluída enviada via WhatsApp para {cliente.whatsapp}")
        return {"mensagem": "Mensagem enviada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar mensagem via WhatsApp")


@router.post("/lembrete-pagamento")
async def lembrete_pagamento_whatsapp(
    request: LembretePagamentoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Envia lembrete de pagamento em aberto via WhatsApp."""
    # Buscar transação
    from app.models.financeiro import Transacao
    
    query = select(Transacao).where(Transacao.id == request.transacao_id)
    result = await db.execute(query)
    transacao = result.scalar_one_or_none()
    
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Buscar cliente
    query_cliente = select(Cliente).where(Cliente.id == transacao.cliente_id)
    result_cliente = await db.execute(query_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if not cliente.whatsapp:
        raise HTTPException(status_code=400, detail="Cliente não tem WhatsApp cadastrado")
    
    # Formatar número para WhatsApp
    numero_whatsapp = re.sub(r'\D', '', cliente.whatsapp)
    if not numero_whatsapp.startswith('55'):
        numero_whatsapp = f'55{numero_whatsapp}'
    
    # Formatar data de vencimento
    data_vencimento = ""
    if transacao.data_vencimento:
        data_vencimento = transacao.data_vencimento.strftime('%d/%m/%Y')
    
    # Enviar mensagem
    mensagem = f"""
⚠️ *Aviso de Pagamento em Aberto*

Olá, {cliente.nome.split()[0]}! 👋

Temos um pagamento pendente:

💰 *Valor:* R$ {transacao.valor:.2f}
📋 *Referência:* {transacao.descricao}
📅 *Vencimento:* {data_vencimento}

Para regularizar, entre em contato: {current_user.nome_completo}

Atenciosamente,
*Assistência Impacto* ⚡
"""
    
    sucesso = await WhatsAppService.enviar_mensagem(numero_whatsapp, mensagem)
    
    if sucesso:
        logger.info(f"Lembrete de pagamento enviado via WhatsApp para {cliente.whatsapp}")
        return {"mensagem": "Lembrete enviado com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar lembrete via WhatsApp")


@router.get("/status")
async def verificar_status_whatsapp(
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Verifica se a integração WhatsApp está ativa."""
    ativo = await WhatsAppService.verificar_instancia_ativa()
    
    return {
        "ativo": ativo,
        "configurado": bool(current_user.nome_completo)
    }
