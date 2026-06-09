from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, EnderecoClienteCreate
from app.schemas.ordem_servico import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    ItemOrdemServicoCreate, FotoOrdemServicoCreate, ChecklistOrdemServicoCreate
)
from app.schemas.orcamento import OrcamentoCreate, OrcamentoUpdate, OrcamentoResponse, ItemOrcamentoCreate
from app.schemas.agenda import AgendaCreate, AgendaUpdate, AgendaResponse
from app.schemas.financeiro import TransacaoCreate, TransacaoUpdate, TransacaoResponse, CategoriaFinanceiraCreate
from app.schemas.estoque import (
    ItemEstoqueCreate, ItemEstoqueUpdate, ItemEstoqueResponse,
    MovimentacaoEstoqueCreate, CategoriaEstoqueCreate
)
from app.schemas.dashboard import DashboardResumo

__all__ = [
    "UsuarioCreate", "UsuarioUpdate", "UsuarioResponse", "UsuarioLogin",
    "ClienteCreate", "ClienteUpdate", "ClienteResponse", "EnderecoClienteCreate",
    "OrdemServicoCreate", "OrdemServicoUpdate", "OrdemServicoResponse",
    "ItemOrdemServicoCreate", "FotoOrdemServicoCreate", "ChecklistOrdemServicoCreate",
    "OrcamentoCreate", "OrcamentoUpdate", "OrcamentoResponse", "ItemOrcamentoCreate",
    "AgendaCreate", "AgendaUpdate", "AgendaResponse",
    "TransacaoCreate", "TransacaoUpdate", "TransacaoResponse", "CategoriaFinanceiraCreate",
    "ItemEstoqueCreate", "ItemEstoqueUpdate", "ItemEstoqueResponse",
    "MovimentacaoEstoqueCreate", "CategoriaEstoqueCreate",
    "DashboardResumo",
]
