import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario, Perfil
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_tecnico():
    async with AsyncSessionLocal() as db:
        # Verificar se o técnico já existe
        result = await db.execute(select(Usuario).where(Usuario.email == 'joao@assistenciaimpacto.com.br'))
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f'Usuário técnico já existe: {existing.email}')
            return
        
        # Criar usuário técnico
        senha_hash = pwd_context.hash('admin123')
        tecnico = Usuario(
            email='joao@assistenciaimpacto.com.br',
            nome_completo='João Silva',
            senha_hash=senha_hash,
            perfil=Perfil.TECNICO,
            ativo=True,
            verificado=True
        )
        
        db.add(tecnico)
        await db.commit()
        await db.refresh(tecnico)
        
        print(f'Usuário técnico criado: {tecnico.email}, Perfil: {tecnico.perfil}')

if __name__ == "__main__":
    asyncio.run(create_tecnico())
