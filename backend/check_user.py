import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario).where(Usuario.email == 'admin@assistenciaimpacto.com.br'))
        user = result.scalar_one_or_none()
        if user:
            print('Usuario encontrado:', user.nome_completo)
            print('Ativo:', user.ativo)
        else:
            print('Usuario NAO encontrado')

asyncio.run(check())
