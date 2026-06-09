from pydantic import BaseModel, ConfigDict
from typing import List


class ConfiguracaoResponse(BaseModel):
    """Schema para resposta de configurações (apenas configs não sensíveis)."""
    
    # Dados da Empresa
    nome_empresa: str
    cnpj_empresa: str
    telefone_empresa: str
    email_empresa: str
    endereco_empresa: str
    
    # Configurações de Email (sem senha)
    smtp_host: str
    smtp_porta: int
    smtp_usuario: str
    email_remetente: str
    nome_remetente: str
    
    # Configurações de WhatsApp (sem API key)
    evolution_api_url: str
    whatsapp_telefone: str
    
    # APIs Externas (sem chaves sensíveis)
    viacep_api_url: str
    
    # Frontend
    url_frontend: str
    
    # Ambiente
    ambiente: str
    permitir_registro_publico: bool
    
    # Uploads
    tamanho_maximo_upload_mb: int
    tipos_imagem_permitidos: str
    
    # Preferências de Notificação
    notif_nova_os: bool = True
    notif_orcamento_aprovado: bool = True
    notif_orcamento_rejeitado: bool = True
    notif_agendamento_proximo: bool = True
    notif_estoque_baixo: bool = True
    notif_relatorio_semanal: bool = False
    notif_canal_email: bool = True
    notif_canal_sistema: bool = True
    notif_frequencia: str = "imediato"  # imediato, diario, semanal
    
    # Preferências de Aparência
    tema_dark_mode: bool = False
    tema_cor_primaria: str = "roxo"  # roxo, azul, verde, laranja, vermelho, rosa
    tema_densidade: str = "normal"  # compacto, normal, espacoso
    
    # Configurações Regionais
    regiao_moeda: str = "BRL"
    regiao_fuso_horario: str = "America/Sao_Paulo"
    regiao_formato_data: str = "DD/MM/AAAA"
    regiao_idioma: str = "pt-BR"
    
    model_config = ConfigDict(from_attributes=True)


class ConfiguracaoUpdate(BaseModel):
    """Schema para atualização de configurações não sensíveis."""
    
    # Dados da Empresa
    nome_empresa: str | None = None
    cnpj_empresa: str | None = None
    telefone_empresa: str | None = None
    email_empresa: str | None = None
    endereco_empresa: str | None = None
    
    # Configurações de Email (sem senha)
    smtp_host: str | None = None
    smtp_porta: int | None = None
    smtp_usuario: str | None = None
    email_remetente: str | None = None
    nome_remetente: str | None = None
    
    # Configurações de WhatsApp (sem API key)
    evolution_api_url: str | None = None
    whatsapp_telefone: str | None = None
    
    # Frontend
    url_frontend: str | None = None
    
    # Ambiente
    ambiente: str | None = None
    permitir_registro_publico: bool | None = None
    
    # Uploads
    tamanho_maximo_upload_mb: int | None = None
    tipos_imagem_permitidos: str | None = None
    
    # Preferências de Notificação
    notif_nova_os: bool | None = None
    notif_orcamento_aprovado: bool | None = None
    notif_orcamento_rejeitado: bool | None = None
    notif_agendamento_proximo: bool | None = None
    notif_estoque_baixo: bool | None = None
    notif_relatorio_semanal: bool | None = None
    notif_canal_email: bool | None = None
    notif_canal_sistema: bool | None = None
    notif_frequencia: str | None = None
    
    # Preferências de Aparência
    tema_dark_mode: bool | None = None
    tema_cor_primaria: str | None = None
    tema_densidade: str | None = None
    
    # Configurações Regionais
    regiao_moeda: str | None = None
    regiao_fuso_horario: str | None = None
    regiao_formato_data: str | None = None
    regiao_idioma: str | None = None
