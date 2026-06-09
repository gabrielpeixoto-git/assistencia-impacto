from typing import List
import math
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, between
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.schemas.agenda import AgendaCreate, AgendaUpdate, AgendaResponse, AgendaStatusUpdate
from app.models.agenda import Agenda, TipoEvento, StatusEvento
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from datetime import datetime, date
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")

router = APIRouter(prefix="/api/agenda", tags=["agenda"])


def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km entre dois pontos geográficos."""
    R = 6371  # raio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


@router.get("", response_model=List[AgendaResponse])
async def listar_agenda(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tecnico_id: str = None,
    cliente_id: str = None,
    tipo_evento: str = None,
    status: str = None,
    data_inicio: datetime = None,
    data_fim: datetime = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os eventos da agenda com filtros opcionais."""
    from app.models.usuario import Usuario
    from app.models.cliente import Cliente
    
    query = select(Agenda).options(
        selectinload(Agenda.tecnico),
        selectinload(Agenda.cliente)
    )
    
    if tecnico_id:
        query = query.where(Agenda.tecnico_id == tecnico_id)
    
    if cliente_id:
        query = query.where(Agenda.cliente_id == cliente_id)
    
    if tipo_evento:
        query = query.where(Agenda.tipo_evento == tipo_evento)
    
    if status:
        query = query.where(Agenda.status == status)
    
    if data_inicio and data_fim:
        query = query.where(
            between(Agenda.data_hora_inicio, data_inicio, data_fim)
        )
    
    query = query.order_by(Agenda.data_hora_inicio).offset(skip).limit(limit)
    result = await db.execute(query)
    eventos = result.scalars().all()
    
    return eventos


@router.get("/disponibilidade")
async def verificar_disponibilidade(
    tecnico_id: str = Query(..., description="ID do técnico"),
    inicio: datetime = Query(..., description="Data/hora início do período"),
    fim: datetime = Query(..., description="Data/hora fim do período"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Verifica disponibilidade do técnico no período especificado."""
    # Query: buscar agendamentos que se sobrepõem ao intervalo
    # Sobreposição: inicio_existente < fim_novo AND fim_existente > inicio_novo
    conflitos = await db.execute(
        select(Agenda).where(
            and_(
                Agenda.tecnico_id == tecnico_id,
                Agenda.status.notin_([StatusEvento.CANCELADO]),
                Agenda.data_hora_inicio < fim,
                Agenda.data_hora_fim > inicio
            )
        )
    )
    lista = conflitos.scalars().all()
    return {
        "sucesso": True,
        "dados": {
            "disponivel": len(lista) == 0,
            "conflitos": [
                {
                    "id": str(c.id),
                    "titulo": c.titulo,
                    "inicio": c.data_hora_inicio.isoformat(),
                    "fim": c.data_hora_fim.isoformat()
                }
                for c in lista
            ]
        }
    }


@router.get("/mapa")
async def mapa_rotas_dia(
    tecnico_id: str = Query(..., description="ID do técnico"),
    data: date = Query(..., description="Data dos agendamentos"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Retorna mapa de rotas do dia com distância total."""
    # Buscar todos os agendamentos do técnico naquela data com coordenadas
    data_inicio = datetime.combine(data, datetime.min.time())
    data_fim = datetime.combine(data, datetime.max.time())

    query = select(Agenda).where(
        and_(
            Agenda.tecnico_id == tecnico_id,
            between(Agenda.data_hora_inicio, data_inicio, data_fim),
            Agenda.status.notin_([StatusEvento.CANCELADO])
        )
    ).order_by(Agenda.data_hora_inicio)

    result = await db.execute(query)
    eventos = result.scalars().all()

    # Calcular distância total usando haversine entre pontos consecutivos
    distancia_total_km = 0.0
    eventos_com_distancia = []

    for i, evento in enumerate(eventos):
        evento_dict = {
            "id": str(evento.id),
            "titulo": evento.titulo,
            "inicio": evento.data_hora_inicio.isoformat(),
            "fim": evento.data_hora_fim.isoformat(),
            "latitude": evento.latitude,
            "longitude": evento.longitude
        }

        if i > 0 and evento.latitude and evento.longitude:
            evento_anterior = eventos[i - 1]
            if evento_anterior.latitude and evento_anterior.longitude:
                distancia = calcular_distancia_haversine(
                    evento_anterior.latitude, evento_anterior.longitude,
                    evento.latitude, evento.longitude
                )
                distancia_total_km += distancia
                evento_dict["distancia_anterior_km"] = round(distancia, 2)

        eventos_com_distancia.append(evento_dict)

    return {
        "sucesso": True,
        "dados": {
            "data": data.isoformat(),
            "tecnico_id": tecnico_id,
            "distancia_total_km": round(distancia_total_km, 2),
            "eventos": eventos_com_distancia
        }
    }


@router.get("/{evento_id}", response_model=AgendaResponse)
async def obter_evento_agenda(
    evento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém um evento específico por ID."""
    query = select(Agenda).where(Agenda.id == evento_id)
    result = await db.execute(query)
    evento = result.scalar_one_or_none()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return evento


@router.post("", response_model=AgendaResponse, status_code=201)
async def criar_evento_agenda(
    evento_data: AgendaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria um novo evento na agenda."""
    # Converter datetimes para BRT se não tiverem timezone
    data_dict = evento_data.model_dump()
    if data_dict.get("data_hora_inicio") and data_dict["data_hora_inicio"].tzinfo is None:
        data_dict["data_hora_inicio"] = data_dict["data_hora_inicio"].replace(tzinfo=BRT)
    if data_dict.get("data_hora_fim") and data_dict["data_hora_fim"].tzinfo is None:
        data_dict["data_hora_fim"] = data_dict["data_hora_fim"].replace(tzinfo=BRT)
    
    evento = Agenda(**data_dict)
    
    db.add(evento)
    await db.commit()
    await db.refresh(evento)
    
    return evento


@router.put("/{evento_id}", response_model=AgendaResponse)
async def atualizar_evento_agenda(
    evento_id: str,
    evento_data: AgendaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza um evento existente."""
    query = select(Agenda).where(Agenda.id == evento_id)
    result = await db.execute(query)
    evento = result.scalar_one_or_none()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    update_data = evento_data.model_dump(exclude_unset=True)
    # Converter datetimes para BRT se não tiverem timezone
    if update_data.get("data_hora_inicio") and update_data["data_hora_inicio"].tzinfo is None:
        update_data["data_hora_inicio"] = update_data["data_hora_inicio"].replace(tzinfo=BRT)
    if update_data.get("data_hora_fim") and update_data["data_hora_fim"].tzinfo is None:
        update_data["data_hora_fim"] = update_data["data_hora_fim"].replace(tzinfo=BRT)
    
    for field, value in update_data.items():
        setattr(evento, field, value)
    
    await db.commit()
    await db.refresh(evento)
    
    return evento


@router.delete("/{evento_id}", status_code=204)
async def deletar_evento_agenda(
    evento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta um evento."""
    query = select(Agenda).where(Agenda.id == evento_id)
    result = await db.execute(query)
    evento = result.scalar_one_or_none()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    await db.delete(evento)
    await db.commit()
    
    return None


@router.get("/calendario/{ano}/{mes}", response_model=List[AgendaResponse])
async def listar_eventos_mes(
    ano: int,
    mes: int,
    tecnico_id: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os eventos de um mês específico."""
    data_inicio = datetime(ano, mes, 1)
    if mes == 12:
        data_fim = datetime(ano + 1, 1, 1)
    else:
        data_fim = datetime(ano, mes + 1, 1)
    
    query = select(Agenda).where(
        between(Agenda.data_hora_inicio, data_inicio, data_fim)
    )
    
    if tecnico_id:
        query = query.where(Agenda.tecnico_id == tecnico_id)
    
    query = query.order_by(Agenda.data_hora_inicio)
    result = await db.execute(query)
    eventos = result.scalars().all()
    
    return eventos


@router.put("/{evento_id}/status", response_model=AgendaResponse)
async def atualizar_status_evento(
    evento_id: str,
    status_data: AgendaStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza o status de um evento."""
    query = select(Agenda).where(Agenda.id == evento_id)
    result = await db.execute(query)
    evento = result.scalar_one_or_none()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    evento.status = status_data.status
    await db.commit()
    await db.refresh(evento)

    return evento
