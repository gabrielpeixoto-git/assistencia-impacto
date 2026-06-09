import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario, Perfil
from app.core.seguranca import hash_senha
from sqlalchemy import select

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Verificar se admin já existe
        result = await db.execute(select(Usuario).where(Usuario.email == "admin@assistenciaimpacto.com.br"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Usuário admin já existe")
            return
        
        # Criar usuário admin
        admin = Usuario(
            email="admin@assistenciaimpacto.com.br",
            nome_completo="Administrador",
            senha_hash=hash_senha("admin123"),
            perfil=Perfil.ADMIN,
            ativo=True,
            verificado=True
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print(f"Usuário admin criado com sucesso: {admin.email}")

if __name__ == "__main__":
    asyncio.run(create_admin())
