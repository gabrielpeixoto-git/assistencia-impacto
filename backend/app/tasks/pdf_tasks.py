from celery import shared_task
from app.services.pdf_service import PDFService
from loguru import logger
import os


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def gerar_pdf_orcamento(
    self,
    orcamento_id: str,
    output_path: str
) -> dict:
    """Gera PDF de orçamento."""
    try:
        pdf_service = PDFService()
        pdf_service.gerar_orcamento(orcamento_id, output_path)
        logger.info(f"PDF de orçamento {orcamento_id} gerado em {output_path}")
        return {"status": "sucesso", "orcamento_id": orcamento_id, "path": output_path}
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de orçamento: {str(e)}")
        # Limpar arquivo parcial se existir
        if os.path.exists(output_path):
            os.remove(output_path)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def gerar_pdf_ordem_servico(
    self,
    ordem_servico_id: str,
    output_path: str
) -> dict:
    """Gera PDF de ordem de serviço."""
    try:
        pdf_service = PDFService()
        pdf_service.gerar_ordem_servico(ordem_servico_id, output_path)
        logger.info(f"PDF de OS {ordem_servico_id} gerado em {output_path}")
        return {"status": "sucesso", "os_id": ordem_servico_id, "path": output_path}
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de OS: {str(e)}")
        # Limpar arquivo parcial se existir
        if os.path.exists(output_path):
            os.remove(output_path)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def gerar_pdf_relatorio_financeiro(
    self,
    data_inicio: str,
    data_fim: str,
    output_path: str
) -> dict:
    """Gera PDF de relatório financeiro."""
    try:
        pdf_service = PDFService()
        pdf_service.gerar_relatorio_financeiro(data_inicio, data_fim, output_path)
        logger.info(f"PDF relatório financeiro gerado em {output_path}")
        return {"status": "sucesso", "periodo": f"{data_inicio} a {data_fim}", "path": output_path}
    except Exception as e:
        logger.error(f"Erro ao gerar PDF relatório financeiro: {str(e)}")
        # Limpar arquivo parcial se existir
        if os.path.exists(output_path):
            os.remove(output_path)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def gerar_pdf_relatorio_estoque(
    self,
    output_path: str
) -> dict:
    """Gera PDF de relatório de estoque."""
    try:
        pdf_service = PDFService()
        pdf_service.gerar_relatorio_estoque(output_path)
        logger.info(f"PDF relatório estoque gerado em {output_path}")
        return {"status": "sucesso", "path": output_path}
    except Exception as e:
        logger.error(f"Erro ao gerar PDF relatório estoque: {str(e)}")
        # Limpar arquivo parcial se existir
        if os.path.exists(output_path):
            os.remove(output_path)
        raise self.retry(exc=e)
