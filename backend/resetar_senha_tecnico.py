#!/usr/bin/env python3
"""
Script para redefinir a senha do usuário técnico.
Usa a função hash_senha correta do backend.
"""

import sys
import os

# Adicionar o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.core.seguranca import hash_senha
from app.models.usuario import Usuario
from app.config import settings

async def resetar_senha_tecnico():
    """Redefine a senha do usuário técnico."""
    
    # Criar engine e sessão - usar URL do banco via Docker
    database_url = "postgresql+asyncpg://assistencia:assistencia123@db:5432/assistencia_impacto"
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Buscar usuário técnico
        result = await db.execute(
            select(Usuario).where(Usuario.email == "joao.silva@assistenciaimpacto.com.br")
        )
        tecnico = result.scalar_one_or_none()
        
        if not tecnico:
            print("✗ Usuário técnico não encontrado")
            return False
        
        # Redefinir senha
        nova_senha = "admin123"  # Senha padrão para testes
        novo_hash = hash_senha(nova_senha)
        
        tecnico.senha_hash = novo_hash
        await db.commit()
        
        print(f"✓ Senha do usuário técnico {tecnico.email} redefinida com sucesso")
        print(f"  Nova senha: {nova_senha}")
        
        return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(resetar_senha_tecnico())
