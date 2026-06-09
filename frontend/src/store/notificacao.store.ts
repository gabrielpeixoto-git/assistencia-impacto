import { create } from 'zustand'

interface Notificacao {
  id: string
  titulo: string
  corpo: string
  tipo: 'info' | 'sucesso' | 'aviso' | 'erro' | 'lembrete'
  lida: boolean
  url_acao?: string
  criada_em?: string
}

interface NotificacaoState {
  notificacoes: Notificacao[]
  naoLidas: number
  adicionarNotificacao: (notificacao: Omit<Notificacao, 'lida'>) => void
  marcarComoLida: (id: string) => void
  marcarTodasComoLidas: () => void
}

export const useNotificacaoStore = create<NotificacaoState>((set: any) => ({
  notificacoes: [],
  naoLidas: 0,
  adicionarNotificacao: (notificacao: any) =>
    set((state: any) => ({
      notificacoes: [{ ...notificacao, lida: false }, ...state.notificacoes],
      naoLidas: state.naoLidas + 1,
    })),
  marcarComoLida: (id: any) =>
    set((state: any) => ({
      notificacoes: state.notificacoes.map((n: any) =>
        n.id === id ? { ...n, lida: true } : n
      ),
      naoLidas: Math.max(0, state.naoLidas - 1),
    })),
  marcarTodasComoLidas: () =>
    set((state: any) => ({
      notificacoes: state.notificacoes.map((n: any) => ({ ...n, lida: true })),
      naoLidas: 0,
    })),
}))
