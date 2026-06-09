import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, X, Download, Calendar, DollarSign, FileText, AlertCircle } from 'lucide-react'
import api from '../lib/api'
import { cn } from '../lib/utils'

interface OrcamentoPublico {
  id: string
  numero_orcamento: string
  titulo: string
  descricao: string
  status: string
  valido_ate: string | null
  subtotal: number
  tipo_desconto: string | null
  valor_desconto: number
  taxa_imposto: number
  total: number
  condicoes_pagamento: string | null
  garantia: string | null
  url_pdf: string | null
  enviado_em: string | null
  visualizado_em: string | null
  aprovado_em: string | null
  criado_em: string
  cliente_nome: string
  cliente_email: string
}

interface ItemOrcamento {
  descricao: string
  quantidade: number
  unidade: string
  preco_unitario: number
  preco_total: number
  ordem: number
}

export function PortalOrcamentoPage() {
  const { token } = useParams<{ token: string }>()
  const queryClient = useQueryClient()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [orcamento, setOrcamento] = useState<OrcamentoPublico | null>(null)
  const [itens, setItens] = useState<ItemOrcamento[]>([])

  const { mutate: aprovarOrcamento } = useMutation({
    mutationFn: () => api.post(`/api/portal/orcamento/${token}/aprovar`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamento-publico', token] })
    },
  })

  const { mutate: rejeitarOrcamento } = useMutation({
    mutationFn: () => api.post(`/api/portal/orcamento/${token}/rejeitar`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamento-publico', token] })
    },
  })

  useEffect(() => {
    const carregarOrcamento = async () => {
      try {
        setLoading(true)
        setError(null)

        const [orcamentoRes, itensRes] = await Promise.all([
          api.get<OrcamentoPublico>(`/api/portal/orcamento/${token}`),
          api.get<ItemOrcamento[]>(`/api/portal/orcamento/${token}/itens`),
        ])

        setOrcamento(orcamentoRes.data)
        setItens(itensRes.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erro ao carregar orçamento')
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      carregarOrcamento()
    }
  }, [token])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando orçamento...</p>
        </div>
      </div>
    )
  }

  if (error || !orcamento) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center mb-4">
            <AlertCircle className="w-12 h-12 text-red-500" />
          </div>
          <h2 className="text-xl font-semibold text-center mb-2">Erro</h2>
          <p className="text-gray-600 text-center">{error || 'Orçamento não encontrado'}</p>
        </div>
      </div>
    )
  }

  const statusColors = {
    rascunho: 'bg-gray-100 text-gray-800',
    enviado: 'bg-blue-100 text-blue-800',
    visualizado: 'bg-yellow-100 text-yellow-800',
    aprovado: 'bg-green-100 text-green-800',
    recusado: 'bg-red-100 text-red-800',
    expirado: 'bg-gray-100 text-gray-800',
    convertido: 'bg-purple-100 text-purple-800',
  }

  const podeAprovar = orcamento.status === 'enviado' || orcamento.status === 'visualizado'

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{orcamento.titulo}</h1>
              <p className="text-gray-600 mt-1">Orçamento #{orcamento.numero_orcamento}</p>
              <p className="text-sm text-gray-500 mt-2">
                Criado em {new Date(orcamento.criado_em).toLocaleDateString('pt-BR')}
              </p>
            </div>
            <span className={cn(
              'px-3 py-1 rounded-full text-sm font-medium',
              statusColors[orcamento.status as keyof typeof statusColors]
            )}>
              {orcamento.status.charAt(0).toUpperCase() + orcamento.status.slice(1)}
            </span>
          </div>
        </div>

        {/* Informações do Cliente */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Informações do Cliente
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Nome</p>
              <p className="font-medium">{orcamento.cliente_nome}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium">{orcamento.cliente_email}</p>
            </div>
          </div>
        </div>

        {/* Descrição */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Descrição</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{orcamento.descricao}</p>
        </div>

        {/* Itens do Orçamento */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Itens do Orçamento</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-600">#</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Descrição</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-600">Qtd</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-600">Unidade</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-600">Preço Unit.</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-600">Total</th>
                </tr>
              </thead>
              <tbody>
                {itens.map((item, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{item.ordem + 1}</td>
                    <td className="py-3 px-4">{item.descricao}</td>
                    <td className="py-3 px-4 text-right">{item.quantidade}</td>
                    <td className="py-3 px-4 text-right">{item.unidade}</td>
                    <td className="py-3 px-4 text-right">
                      R$ {item.preco_unitario.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      R$ {item.preco_total.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Resumo Financeiro */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Resumo Financeiro
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">R$ {orcamento.subtotal.toFixed(2)}</span>
            </div>
            {orcamento.valor_desconto > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Desconto ({orcamento.tipo_desconto})</span>
                <span className="font-medium">-R$ {orcamento.valor_desconto.toFixed(2)}</span>
              </div>
            )}
            {orcamento.taxa_imposto > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Impostos</span>
                <span className="font-medium">R$ {orcamento.taxa_imposto.toFixed(2)}</span>
              </div>
            )}
            <div className="border-t pt-3 flex justify-between text-lg font-bold">
              <span>Total</span>
              <span className="text-primary">R$ {orcamento.total.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Condições e Garantia */}
        {(orcamento.condicoes_pagamento || orcamento.garantia) && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Condições e Garantia</h2>
            {orcamento.condicoes_pagamento && (
              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-1">Condições de Pagamento</p>
                <p className="text-gray-700 whitespace-pre-wrap">{orcamento.condicoes_pagamento}</p>
              </div>
            )}
            {orcamento.garantia && (
              <div>
                <p className="text-sm text-gray-500 mb-1">Garantia</p>
                <p className="text-gray-700 whitespace-pre-wrap">{orcamento.garantia}</p>
              </div>
            )}
          </div>
        )}

        {/* Validade */}
        {orcamento.valido_ate && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Validade
            </h2>
            <p className="text-gray-700">
              Este orçamento é válido até {new Date(orcamento.valido_ate).toLocaleDateString('pt-BR')}
            </p>
          </div>
        )}

        {/* Ações */}
        {podeAprovar && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Ações</h2>
            <div className="flex gap-4">
              <button
                onClick={() => aprovarOrcamento()}
                className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors"
              >
                <Check className="w-5 h-5" />
                Aprovar Orçamento
              </button>
              <button
                onClick={() => rejeitarOrcamento()}
                className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white py-3 px-6 rounded-lg hover:bg-red-700 transition-colors"
              >
                <X className="w-5 h-5" />
                Rejeitar Orçamento
              </button>
            </div>
          </div>
        )}

        {/* Download PDF */}
        {orcamento.url_pdf && (
          <div className="mt-6">
            <a
              href={orcamento.url_pdf}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-5 h-5" />
              Baixar PDF
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
