import asyncio
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.usuario import Usuario
from app.core.seguranca import hash_senha
from app.config import settings

async def seed_test_users():
    """Cria usuários de teste no banco de dados."""
    
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Verificar se usuários já existem
        from sqlalchemy import select
        result = await session.execute(select(Usuario).where(Usuario.email == "admin@assistenciaimpacto.com.br"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("Usuários de teste já existem. Saindo...")
            return
        
        # Criar usuários de teste
        usuarios = [
            Usuario(
                email="admin@assistenciaimpacto.com.br",
                senha_hash=hash_senha("admin123"),
                nome_completo="Administrador",
                perfil="admin",
                telefone="11999999999",
                ativo=True,
                verificado=True
            ),
            Usuario(
                email="joao@assistenciaimpacto.com.br",
                senha_hash=hash_senha("admin123"),
                nome_completo="João Técnico",
                perfil="tecnico",
                telefone="11988888888",
                ativo=True,
                verificado=True
            ),
            Usuario(
                email="maria@assistenciaimpacto.com.br",
                senha_hash=hash_senha("admin123"),
                nome_completo="Maria Gerente",
                perfil="gerente",
                telefone="11977777777",
                ativo=True,
                verificado=True
            ),
            Usuario(
                email="carlos@assistenciaimpacto.com.br",
                senha_hash=hash_senha("admin123"),
                nome_completo="Carlos Visualizador",
                perfil="visualizador",
                telefone="11966666666",
                ativo=True,
                verificado=True
            )
        ]
        
        for usuario in usuarios:
            session.add(usuario)
        
        await session.commit()
        print("Usuários de teste criados com sucesso!")
        
        for usuario in usuarios:
            print(f"  - {usuario.email} ({usuario.perfil})")

if __name__ == "__main__":
    asyncio.run(seed_test_users())
