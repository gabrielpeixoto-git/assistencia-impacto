import asyncio
from app.database import engine
from sqlalchemy import select
from app.models.usuario import Usuario
from sqlalchemy.ext.asyncio import AsyncSession

async def check():
    async with AsyncSession(engine) as session:
        # Verificar se tabela usuarios existe e tem dados
        result = await session.execute(select(Usuario).where(Usuario.email == 'admin@assistenciaimpacto.com.br'))
        admin = result.scalars().first()
        
        if admin:
            print(f'Usuario admin encontrado:')
            print(f'  ID: {admin.id}')
            print(f'  Email: {admin.email}')
            print(f'  Nome: {admin.nome_completo}')
            print(f'  Ativo: {admin.ativo}')
            print(f'  Senha hash existe: {bool(admin.senha_hash)}')
        else:
            print('Usuario admin NAO encontrado no banco')
            # Listar todos os usuarios
            result = await session.execute(select(Usuario))
            usuarios = result.scalars().all()
            print(f'\nTotal de usuarios no banco: {len(usuarios)}')
            for u in usuarios:
                print(f'  - {u.email} ({u.nome_completo})')

asyncio.run(check())
