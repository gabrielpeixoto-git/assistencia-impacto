import asyncio
from app.database import AsyncSessionLocal
from app.models.orcamento import Orcamento
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        orc = (await db.execute(select(Orcamento).limit(1))).scalar_one_or_none()
        if not orc:
            print("Nenhum orçamento encontrado")
            return
        
        from app.services.pdf_service import gerar_pdf_orcamento
        pdf = await gerar_pdf_orcamento(orc.id, db)
        
        # Verificar estrutura do PDF
        print(f'Tamanho: {len(pdf)} bytes')
        print(f'Cabeçalho válido: {pdf[:5] == b"%PDF-"}')
        print(f'Termina com EOF: {b"%%EOF" in pdf[-100:]}')
        
        # Contar páginas (marcador /Page no PDF)
        paginas = pdf.count(b'/Type /Page')
        print(f'Páginas encontradas: {paginas}')
        
        # Contar texto (marcador BT/ET de text block)
        blocos_texto = pdf.count(b'BT')
        print(f'Blocos de texto: {blocos_texto}')

asyncio.run(check())
