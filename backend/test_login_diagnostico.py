import asyncio, traceback, sys

async def test_login():
    from app.database import engine
    from app.services.auth_service import autenticar_usuario
    from app.schemas.usuario import UsuarioLogin
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async with AsyncSession(engine) as session:
        try:
            result = await autenticar_usuario(
                session,
                UsuarioLogin(email='admin@assistenciaimpacto.com.br', senha='Admin@123'),
                ip='127.0.0.1',
                user_agent='test'
            )
            print('LOGIN OK:', result)
        except Exception as e:
            print('ERRO DETALHADO:')
            traceback.print_exc()

asyncio.run(test_login())
