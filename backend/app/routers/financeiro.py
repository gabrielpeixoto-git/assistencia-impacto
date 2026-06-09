from typing import List
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, between, func, text
from app.database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.financeiro import (
    TransacaoCreate, TransacaoUpdate, TransacaoResponse, CategoriaFinanceiraCreate
)
from app.models.financeiro import Transacao, CategoriaFinanceira, TipoTransacao, StatusTransacao
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from app.models.ordem_servico import OrdemServico
from app.core.permissoes import verificar_permissao, Perfil
from datetime import datetime, UTC, date, timedelta, date as date_type
from loguru import logger

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/financeiro", tags=["financeiro"])


def gerar_numero_transacao():
    """Gera um número de transação único."""
    from datetime import datetime
    ano = datetime.now().year
    mes = datetime.now().month
    return f"TRX{ano}{mes:02d}"


def calcular_intervalo_periodo(periodo: str, de: date = None, ate: date = None):
    """Calcula o intervalo de datas baseado no período."""
    hoje = date.today()
    if periodo == "hoje":
        return hoje, hoje
    elif periodo == "semana":
        inicio = hoje - timedelta(days=hoje.weekday())
        return inicio, hoje
    elif periodo == "mes":
        return hoje.replace(day=1), hoje
    elif periodo == "trimestre":
        mes_inicio = ((hoje.month - 1) // 3) * 3 + 1
        return hoje.replace(month=mes_inicio, day=1), hoje
    elif periodo == "ano":
        return hoje.replace(month=1, day=1), hoje
    elif periodo == "personalizado" and de and ate:
        return de, ate
    else:
        return hoje.replace(day=1), hoje  # default: mês atual


@router.get("/transacoes", response_model=List[TransacaoResponse])
async def listar_transacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tipo: str = None,
    status: str = None,
    categoria_id: str = None,
    cliente_id: str = None,
    data_inicio: datetime = None,
    data_fim: datetime = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as transações com filtros opcionais."""
    query = select(Transacao)
    
    if tipo:
        query = query.where(Transacao.tipo == tipo)
    
    if status:
        query = query.where(Transacao.status == status)
    
    if categoria_id:
        query = query.where(Transacao.categoria_id == categoria_id)
    
    if cliente_id:
        query = query.where(Transacao.cliente_id == cliente_id)
    
    if data_inicio and data_fim:
        query = query.where(
            between(Transacao.data_vencimento, data_inicio, data_fim)
        )
    
    query = query.order_by(Transacao.data_vencimento.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    transacoes = result.scalars().all()
    
    return transacoes


@router.get("/transacoes/{transacao_id}", response_model=TransacaoResponse)
async def obter_transacao(
    transacao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém uma transação específica por ID."""
    query = select(Transacao).where(Transacao.id == transacao_id)
    result = await db.execute(query)
    transacao = result.scalar_one_or_none()
    
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    return transacao


@router.post("/transacoes", response_model=TransacaoResponse, status_code=201)
@limiter.limit("20/minute")
async def criar_transacao(
    transacao_data: TransacaoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova transação."""
    # Validação RBAC: apenas admin e gerente podem criar transações
    if not verificar_permissao(current_user.perfil, "financeiro.criar"):
        raise HTTPException(status_code=403, detail="Permissão insuficiente para criar transações")

    try:
        # Gerar número de transação único
        numero_transacao = gerar_numero_transacao()

        # Verificar se já existe transação com este número
        query = select(Transacao).where(Transacao.numero_transacao == numero_transacao)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            # Adicionar sufixo se já existir
            contador = 1
            while True:
                numero_transacao = f"{gerar_numero_transacao()}-{contador}"
                query = select(Transacao).where(Transacao.numero_transacao == numero_transacao)
                result = await db.execute(query)
                if not result.scalar_one_or_none():
                    break
                contador += 1

        # Vincular transação a OS se ordem_servico_id fornecido
        transacao_dict = transacao_data.model_dump()
        if transacao_dict.get("ordem_servico_id"):
            query_os = select(OrdemServico).where(OrdemServico.id == transacao_dict["ordem_servico_id"])
            result_os = await db.execute(query_os)
            os = result_os.scalar_one_or_none()
            if not os:
                raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
            # Preencher cliente_id automaticamente da OS
            if not transacao_dict.get("cliente_id"):
                transacao_dict["cliente_id"] = os.cliente_id
            # Descrição default se não fornecida
            if not transacao_dict.get("descricao"):
                transacao_dict["descricao"] = f"OS #{os.numero_os}"

        transacao = Transacao(
            **transacao_dict,
            numero_transacao=numero_transacao,
            criado_por=current_user.id
        )

        db.add(transacao)
        await db.commit()
        await db.refresh(transacao)

        logger.info(f"Transação {transacao.numero_transacao} (ID: {transacao.id}) criada por {current_user.email}")
        return transacao
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar transação: {str(e)}")
        raise


@router.put("/transacoes/{transacao_id}", response_model=TransacaoResponse)
async def atualizar_transacao(
    transacao_id: str,
    transacao_data: TransacaoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza uma transação existente."""
    # Validação RBAC: apenas admin e gerente podem editar transações
    if not verificar_permissao(current_user.perfil, "financeiro.editar"):
        raise HTTPException(status_code=403, detail="Permissão insuficiente para editar transações")

    try:
        query = select(Transacao).where(Transacao.id == transacao_id)
        result = await db.execute(query)
        transacao = result.scalar_one_or_none()

        if not transacao:
            logger.warning(f"Transação {transacao_id} não encontrada para atualização por {current_user.email}")
            raise HTTPException(status_code=404, detail="Transação não encontrada")

        update_data = transacao_data.model_dump(exclude_unset=True)

        # Se status mudou para pago, registrar data de pagamento
        if "status" in update_data and update_data["status"] == StatusTransacao.pago and not transacao.data_pagamento:
            update_data["data_pagamento"] = datetime.now(UTC)
            # Se transação tem ordem_servico_id, atualizar status_pagamento da OS
            if transacao.ordem_servico_id:
                query_os = select(OrdemServico).where(OrdemServico.id == transacao.ordem_servico_id)
                result_os = await db.execute(query_os)
                os = result_os.scalar_one_or_none()
                if os:
                    os.status_pagamento = "pago"
                    logger.info(f"OS #{os.numero_os} marcada como paga devido ao pagamento da transação {transacao.numero_transacao}")

        for field, value in update_data.items():
            setattr(transacao, field, value)

        await db.commit()
        await db.refresh(transacao)

        logger.info(f"Transação {transacao.numero_transacao} (ID: {transacao_id}) atualizada por {current_user.email}")
        return transacao
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar transação {transacao_id}: {str(e)}")
        raise


@router.delete("/transacoes/{transacao_id}", status_code=204)
async def deletar_transacao(
    transacao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta uma transação."""
    # Validação RBAC: apenas admin e gerente podem deletar transações
    if not verificar_permissao(current_user.perfil, "financeiro.deletar"):
        raise HTTPException(status_code=403, detail="Permissão insuficiente para deletar transações")

    try:
        query = select(Transacao).where(Transacao.id == transacao_id)
        result = await db.execute(query)
        transacao = result.scalar_one_or_none()

        if not transacao:
            logger.warning(f"Transação {transacao_id} não encontrada para deleção por {current_user.email}")
            raise HTTPException(status_code=404, detail="Transação não encontrada")

        await db.delete(transacao)
        await db.commit()

        logger.info(f"Transação {transacao.numero_transacao} (ID: {transacao_id}) deletada por {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar transação {transacao_id}: {str(e)}")
        raise


@router.get("/categorias", response_model=List[dict])
async def listar_categorias_financeiras(
    tipo: str = None,
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as categorias financeiras."""
    query = select(CategoriaFinanceira)
    
    if tipo:
        query = query.where(CategoriaFinanceira.tipo == tipo)
    
    if ativo is not None:
        query = query.where(CategoriaFinanceira.ativo == ativo)
    
    query = query.order_by(CategoriaFinanceira.nome)
    result = await db.execute(query)
    categorias = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "tipo": c.tipo,
            "cor": c.cor,
            "icone": c.icone,
            "ativo": c.ativo
        }
        for c in categorias
    ]


@router.post("/categorias", response_model=dict, status_code=201)
async def criar_categoria_financeira(
    categoria_data: CategoriaFinanceiraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria uma nova categoria financeira."""
    # Verificar se já existe categoria com este nome
    query = select(CategoriaFinanceira).where(CategoriaFinanceira.nome == categoria_data.nome)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe")
    
    categoria = CategoriaFinanceira(**categoria_data.model_dump())
    
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    
    return {"id": categoria.id, "mensagem": "Categoria criada com sucesso"}


@router.put("/categorias/{categoria_id}", response_model=dict)
async def atualizar_categoria_financeira(
    categoria_id: str,
    nome: str = None,
    cor: str = None,
    icone: str = None,
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza uma categoria financeira."""
    query = select(CategoriaFinanceira).where(CategoriaFinanceira.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    if nome:
        categoria.nome = nome
    if cor:
        categoria.cor = cor
    if icone:
        categoria.icone = icone
    if ativo is not None:
        categoria.ativo = ativo
    
    await db.commit()
    
    return {"mensagem": "Categoria atualizada com sucesso"}


@router.delete("/categorias/{categoria_id}", status_code=204)
async def deletar_categoria_financeira(
    categoria_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta uma categoria financeira."""
    query = select(CategoriaFinanceira).where(CategoriaFinanceira.id == categoria_id)
    result = await db.execute(query)
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    await db.delete(categoria)
    await db.commit()
    
    return None


@router.get("/resumo", response_model=dict)
async def resumo_financeiro(
    periodo: str = Query("mes", description="Período: hoje, semana, mes, trimestre, ano, personalizado"),
    de: date = Query(None, description="Data início para filtro customizado"),
    ate: date = Query(None, description="Data fim para filtro customizado"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Retorna resumo financeiro com KPIs reais do período."""
    data_inicio, data_fim = calcular_intervalo_periodo(periodo, de, ate)

    # Converter para datetime para comparação com campos datetime
    data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
    data_fim_dt = datetime.combine(data_fim, datetime.max.time())

    # Receita total do período
    query_receita = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.pago,
            between(Transacao.data_pagamento, data_inicio_dt, data_fim_dt)
        )
    )
    result_receita = await db.execute(query_receita)
    receita_total = result_receita.scalar() or 0

    # Despesa total do período
    query_despesa = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.despesa,
            Transacao.status == StatusTransacao.pago,
            between(Transacao.data_pagamento, data_inicio_dt, data_fim_dt)
        )
    )
    result_despesa = await db.execute(query_despesa)
    despesa_total = result_despesa.scalar() or 0

    # Lucro líquido
    lucro_liquido = receita_total - despesa_total

    # Margem de lucro
    margem_lucro = (lucro_liquido / receita_total * 100) if receita_total > 0 else 0.0

    # Contas a receber (receitas pendentes)
    query_contas_receber = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.pendente
        )
    )
    result_contas_receber = await db.execute(query_contas_receber)
    contas_receber = result_contas_receber.scalar() or 0

    # Contas a pagar (despesas pendentes)
    query_contas_pagar = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.despesa,
            Transacao.status == StatusTransacao.pendente
        )
    )
    result_contas_pagar = await db.execute(query_contas_pagar)
    contas_pagar = result_contas_pagar.scalar() or 0

    # Pagamentos atrasados
    query_pagamentos_atrasados = select(func.count(Transacao.id)).where(
        Transacao.status == StatusTransacao.atrasado
    )
    result_pagamentos_atrasados = await db.execute(query_pagamentos_atrasados)
    pagamentos_atrasados = result_pagamentos_atrasados.scalar() or 0

    # Variação vs mês anterior
    data_inicio_mes_anterior = (data_inicio - timedelta(days=32)).replace(day=1)
    data_fim_mes_anterior = data_inicio - timedelta(days=1)

    data_inicio_mes_anterior_dt = datetime.combine(data_inicio_mes_anterior, datetime.min.time())
    data_fim_mes_anterior_dt = datetime.combine(data_fim_mes_anterior, datetime.max.time())

    query_receita_mes_anterior = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.pago,
            between(Transacao.data_pagamento, data_inicio_mes_anterior_dt, data_fim_mes_anterior_dt)
        )
    )
    result_receita_mes_anterior = await db.execute(query_receita_mes_anterior)
    receita_mes_anterior = result_receita_mes_anterior.scalar() or 0

    variacao_mes_anterior = ((receita_total - receita_mes_anterior) / receita_mes_anterior * 100) if receita_mes_anterior > 0 else 0.0

    return {
        "periodo": {
            "tipo": periodo,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat()
        },
        "kpi": {
            "receita_total": receita_total,
            "despesa_total": despesa_total,
            "lucro_liquido": lucro_liquido,
            "margem_lucro": round(margem_lucro, 2),
            "contas_receber": contas_receber,
            "contas_pagar": contas_pagar,
            "pagamentos_atrasados": pagamentos_atrasados,
            "variacao_mes_anterior": round(variacao_mes_anterior, 2)
        }
    }


@router.get("/exportar")
async def exportar_transacoes(
    formato: str = Query("csv", description="Formato de exportação (csv)"),
    periodo: str = Query("mes", description="Período: hoje, semana, mes, trimestre, ano, personalizado"),
    de: date = Query(None, description="Data início para filtro customizado"),
    ate: date = Query(None, description="Data fim para filtro customizado"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Exporta transações em formato CSV."""
    if formato != "csv":
        raise HTTPException(status_code=400, detail="Atualmente apenas formato CSV é suportado")

    data_inicio, data_fim = calcular_intervalo_periodo(periodo, de, ate)
    data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
    data_fim_dt = datetime.combine(data_fim, datetime.max.time())

    # Buscar transações do período
    query = select(Transacao).where(
        between(Transacao.data_vencimento, data_inicio_dt, data_fim_dt)
    ).order_by(Transacao.data_vencimento)

    result = await db.execute(query)
    transacoes = result.scalars().all()

    # Gerar CSV com BOM para Excel brasileiro
    output = io.StringIO()
    output.write('\ufeff')  # BOM para UTF-8
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Data", "Tipo", "Categoria", "Descrição", "Valor (R$)", "Status", "Forma Pagamento"])

    for t in transacoes:
        writer.writerow([
            t.data_vencimento.strftime("%d/%m/%Y"),
            "Receita" if t.tipo == TipoTransacao.receita else "Despesa",
            t.categoria.nome if t.categoria else "",
            t.descricao,
            f"{t.valor:.2f}".replace(".", ","),
            t.status.value,
            t.forma_pagamento or ""
        ])

    output.seek(0)
    filename = f"transacoes_{periodo}_{date.today().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/dashboard", response_model=dict)
async def dashboard_financeiro(
    data_inicio: datetime = None,
    data_fim: datetime = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Retorna resumo financeiro do período."""
    if not data_inicio:
        from datetime import datetime, timedelta
        data_inicio = datetime.now() - timedelta(days=365)
    if not data_fim:
        from datetime import datetime
        data_fim = datetime.now()
    
    # Total de receitas
    query_receitas = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.pago,
            between(Transacao.data_pagamento, data_inicio, data_fim)
        )
    )
    result_receitas = await db.execute(query_receitas)
    total_receitas = result_receitas.scalar() or 0
    
    # Total de despesas
    query_despesas = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.despesa,
            Transacao.status == StatusTransacao.pago,
            between(Transacao.data_pagamento, data_inicio, data_fim)
        )
    )
    result_despesas = await db.execute(query_despesas)
    total_despesas = result_despesas.scalar() or 0
    
    # Receitas pendentes (todas, não filtradas por período)
    query_receitas_pendentes = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.pendente
        )
    )
    result_receitas_pendentes = await db.execute(query_receitas_pendentes)
    receitas_pendentes = result_receitas_pendentes.scalar() or 0
    
    # Despesas pendentes (todas, não filtradas por período)
    query_despesas_pendentes = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.despesa,
            Transacao.status == StatusTransacao.pendente
        )
    )
    result_despesas_pendentes = await db.execute(query_despesas_pendentes)
    despesas_pendentes = result_despesas_pendentes.scalar() or 0
    
    # Receitas atrasadas
    query_receitas_atrasadas = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.receita,
            Transacao.status == StatusTransacao.atrasado,
            Transacao.data_vencimento < datetime.now()
        )
    )
    result_receitas_atrasadas = await db.execute(query_receitas_atrasadas)
    receitas_atrasadas = result_receitas_atrasadas.scalar() or 0
    
    # Despesas atrasadas
    query_despesas_atrasadas = select(func.sum(Transacao.valor)).where(
        and_(
            Transacao.tipo == TipoTransacao.despesa,
            Transacao.status == StatusTransacao.atrasado,
            Transacao.data_vencimento < datetime.now()
        )
    )
    result_despesas_atrasadas = await db.execute(query_despesas_atrasadas)
    despesas_atrasadas = result_despesas_atrasadas.scalar() or 0
    
    return {
        "periodo": {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        },
        "realizado": {
            "receitas": total_receitas,
            "despesas": total_despesas,
            "saldo": total_receitas - total_despesas
        },
        "pendente": {
            "receitas": receitas_pendentes,
            "despesas": despesas_pendentes
        },
        "atrasado": {
            "receitas": receitas_atrasadas,
            "despesas": despesas_atrasadas
        }
    }


@router.get("/grafico/receitas-despesas-mes")
async def grafico_receitas_despesas_mes(
    meses: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados para o gráfico de Receitas x Despesas por Mês usando SQL raw."""
    from datetime import datetime, timedelta
    
    data_inicio = datetime.now() - timedelta(days=meses * 30)
    data_fim = datetime.now()
    
    # Raw SQL para agrupar por mês
    sql = text("""
        SELECT 
            EXTRACT(YEAR FROM DATE(data_pagamento AT TIME ZONE 'UTC')) as ano,
            EXTRACT(MONTH FROM DATE(data_pagamento AT TIME ZONE 'UTC')) as mes,
            SUM(CASE WHEN tipo::text = 'receita' AND status::text = 'pago' THEN valor ELSE 0 END) as total_receita,
            SUM(CASE WHEN tipo::text = 'despesa' AND status::text = 'pago' THEN valor ELSE 0 END) as total_despesa
        FROM transacoes
        WHERE 
            data_pagamento IS NOT NULL
            AND DATE(data_pagamento AT TIME ZONE 'UTC') >= :inicio
            AND DATE(data_pagamento AT TIME ZONE 'UTC') <= :fim
        GROUP BY 
            EXTRACT(YEAR FROM DATE(data_pagamento AT TIME ZONE 'UTC')),
            EXTRACT(MONTH FROM DATE(data_pagamento AT TIME ZONE 'UTC'))
        ORDER BY ano, mes
    """)
    
    result = await db.execute(sql, {"inicio": data_inicio.date(), "fim": data_fim.date()})
    rows = result.fetchall()
    
    # Criar dicionário para facilitar o merge
    receitas_dict = {}
    despesas_dict = {}
    for row in rows:
        chave = f"{int(row.ano)}-{int(row.mes):02d}"
        receitas_dict[chave] = float(row.total_receita or 0)
        despesas_dict[chave] = float(row.total_despesa or 0)
    
    # Gerar lista de todos os meses no período
    dados = []
    data_atual = data_inicio.replace(day=1)
    while data_atual <= data_fim:
        chave = f"{data_atual.year}-{data_atual.month:02d}"
        dados.append({
            "mes": chave,
            "receita": receitas_dict.get(chave, 0),
            "despesa": despesas_dict.get(chave, 0)
        })
        # Avançar para o próximo mês
        if data_atual.month == 12:
            data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
        else:
            data_atual = data_atual.replace(month=data_atual.month + 1)
    
    # Se não houver dados reais ou se todos os valores forem 0, retornar dados de teste para demonstração
    total_receitas = sum(receitas_dict.values())
    total_despesas = sum(despesas_dict.values())
    
    # Verificar se todos os valores são 0
    todos_zeros = all(d['receita'] == 0 and d['despesa'] == 0 for d in dados)
    
    if todos_zeros:
        dados_teste = []
        for i in range(12):
            mes_data = datetime.now() - timedelta(days=(11 - i) * 30)
            chave = f"{mes_data.year}-{mes_data.month:02d}"
            dados_teste.append({
                "mes": chave,
                "receita": 15000 + (i * 2000) + (i % 3) * 3000,
                "despesa": 8000 + (i * 1500) + (i % 2) * 2000
            })
        return dados_teste
    
    return dados


@router.get("/grafico/distribuicao-categoria")
async def grafico_distribuicao_categoria(
    tipo: str = Query(None, description="Tipo de transação (receita/despesa)"),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados para o gráfico de Distribuição por Categoria."""
    from datetime import datetime, timedelta
    
    # Últimos 12 meses
    data_inicio = datetime.now() - timedelta(days=365)
    
    # Query base
    query = select(
        CategoriaFinanceira.nome.label('categoria'),
        CategoriaFinanceira.cor.label('cor'),
        func.sum(Transacao.valor).label('total')
    ).join(
        Transacao, Transacao.categoria_id == CategoriaFinanceira.id
    ).where(
        and_(
            Transacao.status == StatusTransacao.pago,
            Transacao.data_pagamento >= data_inicio
        )
    )
    
    if tipo:
        query = query.where(Transacao.tipo == tipo)
    
    query = query.group_by(
        CategoriaFinanceira.id,
        CategoriaFinanceira.nome,
        CategoriaFinanceira.cor
    ).order_by(
        func.sum(Transacao.valor).desc()
    )
    
    result = await db.execute(query)
    distribuicao = result.all()
    
    dados = [
        {
            "categoria": d.categoria,
            "valor": float(d.total),
            "cor": d.cor
        }
        for d in distribuicao
    ]
    
    # Se não houver dados reais, retornar dados de teste para demonstração
    if not dados or len(dados) == 0:
        dados_teste = [
            {
                "categoria": "Serviços",
                "valor": 54000,
                "cor": "#10B981"
            },
            {
                "categoria": "Salários",
                "valor": 26000,
                "cor": "#3B82F6"
            },
            {
                "categoria": "Aluguel",
                "valor": 15000,
                "cor": "#F59E0B"
            },
            {
                "categoria": "Material",
                "valor": 6000,
                "cor": "#EF4444"
            }
        ]
        return dados_teste
    
    return dados


@router.get("/grafico/tendencia")
async def grafico_tendencia(
    periodo: str = Query("mes", description="Período: semana, mes, trimestre, ano"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Retorna dados para o gráfico de tendência de receita/despesas usando SQL raw."""
    hoje = date_type.today()
    
    # Determinar período
    if periodo == "semana":
        inicio = hoje - timedelta(days=6)
        date_format = "%d/%m"
        delta = timedelta(days=1)
    elif periodo == "mes":
        inicio = date_type(hoje.year, hoje.month, 1)
        date_format = "%d/%m"
        delta = timedelta(days=1)
    elif periodo == "trimestre":
        inicio = hoje - timedelta(days=89)
        date_format = "%d/%m"
        delta = timedelta(days=1)
    else:  # ano
        inicio = date_type(hoje.year, 1, 1)
        date_format = "%b/%y"
        delta = timedelta(days=1)
    
    # Raw SQL query - bypasses all ORM enum and timezone issues
    sql = text("""
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
    
    result = await db.execute(sql, {"inicio": inicio, "fim": hoje})
    rows = result.fetchall()
    
    # Build lookup dict - key is date object from raw SQL (guaranteed to be date type)
    receita_map = {}
    despesas_map = {}
    for row in rows:
        dia = row.dia  # raw SQL returns date object directly
        if isinstance(dia, str):
            # Safety: parse string if needed
            from datetime import datetime as dt_type
            dia = dt_type.strptime(dia[:10], "%Y-%m-%d").date()
        receita_map[dia] = float(row.total_receita or 0)
        despesas_map[dia] = float(row.total_despesas or 0)
    
    # Build complete series with all days (0 for days with no transactions)
    serie = []
    current = inicio
    while current <= hoje:
        serie.append({
            "data": current.strftime(date_format),
            "receita": round(receita_map.get(current, 0.0), 2),
            "despesas": round(despesas_map.get(current, 0.0), 2)
        })
        current += delta
    
    return {
        "sucesso": True,
        "dados": {
            "serie": serie,
            "periodo": periodo
        }
    }
