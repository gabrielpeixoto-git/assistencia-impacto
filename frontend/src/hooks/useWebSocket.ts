import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/store/auth.store'
import { useNotificacaoStore } from '@/store/notificacao.store'

interface NotificacaoWebSocket {
  type: string
  data: {
    id: string
    titulo: string
    mensagem: string
    tipo: string
    link: string | null
    lida: boolean
    criada_em: string
  }
}

export function useWebSocket() {
  const { token } = useAuthStore()
  const adicionarNotificacao = useNotificacaoStore((state: any) => state.adicionarNotificacao)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    if (!token) {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      return
    }

    const connect = () => {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const wsUrl = `${apiUrl.replace('http', 'ws')}/ws?token=${token}`
      
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          // WebSocket conectado
          
          // Inscrever em notificações
          ws.send(JSON.stringify({
            type: 'subscribe',
            notification_type: 'notificacao'
          }))
        }

        ws.onmessage = (event) => {
          try {
            const message: NotificacaoWebSocket = JSON.parse(event.data)
            
            if (message.type === 'notificacao' && message.data) {
              adicionarNotificacao({
                id: message.data.id,
                titulo: message.data.titulo,
                corpo: message.data.mensagem,
                tipo: message.data.tipo as any,
                url_acao: message.data.link || undefined,
                lida: message.data.lida,
                criada_em: message.data.criada_em
              })
            }
          } catch (error) {
            console.error('Erro ao processar mensagem WebSocket:', error)
          }
        }

        ws.onerror = (error) => {
          console.error('Erro no WebSocket:', error)
        }

        ws.onclose = () => {
          // WebSocket desconectado, tentando reconectar
          
          // Tentar reconectar após 5 segundos
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
          }
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 5000)
        }
      } catch (error) {
        console.error('Erro ao conectar WebSocket:', error)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [token, adicionarNotificacao])

  return wsRef.current
}
