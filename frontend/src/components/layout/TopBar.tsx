import { useState, useEffect, useRef } from 'react'
import { useUIStore } from '@/store/ui.store'
import { useAuthStore } from '@/store/auth.store'
import { Search, Bell, User, ChevronDown, Settings, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'

export function TopBar() {
  const { sidebarAberta, abrirCommandPalette } = useUIStore()
  const { usuario, logout } = useAuthStore()
  const [menuNotificacoesAberto, setMenuNotificacoesAberto] = useState(false)
  const [menuUsuarioAberto, setMenuUsuarioAberto] = useState(false)
  const notificacoesRef = useRef<HTMLDivElement>(null)
  const usuarioRef = useRef<HTMLDivElement>(null)

  // Mock de notificações - substituir por dados reais da API
  const [notificacoes, setNotificacoes] = useState([
    { id: 1, titulo: 'Nova ordem de serviço', corpo: 'OS #1234 foi criada', lida: false, criada_em: new Date().toISOString() },
    { id: 2, titulo: 'Orçamento aprovado', corpo: 'Orçamento #567 foi aprovado', lida: true, criada_em: new Date().toISOString() },
  ])

  const naoLidas = notificacoes.filter(n => !n.lida).length

  const handleClickOutside = (event: MouseEvent) => {
    if (notificacoesRef.current && !notificacoesRef.current.contains(event.target as Node)) {
      setMenuNotificacoesAberto(false)
    }
    if (usuarioRef.current && !usuarioRef.current.contains(event.target as Node)) {
      setMenuUsuarioAberto(false)
    }
  }

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const marcarComoLida = (id: number) => {
    setNotificacoes(prev => prev.map(n => n.id === id ? { ...n, lida: true } : n))
  }

  const marcarTodasComoLidas = () => {
    setNotificacoes(prev => prev.map(n => ({ ...n, lida: true })))
  }

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={abrirCommandPalette}
          className={cn(
            'flex items-center gap-3 px-4 py-2 bg-[var(--input)] border border-[var(--border)] rounded-lg',
            'hover:bg-[var(--hover-bg)] transition-colors cursor-pointer',
            'w-64 transition-all',
            sidebarAberta && 'w-96'
          )}
        >
          <Search className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Buscar...</span>
          <kbd className="ml-auto hidden md:flex items-center gap-1 px-2 py-1 text-xs text-muted-foreground bg-[var(--hover-bg)] rounded">
            <span>⌘</span><span>K</span>
          </kbd>
        </button>
      </div>

      <div className="flex items-center gap-4">
        {/* Notificações */}
        <div className="relative" ref={notificacoesRef}>
          <button
            data-testid="sino-notificacoes"
            onClick={() => setMenuNotificacoesAberto(!menuNotificacoesAberto)}
            className="relative p-2 rounded-lg hover:bg-[var(--hover-bg)] transition-colors"
          >
            <Bell className="w-5 h-5" />
            {naoLidas > 0 && (
              <span data-testid="badge-nao-lidas" className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
            )}
          </button>

          {/* Dropdown de Notificações */}
          {menuNotificacoesAberto && (
            <div data-testid="dropdown-notificacoes" className="absolute right-0 top-12 w-80 bg-card border border-border rounded-lg shadow-lg z-50">
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Notificações</h3>
                  {naoLidas > 0 && (
                    <button
                      data-testid="btn-marcar-todas-lidas"
                      onClick={() => marcarTodasComoLidas()}
                      className="text-xs text-primary hover:underline"
                    >
                      Marcar todas como lidas
                    </button>
                  )}
                </div>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notificacoes.length === 0 ? (
                  <div className="p-4 text-center text-muted-foreground text-sm">
                    Nenhuma notificação
                  </div>
                ) : (
                  notificacoes.map((notificacao) => (
                    <div
                      key={notificacao.id}
                      data-testid={`notificacao-item-${notificacao.id}`}
                      onClick={() => {
                        marcarComoLida(notificacao.id)
                        setMenuNotificacoesAberto(false)
                      }}
                      className={cn(
                        'p-4 border-b border-border cursor-pointer hover:bg-[var(--hover-bg)] transition-colors',
                        !notificacao.lida && 'bg-primary/5'
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className={cn(
                          'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                          notificacao.lida ? 'bg-muted' : 'bg-primary'
                        )} />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm">{notificacao.titulo}</p>
                          <p className="text-xs text-muted-foreground mt-1">{notificacao.corpo}</p>
                          {notificacao.criada_em && (
                            <p className="text-xs text-muted-foreground mt-2">
                              {new Date(notificacao.criada_em).toLocaleDateString('pt-BR')}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Usuário */}
        <div className="relative" ref={usuarioRef}>
          <button
            data-testid="btn-menu-usuario"
            onClick={() => setMenuUsuarioAberto(!menuUsuarioAberto)}
            className="flex items-center gap-3 hover:bg-[var(--hover-bg)] rounded-lg p-2 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="w-4 h-4 text-primary" />
            </div>
            {sidebarAberta && (
              <div className="text-sm flex items-center gap-2">
                <p className="font-medium">{usuario?.nome_completo}</p>
                <ChevronDown className="w-4 h-4" />
              </div>
            )}
          </button>

          {/* Dropdown do Usuário */}
          {menuUsuarioAberto && (
            <div data-testid="dropdown-usuario" className="absolute right-0 top-12 w-48 bg-card border border-border rounded-lg shadow-lg z-50">
              <div className="p-2">
                <button
                  data-testid="btn-configuracoes"
                  onClick={() => {
                    setMenuUsuarioAberto(false)
                    window.location.href = '/configuracoes'
                  }}
                  className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-[var(--hover-bg)] hover:text-foreground transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  Configurações
                </button>
                <button
                  data-testid="btn-logout"
                  onClick={() => {
                    logout()
                    setMenuUsuarioAberto(false)
                    window.location.href = '/login'
                  }}
                  className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-[var(--hover-bg)] hover:text-destructive transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sair
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
