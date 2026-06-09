"""
Script para criar transações de receita distribuídas nos últimos 7 dias.
Isso vai popular o gráfico de tendência de receita com dados realistas.
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import select
from app.database import get_db
from app.models.financeiro import Transacao, TipoTransacao, StatusTransacao, CategoriaFinanceira
from app.models.usuario import Usuario
from datetime import datetime, timedelta
import uuid
import random

async def seed_transacoes_7_dias():
    """Cria transações de receita distribuídas nos últimos 7 dias."""
    
    async for db in get_db():
        # Buscar categoria de receita
        query_cat = select(CategoriaFinanceira).where(
            CategoriaFinanceira.tipo == TipoTransacao.RECEITA
        )
        result_cat = await db.execute(query_cat)
        categorias = result_cat.scalars().all()
        
        if not categorias:
            print("ERROR: Nenhuma categoria de receita encontrada. Crie categorias primeiro.")
            return
        
        categoria = categorias[0]
        
        # Buscar usuário admin
        query_user = select(Usuario).where(Usuario.email == "admin@assistenciaimpacto.com.br")
        result_user = await db.execute(query_user)
        admin = result_user.scalar_one_or_none()
        
        if not admin:
            print("ERROR: Usuário admin não encontrado.")
            return
        
        # Gerar transações para os últimos 7 dias
        hoje = datetime.now()
        transacoes_criadas = []
        
        # Valores realistas para cada dia
        valores_por_dia = [
            (hoje - timedelta(days=6), 1500.00),  # 17/05
            (hoje - timedelta(days=5), 2300.50),  # 18/05
            (hoje - timedelta(days=4), 1800.00),  # 19/05
            (hoje - timedelta(days=3), 3200.75),  # 20/05
            (hoje - timedelta(days=2), 2100.25),  # 21/05
            (hoje - timedelta(days=1), 2800.00),  # 22/05
            (hoje, 1950.50),  # 23/05 (hoje)
        ]
        
        for data, valor in valores_por_dia:
            # Criar 1-2 transações por dia para variação
            num_transacoes = random.randint(1, 2)
            valor_por_transacao = valor / num_transacoes
            
            for i in range(num_transacoes):
                transacao = Transacao(
                    numero_transacao=f"REC-{data.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    tipo=TipoTransacao.RECEITA,
                    categoria_id=categoria.id,
                    descricao=f"Receita de serviços - {data.strftime('%d/%m/%Y')} (DADOS DE TESTE)",
                    valor=valor_por_transacao,
                    data_vencimento=data,
                    data_pagamento=data,
                    status=StatusTransacao.PAGO,
                    forma_pagamento="PIX",
                    criado_por=admin.id,
                    observacoes="DADOS DE TESTE - Gerado automaticamente para popular gráfico de receita"
                )
                
                db.add(transacao)
                transacoes_criadas.append(transacao)
        
        await db.commit()
        
        print(f"✅ Criadas {len(transacoes_criadas)} transações de receita distribuídas nos últimos 7 dias:")
        for t in transacoes_criadas:
            print(f"  - {t.numero_transacao}: R$ {t.valor:.2f} em {t.data_pagamento.strftime('%d/%m/%Y')}")
        
        break

if __name__ == "__main__":
    asyncio.run(seed_transacoes_7_dias())
