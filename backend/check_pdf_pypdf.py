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
        
        # Tentar extrair texto com PyPDF2
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf))
            print(f'Páginas: {len(reader.pages)}')
            
            texto_completo = ""
            for page in reader.pages:
                try:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
                except Exception as e:
                    print(f'Erro ao extrair texto da página: {e}')
            
            print(f'Texto extraído: {len(texto_completo)} caracteres')
            if texto_completo:
                print(f'Primeiros 200 caracteres: {texto_completo[:200]}')
            else:
                print('Nenhum texto extraído')
        except ImportError:
            print('PyPDF2 não instalado, tentando instalar...')
            import subprocess
            subprocess.run(['pip', 'install', 'PyPDF2', '--break-system-packages'])
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf))
            print(f'Páginas: {len(reader.pages)}')
            
            texto_completo = ""
            for page in reader.pages:
                try:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
                except Exception as e:
                    print(f'Erro ao extrair texto da página: {e}')
            
            print(f'Texto extraído: {len(texto_completo)} caracteres')
            if texto_completo:
                print(f'Primeiros 200 caracteres: {texto_completo[:200]}')
            else:
                print('Nenhum texto extraído')

asyncio.run(check())
