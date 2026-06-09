import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { DataTable } from '@/components/comum/DataTable'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { EstadoVazio } from '@/components/comum/EstadoVazio'
import { ModalConfirmacao } from '@/components/ModalConfirmacao'
import { ErroRede } from '@/components/ErroRede'
import CustomSelect from '@/components/ui/CustomSelect'
import { toast } from 'sonner'
import { schemaTransacao } from '@/lib/validacoes'
import { 
  Plus, 
  Search, 
  Edit,
  Trash2,
  DollarSign,
  Calendar,
  Save,
  X
} from 'lucide-react'

interface Transacao {
  id: string
  descricao: string
  tipo: string
  valor: number
  status: string
  data_vencimento: string
  data_pagamento: string
  categoria_id: string
  orcamento_id: string
  ordem_servico_id: string
  criado_em: string
}

interface CategoriaFinanceira {
  id: string
  nome: string
  tipo: string
  cor: string
  icone: string
  ativo: boolean
}

export function TransacoesPage() {
  const [busca, setBusca] = useState('')
  const [filtroTipo, setFiltroTipo] = useState<string | null>(null)
  const [filtroStatus, setFiltroStatus] = useState<string | null>(null)
  const [modalAberto, setModalAberto] = useState(false)
  const [transacaoEditando, setTransacaoEditando] = useState<Transacao | null>(null)
  const [modalConfirmacaoAberto, setModalConfirmacaoAberto] = useState(false)
  const [transacaoParaDeletar, setTransacaoParaDeletar] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    tipo: 'receita',
    categoria_id: '',
    descricao: '',
    valor: '',
    data_vencimento: '',
    forma_pagamento: '',
    conta_bancaria: '',
    cliente_id: '',
    fornecedor_id: '',
    observacoes: '',
    recorrente: false,
    intervalo_recorrencia: ''
  })

  const queryClient = useQueryClient()

  const { data: transacoes, isLoading, isError, error, refetch } = useQuery<Transacao[]>({
    queryKey: ['transacoes', busca, filtroTipo, filtroStatus],
    queryFn: async () => {
      const params: any = {}
      if (busca) params.busca = busca
      if (filtroTipo) params.tipo = filtroTipo
      if (filtroStatus) params.status = filtroStatus
      
      const response = await api.get('/financeiro/transacoes', { params })
      return response.data
    },
    throwOnError: false
  })

  useEffect(() => {
    if (isError) {
      toast.error('Erro ao carregar transações', {
        description: error?.message
      })
    }
  }, [isError, error])

  const { data: categorias, isError: isErrorCategorias, error: errorCategorias } = useQuery<CategoriaFinanceira[]>({
    queryKey: ['categorias-financeiras'],
    queryFn: async () => {
      const response = await api.get('/financeiro/categorias')
      return response.data
    },
    throwOnError: false
  })

  useEffect(() => {
    if (isErrorCategorias) {
      toast.error('Erro ao carregar categorias', {
        description: errorCategorias?.message
      })
    }
  }, [isErrorCategorias, errorCategorias])

  const deletarTransacaoMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/financeiro/transacoes/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transacoes'] })
      toast.success('Transação removida com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao deletar transação')
    }
  })

  const criarTransacaoMutation = useMutation({
    mutationFn: async (transacaoData: any) => {
      return api.post('/financeiro/transacoes', transacaoData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transacoes'] })
      setModalAberto(false)
      setTransacaoEditando(null)
      resetForm()
      toast.success('Transação criada com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao criar transação')
    }
  })

  const atualizarTransacaoMutation = useMutation({
    mutationFn: async ({ id, transacaoData }: { id: string; transacaoData: any }) => {
      return api.put(`/financeiro/transacoes/${id}`, transacaoData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transacoes'] })
      setModalAberto(false)
      setTransacaoEditando(null)
      resetForm()
      toast.success('Transação atualizada com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar transação')
    }
  })

  const resetForm = () => {
    setFormData({
      tipo: 'receita',
      categoria_id: '',
      descricao: '',
      valor: '',
      data_vencimento: '',
      forma_pagamento: '',
      conta_bancaria: '',
      cliente_id: '',
      fornecedor_id: '',
      observacoes: '',
      recorrente: false,
      intervalo_recorrencia: ''
    })
  }

  const handleCriarTransacao = () => {
    setTransacaoEditando(null)
    resetForm()
    setModalAberto(true)
  }

  const handleEditarTransacao = (transacao: Transacao) => {
    setTransacaoEditando(transacao)
    setFormData({
      tipo: transacao.tipo,
      categoria_id: transacao.categoria_id,
      descricao: transacao.descricao,
      valor: transacao.valor.toString(),
      data_vencimento: transacao.data_vencimento.slice(0, 10),
      forma_pagamento: '',
      conta_bancaria: '',
      cliente_id: '',
      fornecedor_id: '',
      observacoes: '',
      recorrente: false,
      intervalo_recorrencia: ''
    })
    setModalAberto(true)
  }

  const handleDeletarTransacao = (id: string) => {
    setTransacaoParaDeletar(id)
    setModalConfirmacaoAberto(true)
  }

  const confirmarDeletarTransacao = () => {
    if (transacaoParaDeletar) {
      deletarTransacaoMutation.mutate(transacaoParaDeletar)
      setModalConfirmacaoAberto(false)
      setTransacaoParaDeletar(null)
    }
  }

  const handleSalvarTransacao = () => {
    const valorNumerico = parseFloat(formData.valor)
    
    const validationResult = schemaTransacao.safeParse({
      tipo: formData.tipo,
      categoria_id: formData.categoria_id,
      descricao: formData.descricao,
      valor: valorNumerico,
      data_vencimento: formData.data_vencimento
    })

    if (!validationResult.success) {
      const erros = validationResult.error.issues.map((e: any) => e.message).join(', ')
      toast.error('Erro de validação', {
        description: erros
      })
      return
    }

    const transacaoData = {
      tipo: formData.tipo,
      categoria_id: formData.categoria_id,
      descricao: formData.descricao,
      valor: valorNumerico,
      data_vencimento: new Date(formData.data_vencimento + 'T00:00:00').toISOString(),
      forma_pagamento: formData.forma_pagamento || undefined,
      conta_bancaria: formData.conta_bancaria || undefined,
      cliente_id: formData.cliente_id || undefined,
      fornecedor_id: formData.fornecedor_id || undefined,
      observacoes: formData.observacoes || undefined,
      recorrente: formData.recorrente,
      intervalo_recorrencia: formData.intervalo_recorrencia || undefined
    }

    if (transacaoEditando) {
      atualizarTransacaoMutation.mutate({ id: transacaoEditando.id, transacaoData })
    } else {
      criarTransacaoMutation.mutate(transacaoData)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pendente: 'bg-yellow-500/20 text-yellow-400',
      pago: 'bg-green-500/20 text-green-400',
      cancelado: 'bg-red-500/20 text-red-400',
      atrasado: 'bg-red-500/20 text-red-400',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400'
  }

  const getTipoColor = (tipo: string) => {
    const colors: Record<string, string> = {
      receita: 'bg-green-500/20 text-green-400',
      despesa: 'bg-red-500/20 text-red-400',
    }
    return colors[tipo] || 'bg-gray-500/20 text-gray-400'
  }

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR')
  }

  return (
    <PageWrapper>
      <div className="space-y-6" data-testid="financeiro-container">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Financeiro</h1>
            <p className="text-muted-foreground">
              Gerencie as transações financeiras
            </p>
          </div>
          <button
            data-testid="btn-nova-transacao"
            onClick={handleCriarTransacao}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nova Transação
          </button>
        </div>

        {/* Filtros */}
        <GlassCard className="p-4" data-testid="card-filtros">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                data-testid="input-busca"
                type="text"
                placeholder="Buscar por descrição..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <CustomSelect
              data-testid="seletor-periodo"
              value={filtroTipo || ''}
              onChange={(e) => setFiltroTipo(e.target.value || null)}
            >
              <option value="">Todos os Tipos</option>
              <option value="mes">Mês Atual</option>
              <option value="receita">Receita</option>
              <option value="despesa">Despesa</option>
            </CustomSelect>
            <CustomSelect
              data-testid="select-status"
              value={filtroStatus || ''}
              onChange={(e) => setFiltroStatus(e.target.value || null)}
            >
              <option value="">Todos os Status</option>
              <option value="pendente">Pendente</option>
              <option value="pago">Pago</option>
              <option value="cancelado">Cancelado</option>
              <option value="atrasado">Atrasado</option>
            </CustomSelect>
            <button
              data-testid="btn-exportar-csv"
              onClick={() => {
                if (!transacoes || transacoes.length === 0) {
                  toast.warning('Não há transações para exportar');
                  return;
                }
                
                const headers = ['ID', 'Descrição', 'Tipo', 'Valor', 'Status', 'Data Vencimento'];
                const rows = transacoes.map(t => [
                  t.id,
                  t.descricao,
                  t.tipo,
                  (t.valor / 100).toFixed(2),
                  t.status,
                  t.data_vencimento
                ]);
                
                const csvContent = [
                  headers.join(','),
                  ...rows.map(row => row.join(','))
                ].join('\n');
                
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `transacoes-${new Date().toISOString().split('T')[0]}.csv`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                toast.success('CSV exportado com sucesso');
              }}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
            >
              Exportar CSV
            </button>
          </div>
        </GlassCard>

        {/* Tabela de Transações */}
        <GlassCard className="p-6" data-testid="card-tabela-transacoes">
          {isError ? (
            <ErroRede onTentarNovamente={() => refetch()} />
          ) : isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : transacoes && transacoes.length > 0 ? (
            <DataTable
              columns={[
                { key: 'descricao', header: 'Descrição' },
                { key: 'tipo', header: 'Tipo', render: (_value: any, row: Transacao) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getTipoColor(row.tipo)}`}>
                    {row.tipo}
                  </span>
                )},
                { key: 'valor', header: 'Valor', render: (_value: any, row: Transacao) => (
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-muted-foreground" />
                    {row.valor !== undefined && row.valor !== null ? formatarMoeda(row.valor) : '—'}
                  </div>
                )},
                { key: 'status', header: 'Status', render: (_value: any, row: Transacao) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(row.status ?? '')}`}>
                    {row.status ?? '—'}
                  </span>
                )},
                { key: 'data_vencimento', header: 'Vencimento', render: (_value: any, row: Transacao) => (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    {formatarData(row.data_vencimento)}
                  </div>
                )},
                { key: 'data_pagamento', header: 'Pagamento', render: (_value: any, row: Transacao) => (
                  row.data_pagamento ? formatarData(row.data_pagamento) : '-'
                )},
                { key: 'criado_em', header: 'Criado em', render: (_value: any, row: Transacao) => formatarData(row.criado_em) },
                { key: 'acoes', header: 'Ações', render: (_value: any, row: Transacao) => (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEditarTransacao(row)}
                      className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeletarTransacao(row.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                      title="Deletar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )},
              ]}
              data={transacoes}
            />
          ) : (
            <EstadoVazio
              icon={<DollarSign className="w-12 h-12" />}
              titulo="Nenhuma transação encontrada"
              descricao="Comece adicionando uma nova transação ao sistema"
              acao={{
                label: "Adicionar Transação",
                onClick: handleCriarTransacao
              }}
            />
          )}
        </GlassCard>

        {/* Modal de Confirmação */}
        <ModalConfirmacao
          aberto={modalConfirmacaoAberto}
          titulo="Deletar Transação"
          mensagem="Tem certeza que deseja deletar esta transação? Esta ação não pode ser desfeita."
          textoBotaoConfirmar="Deletar"
          carregando={deletarTransacaoMutation.isPending}
          onConfirmar={confirmarDeletarTransacao}
          onCancelar={() => {
            setModalConfirmacaoAberto(false)
            setTransacaoParaDeletar(null)
          }}
        />

        {/* Modal de Transação */}
        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" data-testid="modal-transacao">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6" data-testid="modal-titulo">
                {transacaoEditando ? 'Editar Transação' : 'Nova Transação'}
              </h2>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="tipo-transacao" className="block text-sm font-medium mb-2">Tipo *</label>
                    <CustomSelect
                      data-testid="select-tipo-modal"
                      id="tipo-transacao"
                      value={formData.tipo}
                      onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                    >
                      <option value="receita">Receita</option>
                      <option value="despesa">Despesa</option>
                    </CustomSelect>
                  </div>

                  <div>
                    <label htmlFor="categoria-transacao" className="block text-sm font-medium mb-2">Categoria *</label>
                    <CustomSelect
                      data-testid="select-categoria-modal"
                      id="categoria-transacao"
                      value={formData.categoria_id}
                      onChange={(e) => setFormData({ ...formData, categoria_id: e.target.value })}
                    >
                      <option value="">Selecione uma categoria</option>
                      {categorias?.filter(c => c.tipo === formData.tipo && c.ativo).map((categoria) => (
                        <option key={categoria.id} value={categoria.id}>
                          {categoria.nome}
                        </option>
                      ))}
                    </CustomSelect>
                  </div>
                </div>

                <div>
                  <label htmlFor="descricao-transacao" className="block text-sm font-medium mb-2">Descrição *</label>
                  <input
                    data-testid="input-descricao-modal"
                    id="descricao-transacao"
                    type="text"
                    value={formData.descricao}
                    onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Descrição da transação"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="valor-transacao" className="block text-sm font-medium mb-2">Valor *</label>
                    <input
                      data-testid="input-valor-modal"
                      id="valor-transacao"
                      type="text"
                      step="0.01"
                      min="0"
                      value={formData.valor && !isNaN(parseFloat(formData.valor)) 
                        ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(parseFloat(formData.valor))
                        : ''}
                      onChange={(e) => {
                        const valorLimpo = e.target.value.replace(/[^0-9,]/g, '').replace(',', '.')
                        setFormData({ ...formData, valor: valorLimpo ? valorLimpo : '' })
                      }}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="R$ 0,00"
                    />
                  </div>

                  <div>
                    <label htmlFor="data-vencimento-transacao" className="block text-sm font-medium mb-2">Data de Vencimento *</label>
                    <input
                      data-testid="input-data-vencimento-modal"
                      id="data-vencimento-transacao"
                      type="date"
                      value={formData.data_vencimento}
                      onChange={(e) => setFormData({ ...formData, data_vencimento: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="forma-pagamento-transacao" className="block text-sm font-medium mb-2">Forma de Pagamento</label>
                    <input
                      data-testid="input-forma-pagamento-modal"
                      id="forma-pagamento-transacao"
                      type="text"
                      value={formData.forma_pagamento}
                      onChange={(e) => setFormData({ ...formData, forma_pagamento: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Ex: Dinheiro, Cartão, PIX"
                    />
                  </div>

                  <div>
                    <label htmlFor="conta-bancaria-transacao" className="block text-sm font-medium mb-2">Conta Bancária</label>
                    <input
                      data-testid="input-conta-bancaria-modal"
                      id="conta-bancaria-transacao"
                      type="text"
                      value={formData.conta_bancaria}
                      onChange={(e) => setFormData({ ...formData, conta_bancaria: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Ex: Itaú, Nubank"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="observacoes-transacao" className="block text-sm font-medium mb-2">Observações</label>
                  <textarea
                    data-testid="textarea-observacoes-modal"
                    id="observacoes-transacao"
                    value={formData.observacoes}
                    onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
                    placeholder="Observações adicionais"
                    rows={3}
                  />
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      data-testid="checkbox-recorrente-modal"
                      type="checkbox"
                      checked={formData.recorrente}
                      onChange={(e) => setFormData({ ...formData, recorrente: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Transação Recorrente</span>
                  </label>

                  {formData.recorrente && (
                    <div className="flex-1">
                      <CustomSelect
                        data-testid="select-intervalo-recorrencia-modal"
                        value={formData.intervalo_recorrencia}
                        onChange={(e) => setFormData({ ...formData, intervalo_recorrencia: e.target.value })}
                      >
                        <option value="">Selecione o intervalo</option>
                        <option value="mensal">Mensal</option>
                        <option value="semanal">Semanal</option>
                        <option value="quinzenal">Quinzenal</option>
                        <option value="anual">Anual</option>
                      </CustomSelect>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  data-testid="btn-cancelar-modal"
                  onClick={() => setModalAberto(false)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Cancelar
                </button>
                <button
                  data-testid="btn-salvar-modal"
                  onClick={handleSalvarTransacao}
                  disabled={criarTransacaoMutation.isPending || atualizarTransacaoMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {criarTransacaoMutation.isPending || atualizarTransacaoMutation.isPending ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
