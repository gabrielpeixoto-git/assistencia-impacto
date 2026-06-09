"""
Recria os eventos de agenda com dados corretos.
- Títulos com nome do cliente
- Máx 3 eventos por técnico por dia (realista)
- Cores corretas por técnico
- Horários realistas entre 08:00 e 18:00
"""
import asyncio
import random
import sys
import os
from datetime import datetime, timedelta, date, time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Executar com: docker compose exec backend python scripts/seed_agenda_corrigida.py

async def recriar_agenda():
    from app.database import AsyncSessionLocal
    from app.models.agenda import Agenda, TipoEvento, StatusEvento
    from app.models.usuario import Usuario
    from app.models.cliente import Cliente
    from sqlalchemy import select, delete

    async with AsyncSessionLocal() as db:
        # Buscar técnicos
        result = await db.execute(
            select(Usuario).where(Usuario.perfil == 'TECNICO')
        )
        tecnicos = result.scalars().all()

        # Atualizar cores dos técnicos
        for tecnico in tecnicos:
            nome_lower = tecnico.nome_completo.lower()
            if 'jo' in nome_lower:
                tecnico.cor = '#6C63FF'  # violeta elétrico
            elif 'maria' in nome_lower:
                tecnico.cor = '#00D4FF'  # ciano cyber
            elif 'carlos' in nome_lower:
                tecnico.cor = '#10B981'  # esmeralda
            else:
                tecnico.cor = '#F59E0B'  # âmbar
        await db.commit()

        # Buscar clientes
        result = await db.execute(select(Cliente).limit(20))
        clientes = result.scalars().all()

        # Serviços realistas
        servicos = [
            'Manutenção Hidráulica', 'Reparo Elétrico', 'Pintura Interna',
            'Instalação AC', 'Serviço de Alvenaria', 'Troca de Vidro',
            'Reparo Marcenaria', 'Manutenção Informática', 'Limpeza Geral',
            'Instalação Serralheria', 'Revisão Elétrica', 'Reparo Hidráulico',
        ]

        # Horários de início possíveis (hh:mm)
        horarios = [
            (7, 30), (8, 0), (8, 30), (9, 0), (9, 30),
            (10, 0), (11, 0), (13, 0), (13, 30), (14, 0),
            (14, 30), (15, 0), (15, 30), (16, 0),
        ]

        hoje = date.today()
        novos_eventos = []

        # Para cada dia nos próximos 15 dias úteis
        dias_gerados = 0
        dia_cursor = hoje
        while dias_gerados < 15:
            # Pular fins de semana
            if dia_cursor.weekday() >= 5:
                dia_cursor += timedelta(days=1)
                continue

            # Para cada técnico, criar 2-3 eventos por dia
            for tecnico in tecnicos:
                # 2 ou 3 eventos por técnico por dia
                qtd_eventos = random.choice([2, 2, 3])
                horarios_dia = random.sample(horarios, qtd_eventos)
                horarios_dia.sort()  # Ordenar cronologicamente

                for h_inicio in horarios_dia:
                    cliente = random.choice(clientes)
                    servico = random.choice(servicos)

                    # Calcular horário de fim (1h30 a 3h de duração)
                    duracao_h = random.choice([1, 1, 2, 2, 3])
                    duracao_min = random.choice([0, 30])

                    dt_inicio = datetime.combine(dia_cursor, time(h_inicio[0], h_inicio[1]))
                    dt_fim = dt_inicio + timedelta(hours=duracao_h, minutes=duracao_min)

                    # Título: Nome do cliente - Tipo de Serviço
                    titulo = f"{cliente.nome.split()[0]} {cliente.nome.split()[-1]} — {servico}"

                    # Status baseado na data
                    if dia_cursor < hoje:
                        status = StatusEvento.CONCLUIDO
                    elif dia_cursor == hoje:
                        status = StatusEvento.EM_ANDAMENTO
                    else:
                        status = random.choice([StatusEvento.AGENDADO, StatusEvento.CONFIRMADO])

                    evento = Agenda(
                        titulo=titulo,
                        tecnico_id=tecnico.id,
                        cliente_id=cliente.id,
                        data_hora_inicio=dt_inicio,
                        data_hora_fim=dt_fim,
                        tipo_evento=TipoEvento.SERVICO,
                        status=status,
                        cor=tecnico.cor,  # Usar a cor do técnico
                        observacoes=f"Serviço agendado para {cliente.nome}",
                    )
                    novos_eventos.append(evento)

            # Reunião semanal às segundas
            if dia_cursor.weekday() == 0:  # Segunda-feira
                reuniao = Agenda(
                    titulo='Reunião de Equipe — Planejamento Semanal',
                    tecnico_id=tecnicos[0].id,  # Primeiro técnico como responsável
                    data_hora_inicio=datetime.combine(dia_cursor, time(8, 0)),
                    data_hora_fim=datetime.combine(dia_cursor, time(9, 0)),
                    tipo_evento=TipoEvento.REUNIAO,
                    status=StatusEvento.CONFIRMADO,
                    cor='#F59E0B',  # âmbar para reunião
                    observacoes='Reunião semanal com toda a equipe',
                )
                novos_eventos.append(reuniao)

            dias_gerados += 1
            dia_cursor += timedelta(days=1)

        # Salvar todos os eventos
        db.add_all(novos_eventos)
        await db.commit()
        print(f"✅ {len(novos_eventos)} eventos criados com sucesso!")

asyncio.run(recriar_agenda())
