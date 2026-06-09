import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import api from '@/lib/api'
import { DataTable } from '@/components/comum/DataTable'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { EstadoVazio } from '@/components/comum/EstadoVazio'
import { ModalConfirmacao } from '@/components/ModalConfirmacao'
import { ErroRede } from '@/components/ErroRede'
import CustomSelect from '@/components/ui/CustomSelect'
import { toast } from 'sonner'
import { schemaOrcamento, OrcamentoFormData } from '@/lib/validacoes'
import { 
  Plus, 
  Search, 
  Edit,
  Trash2,
  FileText,
  Send,
  CheckCircle,
  XCircle,
  DollarSign,
  Calendar,
  X,
  Save,
  Download
} from 'lucide-react'

interface Orcamento {
  id: string
  numero_orcamento: string
  titulo: string
  descricao: string
  status: string
  cliente_id: string
  cliente_nome?: string
  tipo_calculo?: string
  subtotal?: number
  tipo_desconto?: string
  valor_desconto?: number
  taxa_imposto?: number
  valor_total_manual?: number
  total?: number
  valido_ate?: string
  condicoes_pagamento?: string
  garantia?: string
  observacoes_internas?: string
  criado_em?: string
}

interface Cliente {
  id: string
  nome: string
  email?: string
  telefone?: string
}

interface ItemEstoque {
  id: string
  nome: string
  sku: string
  unidade: string
  preco_venda: number
}

interface ItemOrcamentoForm {
  id?: string
  orcamento_id?: string
  item_estoque_id?: string
  descricao: string
  quantidade: number
  unidade: string
  preco_unitario: number
  preco_total: number
}

export function OrcamentosPage() {
  const [busca, setBusca] = useState('')
  const [filtroStatus, setFiltroStatus] = useState<string | null>(null)
  const [modalAberto, setModalAberto] = useState(false)
  const [orcamentoEditando, setOrcamentoEditando] = useState<Orcamento | null>(null)
  const [erro, setErro] = useState('')
  const [modalConfirmacaoAberto, setModalConfirmacaoAberto] = useState(false)
  const [acaoConfirmacao, setAcaoConfirmacao] = useState<'deletar' | 'converter' | null>(null)
  const [orcamentoParaAcao, setOrcamentoParaAcao] = useState<string | null>(null)
  
  // Form state
  const { register, handleSubmit, formState: { errors }, reset, setValue, watch } = useForm<OrcamentoFormData>({
    resolver: zodResolver(schemaOrcamento),
    defaultValues: {
      cliente_id: '',
      titulo: '',
      descricao: '',
      tipo_calculo: 'automatico',
      valido_ate: '',
      condicoes_pagamento: '',
      garantia: '',
      observacoes_internas: '',
      tipo_desconto: '',
      valor_desconto: 0,
      taxa_imposto: 0,
      valor_total_manual: undefined
    }
  })
  const formData = watch()
  const [itens, setItens] = useState<ItemOrcamentoForm[]>([])
  const [itemEditando, setItemEditando] = useState<ItemOrcamentoForm | null>(null)

  const queryClient = useQueryClient()

  const { data: orcamentos, isLoading, isError, refetch } = useQuery<Orcamento[]>({
    queryKey: ['orcamentos', busca, filtroStatus],
    queryFn: async () => {
      const params: any = {}
      if (busca) params.busca = busca
      if (filtroStatus) params.status = filtroStatus
      
      const response = await api.get('/orcamentos', { params })
      return response.data
    }
  })

  const { data: clientes } = useQuery<Cliente[]>({
    queryKey: ['clientes'],
    queryFn: async () => {
      const response = await api.get('/clientes?ativo=true&limit=100')
      return response.data
    }
  })

  const { data: itensEstoque } = useQuery<ItemEstoque[]>({
    queryKey: ['itens-estoque'],
    queryFn: async () => {
      const response = await api.get('/estoque/itens?ativo=true&limit=100')
      return response.data
    }
  })



  const enviarOrcamentoMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/orcamentos/${id}/enviar`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      toast.success('Orçamento enviado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao enviar orçamento. Tente novamente.')
    }
  })

  const aprovarOrcamentoMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/orcamentos/${id}/aprovar`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      toast.success('Orçamento aprovado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao aprovar orçamento. Tente novamente.')
    }
  })

  const rejeitarOrcamentoMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/orcamentos/${id}/rejeitar`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      toast.success('Orçamento rejeitado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao rejeitar orçamento. Tente novamente.')
    }
  })

  const converterOSMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.post(`/orcamentos/${id}/converter`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] })
      toast.success('Orçamento convertido em OS com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao converter orçamento em OS. Tente novamente.')
    }
  })

  const deletarOrcamentoMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/orcamentos/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      toast.success('Orçamento removido com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao deletar orçamento. Tente novamente.')
    }
  })

  const criarOrcamentoMutation = useMutation({
    mutationFn: async (data: any) => {
      return api.post('/orcamentos', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      setModalAberto(false)
      setOrcamentoEditando(null)
      resetForm()
      setErro('')
      toast.success('Orçamento criado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao criar orçamento. Tente novamente.')
    }
  })

  const atualizarOrcamentoMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      return api.put(`/orcamentos/${id}`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      setModalAberto(false)
      setOrcamentoEditando(null)
      resetForm()
      setErro('')
      toast.success('Orçamento atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar orçamento. Tente novamente.')
    }
  })

  const adicionarItemMutation = useMutation({
    mutationFn: async (item: ItemOrcamentoForm) => {
      return api.post(`/orcamentos/${orcamentoEditando?.id}/itens`, item)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orcamentos'] })
      toast.success('Item adicionado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao adicionar item. Tente novamente.')
    }
  })

  const handleCriarOrcamento = () => {
    setOrcamentoEditando(null)
    setErro('')
    resetForm()
    setModalAberto(true)
  }

  const handleEditarOrcamento = async (orcamento: Orcamento) => {
    setOrcamentoEditando(orcamento)
    setValue('cliente_id', orcamento.cliente_id)
    setValue('titulo', orcamento.titulo)
    setValue('descricao', orcamento.descricao)
    setValue('tipo_calculo', (orcamento.tipo_calculo || 'automatico') as 'automatico' | 'manual')
    setValue('valido_ate', orcamento.valido_ate ? orcamento.valido_ate.split('T')[0] : '')
    setValue('condicoes_pagamento', orcamento.condicoes_pagamento || '')
    setValue('garantia', orcamento.garantia || '')
    setValue('observacoes_internas', orcamento.observacoes_internas || '')
    setValue('tipo_desconto', (orcamento.tipo_desconto || '') as '' | 'valor' | 'percentual')
    setValue('valor_desconto', orcamento.valor_desconto || 0)
    setValue('taxa_imposto', orcamento.taxa_imposto || 0)
    setValue('valor_total_manual', orcamento.valor_total_manual || undefined)
    
    // Buscar itens do orçamento
    try {
      const response = await api.get(`/orcamentos/${orcamento.id}/itens`)
      setItens(response.data.map((item: any) => ({
        id: item.id,
        item_estoque_id: item.item_estoque_id,
        descricao: item.descricao,
        quantidade: item.quantidade,
        unidade: item.unidade,
        preco_unitario: item.preco_unitario,
        preco_total: item.preco_total
      })))
    } catch (error) {
      console.error('Erro ao buscar itens:', error)
      setItens([])
    }
    
    setModalAberto(true)
  }

  const handleDeletarOrcamento = (id: string) => {
    setOrcamentoParaAcao(id)
    setAcaoConfirmacao('deletar')
    setModalConfirmacaoAberto(true)
  }

  const handleEnviarOrcamento = (id: string) => {
    enviarOrcamentoMutation.mutate(id)
  }

  const handleAprovarOrcamento = (id: string) => {
    aprovarOrcamentoMutation.mutate(id)
  }

  const handleRejeitarOrcamento = (id: string) => {
    rejeitarOrcamentoMutation.mutate(id)
  }

  const handleConverterOS = (id: string) => {
    setOrcamentoParaAcao(id)
    setAcaoConfirmacao('converter')
    setModalConfirmacaoAberto(true)
  }

  const handleBaixarPDF = async (id: string, numero: string) => {
    try {
      const response = await api.get(`/orcamentos/${id}/pdf`, { 
        responseType: 'blob' 
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `orcamento_${numero}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF baixado com sucesso!');
    } catch (error) {
      toast.error('Erro ao gerar PDF');
    }
  }

  const resetForm = () => {
    reset()
    setItens([])
    setItemEditando(null)
  }

  const calcularTotais = () => {
    if (formData.tipo_calculo === 'manual') {
      return {
        subtotal: 0,
        desconto: 0,
        imposto: 0,
        total: formData.valor_total_manual || 0
      }
    }

    const subtotal = itens.reduce((acc, item) => acc + (item.preco_total || 0), 0)
    let desconto = 0
    if (formData.tipo_desconto === 'percentual' && formData.valor_desconto) {
      desconto = subtotal * (formData.valor_desconto / 100)
    } else {
      desconto = formData.valor_desconto || 0
    }
    const imposto = subtotal * ((formData.taxa_imposto || 0) / 100)
    const total = subtotal - desconto + imposto
    return { subtotal, desconto, imposto, total }
  }


  const handleAdicionarItem = () => {
    if (!itemEditando) return
    
    const novoItem = {
      ...itemEditando,
      preco_total: itemEditando.quantidade * itemEditando.preco_unitario
    }
    
    setItens([...itens, novoItem])
    setItemEditando(null)
  }

  const handleRemoverItem = (index: number) => {
    setItens(itens.filter((_, i) => i !== index))
  }

  const confirmarAcao = () => {
    if (!orcamentoParaAcao) return

    if (acaoConfirmacao === 'deletar') {
      deletarOrcamentoMutation.mutate(orcamentoParaAcao)
    } else if (acaoConfirmacao === 'converter') {
      converterOSMutation.mutate(orcamentoParaAcao)
    }

    setModalConfirmacaoAberto(false)
    setAcaoConfirmacao(null)
    setOrcamentoParaAcao(null)
  }

  const handleSelecionarItemEstoque = (itemEstoqueId: string) => {
    const item = itensEstoque?.find(i => i.id === itemEstoqueId)
    if (item) {
      setItemEditando({
        item_estoque_id: item.id,
        descricao: item.nome,
        quantidade: 1,
        unidade: item.unidade,
        preco_unitario: item.preco_venda,
        preco_total: item.preco_venda
      })
    }
  }

  const onSubmit = async (data: OrcamentoFormData) => {
    try {
      const { subtotal, total } = calcularTotais()

      const orcamentoData = {
        ...data,
        valido_ate: data.valido_ate ? new Date(data.valido_ate).toISOString() : null,
        subtotal,
        total
      }

      if (orcamentoEditando) {
        await atualizarOrcamentoMutation.mutateAsync({ id: orcamentoEditando.id, data: orcamentoData })
      } else {
        const result = await criarOrcamentoMutation.mutateAsync(orcamentoData)

        // Adicionar itens se houver
        if (itens.length > 0 && result.data.id) {
          for (const item of itens) {
            const { orcamento_id, ...itemData } = item
            await adicionarItemMutation.mutateAsync({
              ...itemData
            })
          }
        }
      }
    } catch (error) {
      console.error('Erro ao salvar orçamento:', error)
      toast.error('Erro ao salvar orçamento', {
        description: 'Verifique o console para mais detalhes'
      })
    }
  }

  const { subtotal, desconto, imposto, total } = calcularTotais()


  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      rascunho: 'bg-gray-500/20 text-gray-400',
      enviado: 'bg-blue-500/20 text-blue-400',
      aprovado: 'bg-green-500/20 text-green-400',
      rejeitado: 'bg-red-500/20 text-red-400',
      convertido: 'bg-purple-500/20 text-purple-400',
      expirado: 'bg-orange-500/20 text-orange-400',
    }
    return colors[status] ?? 'bg-gray-500/20 text-gray-400'
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
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Orçamentos</h1>
            <p className="text-muted-foreground">
              Gerencie os orçamentos do sistema
            </p>
          </div>
          <button
            onClick={handleCriarOrcamento}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            data-testid="botao-novo-orcamento"
          >
            <Plus className="w-5 h-5" />
            Novo Orçamento
          </button>
        </div>

        {/* Filtros */}
        <GlassCard className="p-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar por número, título..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <CustomSelect
              value={filtroStatus || ''}
              onChange={(e) => setFiltroStatus(e.target.value || null)}
            >
              <option value="">Todos os Status</option>
              <option value="rascunho">Rascunho</option>
              <option value="enviado">Enviado</option>
              <option value="aprovado">Aprovado</option>
              <option value="rejeitado">Rejeitado</option>
              <option value="convertido">Convertido</option>
              <option value="expirado">Expirado</option>
            </CustomSelect>
          </div>
        </GlassCard>

        {/* Tabela de Orçamentos */}
        <GlassCard className="p-6" data-testid="tabela-orcamentos">
          {isError ? (
            <ErroRede onTentarNovamente={() => refetch()} />
          ) : isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : orcamentos && orcamentos.length > 0 ? (
            <DataTable
              columns={[
                { key: 'numero_orcamento', header: 'Número' },
                { key: 'titulo', header: 'Título' },
                { key: 'status', header: 'Status', render: (_value: any, row: Orcamento) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(row.status || 'rascunho')}`}>
                    {row.status || 'rascunho'}
                  </span>
                )},
                { key: 'total', header: 'Total', render: (_value: any, row: Orcamento) => (
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-muted-foreground" />
                    {row.total !== undefined && row.total !== null ? formatarMoeda(row.total) : '—'}
                  </div>
                )},
                { key: 'valido_ate', header: 'Válido até', render: (_value: any, row: Orcamento) => (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    {row.valido_ate ? formatarData(row.valido_ate) : '—'}
                  </div>
                )},
                { key: 'criado_em', header: 'Criado em', render: (_value: any, row: Orcamento) => row.criado_em ? formatarData(row.criado_em) : '—' },
                { key: 'acoes', header: 'Ações', render: (_value: any, row: Orcamento) => (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEditarOrcamento(row)}
                      className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleBaixarPDF(row.id, row.numero_orcamento)}
                      className="p-2 hover:bg-violet-500/20 rounded-lg transition-colors text-violet-400"
                      title="Baixar PDF"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    {(row.status || 'rascunho') === 'rascunho' && (
                      <button
                        onClick={() => handleEnviarOrcamento(row.id)}
                        className="p-2 hover:bg-blue-500/20 rounded-lg transition-colors text-blue-400"
                        title="Enviar"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    )}
                    {(row.status || 'rascunho') === 'enviado' && (
                      <>
                        <button
                          onClick={() => handleAprovarOrcamento(row.id)}
                          className="p-2 hover:bg-green-500/20 rounded-lg transition-colors text-green-400"
                          title="Aprovar"
                          data-testid="botao-aprovar"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleRejeitarOrcamento(row.id)}
                          className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                          title="Rejeitar"
                          data-testid="botao-rejeitar"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    {(row.status || 'rascunho') === 'aprovado' && (
                      <button
                        onClick={() => handleConverterOS(row.id)}
                        className="p-2 hover:bg-purple-500/20 rounded-lg transition-colors text-purple-400"
                        title="Converter para OS"
                        data-testid="botao-converter-os"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDeletarOrcamento(row.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                      title="Deletar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )},
              ]}
              data={orcamentos}
            />
          ) : (
            <EstadoVazio
              icon={<FileText className="w-12 h-12" />}
              titulo="Nenhum orçamento encontrado"
              descricao="Comece adicionando um novo orçamento ao sistema"
              acao={{
                label: "Adicionar Orçamento",
                onClick: handleCriarOrcamento
              }}
            />
          )}
        </GlassCard>

        {/* Modal de Orçamento */}
        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="modal-novo-orcamento">
            <GlassCard className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  {orcamentoEditando ? 'Editar Orçamento' : 'Novo Orçamento'}
                </h2>
                <button
                  onClick={() => setModalAberto(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Informações Básicas */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Informações Básicas</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="cliente-orcamento" className="block text-sm font-medium mb-2">Cliente *</label>
                      <CustomSelect
                        id="cliente-orcamento"
                        data-testid="campo-cliente"
                        {...register('cliente_id')}
                        disabled={!!orcamentoEditando}
                      >
                        <option value="">Selecione um cliente</option>
                        {clientes?.map(cliente => (
                          <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>
                        ))}
                      </CustomSelect>
                      {errors.cliente_id && (
                        <p className="text-red-400 text-sm mt-1">{errors.cliente_id.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <label htmlFor="tipo-calculo-orcamento" className="block text-sm font-medium mb-2">Tipo de Cálculo</label>
                      <CustomSelect
                        id="tipo-calculo-orcamento"
                        data-testid="campo-tipo-calculo"
                        {...register('tipo_calculo')}
                      >
                        <option value="automatico">Automático (por itens)</option>
                        <option value="manual">Manual (valor direto)</option>
                      </CustomSelect>
                      {errors.tipo_calculo && (
                        <p className="text-red-400 text-sm mt-1">{errors.tipo_calculo.message}</p>
                      )}
                    </div>
                  </div>

                  {formData.tipo_calculo === 'manual' && (
                    <div>
                      <label htmlFor="valor-total-manual-orcamento" className="block text-sm font-medium mb-2">Valor Total Manual *</label>
                      <input
                        id="valor-total-manual-orcamento"
                        type="number"
                        data-testid="campo-valor-total-manual"
                        {...register('valor_total_manual', { valueAsNumber: true })}
                        min="0"
                        step="0.01"
                        placeholder="Digite o valor total do orçamento"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {errors.valor_total_manual && (
                        <p className="text-red-400 text-sm mt-1">{errors.valor_total_manual.message}</p>
                      )}
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="valido-ate-orcamento" className="block text-sm font-medium mb-2">Válido até</label>
                      <input
                        id="valido-ate-orcamento"
                        type="date"
                        {...register('valido_ate')}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {errors.valido_ate && (
                        <p className="text-red-400 text-sm mt-1">{errors.valido_ate.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="titulo-orcamento" className="block text-sm font-medium mb-2">Título *</label>
                    <input
                      id="titulo-orcamento"
                      type="text"
                      {...register('titulo')}
                      placeholder="Ex: Instalação de Ar Condicionado"
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    {errors.titulo && (
                      <p className="text-red-400 text-sm mt-1">{errors.titulo.message}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="descricao-orcamento" className="block text-sm font-medium mb-2">Descrição *</label>
                    <textarea
                      id="descricao-orcamento"
                      data-testid="campo-descricao"
                      {...register('descricao')}
                      placeholder="Descreva os detalhes do orçamento..."
                      rows={4}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    {errors.descricao && (
                      <p className="text-red-400 text-sm mt-1">{errors.descricao.message}</p>
                    )}
                  </div>
                </div>

                {/* Itens do Orçamento */}
                {formData.tipo_calculo === 'automatico' && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Itens do Orçamento</h3>

                    {!orcamentoEditando && (
                    <div className="bg-white/5 p-4 rounded-lg space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label htmlFor="item-estoque-orcamento" className="block text-sm font-medium mb-2">Item do Estoque</label>
                          <CustomSelect
                            id="item-estoque-orcamento"
                            data-testid="campo-item-estoque"
                            value={itemEditando?.item_estoque_id || ''}
                            onChange={(e) => handleSelecionarItemEstoque(e.target.value)}
                          >
                            <option value="">Selecione um item</option>
                            {itensEstoque?.map(item => (
                              <option key={item.id} value={item.id}>{item.nome} - {formatarMoeda(item.preco_venda)}</option>
                            ))}
                          </CustomSelect>
                        </div>
                        
                        <div>
                          <label htmlFor="quantidade-orcamento" className="block text-sm font-medium mb-2">Quantidade</label>
                          <input
                            id="quantidade-orcamento"
                            type="number"
                            data-testid="campo-item-quantidade"
                            value={itemEditando?.quantidade || 1}
                            onChange={(e) => setItemEditando(prev => ({ ...prev!, quantidade: parseFloat(e.target.value) || 0, preco_total: (parseFloat(e.target.value) || 0) * (prev?.preco_unitario || 0) }))}
                            min="0"
                            step="0.01"
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                          />
                        </div>
                        
                        <div className="flex items-end">
                          <button
                            onClick={handleAdicionarItem}
                            disabled={!itemEditando}
                            className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                          >
                            Adicionar Item
                          </button>
                        </div>
                      </div>
                      
                      {itemEditando && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <label htmlFor="descricao-item-orcamento" className="block text-sm font-medium mb-2">Descrição</label>
                            <input
                              id="descricao-item-orcamento"
                              type="text"
                              data-testid="campo-item-descricao"
                              value={itemEditando.descricao}
                              onChange={(e) => setItemEditando(prev => ({ ...prev!, descricao: e.target.value }))}
                              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Unidade</label>
                            <input
                              type="text"
                              value={itemEditando.unidade}
                              onChange={(e) => setItemEditando(prev => ({ ...prev!, unidade: e.target.value }))}
                              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Preço Unitário</label>
                            <input
                              type="number"
                              data-testid="campo-item-valor"
                              value={itemEditando.preco_unitario}
                              onChange={(e) => setItemEditando(prev => ({ ...prev!, preco_unitario: parseFloat(e.target.value) || 0, preco_total: (prev?.quantidade || 0) * (parseFloat(e.target.value) || 0) }))}
                              min="0"
                              step="0.01"
                              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {itens.length > 0 && (
                    <div className="space-y-2">
                      {itens.map((item, index) => (
                        <div key={index} className="flex items-center justify-between bg-white/5 p-3 rounded-lg">
                          <div className="flex-1">
                            <div className="font-medium">{item.descricao}</div>
                            <div className="text-sm text-muted-foreground">
                              {item.quantidade} {item.unidade} x {formatarMoeda(item.preco_unitario)} = {formatarMoeda(item.preco_total)}
                            </div>
                          </div>
                          {!orcamentoEditando && (
                            <button
                              onClick={() => handleRemoverItem(index)}
                              className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                )}

                {/* Descontos e Impostos */}
                {formData.tipo_calculo === 'automatico' && (
                  <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Descontos e Impostos</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Tipo de Desconto</label>
                      <CustomSelect
                        {...register('tipo_desconto')}
                      >
                        <option value="">Nenhum</option>
                        <option value="valor">Valor Fixo</option>
                        <option value="percentual">Percentual</option>
                      </CustomSelect>
                      {errors.tipo_desconto && (
                        <p className="text-red-400 text-sm mt-1">{errors.tipo_desconto.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Valor do Desconto</label>
                      <input
                        type="number"
                        {...register('valor_desconto', { valueAsNumber: true })}
                        min="0"
                        step="0.01"
                        disabled={!formData.tipo_desconto}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                      />
                      {errors.valor_desconto && (
                        <p className="text-red-400 text-sm mt-1">{errors.valor_desconto.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Taxa de Imposto (%)</label>
                      <input
                        type="number"
                        {...register('taxa_imposto', { valueAsNumber: true })}
                        min="0"
                        step="0.01"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {errors.taxa_imposto && (
                        <p className="text-red-400 text-sm mt-1">{errors.taxa_imposto.message}</p>
                      )}
                    </div>
                  </div>
                </div>
                )}

                {/* Informações Adicionais */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Informações Adicionais</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Condições de Pagamento</label>
                      <input
                        type="text"
                        {...register('condicoes_pagamento')}
                        placeholder="Ex: 50% na entrega, 50% após 30 dias"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {errors.condicoes_pagamento && (
                        <p className="text-red-400 text-sm mt-1">{errors.condicoes_pagamento.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Garantia</label>
                      <input
                        type="text"
                        {...register('garantia')}
                        placeholder="Ex: 90 dias"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {errors.garantia && (
                        <p className="text-red-400 text-sm mt-1">{errors.garantia.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Observações Internas</label>
                    <textarea
                      {...register('observacoes_internas')}
                      placeholder="Observações apenas para equipe interna..."
                      rows={3}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    {errors.observacoes_internas && (
                      <p className="text-red-400 text-sm mt-1">{errors.observacoes_internas.message}</p>
                    )}
                  </div>
                </div>

                {/* Resumo de Valores */}
                <div className="bg-white/5 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Subtotal:</span>
                    <span className="font-medium">{formatarMoeda(subtotal)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Desconto:</span>
                    <span className="font-medium text-red-400">- {formatarMoeda(desconto)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Imposto:</span>
                    <span className="font-medium">+ {formatarMoeda(imposto)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold border-t border-white/20 pt-2">
                    <span>Total:</span>
                    <span className="text-primary">{formatarMoeda(total)}</span>
                  </div>
                </div>

                {erro && (
                  <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
                    {erro}
                  </div>
                )}

                {/* Ações */}
                <div className="flex justify-end gap-4">
                  <button
                    onClick={() => setModalAberto(false)}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSubmit(onSubmit)}
                    disabled={criarOrcamentoMutation.isPending || atualizarOrcamentoMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2 disabled:opacity-50"
                    data-testid="botao-salvar"
                  >
                    <Save className="w-4 h-4" />
                    {criarOrcamentoMutation.isPending || atualizarOrcamentoMutation.isPending ? 'Salvando...' : 'Salvar'}
                  </button>
                </div>
              </div>
            </GlassCard>
          </div>
        )}

        {/* Modal de Confirmação */}
        <ModalConfirmacao
          aberto={modalConfirmacaoAberto}
          titulo={acaoConfirmacao === 'deletar' ? 'Deletar Orçamento' : 'Converter em Ordem de Serviço'}
          mensagem={acaoConfirmacao === 'deletar' 
            ? 'Tem certeza que deseja deletar este orçamento? Esta ação não pode ser desfeita.' 
            : 'Deseja converter este orçamento em ordem de serviço?'}
          textoBotaoConfirmar={acaoConfirmacao === 'deletar' ? 'Deletar' : 'Converter'}
          carregando={deletarOrcamentoMutation.isPending || converterOSMutation.isPending}
          onConfirmar={confirmarAcao}
          onCancelar={() => {
            setModalConfirmacaoAberto(false)
            setAcaoConfirmacao(null)
            setOrcamentoParaAcao(null)
          }}
        />
      </div>
    </PageWrapper>
  )
}
