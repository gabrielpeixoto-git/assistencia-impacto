from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações do aplicativo usando pydantic-settings."""
    
    model_config = SettingsConfigDict(
        env_file="../.env",  # Ler arquivo .env da raiz do projeto
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Banco de Dados
    database_url: str = "sqlite+aiosqlite:///./assistencia_impacto.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Autenticação JWT
    chave_secreta: str = "sua-chave-secreta-de-256-bits-aqui"
    algoritmo: str = "HS256"
    expiracao_token_acesso_minutos: int = 15
    expiracao_refresh_token_dias: int = 7
    
    # CORS e Segurança
    origens_cors: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://localhost:3000"
    hosts_permitidos: str = "localhost,127.0.0.1"
    
    # Uploads
    diretorio_uploads: str = "../uploads"
    tamanho_maximo_upload_mb: int = 10
    tipos_imagem_permitidos: str = "image/jpeg,image/png,image/webp"
    
    # E-mail SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_porta: int = 587
    smtp_usuario: str = "email@gmail.com"
    smtp_senha: str = "senha-de-app"
    email_remetente: str = "noreply@assistenciaimpacto.com.br"
    nome_remetente: str = "Assistência Impacto"
    
    # WhatsApp (Evolution API)
    evolution_api_url: str = "http://evolution-api:8080"
    evolution_api_key: str = "sua-chave-api"
    whatsapp_telefone: str = "5511999999999"
    
    # APIs Externas
    google_maps_api_key: str = "sua-chave-google-maps"
    viacep_api_url: str = "https://viacep.com.br/ws"
    
    # Dados da Empresa (sem valores fake - usar string vazia se não configurado)
    nome_empresa: str = ""
    cnpj_empresa: str = ""
    telefone_empresa: str = ""
    email_empresa: str = ""
    endereco_empresa: str = ""
    
    # Frontend
    url_frontend: str = "http://localhost:5173"
    
    # Ambiente
    ambiente: str = "development"  # "development" ou "production"
    permitir_registro_publico: bool = True  # Só deve ser True em development

    @property
    def origens_cors_lista(self) -> List[str]:
        """Retorna lista de origens CORS."""
        return [origem.strip() for origem in self.origens_cors.split(",")]
    
    @property
    def hosts_permitidos_lista(self) -> List[str]:
        """Retorna lista de hosts permitidos."""
        return [host.strip() for host in self.hosts_permitidos.split(",")]
    
    @property
    def tipos_imagem_permitidos_lista(self) -> List[str]:
        """Retorna lista de tipos de imagem permitidos."""
        return [tipo.strip() for tipo in self.tipos_imagem_permitidos.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()
