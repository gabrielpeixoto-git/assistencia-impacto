from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DashboardResumo(BaseModel):
    os_hoje: int = 0
    os_semana: int = 0
    receita_mes: float = 0.0
    despesas_mes: float = 0.0
    lucro_mes: float = 0.0
    orcamentos_pendentes: int = 0
    pagamentos_atrasados: int = 0
    itens_estoque_critico: int = 0
    os_por_status: List[Dict[str, Any]] = []
    grafico_receita: List[Dict[str, Any]] = []
    top_clientes: List[Dict[str, Any]] = []
    top_tecnicos: List[Dict[str, Any]] = []
    os_recentes: List[Dict[str, Any]] = []
    agenda_proximos_dias: List[Dict[str, Any]] = []
