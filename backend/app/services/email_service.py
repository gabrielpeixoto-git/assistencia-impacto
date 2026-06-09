import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.config import settings
from typing import Optional, List
from loguru import logger
import os


class EmailService:
    """Service para envio de emails."""
    
    @staticmethod
    def enviar_email(
        destinatario: str,
        assunto: str,
        corpo_html: str,
        anexos: Optional[List[str]] = None
    ) -> bool:
        """Envia um email."""
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = settings.email_remetente
            msg['To'] = destinatario
            
            # Adicionar corpo HTML
            html_part = MIMEText(corpo_html, 'html')
            msg.attach(html_part)
            
            # Adicionar anexos se fornecidos
            if anexos:
                for anexo_path in anexos:
                    if os.path.exists(anexo_path):
                        with open(anexo_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{os.path.basename(anexo_path)}"'
                            )
                            msg.attach(part)
            
            # Conectar ao servidor SMTP e enviar
            with smtplib.SMTP(settings.smtp_host, settings.smtp_porta) as server:
                server.starttls()
                server.login(settings.smtp_usuario, settings.smtp_senha)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    @staticmethod
    def enviar_orcamento_email(
        destinatario: str,
        cliente_nome: str,
        numero_orcamento: str,
        valor_total: float,
        valido_ate: str,
        url_pdf: Optional[str] = None
    ) -> bool:
        """Envia email com orçamento."""
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6C63FF; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Assistência Impacto</h1>
                </div>
                <div class="content">
                    <h2>Orçamento {numero_orcamento}</h2>
                    <p>Olá, {cliente_nome}!</p>
                    <p>Enviamos o orçamento solicitado com as seguintes informações:</p>
                    <ul>
                        <li>Número do Orçamento: {numero_orcamento}</li>
                        <li>Valor Total: R$ {valor_total:.2f}</li>
                        <li>Válido até: {valido_ate}</li>
                    </ul>
                    <p>Por favor, revise o orçamento e entre em contato caso tenha dúvidas.</p>
                    <p>Atenciosamente,<br>Equipe Assistência Impacto</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        anexos = [url_pdf] if url_pdf and os.path.exists(url_pdf) else None
        
        return EmailService.enviar_email(
            destinatario=destinatario,
            assunto=f"Orçamento {numero_orcamento} - Assistência Impacto",
            corpo_html=corpo_html,
            anexos=anexos
        )
    
    @staticmethod
    def enviar_confirmacao_os_email(
        destinatario: str,
        cliente_nome: str,
        numero_os: str,
        data_agendada: str,
        endereco: str
    ) -> bool:
        """Envia email de confirmação de ordem de serviço."""
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6C63FF; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Assistência Impacto</h1>
                </div>
                <div class="content">
                    <h2>Confirmação de Ordem de Serviço</h2>
                    <p>Olá, {cliente_nome}!</p>
                    <p>Sua ordem de serviço foi agendada com sucesso:</p>
                    <ul>
                        <li>Número da OS: {numero_os}</li>
                        <li>Data Agendada: {data_agendada}</li>
                        <li>Endereço: {endereco}</li>
                    </ul>
                    <p>Por favor, certifique-se de que alguém estará no endereço no horário agendado.</p>
                    <p>Atenciosamente,<br>Equipe Assistência Impacto</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.enviar_email(
            destinatario=destinatario,
            assunto=f"Confirmação OS {numero_os} - Assistência Impacto",
            corpo_html=corpo_html
        )
    
    @staticmethod
    def enviar_recuperacao_senha_email(
        destinatario: str,
        nome_usuario: str,
        token_reset: str,
        url_reset: str
    ) -> bool:
        """Envia email de recuperação de senha."""
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6C63FF; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #6C63FF; color: white; text-decoration: none; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Assistência Impacto</h1>
                </div>
                <div class="content">
                    <h2>Recuperação de Senha</h2>
                    <p>Olá, {nome_usuario}!</p>
                    <p>Recebemos uma solicitação para redefinir sua senha.</p>
                    <p>Clique no botão abaixo para redefinir sua senha:</p>
                    <p style="text-align: center;">
                        <a href="{url_reset}" class="button">Redefinir Senha</a>
                    </p>
                    <p>Este link expirará em 1 hora.</p>
                    <p>Se você não solicitou esta redefinição, ignore este email.</p>
                    <p>Atenciosamente,<br>Equipe Assistência Impacto</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.enviar_email(
            destinatario=destinatario,
            assunto="Recuperação de Senha - Assistência Impacto",
            corpo_html=corpo_html
        )
    
    @staticmethod
    def enviar_reset_senha(
        destinatario: str,
        token: str
    ) -> bool:
        """Envia email de recuperação de senha com token (wrapper para task Celery)."""
        from app.config import settings
        
        url_reset = f"{settings.url_frontend}/redefinir-senha?token={token}"
        
        return EmailService.enviar_recuperacao_senha_email(
            destinatario=destinatario,
            nome_usuario="Usuário",
            token_reset=token,
            url_reset=url_reset
        )
