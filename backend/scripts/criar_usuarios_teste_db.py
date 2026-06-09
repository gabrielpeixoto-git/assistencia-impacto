import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.seguranca import hash_senha
from app.models.usuario import Usuario, Perfil
import uuid

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_assistencia_impacto"

async def criar_usuarios():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Admin
        admin = Usuario(
            id=str(uuid.uuid4()),
            email="admin@assistenciaimpacto.com.br",
            senha_hash=hash_senha("Admin@123"),
            nome_completo="Administrador",
            perfil=Perfil.ADMIN,
            telefone="11999999999",
            ativo=True,
            verificado=True
        )
        session.add(admin)
        
        # Técnico
        tecnico = Usuario(
            id=str(uuid.uuid4()),
            email="joao@assistenciaimpacto.com.br",
            senha_hash=hash_senha("Tecnico@123"),
            nome_completo="João Silva",
            perfil=Perfil.TECNICO,
            telefone="11988888888",
            ativo=True,
            verificado=True
        )
        session.add(tecnico)
        
        # Gerente
        gerente = Usuario(
            id=str(uuid.uuid4()),
            email="gerente@assistenciaimpacto.com.br",
            senha_hash=hash_senha("Gerente@123"),
            nome_completo="Gerente Teste",
            perfil=Perfil.GERENTE,
            telefone="11977777777",
            ativo=True,
            verificado=True
        )
        session.add(gerente)
        
        await session.commit()
        print("Usuários de teste criados com sucesso!")

if __name__ == "__main__":
    asyncio.run(criar_usuarios())
