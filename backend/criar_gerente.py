import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.seguranca import hash_senha
from sqlalchemy import select
from app.models.usuario import Perfil

async def create():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Usuario).where(Usuario.email == 'gerente@assistenciaimpacto.com.br')
        )
        user = result.scalar_one_or_none()
        if not user:
            user = Usuario(
                email='gerente@assistenciaimpacto.com.br',
                nome_completo='Gerente Teste',
                senha_hash=hash_senha('Gerente@123'),
                perfil=Perfil.GERENTE,
                ativo=True,
                verificado=True
            )
            db.add(user)
            await db.commit()
            print('Gerente criado com sucesso')
        else:
            user.senha_hash = hash_senha('Gerente@123')
            await db.commit()
            print('Senha do gerente redefinida com sucesso')

asyncio.run(create())
