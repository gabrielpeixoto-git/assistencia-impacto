import asyncio
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.financeiro import CategoriaFinanceira
from app.config import settings
from sqlalchemy import select

async def verificar_categorias():
    # Usar a URL do PostgreSQL do Docker
    database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/assistencia_impacto"
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        query = select(CategoriaFinanceira)
        result = await session.execute(query)
        categorias = result.scalars().all()
        
        if categorias:
            print(f"Encontradas {len(categorias)} categorias financeiras:")
            for cat in categorias:
                print(f"  - {cat.nome} (tipo: {cat.tipo}, cor: {cat.cor})")
        else:
            print("Nenhuma categoria financeira encontrada no banco de dados.")
            print("Criando categorias padrão...")
            
            categorias_padrao = [
                CategoriaFinanceira(nome="Serviços", tipo="receita", cor="#10B981", icone="💼", ativo=True),
                CategoriaFinanceira(nome="Salários", tipo="despesa", cor="#3B82F6", icone="💰", ativo=True),
                CategoriaFinanceira(nome="Aluguel", tipo="despesa", cor="#F59E0B", icone="🏠", ativo=True),
                CategoriaFinanceira(nome="Material", tipo="despesa", cor="#EF4444", icone="📦", ativo=True),
                CategoriaFinanceira(nome="Equipamentos", tipo="despesa", cor="#8B5CF6", icone="🔧", ativo=True),
                CategoriaFinanceira(nome="Outros", tipo="despesa", cor="#6B7280", icone="📋", ativo=True),
            ]
            
            for cat in categorias_padrao:
                session.add(cat)
            
            await session.commit()
            print("Categorias padrão criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(verificar_categorias())
