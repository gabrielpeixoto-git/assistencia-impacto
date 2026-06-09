import httpx
from app.config import settings
from typing import Optional, List
from loguru import logger


class WhatsAppService:
    """Service para integração com Evolution API (WhatsApp)."""
    
    @staticmethod
    async def enviar_mensagem(
        numero: str,
        mensagem: str,
        instancia: str = "default"
    ) -> bool:
        """Envia uma mensagem WhatsApp."""
        try:
            url = f"{settings.evolution_api_url}/message/sendText/{instancia}"
            
            payload = {
                "number": numero,
                "text": mensagem,
                "delay": 1200
            }
            
            headers = {
                "Content-Type": "application/json",
                "apikey": settings.evolution_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return False
    
    @staticmethod
    async def enviar_mensagem_com_midia(
        numero: str,
        url_midia: str,
        legenda: Optional[str] = None,
        instancia: str = "default"
    ) -> bool:
        """Envia uma mensagem com mídia (imagem, documento, etc.)."""
        try:
            url = f"{settings.evolution_api_url}/message/sendMedia/{instancia}"
            
            payload = {
                "number": numero,
                "mediatype": "image",
                "media": url_midia,
                "caption": legenda or "",
                "delay": 1200
            }
            
            headers = {
                "Content-Type": "application/json",
                "apikey": settings.evolution_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao enviar mídia WhatsApp: {e}")
            return False
    
    @staticmethod
    async def enviar_orcamento_whatsapp(
        numero: str,
        cliente_nome: str,
        numero_orcamento: str,
        valor_total: float,
        url_pdf: Optional[str] = None
    ) -> bool:
        """Envia orçamento via WhatsApp."""
        mensagem = f"""
📋 *Orçamento {numero_orcamento}*

Olá, {cliente_nome}! 👋

Enviamos seu orçamento com as seguintes informações:

💰 *Valor Total:* R$ {valor_total:.2f}

Por favor, revise o orçamento e entre em contato caso tenha dúvidas.

Atenciosamente,
*Assistência Impacto* ⚡
"""
        
        # Enviar mensagem de texto
        sucesso = await WhatsAppService.enviar_mensagem(numero, mensagem)
        
        # Enviar PDF se fornecido
        if sucesso and url_pdf:
            await WhatsAppService.enviar_mensagem_com_midia(
                numero=numero,
                url_midia=url_pdf,
                legenda=f"Orçamento {numero_orcamento}"
            )
        
        return sucesso
    
    @staticmethod
    async def enviar_confirmacao_os_whatsapp(
        numero: str,
        cliente_nome: str,
        numero_os: str,
        data_agendada: str,
        endereco: str
    ) -> bool:
        """Envia confirmação de ordem de serviço via WhatsApp."""
        mensagem = f"""
✅ *Confirmação de Ordem de Serviço*

Olá, {cliente_nome}! 👋

Sua ordem de serviço foi agendada com sucesso:

🔧 *Número da OS:* {numero_os}
📅 *Data Agendada:* {data_agendada}
📍 *Endereço:* {endereco}

Por favor, certifique-se de que alguém estará no endereço no horário agendado.

Atenciosamente,
*Assistência Impacto* ⚡
"""
        
        return await WhatsAppService.enviar_mensagem(numero, mensagem)
    
    @staticmethod
    async def enviar_alerta_estoque_whatsapp(
        numero: str,
        item_nome: str,
        estoque_atual: float,
        estoque_minimo: float
    ) -> bool:
        """Envia alerta de estoque baixo via WhatsApp."""
        mensagem = f"""
⚠️ *Alerta de Estoque*

O item *{item_nome}* está com estoque abaixo do mínimo:

📦 *Estoque Atual:* {estoque_atual}
📉 *Estoque Mínimo:* {estoque_minimo}

Por favor, reabasteça este item o mais rápido possível.

*Assistência Impacto* ⚡
"""
        
        return await WhatsAppService.enviar_mensagem(numero, mensagem)
    
    @staticmethod
    async def verificar_instancia_ativa(instancia: str = "default") -> bool:
        """Verifica se a instância do WhatsApp está ativa."""
        try:
            url = f"{settings.evolution_api_url}/instance/connectionState/{instancia}"
            
            headers = {
                "apikey": settings.evolution_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("state") == "open"
                return False
        except Exception as e:
            logger.error(f"Erro ao verificar instância WhatsApp: {e}")
            return False
    
    @staticmethod
    async def obter_qr_code(instancia: str = "default") -> Optional[str]:
        """Obtém o QR code para conectar o WhatsApp."""
        try:
            url = f"{settings.evolution_api_url}/instance/connect/{instancia}"
            
            headers = {
                "apikey": settings.evolution_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("base64")
                return None
        except Exception as e:
            logger.error(f"Erro ao obter QR code: {e}")
            return None
