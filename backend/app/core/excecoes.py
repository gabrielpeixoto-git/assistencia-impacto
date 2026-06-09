from typing import Any, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Exceção base da aplicação."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NaoEncontradoException(AppException):
    """Exceção para recurso não encontrado."""
    
    def __init__(self, detail: str = "Recurso não encontrado") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConflitoException(AppException):
    """Exceção para conflito de dados."""
    
    def __init__(self, detail: str = "Conflito de dados") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ValidacaoException(AppException):
    """Exceção para erro de validação."""
    
    def __init__(self, detail: str = "Erro de validação") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class NaoAutorizadoException(AppException):
    """Exceção para não autorizado."""
    
    def __init__(self, detail: str = "Não autorizado") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ProibidoException(AppException):
    """Exceção para acesso proibido."""
    
    def __init__(self, detail: str = "Acesso proibido") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ErroInternoException(AppException):
    """Exceção para erro interno do servidor."""
    
    def __init__(self, detail: str = "Erro interno do servidor") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
