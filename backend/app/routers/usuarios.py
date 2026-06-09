from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.dependencies import get_usuario_atual, require_admin
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.models.usuario import Usuario
from app.services.auth_service import criar_usuario

router = APIRouter()


@router.get("/", response_model=List[UsuarioResponse], status_code=status.HTTP_200_OK)
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_atual: Usuario = Depends(require_admin)
):
    """Lista todos os usuários (apenas admin)."""
    result = await db.execute(select(Usuario).offset(skip).limit(limit))
    usuarios = result.scalars().all()
    return usuarios


@router.get("/eu", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obter_usuario_atual(
    usuario_atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados do usuário autenticado."""
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_atual.id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def obter_usuario(
    usuario_id: str,
    db: AsyncSession = Depends(get_db),
    usuario_atual: Usuario = Depends(require_admin)
):
    """Retorna dados de um usuário específico (apenas admin)."""
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario_endpoint(
    usuario_data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    usuario_atual: Usuario = Depends(require_admin)
):
    """Cria um novo usuário (apenas admin)."""
    try:
        usuario = await criar_usuario(db, usuario_data)
        return usuario
    except Exception as e:
        raise


@router.patch("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def atualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_atual: Usuario = Depends(require_admin)
):
    """Atualiza dados de um usuário (apenas admin)."""
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = usuario_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    await db.commit()
    await db.refresh(usuario)
    
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: str,
    db: AsyncSession = Depends(get_db),
    usuario_atual: Usuario = Depends(require_admin)
):
    """Deleta um usuário (apenas admin)."""
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    await db.delete(usuario)
    await db.commit()
