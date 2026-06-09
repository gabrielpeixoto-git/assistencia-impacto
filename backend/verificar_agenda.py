import asyncio
from app.database import AsyncSessionLocal
from app.models.agenda import Agenda
from sqlalchemy import select

async def verificar_agenda():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Agenda))
        eventos = result.scalars().all()
        
        print(f"Total de eventos na agenda: {len(eventos)}")
        for evento in eventos:
            print(f"- {evento.titulo} ({evento.data_hora_inicio})")

if __name__ == "__main__":
    asyncio.run(verificar_agenda())
