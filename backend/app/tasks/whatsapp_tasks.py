from celery import shared_task
from app.services.whatsapp_service import WhatsAppService
from loguru import logger


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_mensagem_whatsapp(
    self,
    telefone: str,
    mensagem: str
) -> dict:
    """Envia mensagem via WhatsApp."""
    try:
        whatsapp_service = WhatsAppService()
        whatsapp_service.enviar_mensagem(telefone, mensagem)
        logger.info(f"Mensagem WhatsApp enviada para {telefone}")
        return {"status": "sucesso", "telefone": telefone}
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_confirmacao_os_whatsapp(
    self,
    telefone: str,
    numero_os: str,
    nome_cliente: str,
    data_agendada: str
) -> dict:
    """Envia confirmação de OS via WhatsApp."""
    try:
        whatsapp_service = WhatsAppService()
        whatsapp_service.enviar_confirmacao_os(telefone, numero_os, nome_cliente, data_agendada)
        logger.info(f"Confirmação OS {numero_os} enviada via WhatsApp para {telefone}")
        return {"status": "sucesso", "os": numero_os, "telefone": telefone}
    except Exception as e:
        logger.error(f"Erro ao enviar confirmação OS WhatsApp: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_orcamento_whatsapp(
    self,
    telefone: str,
    numero_orcamento: str,
    valor_total: float
) -> dict:
    """Envia notificação de orçamento via WhatsApp."""
    try:
        whatsapp_service = WhatsAppService()
        whatsapp_service.enviar_orcamento(telefone, numero_orcamento, valor_total)
        logger.info(f"Orçamento {numero_orcamento} enviado via WhatsApp para {telefone}")
        return {"status": "sucesso", "orcamento": numero_orcamento, "telefone": telefone}
    except Exception as e:
        logger.error(f"Erro ao enviar orçamento WhatsApp: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def enviar_lembrete_agendamento(
    self,
    telefone: str,
    numero_os: str,
    data: str,
    hora: str
) -> dict:
    """Envia lembrete de agendamento via WhatsApp."""
    try:
        whatsapp_service = WhatsAppService()
        whatsapp_service.enviar_lembrete_agendamento(telefone, numero_os, data, hora)
        logger.info(f"Lembrete agendamento OS {numero_os} enviado para {telefone}")
        return {"status": "sucesso", "os": numero_os, "telefone": telefone}
    except Exception as e:
        logger.error(f"Erro ao enviar lembrete agendamento: {str(e)}")
        raise self.retry(exc=e)


@shared_task
def verificar_os_agendadas() -> dict:
    """Verifica OS agendadas e envia lembretes (task agendada)."""
    try:
        # Usar async/await não funciona diretamente em tasks Celery
        # Por enquanto, apenas logar a verificação
        # A implementação completa requer um contexto async separado
        logger.info("Verificação de OS agendadas iniciada")
        
        # Lógica futura:
        # - Verificar OS agendadas para amanhã
        # - Verificar OS agendadas para hoje (manhã)
        # - Enviar lembretes WhatsApp para clientes
        # - Notificar técnicos sobre agendamentos
        
        logger.info("Verificação de OS agendadas concluída")
        return {"status": "sucesso", "mensagem": "Verificação concluída"}
    except Exception as e:
        logger.error(f"Erro ao verificar OS agendadas: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}
