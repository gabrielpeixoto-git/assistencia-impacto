from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional
from app.models.cliente import TipoDocumento, TipoCliente


def validar_cpf(cpf: str) -> bool:
    """Valida CPF com algoritmo dos dígitos verificadores."""
    numeros = ''.join(filter(str.isdigit, cpf))
    if len(numeros) != 11 or len(set(numeros)) == 1:
        return False
    # Primeiro dígito verificador
    soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10 % 11) % 10
    if d1 != int(numeros[9]):
        return False
    # Segundo dígito verificador
    soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10 % 11) % 10
    return d2 == int(numeros[10])


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ com algoritmo dos dígitos verificadores."""
    numeros = ''.join(filter(str.isdigit, cnpj))
    if len(numeros) != 14 or len(set(numeros)) == 1:
        return False
    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]
    soma = sum(int(numeros[i]) * pesos1[i] for i in range(12))
    d1 = 0 if soma % 11 < 2 else 11 - soma % 11
    if d1 != int(numeros[12]):
        return False
    soma = sum(int(numeros[i]) * pesos2[i] for i in range(13))
    d2 = 0 if soma % 11 < 2 else 11 - soma % 11
    return d2 == int(numeros[13])


class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    tipo_documento: TipoDocumento = TipoDocumento.CPF
    numero_documento: Optional[str] = None
    tipo_cliente: TipoCliente = TipoCliente.RESIDENCIAL
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    observacoes: Optional[str] = None


class ClienteCreate(ClienteBase):
    @field_validator('numero_documento')
    @classmethod
    def validar_documento(cls, v, info):
        """Valida CPF ou CNPJ conforme o tipo."""
        if v is None:
            return v
        tipo_documento = info.data.get('tipo_documento', TipoDocumento.CPF)
        if tipo_documento == TipoDocumento.CPF:
            if not validar_cpf(v):
                raise ValueError('CPF inválido')
        elif tipo_documento == TipoDocumento.CNPJ:
            if not validar_cnpj(v):
                raise ValueError('CNPJ inválido')
        return v


class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    tipo_documento: Optional[TipoDocumento] = None
    numero_documento: Optional[str] = None
    tipo_cliente: Optional[TipoCliente] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    observacoes: Optional[str] = None
    avaliacao: Optional[int] = None
    ativo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    id: str
    avaliacao: Optional[int]
    ativo: bool
    latitude: Optional[float]
    longitude: Optional[float]
    criado_por: str
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class EnderecoClienteCreate(BaseModel):
    rotulo: str = Field(..., min_length=1, max_length=50)
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    padrao: bool = False
