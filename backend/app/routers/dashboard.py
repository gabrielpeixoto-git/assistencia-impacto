from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Date, text
from app.database import get_db
from app.schemas.dashboard import DashboardResumo
from app.dependencies import get_usuario_atual, get_redis
from app.models.usuario import Usuario
from app.models.ordem_servico import OrdemServico, StatusOS
from app.models.orcamento import Orcamento, StatusOrcamento
from app.models.cliente import Cliente
from app.models.financeiro import Transacao, TipoTransacao, StatusTransacao
from app.models.agenda import Agenda
from app.models.estoque import ItemEstoque
from datetime import datetime, timedelta, UTC, date as date_type
from redis.asyncio import Redis
import json

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/resumo", response_model=DashboardResumo)
async def dashboard_resumo(
    periodo: str = Query(None, description="Período: hoje, semana, mes, trimestre, ano"),
    data_inicio: datetime = Query(None, description="Data início para filtro customizado"),
    data_fim: datetime = Query(None, description="Data fim para filtro customizado"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual),
    redis: Redis = Depends(get_redis)
):
    """Retorna resumo geral do dashboard com cache Redis (TTL=300s)."""
    # Gerar chave de cache baseada nos parâmetros
    cache_key = f"dashboard:resumo:{periodo}:{data_inicio}:{data_fim}:{current_user.id}"
    cached = await redis.get(cache_key)
    if cached:
        return DashboardResumo.model_validate_json(cached)
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    
    # Determinar período de filtro
    if data_inicio and data_fim:
        filtro_inicio = data_inicio
        filtro_fim = data_fim
    elif periodo == "hoje":
        filtro_inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "semana":
        filtro_inicio = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "mes":
        filtro_inicio = inicio_mes.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "trimestre":
        trimestre_atual = (hoje.month - 1) // 3
        inicio_trimestre = datetime(hoje.year, trimestre_atual * 3 + 1, 1)
        filtro_inicio = inicio_trimestre.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif periodo == "ano":
        inicio_ano = datetime(hoje.year, 1, 1)
        filtro_inicio = inicio_ano.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Padrão: mês atual
        filtro_inicio = inicio_mes.replace(hour=0, minute=0, second=0, microsecond=0)
        filtro_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    
    # Ordens de serviço hoje
    query_os_hoje = select(func.count(OrdemServico.id)).where(
        func.date(OrdemServico.criado_em) == func.date(hoje)
    )
    result_os_hoje = await db.execute(query_os_hoje)
    os_hoje = result_os_hoje.scalar() or 0
    
    # Ordens de serviço esta semana
    query_os_semana = select(func.count(OrdemServico.id)).where(
        func.date(OrdemServico.criado_em) >= func.date(inicio_semana)
    )
    result_os_semana = await db.execute(query_os_semana)
    os_semana = result_os_semana.scalar() or 0
    
    # ---------- RECEITA/DESPESAS DO MÊS (raw SQL para evitar datetime/date mismatch) ----------
    hoje_date = hoje.date() if hasattr(hoje, 'date') else hoje
    inicio_mes = date_type(hoje_date.year, hoje_date.month, 1)
    
    # Raw SQL para totais do mês
    sql_totais = text("""
        SELECT 
            SUM(CASE WHEN tipo::text = 'receita' AND status::text = 'pago' THEN valor ELSE 0 END) as receita_mes,
            SUM(CASE WHEN tipo::text = 'despesa' AND status::text = 'pago' THEN valor ELSE 0 END) as despesas_mes
        FROM transacoes
        WHERE 
            data_pagamento IS NOT NULL
            AND DATE(data_pagamento AT TIME ZONE 'UTC') >= :inicio
            AND DATE(data_pagamento AT TIME ZONE 'UTC') <= :fim
    """)
    
    result_totais = await db.execute(
        sql_totais, 
        {"inicio": inicio_mes, "fim": hoje_date}
    )
    row_totais = result_totais.fetchone()
    receita_mes = float(row_totais.receita_mes or 0)
    despesas_mes = float(row_totais.despesas_mes or 0)
    
    # Lucro do mês
    lucro_mes = receita_mes - despesas_mes
    
    # Orçamentos pendentes
    query_orcamentos_pendentes = select(func.count(Orcamento.id)).where(
        Orcamento.status == StatusOrcamento.ENVIADO
    )
    result_orcamentos_pendentes = await db.execute(query_orcamentos_pendentes)
    orcamentos_pendentes = result_orcamentos_pendentes.scalar() or 0
    
    # Pagamentos atrasados
    query_pagamentos_atrasados = select(func.count(Transacao.id)).where(
        and_(
            Transacao.status == StatusTransacao.atrasado
        )
    )
    result_pagamentos_atrasados = await db.execute(query_pagamentos_atrasados)
    pagamentos_atrasados = result_pagamentos_atrasados.scalar() or 0
    
    # Itens de estoque crítico
    query_estoque_critico = select(func.count(ItemEstoque.id)).where(
        and_(
            ItemEstoque.ativo == True,
            ItemEstoque.estoque_atual <= ItemEstoque.estoque_minimo
        )
    )
    result_estoque_critico = await db.execute(query_estoque_critico)
    itens_estoque_critico = result_estoque_critico.scalar() or 0
    
    # Ordens de serviço por status (filtrado por período)
    query_os_por_status = select(
        OrdemServico.status,
        func.count(OrdemServico.id)
    ).where(
        and_(
            OrdemServico.criado_em >= filtro_inicio,
            OrdemServico.criado_em <= filtro_fim
        )
    ).group_by(OrdemServico.status)
    result_os_por_status = await db.execute(query_os_por_status)
    os_por_status = [
        {"status": status, "quantidade": count}
        for status, count in result_os_por_status.all()
    ]
    
    # Gráfico de receita e despesas (baseado no período selecionado)
    dias_grafico = 7
    if periodo == "hoje":
        dias_grafico = 1
    elif periodo == "semana":
        dias_grafico = 7
    elif periodo == "mes":
        dias_grafico = 30
    elif periodo == "trimestre":
        dias_grafico = 90
    elif periodo == "ano":
        dias_grafico = 365
    
    data_inicio_grafico = filtro_inicio
    
    # ---------- GRAFICO RECEITA (raw SQL para evitar datetime/date mismatch) ----------
    # Converter para date objects para o SQL
    inicio_chart = filtro_inicio.date() if hasattr(filtro_inicio, 'date') else filtro_inicio
    fim_chart = filtro_fim.date() if hasattr(filtro_fim, 'date') else filtro_fim
    
    # Raw SQL query - bypasses all ORM enum and timezone issues
    sql_grafico = text("""
        SELECT 
            DATE(data_pagamento AT TIME ZONE 'UTC') as dia,
            SUM(CASE WHEN tipo::text = 'receita' THEN valor ELSE 0 END) as total_receita,
            SUM(CASE WHEN tipo::text = 'despesa' THEN valor ELSE 0 END) as total_despesas
        FROM transacoes
        WHERE 
            status::text = 'pago'
            AND data_pagamento IS NOT NULL
            AND DATE(data_pagamento AT TIME ZONE 'UTC') >= :inicio
            AND DATE(data_pagamento AT TIME ZONE 'UTC') <= :fim
        GROUP BY DATE(data_pagamento AT TIME ZONE 'UTC')
        ORDER BY dia ASC
    """)
    
    result_grafico = await db.execute(
        sql_grafico,
        {"inicio": inicio_chart, "fim": fim_chart}
    )
    rows_grafico = result_grafico.fetchall()
    
    # Build lookup dict - key is date object from raw SQL (guaranteed to be date type)
    receita_map = {}
    despesas_map = {}
    for row in rows_grafico:
        dia = row.dia  # raw SQL returns date object directly
        if isinstance(dia, str):
            # Safety: parse string if needed
            from datetime import datetime as dt_type
            dia = dt_type.strptime(dia[:10], "%Y-%m-%d").date()
        receita_map[dia] = float(row.total_receita or 0)
        despesas_map[dia] = float(row.total_despesas or 0)
    
    # Criar lista com todos os dias (incluindo dias sem receita/despesas)
    grafico_receita = []
    delta = (fim_chart - inicio_chart).days
    if delta > dias_grafico:
        delta = dias_grafico
    
    # Usar os últimos 'delta' dias até hoje
    inicio_iteracao = fim_chart - timedelta(days=delta)
    
    for i in range(delta + 1):
        dia = inicio_iteracao + timedelta(days=i)
        grafico_receita.append({
            "data": dia.strftime("%d/%m"),
            "receita": round(receita_map.get(dia, 0.0), 2),
            "despesas": round(despesas_map.get(dia, 0.0), 2)
        })
    
    # Top clientes (por valor total de ordens de serviço no período)
    query_top_clientes = select(
        Cliente.id,
        Cliente.nome,
        func.sum(OrdemServico.valor_final).label("total")
    ).join(
        OrdemServico, Cliente.id == OrdemServico.cliente_id
    ).where(
        and_(
            OrdemServico.criado_em >= filtro_inicio,
            OrdemServico.criado_em <= filtro_fim
        )
    ).group_by(
        Cliente.id, Cliente.nome
    ).order_by(
        func.sum(OrdemServico.valor_final).desc()
    ).limit(5)
    result_top_clientes = await db.execute(query_top_clientes)
    top_clientes = [
        {"id": id, "nome": nome, "total": total}
        for id, nome, total in result_top_clientes.all()
    ]
    
    # Top técnicos (por número de ordens de serviço concluídas no período)
    query_top_tecnicos = select(
        OrdemServico.tecnico_id,
        Usuario.nome_completo,
        func.count(OrdemServico.id).label("quantidade")
    ).join(
        Usuario, OrdemServico.tecnico_id == Usuario.id
    ).where(
        and_(
            OrdemServico.status == StatusOS.CONCLUIDA,
            OrdemServico.criado_em >= filtro_inicio,
            OrdemServico.criado_em <= filtro_fim
        )
    ).group_by(
        OrdemServico.tecnico_id,
        Usuario.nome_completo
    ).order_by(
        func.count(OrdemServico.id).desc()
    ).limit(5)
    result_top_tecnicos = await db.execute(query_top_tecnicos)
    top_tecnicos = [
        {"tecnico_id": tecnico_id, "nome": nome_completo, "quantidade": quantidade}
        for tecnico_id, nome_completo, quantidade in result_top_tecnicos.all()
    ]
    
    # Ordens de serviço recentes
    query_os_recentes = select(OrdemServico).where(
        OrdemServico.status.in_([StatusOS.PENDENTE, StatusOS.EM_ANDAMENTO])
    ).order_by(
        OrdemServico.criado_em.desc()
    ).limit(5)
    result_os_recentes = await db.execute(query_os_recentes)
    os_recentes = [
        {
            "id": os.id,
            "numero_os": os.numero_os,
            "titulo": os.titulo,
            "status": os.status,
            "prioridade": os.prioridade,
            "cliente_id": os.cliente_id,
            "tecnico_id": os.tecnico_id,
            "criado_em": os.criado_em
        }
        for os in result_os_recentes.scalars().all()
    ]
    
    # Agenda próximos dias
    query_agenda = select(Agenda).where(
        and_(
            Agenda.data_hora_inicio >= hoje,
            Agenda.data_hora_inicio <= hoje + timedelta(days=7)
        )
    ).order_by(
        Agenda.data_hora_inicio
    ).limit(10)
    result_agenda = await db.execute(query_agenda)
    agenda_proximos_dias = [
        {
            "id": a.id,
            "titulo": a.titulo,
            "data_hora_inicio": a.data_hora_inicio,
            "data_hora_fim": a.data_hora_fim,
            "tipo_evento": a.tipo_evento,
            "status": a.status,
            "tecnico_id": a.tecnico_id,
            "cliente_id": a.cliente_id
        }
        for a in result_agenda.scalars().all()
    ]
    
    resultado = DashboardResumo(
        os_hoje=os_hoje,
        os_semana=os_semana,
        receita_mes=receita_mes,
        despesas_mes=despesas_mes,
        lucro_mes=lucro_mes,
        orcamentos_pendentes=orcamentos_pendentes,
        pagamentos_atrasados=pagamentos_atrasados,
        itens_estoque_critico=itens_estoque_critico,
        os_por_status=os_por_status,
        grafico_receita=grafico_receita,
        top_clientes=top_clientes,
        top_tecnicos=top_tecnicos,
        os_recentes=os_recentes,
        agenda_proximos_dias=agenda_proximos_dias
    )

    # Salvar no cache com TTL=300 (5 minutos)
    await redis.setex(cache_key, 300, resultado.model_dump_json())

    return resultado
