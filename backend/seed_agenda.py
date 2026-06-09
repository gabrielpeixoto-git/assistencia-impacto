"""
Seed script para recriar eventos da Agenda com dados corretos.
- Remove todos os eventos existentes
- Cria no máximo 2-3 eventos por técnico por dia
- Todos os eventos com horários realistas (8h–18h)
- Títulos formatados como "Nome do Cliente — Tipo de Serviço"
- Reuniões de equipe apenas às segundas-feiras
- Distribui eventos nas próximas 3 semanas
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Ajustar conforme seu DATABASE_URL
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@banco:5432/assistencia_impacto"

BRT = ZoneInfo("America/Sao_Paulo")

# Buscar IDs reais do banco
QUERY_TECNICOS = "SELECT id, nome_completo FROM usuarios WHERE perfil = 'TECNICO' LIMIT 3"
QUERY_CLIENTES = "SELECT id, nome FROM clientes WHERE ativo = true LIMIT 20"
QUERY_CATEGORIAS = "SELECT id, nome FROM categorias_servico WHERE ativo = true LIMIT 10"

# Cores dos técnicos (ordem: João, Maria, Carlos)
TECH_COLORS = ["#6C63FF", "#00D4FF", "#10B981"]

# Tipos de evento possíveis para serviços
TIPOS_SERVICO_OS = "SERVICO"
TIPOS_REUNIAO = "REUNIAO"

# Horários realistas para eventos de serviço
SERVICE_SLOTS = [
    (8, 0, 10, 0),    # 08:00 – 10:00
    (10, 0, 12, 0),   # 10:00 – 12:00
    (13, 0, 15, 0),   # 13:00 – 15:00
    (15, 0, 17, 0),   # 15:00 – 17:00
]

# Horário de reunião de equipe
REUNIAO_SLOT = (9, 0, 10, 0)


async def seed_agenda():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Buscar dados existentes
        result_tecs = await session.execute(text(QUERY_TECNICOS))
        tecnicos = result_tecs.fetchall()

        result_clientes = await session.execute(text(QUERY_CLIENTES))
        clientes = result_clientes.fetchall()

        result_cats = await session.execute(text(QUERY_CATEGORIAS))
        categorias = result_cats.fetchall()

        if not tecnicos:
            print("ERRO: Nenhum técnico encontrado. Execute o seed principal primeiro.")
            return
        if not clientes:
            print("ERRO: Nenhum cliente encontrado. Execute o seed principal primeiro.")
            return
        if not categorias:
            print("ERRO: Nenhuma categoria encontrada. Execute o seed principal primeiro.")
            return

        print(f"Técnicos encontrados: {len(tecnicos)}")
        print(f"Clientes encontrados: {len(clientes)}")
        print(f"Categorias encontradas: {len(categorias)}")

        # 2. Remover TODOS os eventos existentes
        await session.execute(text("DELETE FROM agenda"))
        await session.commit()
        print("Eventos anteriores removidos.")

        # 3. Calcular range de datas: hoje - 1 semana até hoje + 3 semanas
        hoje = date.today()
        data_inicio = hoje - timedelta(days=7)
        data_fim = hoje + timedelta(days=21)

        eventos_criados = 0
        current_date = data_inicio

        while current_date <= data_fim:
            dia_semana = current_date.weekday()  # 0=Mon ... 6=Sun

            # Pular domingos
            if dia_semana == 6:
                current_date += timedelta(days=1)
                continue

            # Às segundas: criar 1 reunião de equipe (apenas 1, não por técnico)
            if dia_semana == 0:
                h_inicio, m_inicio, h_fim, m_fim = REUNIAO_SLOT
                dt_inicio = datetime(
                    current_date.year, current_date.month, current_date.day,
                    h_inicio, m_inicio, tzinfo=BRT
                )
                dt_fim = datetime(
                    current_date.year, current_date.month, current_date.day,
                    h_fim, m_fim, tzinfo=BRT
                )
                # Reunião atribuída ao primeiro técnico, mas visível a todos
                tecnico_id = str(tecnicos[0][0])
                await session.execute(
                    text("""
                        INSERT INTO agenda 
                          (id, titulo, tecnico_id, data_hora_inicio, data_hora_fim,
                           tipo_evento, status, cor, lembrete_enviado, criado_em)
                        VALUES 
                          (:id, :titulo, :tecnico_id, :inicio, :fim,
                           :tipo, :status, :cor, :lembrete, NOW())
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "titulo": "Reunião de Equipe",
                        "tecnico_id": tecnico_id,
                        "inicio": dt_inicio,
                        "fim": dt_fim,
                        "tipo": "REUNIAO",
                        "status": "AGENDADO",
                        "cor": "#F59E0B",
                        "lembrete": False,
                    }
                )
                eventos_criados += 1

            # Para cada técnico: criar NO MÁXIMO 2 eventos de serviço por dia
            # (dias da semana apenas, não sábados)
            if dia_semana < 5:  # Segunda a Sexta
                for i, tecnico in enumerate(tecnicos):
                    tech_id = str(tecnico[0])
                    tech_color = TECH_COLORS[i % len(TECH_COLORS)]

                    # Selecionar 2 slots aleatórios (mas determinísticos) para este dia/técnico
                    # Usar dia do ano + índice do técnico para determinismo
                    day_of_year = current_date.timetuple().tm_yday
                    slot_indices = [
                        (day_of_year + i * 3) % len(SERVICE_SLOTS),
                        (day_of_year + i * 3 + 2) % len(SERVICE_SLOTS),
                    ]
                    # Garantir slots únicos
                    slot_indices = list(dict.fromkeys(slot_indices))[:2]

                    for j, slot_idx in enumerate(slot_indices):
                        h_inicio, m_inicio, h_fim, m_fim = SERVICE_SLOTS[slot_idx]
                        dt_inicio = datetime(
                            current_date.year, current_date.month, current_date.day,
                            h_inicio, m_inicio, tzinfo=BRT
                        )
                        dt_fim = datetime(
                            current_date.year, current_date.month, current_date.day,
                            h_fim, m_fim, tzinfo=BRT
                        )

                        # Selecionar cliente e categoria de forma determinística
                        cliente_idx = (day_of_year + i + j * 7) % len(clientes)
                        cat_idx = (day_of_year + i * 2 + j) % len(categorias)
                        
                        cliente = clientes[cliente_idx]
                        categoria = categorias[cat_idx]
                        
                        cliente_id = str(cliente[0])
                        cliente_nome = cliente[1]
                        cat_nome = categoria[1]

                        # Título limpo e informativo: "Cliente — Categoria"
                        titulo = f"{cliente_nome} — {cat_nome}"

                        # Status baseado na data
                        if current_date < hoje:
                            status = "CONCLUIDO"
                        elif current_date == hoje:
                            status = "EM_ANDAMENTO" if j == 0 else "CONFIRMADO"
                        else:
                            status = "AGENDADO"

                        await session.execute(
                            text("""
                                INSERT INTO agenda 
                                  (id, titulo, tecnico_id, cliente_id, data_hora_inicio, 
                                   data_hora_fim, tipo_evento, status, cor, lembrete_enviado, criado_em)
                                VALUES 
                                  (:id, :titulo, :tecnico_id, :cliente_id, :inicio, 
                                   :fim, :tipo, :status, :cor, :lembrete, NOW())
                            """),
                            {
                                "id": str(uuid.uuid4()),
                                "titulo": titulo,
                                "tecnico_id": tech_id,
                                "cliente_id": cliente_id,
                                "inicio": dt_inicio,
                                "fim": dt_fim,
                                "tipo": "SERVICO",
                                "status": status,
                                "cor": tech_color,
                                "lembrete": False,
                            }
                        )
                        eventos_criados += 1

            # Sábados: apenas 1 evento por técnico (meio período)
            elif dia_semana == 5:
                for i, tecnico in enumerate(tecnicos):
                    tech_id = str(tecnico[0])
                    tech_color = TECH_COLORS[i % len(TECH_COLORS)]
                    
                    day_of_year = current_date.timetuple().tm_yday
                    cliente_idx = (day_of_year + i * 5) % len(clientes)
                    cat_idx = (day_of_year + i) % len(categorias)
                    
                    cliente = clientes[cliente_idx]
                    categoria = categorias[cat_idx]
                    
                    # Sábado: apenas manhã (8:00–12:00)
                    dt_inicio = datetime(
                        current_date.year, current_date.month, current_date.day,
                        8, 0, tzinfo=BRT
                    )
                    dt_fim = datetime(
                        current_date.year, current_date.month, current_date.day,
                        12, 0, tzinfo=BRT
                    )

                    titulo = f"{cliente[1]} — {categoria[1]}"
                    status = "CONCLUIDO" if current_date < hoje else "AGENDADO"

                    await session.execute(
                        text("""
                            INSERT INTO agenda 
                              (id, titulo, tecnico_id, cliente_id, data_hora_inicio, 
                               data_hora_fim, tipo_evento, status, cor, lembrete_enviado, criado_em)
                            VALUES 
                              (:id, :titulo, :tecnico_id, :cliente_id, :inicio, 
                               :fim, :tipo, :status, :cor, :lembrete, NOW())
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "titulo": titulo,
                            "tecnico_id": tech_id,
                            "cliente_id": str(cliente[0]),
                            "inicio": dt_inicio,
                            "fim": dt_fim,
                            "tipo": "SERVICO",
                            "status": status,
                            "cor": tech_color,
                            "lembrete": False,
                        }
                    )
                    eventos_criados += 1

            await session.commit()
            current_date += timedelta(days=1)

        print(f"✅ Seed da Agenda concluído: {eventos_criados} eventos criados.")
        print("   Máximo de 3 eventos visíveis por dia (2 serviços + 1 reunião às segundas)")
        print("   Horários: 08:00, 10:00, 13:00 ou 15:00")
        print("   Títulos: 'Nome do Cliente — Categoria do Serviço'")


if __name__ == "__main__":
    asyncio.run(seed_agenda())
