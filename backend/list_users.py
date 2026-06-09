import asyncio
from app.database import AsyncSessionLocal
from app.models import Usuario
from sqlalchemy import select

async def list_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario))
        users = result.scalars().all()
        print([(u.email, u.ativo) for u in users])

if __name__ == "__main__":
    asyncio.run(list_users())
