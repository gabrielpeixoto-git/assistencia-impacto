"""Testes do WhatsApp Service com mocking de httpx."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.whatsapp_service import WhatsAppService


class TestWhatsAppServiceEnviarMensagem:
    """Testa o método enviar_mensagem."""

    @pytest.mark.asyncio
    async def test_enviar_mensagem_sucesso(self):
        """Testa envio de mensagem com sucesso."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": {"id": "msg_123"}}
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem(
                numero="5511999999999",
                mensagem="Teste de mensagem"
            )
            assert resultado is True

    @pytest.mark.asyncio
    async def test_enviar_mensagem_falha(self):
        """Testa envio de mensagem com falha."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal Server Error"}
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem(
                numero="5511999999999",
                mensagem="Teste de mensagem"
            )
            assert resultado is False

    @pytest.mark.asyncio
    async def test_enviar_mensagem_excecao(self):
        """Testa envio de mensagem com exceção de rede."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=Exception("Connection error"))

            resultado = await WhatsAppService.enviar_mensagem(
                numero="5511999999999",
                mensagem="Teste"
            )
            assert resultado is False

    @pytest.mark.asyncio
    async def test_enviar_mensagem_instancia_customizada(self):
        """Testa envio de mensagem com instância customizada."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem(
                numero="5511999999999",
                mensagem="Teste",
                instancia="custom"
            )
            assert resultado is True


class TestWhatsAppServiceEnviarMensagemComMidia:
    """Testa o método enviar_mensagem_com_midia."""

    @pytest.mark.asyncio
    async def test_enviar_midia_sucesso(self):
        """Testa envio de mídia com sucesso."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem_com_midia(
                numero="5511999999999",
                url_midia="https://example.com/image.jpg"
            )
            assert resultado is True

    @pytest.mark.asyncio
    async def test_enviar_midia_com_legenda(self):
        """Testa envio de mídia com legenda."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem_com_midia(
                numero="5511999999999",
                url_midia="https://example.com/image.jpg",
                legenda="Foto do produto"
            )
            assert resultado is True

    @pytest.mark.asyncio
    async def test_enviar_midia_falha(self):
        """Testa envio de mídia com falha."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.post = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.enviar_mensagem_com_midia(
                numero="5511999999999",
                url_midia="https://example.com/image.jpg"
            )
            assert resultado is False

    @pytest.mark.asyncio
    async def test_enviar_midia_excecao(self):
        """Testa envio de mídia com exceção."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=Exception("Network error"))

            resultado = await WhatsAppService.enviar_mensagem_com_midia(
                numero="5511999999999",
                url_midia="https://example.com/image.jpg"
            )
            assert resultado is False


class TestWhatsAppServiceEnviarOrcamento:
    """Testa o método enviar_orcamento_whatsapp."""

    @pytest.mark.asyncio
    async def test_enviar_orcamento_sucesso(self):
        """Testa envio de orçamento com sucesso."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = True

            resultado = await WhatsAppService.enviar_orcamento_whatsapp(
                numero="5511999999999",
                cliente_nome="João Silva",
                numero_orcamento="ORC001",
                valor_total=1500.00
            )
            assert resultado is True
            mock_envio.assert_called_once()

    @pytest.mark.asyncio
    async def test_enviar_orcamento_com_pdf(self):
        """Testa envio de orçamento com PDF."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio, \
             patch.object(WhatsAppService, 'enviar_mensagem_com_midia', new_callable=AsyncMock) as mock_midia:
            mock_envio.return_value = True
            mock_midia.return_value = True

            resultado = await WhatsAppService.enviar_orcamento_whatsapp(
                numero="5511999999999",
                cliente_nome="Maria Santos",
                numero_orcamento="ORC002",
                valor_total=2000.00,
                url_pdf="https://example.com/orcamento.pdf"
            )
            assert resultado is True
            mock_envio.assert_called_once()
            mock_midia.assert_called_once()

    @pytest.mark.asyncio
    async def test_enviar_orcamento_falha_envio(self):
        """Testa envio de orçamento quando envio falha."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = False

            resultado = await WhatsAppService.enviar_orcamento_whatsapp(
                numero="5511999999999",
                cliente_nome="Pedro Oliveira",
                numero_orcamento="ORC003",
                valor_total=1800.00
            )
            assert resultado is False


class TestWhatsAppServiceEnviarConfirmacaoOS:
    """Testa o método enviar_confirmacao_os_whatsapp."""

    @pytest.mark.asyncio
    async def test_enviar_confirmacao_os_sucesso(self):
        """Testa envio de confirmação de OS com sucesso."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = True

            resultado = await WhatsAppService.enviar_confirmacao_os_whatsapp(
                numero="5511999999999",
                cliente_nome="Carlos Lima",
                numero_os="OS001",
                data_agendada="01/07/2026 14:00",
                endereco="Rua Teste, 123"
            )
            assert resultado is True
            mock_envio.assert_called_once()

    @pytest.mark.asyncio
    async def test_enviar_confirmacao_os_falha(self):
        """Testa envio de confirmação de OS com falha."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = False

            resultado = await WhatsAppService.enviar_confirmacao_os_whatsapp(
                numero="5511999999999",
                cliente_nome="Ana Costa",
                numero_os="OS002",
                data_agendada="02/07/2026 10:00",
                endereco="Av. Principal, 456"
            )
            assert resultado is False


class TestWhatsAppServiceEnviarAlertaEstoque:
    """Testa o método enviar_alerta_estoque_whatsapp."""

    @pytest.mark.asyncio
    async def test_enviar_alerta_estoque_sucesso(self):
        """Testa envio de alerta de estoque com sucesso."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = True

            resultado = await WhatsAppService.enviar_alerta_estoque_whatsapp(
                numero="5511999999999",
                item_nome="Parafuso 1/4\"",
                estoque_atual=5.0,
                estoque_minimo=10.0
            )
            assert resultado is True
            mock_envio.assert_called_once()

    @pytest.mark.asyncio
    async def test_enviar_alerta_estoque_falha(self):
        """Testa envio de alerta de estoque com falha."""
        with patch.object(WhatsAppService, 'enviar_mensagem', new_callable=AsyncMock) as mock_envio:
            mock_envio.return_value = False

            resultado = await WhatsAppService.enviar_alerta_estoque_whatsapp(
                numero="5511999999999",
                item_nome="Porca 1/4\"",
                estoque_atual=2.0,
                estoque_minimo=15.0
            )
            assert resultado is False


class TestWhatsAppServiceVerificarInstancia:
    """Testa o método verificar_instancia_ativa."""

    @pytest.mark.asyncio
    async def test_verificar_instancia_ativa_sucesso(self):
        """Testa verificação de instância ativa com sucesso."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"state": "open"}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.verificar_instancia_ativa()
            assert resultado is True

    @pytest.mark.asyncio
    async def test_verificar_instancia_inativa(self):
        """Testa verificação de instância inativa."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"state": "close"}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.verificar_instancia_ativa()
            assert resultado is False

    @pytest.mark.asyncio
    async def test_verificar_instancia_erro_status(self):
        """Testa verificação de instância com erro de status."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.verificar_instancia_ativa()
            assert resultado is False

    @pytest.mark.asyncio
    async def test_verificar_instancia_excecao(self):
        """Testa verificação de instância com exceção."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Connection error"))

            resultado = await WhatsAppService.verificar_instancia_ativa()
            assert resultado is False

    @pytest.mark.asyncio
    async def test_verificar_instancia_customizada(self):
        """Testa verificação de instância customizada."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"state": "open"}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.verificar_instancia_ativa(instancia="custom")
            assert resultado is True


class TestWhatsAppServiceObterQRCode:
    """Testa o método obter_qr_code."""

    @pytest.mark.asyncio
    async def test_obter_qrcode_sucesso(self):
        """Testa obtenção de QR code com sucesso."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"base64": "iVBORw0KGgoAAAANSUhEUgAA..."}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.obter_qr_code()
            assert resultado == "iVBORw0KGgoAAAANSUhEUgAA..."

    @pytest.mark.asyncio
    async def test_obter_qrcode_sem_base64(self):
        """Testa obtenção de QR code quando não há base64 na resposta."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"other": "data"}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.obter_qr_code()
            assert resultado is None

    @pytest.mark.asyncio
    async def test_obter_qrcode_erro_status(self):
        """Testa obtenção de QR code com erro de status."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.obter_qr_code()
            assert resultado is None

    @pytest.mark.asyncio
    async def test_obter_qrcode_excecao(self):
        """Testa obtenção de QR code com exceção."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))

            resultado = await WhatsAppService.obter_qr_code()
            assert resultado is None

    @pytest.mark.asyncio
    async def test_obter_qrcode_instancia_customizada(self):
        """Testa obtenção de QR code com instância customizada."""
        with patch('app.services.whatsapp_service.httpx.AsyncClient') as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"base64": "iVBORw0KGgoAAAANSUhEUgAA..."}
            mock_client.get = AsyncMock(return_value=mock_response)

            resultado = await WhatsAppService.obter_qr_code(instancia="custom")
            assert resultado == "iVBORw0KGgoAAAANSUhEUgAA..."
