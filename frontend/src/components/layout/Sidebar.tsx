import { Link, useLocation } from 'react-router-dom'
import { useUIStore } from '@/store/ui.store'
import { useAuthStore } from '@/store/auth.store'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  ClipboardList,
  FileText,
  Calendar,
  Users,
  DollarSign,
  Package,
  Users as UsersIcon,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Zap,
  ArrowRightLeft,
} from 'lucide-react'

const navegacao = [
  {
    grupo: 'VISÃO GERAL',
    itens: [
      { nome: 'Dashboard', icone: LayoutDashboard, caminho: '/', testid: 'nav-dashboard' },
    ],
  },
  {
    grupo: 'OPERAÇÕES',
    itens: [
      { nome: 'Ordens de Serviço', icone: ClipboardList, caminho: '/ordens-servico', testid: 'nav-ordens-servico' },
      { nome: 'Orçamentos', icone: FileText, caminho: '/orcamentos', testid: 'nav-orcamentos' },
      { nome: 'Agenda', icone: Calendar, caminho: '/agenda', testid: 'nav-agenda' },
      { nome: 'Clientes', icone: Users, caminho: '/clientes', testid: 'nav-clientes' },
    ],
  },
  {
    grupo: 'FINANCEIRO',
    itens: [
      { nome: 'Visão Financeira', icone: DollarSign, caminho: '/financeiro', testid: 'nav-financeiro' },
      { nome: 'Transações', icone: ArrowRightLeft, caminho: '/transacoes', testid: 'nav-transacoes' },
    ],
  },
  {
    grupo: 'RECURSOS',
    itens: [
      { nome: 'Estoque', icone: Package, caminho: '/estoque', testid: 'nav-estoque' },
      { nome: 'Equipe', icone: UsersIcon, caminho: '/equipe', testid: 'nav-equipe' },
    ],
  },
  {
    grupo: 'ANÁLISE',
    itens: [
      { nome: 'Relatórios', icone: BarChart3, caminho: '/relatorios', testid: 'nav-relatorios' },
    ],
  },
  {
    grupo: 'SISTEMA',
    itens: [
      { nome: 'Configurações', icone: Settings, caminho: '/configuracoes', testid: 'nav-configuracoes' },
    ],
  },
]

export function Sidebar() {
  const { sidebarAberta, toggleSidebar } = useUIStore()
  const { usuario, logout } = useAuthStore()
  const location = useLocation()

  // Filtrar itens de navegação baseado no perfil
  const filtrarNavegacao = () => {
    if (!usuario) return navegacao

    const perfil = usuario.perfil

    return navegacao.map(grupo => ({
      ...grupo,
      itens: grupo.itens.filter(item => {
        // Financeiro: apenas admin e gerente
        if (item.testid === 'nav-financeiro' || item.testid === 'nav-transacoes') {
          return perfil === 'admin' || perfil === 'gerente'
        }
        // Relatórios: apenas admin e gerente
        if (item.testid === 'nav-relatorios') {
          return perfil === 'admin' || perfil === 'gerente'
        }
        // Configurações: apenas admin
        if (item.testid === 'nav-configuracoes') {
          return perfil === 'admin'
        }
        return true
      })
    })).filter(grupo => grupo.itens.length > 0)
  }

  const navegacaoFiltrada = filtrarNavegacao()

  return (
    <aside
      data-testid="sidebar"
      className={cn(
        'fixed left-0 top-0 h-screen bg-card border-r border-border transition-all duration-300 z-50',
        sidebarAberta ? 'w-64' : 'w-20'
      )}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            {sidebarAberta && (
              <div className="flex-1">
                <h1 className="font-bold text-lg gradient-text">
                  Assistência Impacto
                </h1>
              </div>
            )}
            <button
              onClick={toggleSidebar}
              className="p-1 rounded hover:bg-[var(--hover-bg)] transition-colors"
            >
              {sidebarAberta ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Navegação */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-6">
          {navegacaoFiltrada.map((grupo) => (
            <div key={grupo.grupo}>
              {sidebarAberta && (
                <p className="text-xs font-semibold text-muted-foreground mb-2 px-2">
                  {grupo.grupo}
                </p>
              )}
              <div className="space-y-1">
                {grupo.itens.map((item) => {
                  const Icon = item.icone
                  const ativo = location.pathname === item.caminho
                  return (
                    <Link
                      key={item.nome}
                      to={item.caminho}
                      data-testid={item.testid}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
                        ativo
                          ? 'bg-primary/10 text-primary border-l-2 border-primary'
                          : 'text-muted-foreground hover:bg-[var(--hover-bg-subtle)] hover:text-foreground'
                      )}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      {sidebarAberta && <span className="flex-1">{item.nome}</span>}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Usuário */}
        <div className="p-4 border-t border-border">
          {sidebarAberta && usuario ? (
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="font-semibold text-primary">
                  {usuario.nome_completo
                    .split(' ')
                    .map((n) => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2)}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">
                  {usuario.nome_completo}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {usuario.email}
                </p>
              </div>
            </div>
          ) : (
            <div className="w-10 h-10 mx-auto rounded-full bg-primary/20 flex items-center justify-center mb-3">
              <span className="font-semibold text-primary">
                {usuario?.nome_completo
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2)}
              </span>
            </div>
          )}
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-muted-foreground hover:bg-[var(--hover-bg-subtle)] hover:text-destructive transition-colors"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {sidebarAberta && <span>Sair</span>}
          </button>
        </div>
      </div>
    </aside>
  )
}
