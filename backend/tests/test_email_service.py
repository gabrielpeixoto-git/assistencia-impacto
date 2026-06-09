import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService


def test_enviar_orcamento_email():
    """Testa envio de email de orçamento."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_orcamento_email(
            destinatario="cliente@example.com",
            cliente_nome="João Silva",
            numero_orcamento="ORC202601001",
            valor_total=1500.00,
            valido_ate="30/06/2026",
            url_pdf=None
        )
        
        assert resultado is True
        mock_server.starttls.assert_called_once()
        mock_server.send_message.assert_called_once()


def test_enviar_orcamento_email_com_pdf():
    """Testa envio de email de orçamento com anexo PDF."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp, \
         patch('app.services.email_service.os.path.exists', return_value=True), \
         patch('builtins.open', create=True) as mock_open:
        
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake pdf content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_orcamento_email(
            destinatario="cliente@example.com",
            cliente_nome="Maria Santos",
            numero_orcamento="ORC202601002",
            valor_total=2000.00,
            valido_ate="15/07/2026",
            url_pdf="/tmp/orcamento.pdf"
        )
        
        assert resultado is True


def test_enviar_confirmacao_os_email():
    """Testa envio de email de confirmação de ordem de serviço."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_confirmacao_os_email(
            destinatario="cliente@example.com",
            cliente_nome="Pedro Oliveira",
            numero_os="OS202601001",
            data_agendada="01/07/2026 14:00",
            endereco="Rua Teste, 123"
        )
        
        assert resultado is True
        mock_server.send_message.assert_called_once()


def test_enviar_recuperacao_senha_email():
    """Testa envio de email de recuperação de senha."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_recuperacao_senha_email(
            destinatario="usuario@example.com",
            nome_usuario="Carlos Lima",
            token_reset="abc123xyz",
            url_reset="https://example.com/reset/abc123xyz"
        )
        
        assert resultado is True
        mock_server.send_message.assert_called_once()


def test_enviar_email_erro_smtp():
    """Testa tratamento de erro ao enviar email quando SMTP falha."""
    with patch('app.services.email_service.smtplib.SMTP', side_effect=Exception("SMTP Error")):
        resultado = EmailService.enviar_email(
            destinatario="cliente@example.com",
            assunto="Teste",
            corpo_html="<p>Teste</p>"
        )
        
        assert resultado is False


def test_enviar_email_com_anexos():
    """Testa envio de email com anexos."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp, \
         patch('app.services.email_service.os.path.exists', return_value=True), \
         patch('builtins.open', create=True) as mock_open:
        
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_email(
            destinatario="cliente@example.com",
            assunto="Email com anexos",
            corpo_html="<p>Email com anexos</p>",
            anexos=["/tmp/arquivo1.pdf", "/tmp/arquivo2.pdf"]
        )
        
        assert resultado is True


def test_enviar_email_sem_anexos():
    """Testa envio de email sem anexos."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_email(
            destinatario="cliente@example.com",
            assunto="Email simples",
            corpo_html="<p>Email simples</p>"
        )
        
        assert resultado is True


def test_enviar_email_arquivo_nao_existe():
    """Testa envio de email com anexo que não existe - anexo é ignorado."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp, \
         patch('app.services.email_service.os.path.exists', return_value=False):
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_email(
            destinatario="cliente@example.com",
            assunto="Email com anexo",
            corpo_html="<p>Email</p>",
            anexos=["/tmp/arquivo-inexistente.pdf"]
        )
        
        # O email deve ser enviado mesmo se o anexo não existe (anexo é ignorado)
        assert resultado is True
        mock_server.send_message.assert_called_once()


def test_enviar_confirmacao_os_email_com_endereco():
    """Testa envio de email de confirmação de OS com endereço completo."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        resultado = EmailService.enviar_confirmacao_os_email(
            destinatario="cliente@example.com",
            cliente_nome="João Silva",
            numero_os="OS202601001",
            data_agendada="01/07/2026 14:00",
            endereco="Rua Teste, 123, Centro, São Paulo - SP"
        )
        
        assert resultado is True


def test_enviar_recuperacao_senha_email_com_url_personalizada():
    """Testa envio de email de recuperação de senha com URL personalizada."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        resultado = EmailService.enviar_recuperacao_senha_email(
            destinatario="usuario@example.com",
            nome_usuario="Carlos Lima",
            token_reset="abc123xyz",
            url_reset="https://meusistema.com/reset-password?token=abc123xyz"
        )

        assert resultado is True


def test_enviar_reset_senha():
    """Testa envio de email de reset de senha (wrapper para task Celery)."""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp, \
         patch('app.services.email_service.settings.url_frontend', 'http://localhost:3000'):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        resultado = EmailService.enviar_reset_senha(
            destinatario="usuario@example.com",
            token="abc123xyz"
        )

        assert resultado is True
        mock_server.send_message.assert_called_once()


def test_enviar_reset_senha_falha():
    """Testa envio de email de reset de senha com falha no SMTP."""
    with patch('app.services.email_service.smtplib.SMTP', side_effect=Exception("SMTP Error")), \
         patch('app.services.email_service.settings.url_frontend', 'http://localhost:3000'):
        resultado = EmailService.enviar_reset_senha(
            destinatario="usuario@example.com",
            token="abc123xyz"
        )

        assert resultado is False
