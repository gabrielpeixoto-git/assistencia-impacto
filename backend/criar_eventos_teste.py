import asyncio
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal
from app.models.agenda import Agenda, TipoEvento, StatusEvento
from sqlalchemy import select
import uuid

async def criar_eventos_teste():
    async with AsyncSessionLocal() as db:
        # Buscar usuário admin para usar como técnico
        from app.models.usuario import Usuario
        result = await db.execute(select(Usuario).where(Usuario.email == "admin@assistenciaimpacto.com.br"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Usuário admin não encontrado")
            return
        
        # Criar eventos de teste
        eventos = [
            {
                "titulo": "Manutenção Ar Condicionado",
                "tecnico_id": admin.id,
                "cliente_id": None,
                "data_hora_inicio": datetime.now() + timedelta(hours=2),
                "data_hora_fim": datetime.now() + timedelta(hours=4),
                "tipo_evento": TipoEvento.SERVICO,
                "endereco": "Rua das Flores, 123",
                "observacoes": "Levar ferramentas específicas",
                "cor": "#3b82f6"
            },
            {
                "titulo": "Reunião com Cliente",
                "tecnico_id": admin.id,
                "cliente_id": None,
                "data_hora_inicio": datetime.now() + timedelta(days=1, hours=10),
                "data_hora_fim": datetime.now() + timedelta(days=1, hours=11),
                "tipo_evento": TipoEvento.REUNIAO,
                "endereco": "Av. Paulista, 1000",
                "observacoes": "Apresentação de proposta",
                "cor": "#10b981"
            },
            {
                "titulo": "Instalação Elétrica",
                "tecnico_id": admin.id,
                "cliente_id": None,
                "data_hora_inicio": datetime.now() + timedelta(days=2, hours=9),
                "data_hora_fim": datetime.now() + timedelta(days=2, hours=17),
                "tipo_evento": TipoEvento.SERVICO,
                "endereco": "Rua Augusta, 500",
                "observacoes": "Instalação completa",
                "cor": "#f59e0b"
            },
            {
                "titulo": "Manutenção Preventiva",
                "tecnico_id": admin.id,
                "cliente_id": None,
                "data_hora_inicio": datetime.now() + timedelta(days=3, hours=14),
                "data_hora_fim": datetime.now() + timedelta(days=3, hours=16),
                "tipo_evento": TipoEvento.MANUTENCAO,
                "endereco": "Rua Consolação, 200",
                "observacoes": "Verificação geral",
                "cor": "#ef4444"
            },
            {
                "titulo": "Férias",
                "tecnico_id": admin.id,
                "cliente_id": None,
                "data_hora_inicio": datetime.now() + timedelta(days=5),
                "data_hora_fim": datetime.now() + timedelta(days=10),
                "tipo_evento": TipoEvento.INDISPONIVEL,
                "endereco": None,
                "observacoes": "Férias programadas",
                "cor": "#8b5cf6"
            }
        ]
        
        for evento_data in eventos:
            evento = Agenda(
                id=str(uuid.uuid4()),
                **evento_data,
                status=StatusEvento.AGENDADO,
                lembrete_enviado=False
            )
            db.add(evento)
        
        await db.commit()
        print(f"{len(eventos)} eventos de teste criados com sucesso")

if __name__ == "__main__":
    asyncio.run(criar_eventos_teste())
