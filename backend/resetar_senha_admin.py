import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.seguranca import hash_senha
from sqlalchemy import select

async def resetar_senha_admin():
    async with AsyncSessionLocal() as db:
        # Buscar usuário admin
        result = await db.execute(select(Usuario).where(Usuario.email == "admin@assistenciaimpacto.com.br"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Usuário admin não encontrado")
            return
        
        # Resetar senha
        nova_senha = "admin123"
        admin.senha_hash = hash_senha(nova_senha)
        await db.commit()
        
        print(f"Senha do admin resetada com sucesso")
        print(f"Email: admin@assistenciaimpacto.com.br")
        print(f"Senha: {nova_senha}")

if __name__ == "__main__":
    asyncio.run(resetar_senha_admin())
