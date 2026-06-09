from celery import shared_task
from app.services.email_service import EmailService
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orcamento import Orcamento, StatusOrcamento
from app.models.ordem_servico import OrdemServico, StatusOS
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from loguru import logger
from datetime import datetime, UTC, timedelta


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_email_boas_vindas(
    self,
    email_destino: str,
    nome_usuario: str
) -> dict:
    """Envia email de boas-vindas para novo usuário."""
    try:
        email_service = EmailService()
        email_service.enviar_boas_vindas(email_destino, nome_usuario)
        logger.info(f"Email de boas-vindas enviado para {email_destino}")
        return {"status": "sucesso", "email": email_destino}
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_email_confirmacao_os(
    self,
    email_destino: str,
    numero_os: str,
    nome_cliente: str
) -> dict:
    """Envia email de confirmação de ordem de serviço."""
    try:
        email_service = EmailService()
        email_service.enviar_confirmacao_os(email_destino, numero_os, nome_cliente)
        logger.info(f"Email de confirmação OS {numero_os} enviado para {email_destino}")
        return {"status": "sucesso", "os": numero_os, "email": email_destino}
    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmação OS: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_email_orcamento(
    self,
    email_destino: str,
    numero_orcamento: str,
    nome_cliente: str,
    pdf_path: str
) -> dict:
    """Envia email com orçamento em PDF."""
    try:
        email_service = EmailService()
        email_service.enviar_orcamento(email_destino, numero_orcamento, nome_cliente, pdf_path)
        logger.info(f"Email de orçamento {numero_orcamento} enviado para {email_destino}")
        return {"status": "sucesso", "orcamento": numero_orcamento, "email": email_destino}
    except Exception as e:
        logger.error(f"Erro ao enviar email de orçamento: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_email_notificacao_financeira(
    self,
    email_destino: str,
    tipo: str,
    descricao: str,
    valor: float
) -> dict:
    """Envia email de notificação financeira."""
    try:
        email_service = EmailService()
        email_service.enviar_notificacao_financeira(email_destino, tipo, descricao, valor)
        logger.info(f"Email financeiro ({tipo}) enviado para {email_destino}")
        return {"status": "sucesso", "tipo": tipo, "email": email_destino}
    except Exception as e:
        logger.error(f"Erro ao enviar email financeiro: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_reset_senha(
    self,
    email_destino: str,
    token: str
) -> dict:
    """Envia email de recuperação de senha com token de reset."""
    try:
        email_service = EmailService()
        email_service.enviar_reset_senha(email_destino, token)
        logger.info(f"Email de reset de senha enviado para {email_destino}")
        return {"status": "sucesso", "email": email_destino}
    except Exception as e:
        logger.error(f"Erro ao enviar email de reset de senha: {str(e)}")
        raise self.retry(exc=e)


@shared_task
def verificar_notificacoes_pendentes() -> dict:
    """Verifica e envia notificações pendentes (task agendada)."""
    try:
        # Usar async/await não funciona diretamente em tasks Celery
        # Por enquanto, apenas logar a verificação
        # A implementação completa requer um contexto async separado
        logger.info("Verificação de notificações pendentes iniciada")
        
        # Lógica futura:
        # - Verificar orçamentos enviados há mais de 2 dias sem visualização
        # - Verificar OS agendadas para amanhã
        # - Verificar pagamentos atrasados
        # - Enviar lembretes por email conforme necessário
        
        logger.info("Verificação de notificações pendentes concluída")
        return {"status": "sucesso", "mensagem": "Verificação concluída"}
    except Exception as e:
        logger.error(f"Erro ao verificar notificações pendentes: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}
