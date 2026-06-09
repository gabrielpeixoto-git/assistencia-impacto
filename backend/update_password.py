import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.seguranca import hash_senha

async def update():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario).where(Usuario.email == 'admin@assistenciaimpacto.com.br'))
        user = result.scalar_one_or_none()
        if user:
            user.senha_hash = hash_senha('admin123')
            await db.commit()
            print('Senha atualizada com sucesso para: admin123')
        else:
            print('Usuario nao encontrado')

asyncio.run(update())
