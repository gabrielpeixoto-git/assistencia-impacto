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
        
        try:
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
            
            # Verificar se há string de texto no PDF
            texto_str = pdf.count(b'string')
            print(f'Strings de texto: {texto_str}')
            
            # Mostrar primeiros 200 bytes em hex para debug
            print(f'Primeiros 200 bytes: {pdf[:200]}')
        except Exception as e:
            print(f'Erro: {e}')
            import traceback
            traceback.print_exc()

asyncio.run(check())
