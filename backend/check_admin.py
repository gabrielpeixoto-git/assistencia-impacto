import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario).where(Usuario.email == 'admin@assistenciaimpacto.com.br'))
        user = result.scalar_one_or_none()
        print(f'User exists: {user is not None}')
        if user:
            print(f'Email: {user.email}, Perfil: {user.perfil}, Ativo: {user.ativo}')

if __name__ == "__main__":
    asyncio.run(check())
