import secrets
import sys
sys.path.append('backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.models.orcamento import Orcamento
from app.config import settings

async def gerar_tokens():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Buscar orçamentos sem token
        result = await session.execute(
            select(Orcamento).where(Orcamento.token_acesso_publico.is_(None))
        )
        orcamentos = result.scalars().all()
        
        print(f"Encontrados {len(orcamentos)} orçamentos sem token")
        
        for orcamento in orcamentos:
            token = secrets.token_hex(32)
            orcamento.token_acesso_publico = token
            print(f"Gerando token para {orcamento.numero_orcamento}: {token[:16]}...")
        
        await session.commit()
        print(f"Tokens gerados com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(gerar_tokens())
