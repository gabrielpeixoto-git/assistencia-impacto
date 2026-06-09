import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Star, Calendar, Clock, User, DollarSign, CheckCircle, AlertCircle } from 'lucide-react'
import api from '../lib/api'
import { cn } from '../lib/utils'

interface OSPublica {
  id: string
  numero_os: string
  titulo: string
  descricao: string
  status: string
  prioridade: string
  data_agendada: string | null
  hora_inicio: string | null
  hora_fim: string | null
  data_conclusao: string | null
  duracao_minutos: number | null
  valor_estimado: number
  valor_final: number
  status_pagamento: string
  forma_pagamento: string | null
  criado_em: string
  atualizado_em: string
  cliente_nome: string
  cliente_email: string
  tecnico_nome: string | null
}

interface ItemOS {
  descricao: string
  quantidade: number
  unidade: string
  custo_unitario: number
  custo_total: number
}

interface FotoOS {
  url_arquivo: string
  url_miniatura: string | null
  legenda: string | null
  tipo_foto: string
  tirada_em: string | null
}

interface ChecklistOS {
  descricao: string
  concluido: boolean
  concluido_em: string | null
}

export function PortalOSPage() {
  const { token } = useParams<{ token: string }>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [os, setOS] = useState<OSPublica | null>(null)
  const [itens, setItens] = useState<ItemOS[]>([])
  const [fotos, setFotos] = useState<FotoOS[]>([])
  const [checklist, setChecklist] = useState<ChecklistOS[]>([])
  const [abaAtiva, setAbaAtiva] = useState<'detalhes' | 'itens' | 'fotos' | 'checklist'>('detalhes')
  const [nota, setNota] = useState(0)
  const [comentario, setComentario] = useState('')
  const [avaliando, setAvaliando] = useState(false)

  const { mutate: avaliarOS } = useMutation({
    mutationFn: (dados: { nota: number; comentario: string }) =>
      api.post(`/api/portal/os/${token}/avaliar`, dados),
    onSuccess: () => {
      setAvaliando(false)
      setNota(0)
      setComentario('')
      alert('Avaliação enviada com sucesso!')
    },
    onError: () => {
      setAvaliando(false)
      alert('Erro ao enviar avaliação')
    },
  })

  useEffect(() => {
    const carregarOS = async () => {
      try {
        setLoading(true)
        setError(null)

        const [osRes, itensRes, fotosRes, checklistRes] = await Promise.all([
          api.get<OSPublica>(`/api/portal/os/${token}`),
          api.get<ItemOS[]>(`/api/portal/os/${token}/itens`),
          api.get<FotoOS[]>(`/api/portal/os/${token}/fotos`),
          api.get<ChecklistOS[]>(`/api/portal/os/${token}/checklist`),
        ])

        setOS(osRes.data)
        setItens(itensRes.data)
        setFotos(fotosRes.data)
        setChecklist(checklistRes.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erro ao carregar ordem de serviço')
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      carregarOS()
    }
  }, [token])

  const handleAvaliar = () => {
    if (nota === 0) {
      alert('Por favor, selecione uma nota')
      return
    }
    setAvaliando(true)
    avaliarOS({ nota, comentario })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando ordem de serviço...</p>
        </div>
      </div>
    )
  }

  if (error || !os) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center mb-4">
            <AlertCircle className="w-12 h-12 text-red-500" />
          </div>
          <h2 className="text-xl font-semibold text-center mb-2">Erro</h2>
          <p className="text-gray-600 text-center">{error || 'Ordem de serviço não encontrada'}</p>
        </div>
      </div>
    )
  }

  const statusColors = {
    pendente: 'bg-yellow-100 text-yellow-800',
    confirmada: 'bg-blue-100 text-blue-800',
    em_andamento: 'bg-purple-100 text-purple-800',
    concluida: 'bg-green-100 text-green-800',
    cancelada: 'bg-red-100 text-red-800',
    aguardando: 'bg-gray-100 text-gray-800',
  }

  const prioridadeColors = {
    baixa: 'bg-gray-100 text-gray-800',
    normal: 'bg-blue-100 text-blue-800',
    alta: 'bg-orange-100 text-orange-800',
    urgente: 'bg-red-100 text-red-800',
  }

  const podeAvaliar = os.status === 'concluida'

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{os.titulo}</h1>
              <p className="text-gray-600 mt-1">OS #{os.numero_os}</p>
              <p className="text-sm text-gray-500 mt-2">
                Criada em {new Date(os.criado_em).toLocaleDateString('pt-BR')}
              </p>
            </div>
            <div className="flex gap-2">
              <span className={cn(
                'px-3 py-1 rounded-full text-sm font-medium',
                statusColors[os.status as keyof typeof statusColors]
              )}>
                {os.status.charAt(0).toUpperCase() + os.status.slice(1)}
              </span>
              <span className={cn(
                'px-3 py-1 rounded-full text-sm font-medium',
                prioridadeColors[os.prioridade as keyof typeof prioridadeColors]
              )}>
                {os.prioridade.charAt(0).toUpperCase() + os.prioridade.slice(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Informações do Cliente e Técnico */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Cliente
              </h2>
              <div className="space-y-2">
                <div>
                  <p className="text-sm text-gray-500">Nome</p>
                  <p className="font-medium">{os.cliente_nome}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{os.cliente_email}</p>
                </div>
              </div>
            </div>
            {os.tecnico_nome && (
              <div>
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Técnico Responsável
                </h2>
                <p className="font-medium">{os.tecnico_nome}</p>
              </div>
            )}
          </div>
        </div>

        {/* Abas */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="border-b">
            <nav className="flex gap-4 px-6">
              <button
                onClick={() => setAbaAtiva('detalhes')}
                className={cn(
                  'py-4 px-2 border-b-2 font-medium transition-colors',
                  abaAtiva === 'detalhes'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
              >
                Detalhes
              </button>
              <button
                onClick={() => setAbaAtiva('itens')}
                className={cn(
                  'py-4 px-2 border-b-2 font-medium transition-colors',
                  abaAtiva === 'itens'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
              >
                Itens
              </button>
              <button
                onClick={() => setAbaAtiva('fotos')}
                className={cn(
                  'py-4 px-2 border-b-2 font-medium transition-colors',
                  abaAtiva === 'fotos'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
              >
                Fotos ({fotos.length})
              </button>
              <button
                onClick={() => setAbaAtiva('checklist')}
                className={cn(
                  'py-4 px-2 border-b-2 font-medium transition-colors',
                  abaAtiva === 'checklist'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
              >
                Checklist ({checklist.filter(c => c.concluido).length}/{checklist.length})
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* Aba Detalhes */}
            {abaAtiva === 'detalhes' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Descrição</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{os.descricao}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {os.data_agendada && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                      <Calendar className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-gray-500">Data Agendada</p>
                        <p className="font-medium">
                          {new Date(os.data_agendada).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  )}
                  {os.hora_inicio && os.hora_fim && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                      <Clock className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-gray-500">Horário</p>
                        <p className="font-medium">
                          {os.hora_inicio} - {os.hora_fim}
                        </p>
                      </div>
                    </div>
                  )}
                  {os.duracao_minutos && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                      <Clock className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-gray-500">Duração Estimada</p>
                        <p className="font-medium">{os.duracao_minutos} minutos</p>
                      </div>
                    </div>
                  )}
                  {os.data_conclusao && (
                    <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="text-sm text-gray-500">Concluída em</p>
                        <p className="font-medium">
                          {new Date(os.data_conclusao).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg">
                  <DollarSign className="w-5 h-5 text-primary" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-500">Valor Estimado</p>
                    <p className="font-medium text-lg">R$ {os.valor_estimado.toFixed(2)}</p>
                  </div>
                  {os.valor_final > 0 && (
                    <div className="flex-1">
                      <p className="text-sm text-gray-500">Valor Final</p>
                      <p className="font-medium text-lg">R$ {os.valor_final.toFixed(2)}</p>
                    </div>
                  )}
                </div>

                {os.forma_pagamento && (
                  <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                    <DollarSign className="w-5 h-5 text-primary" />
                    <div>
                      <p className="text-sm text-gray-500">Forma de Pagamento</p>
                      <p className="font-medium capitalize">{os.forma_pagamento.replace('_', ' ')}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Aba Itens */}
            {abaAtiva === 'itens' && (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Descrição</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-600">Qtd</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-600">Unidade</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-600">Custo Unit.</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-600">Custo Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {itens.map((item, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">{item.descricao}</td>
                        <td className="py-3 px-4 text-right">{item.quantidade}</td>
                        <td className="py-3 px-4 text-right">{item.unidade}</td>
                        <td className="py-3 px-4 text-right">
                          R$ {item.custo_unitario.toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-right font-medium">
                          R$ {item.custo_total.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Aba Fotos */}
            {abaAtiva === 'fotos' && (
              <div>
                {fotos.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Nenhuma foto disponível</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {fotos.map((foto, index) => (
                      <div key={index} className="relative">
                        <img
                          src={foto.url_miniatura || foto.url_arquivo}
                          alt={foto.legenda || `Foto ${index + 1}`}
                          className="w-full h-48 object-cover rounded-lg"
                        />
                        {foto.legenda && (
                          <p className="text-sm text-gray-600 mt-2">{foto.legenda}</p>
                        )}
                        {foto.tirada_em && (
                          <p className="text-xs text-gray-500">
                            {new Date(foto.tirada_em).toLocaleDateString('pt-BR')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Aba Checklist */}
            {abaAtiva === 'checklist' && (
              <div>
                {checklist.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Nenhum checklist disponível</p>
                ) : (
                  <div className="space-y-3">
                    {checklist.map((item, index) => (
                      <div
                        key={index}
                        className={cn(
                          'flex items-center gap-3 p-4 rounded-lg',
                          item.concluido ? 'bg-green-50' : 'bg-gray-50'
                        )}
                      >
                        <div className={cn(
                          'w-6 h-6 rounded-full flex items-center justify-center',
                          item.concluido ? 'bg-green-600' : 'bg-gray-300'
                        )}>
                          {item.concluido && <CheckCircle className="w-4 h-4 text-white" />}
                        </div>
                        <div className="flex-1">
                          <p className={cn(
                            'font-medium',
                            item.concluido ? 'text-green-800' : 'text-gray-700'
                          )}>
                            {item.descricao}
                          </p>
                          {item.concluido_em && (
                            <p className="text-xs text-gray-500">
                              Concluído em {new Date(item.concluido_em).toLocaleDateString('pt-BR')}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Avaliação */}
        {podeAvaliar && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Star className="w-5 h-5" />
              Avaliar Serviço
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-2">Nota (1 a 5)</p>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((estrela) => (
                    <button
                      key={estrela}
                      onClick={() => setNota(estrela)}
                      className={cn(
                        'p-2 rounded-lg transition-colors',
                        nota >= estrela
                          ? 'text-yellow-500 bg-yellow-50'
                          : 'text-gray-300 hover:text-yellow-500'
                      )}
                    >
                      <Star className={cn('w-6 h-6', nota >= estrela && 'fill-current')} />
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-2">Comentário (opcional)</p>
                <textarea
                  value={comentario}
                  onChange={(e) => setComentario(e.target.value)}
                  placeholder="Deixe seu comentário sobre o serviço..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                  maxLength={1000}
                />
              </div>
              <button
                onClick={handleAvaliar}
                disabled={avaliando || nota === 0}
                className="w-full bg-primary text-white py-3 px-6 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {avaliando ? 'Enviando...' : 'Enviar Avaliação'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
