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
        
        print(f'Tamanho: {len(pdf)} bytes')
        
        # Verificar se há texto buscando por strings comuns
        texto_orcamento = b"OR"
        if texto_orcamento in pdf:
            print(f'Texto "OR" encontrado (orçamento)')
        else:
            print(f'Texto "OR" NÃO encontrado')
        
        texto_assistencia = b"Assistencia"
        if texto_assistencia in pdf:
            print(f'Texto "Assistencia" encontrado')
        else:
            print(f'Texto "Assistencia" NÃO encontrado')
        
        # Verificar se há stream de dados
        if b"stream" in pdf:
            print(f'Stream encontrado: {pdf.count(b"stream")} vezes')
        
        # Verificar se há fontes
        if b"Font" in pdf:
            print(f'Font encontrado: {pdf.count(b"Font")} vezes')
        
        # Salvar para inspeção manual
        with open("/tmp/orcamento_check.pdf", "wb") as f:
            f.write(pdf)
        print("PDF salvo em /tmp/orcamento_check.pdf")

asyncio.run(check())
