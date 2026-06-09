from enum import Enum
from typing import List, Set


class Perfil(str, Enum):
    """Perfis de usuário do sistema."""
    ADMIN = "admin"
    GERENTE = "gerente"
    TECNICO = "tecnico"
    VISUALIZADOR = "visualizador"


# Permissões por perfil
PERMISSOES_POR_PERFIL: dict[Perfil, Set[str]] = {
    Perfil.ADMIN: {
        "usuarios.criar", "usuarios.editar", "usuarios.deletar", "usuarios.visualizar",
        "clientes.criar", "clientes.editar", "clientes.deletar", "clientes.visualizar",
        "ordens.criar", "ordens.editar", "ordens.deletar", "ordens.visualizar", "ordens.alterar_status",
        "orcamentos.criar", "orcamentos.editar", "orcamentos.deletar", "orcamentos.visualizar", "orcamentos.aprovar",
        "agenda.criar", "agenda.editar", "agenda.deletar", "agenda.visualizar",
        "financeiro.criar", "financeiro.editar", "financeiro.deletar", "financeiro.visualizar",
        "estoque.criar", "estoque.editar", "estoque.deletar", "estoque.visualizar",
        "equipe.criar", "equipe.editar", "equipe.deletar", "equipe.visualizar",
        "relatorios.visualizar", "configuracoes.editar"
    },
    Perfil.GERENTE: {
        "clientes.criar", "clientes.editar", "clientes.deletar", "clientes.visualizar",
        "ordens.criar", "ordens.editar", "ordens.deletar", "ordens.visualizar", "ordens.alterar_status",
        "orcamentos.criar", "orcamentos.editar", "orcamentos.deletar", "orcamentos.visualizar", "orcamentos.aprovar",
        "agenda.criar", "agenda.editar", "agenda.deletar", "agenda.visualizar",
        "financeiro.criar", "financeiro.editar", "financeiro.deletar", "financeiro.visualizar",
        "estoque.criar", "estoque.editar", "estoque.deletar", "estoque.visualizar",
        "equipe.visualizar",
        "relatorios.visualizar"
    },
    Perfil.TECNICO: {
        "clientes.visualizar",
        "ordens.visualizar", "ordens.alterar_status",
        "agenda.visualizar", "agenda.editar",
        "estoque.visualizar",
        "equipe.visualizar"
    },
    Perfil.VISUALIZADOR: {
        "clientes.visualizar",
        "ordens.visualizar",
        "agenda.visualizar",
        "financeiro.visualizar",
        "estoque.visualizar",
        "equipe.visualizar",
        "relatorios.visualizar"
    }
}


def verificar_permissao(perfil: Perfil, permissao: str) -> bool:
    """Verifica se o perfil tem a permissão especificada."""
    return permissao in PERMISSOES_POR_PERFIL.get(perfil, set())


def verificar_permissoes(perfil: Perfil, permissoes: List[str]) -> bool:
    """Verifica se o perfil tem todas as permissões especificadas."""
    perfil_permissoes = PERMISSOES_POR_PERFIL.get(perfil, set())
    return all(p in perfil_permissoes for p in permissoes)
