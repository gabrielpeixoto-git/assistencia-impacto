import asyncio
from sqlalchemy import select, func
from app.database import get_db
from app.models.financeiro import Transacao, TipoTransacao, StatusTransacao
from datetime import datetime, timedelta

async def check():
    async for db in get_db():
        hoje = datetime.now()
        inicio = hoje - timedelta(days=6)
        
        print(f"Verificando transações de {inicio.date()} até {hoje.date()}")
        print(f"Tipo: {TipoTransacao.RECEITA}, Status: {StatusTransacao.PAGO}")
        print()
        
        query = select(Transacao).where(
            Transacao.tipo == TipoTransacao.RECEITA,
            Transacao.status == StatusTransacao.PAGO,
            Transacao.data_pagamento >= inicio
        )
        result = await db.execute(query)
        transacoes = result.scalars().all()
        
        print(f'Transações encontradas: {len(transacoes)}')
        for t in transacoes:
            print(f'  - ID: {t.id}, Valor: {t.valor}, Data: {t.data_pagamento}, Tipo: {t.tipo}, Status: {t.status}')
        
        # Verificar todas as transações
        query_all = select(Transacao)
        result_all = await db.execute(query_all)
        all_transacoes = result_all.scalars().all()
        print(f'\nTotal de transações no banco: {len(all_transacoes)}')
        for t in all_transacoes[:10]:
            print(f'  - ID: {t.id}, Valor: {t.valor}, Tipo: {t.tipo}, Status: {t.status}, Data Pagamento: {t.data_pagamento}')
        
        break

asyncio.run(check())
