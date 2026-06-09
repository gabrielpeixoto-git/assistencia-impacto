import asyncio
from app.database import get_db
from app.services.auth_service import autenticar_usuario
from app.schemas.usuario import UsuarioLogin

async def test():
    async for db in get_db():
        try:
            data = UsuarioLogin(email='admin@assistenciaimpacto.com.br', senha='admin123')
            result = await autenticar_usuario(db, data)
            print('LOGIN OK:', result)
        except Exception as e:
            print('ERRO:', str(e))
        break

asyncio.run(test())
