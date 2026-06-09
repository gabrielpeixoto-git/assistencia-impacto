import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { DataTable } from '@/components/comum/DataTable'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { EstadoVazio } from '@/components/comum/EstadoVazio'
import CustomSelect from '@/components/ui/CustomSelect'
import toast from 'react-hot-toast'
import { 
  Plus, 
  Search, 
  Edit,
  Trash2,
  Wrench,
  Camera,
  CheckSquare,
  X,
  Download
} from 'lucide-react'

interface OrdemServico {
  id: string
  numero_os: string
  titulo: string
  descricao: string
  status: string
  prioridade: string
  cliente_id: string
  tecnico_id: string | null
  tipo_servico_id: string
  valor_estimado: number
  valor_final: number
  data_agendada: string | null
  criado_em: string
}

interface CategoriaServico {
  id: string
  nome: string
  descricao: string | null
  icone: string
  cor: string
}

interface Cliente {
  id: string
  nome: string
  email: string
  telefone: string | null
}

interface Usuario {
  id: string
  nome_completo: string
  email: string
  perfil: string
}

export function OrdensServicoPage() {
  const [busca, setBusca] = useState('')
  const [filtroStatus, setFiltroStatus] = useState<string | null>(null)
  const [filtroPrioridade, setFiltroPrioridade] = useState<string | null>(null)
  const [modalAberto, setModalAberto] = useState(false)
  const [osEditando, setOsEditando] = useState<OrdemServico | null>(null)
  const [modalItensAberto, setModalItensAberto] = useState(false)
  const [osItens, setOsItens] = useState<OrdemServico | null>(null)
  const [itemFormData, setItemFormData] = useState({
    item_estoque_id: '',
    descricao: '',
    quantidade: 1,
    unidade: 'un',
    custo_unitario: 0,
    compra_externa: false
  })
  const [itemErro, setItemErro] = useState('')
  const [modalFotosAberto, setModalFotosAberto] = useState(false)
  const [osFotos, setOsFotos] = useState<OrdemServico | null>(null)
  const [fotoFormData, setFotoFormData] = useState({
    legenda: '',
    tipo_foto: 'outro' as const,
    tirada_em: '',
    url_arquivo: '',
    url_miniatura: ''
  })
  const [fotoErro, setFotoErro] = useState('')
  const [modalChecklistAberto, setModalChecklistAberto] = useState(false)
  const [osChecklist, setOsChecklist] = useState<OrdemServico | null>(null)
  const [checklistFormData, setChecklistFormData] = useState({
    descricao: ''
  })
  const [checklistErro, setChecklistErro] = useState('')
  const [osParaDeletar, setOsParaDeletar] = useState<OrdemServico | null>(null)
  
  // Form data
  const [formData, setFormData] = useState({
    cliente_id: '',
    tecnico_id: '',
    tipo_servico_id: '',
    titulo: '',
    descricao: '',
    prioridade: 'normal',
    valor_estimado: 0,
    data_agendada: '',
    status: 'pendente',
    observacoes_internas: '',
    endereco_id: '',
    forma_pagamento: '',
    emitir_nota: false
  })
  const [erro, setErro] = useState('')

  const resetForm = () => {
    setFormData({
      cliente_id: '',
      tecnico_id: '',
      tipo_servico_id: '',
      titulo: '',
      descricao: '',
      prioridade: 'normal',
      valor_estimado: 0,
      data_agendada: '',
      status: 'pendente',
      observacoes_internas: '',
      endereco_id: '',
      forma_pagamento: '',
      emitir_nota: false
    })
  }

  const queryClient = useQueryClient()

  // Buscar categorias de serviço
  const { data: categoriasServico } = useQuery<CategoriaServico[]>({
    queryKey: ['categorias-servico'],
    queryFn: async () => {
      const response = await api.get('/categorias-servico')
      return response.data
    }
  })

  // Buscar clientes
  const { data: clientes } = useQuery<Cliente[]>({
    queryKey: ['clientes'],
    queryFn: async () => {
      const response = await api.get('/clientes')
      return response.data
    }
  })

  // Buscar técnicos
  const { data: usuarios } = useQuery<Usuario[]>({
    queryKey: ['usuarios'],
    queryFn: async () => {
      const response = await api.get('/usuarios')
      return response.data
    }
  })

  // Buscar itens da OS
  const { data: itensOS, refetch: refetchItens } = useQuery({
    queryKey: ['itens-os', osItens?.id],
    queryFn: async () => {
      if (!osItens) return []
      const response = await api.get(`/ordens-servico/${osItens.id}/itens`)
      return response.data
    },
    enabled: !!osItens
  })

  // Buscar itens de estoque
  const { data: itensEstoque } = useQuery({
    queryKey: ['itens-estoque'],
    queryFn: async () => {
      const response = await api.get('/itens-estoque')
      return response.data
    }
  })

  // Buscar fotos da OS
  const { data: fotosOS, refetch: refetchFotos } = useQuery({
    queryKey: ['fotos-os', osFotos?.id],
    queryFn: async () => {
      if (!osFotos) return []
      const response = await api.get(`/ordens-servico/${osFotos.id}/fotos`)
      return response.data
    },
    enabled: !!osFotos
  })

  // Buscar checklist da OS
  const { data: checklistOS, refetch: refetchChecklist } = useQuery({
    queryKey: ['checklist-os', osChecklist?.id],
    queryFn: async () => {
      if (!osChecklist) return []
      const response = await api.get(`/ordens-servico/${osChecklist.id}/checklist`)
      return response.data
    },
    enabled: !!osChecklist
  })

  const { data: ordens, isLoading } = useQuery<OrdemServico[]>({
    queryKey: ['ordens-servico', busca, filtroStatus, filtroPrioridade],
    queryFn: async () => {
      const params: any = {}
      if (busca) params.busca = busca
      if (filtroStatus) params.status = filtroStatus
      if (filtroPrioridade) params.prioridade = filtroPrioridade
      
      const response = await api.get('/ordens-servico', { params })
      const data = response.data
      // Garantir que os dados sejam válidos
      return Array.isArray(data) ? data.filter((item): item is OrdemServico => item && typeof item === 'object') : []
    }
  })



  const adicionarChecklistMutation = useMutation({
    mutationFn: async (data: any) => {
      if (!osChecklist) throw new Error('OS não selecionada')
      return api.post(`/ordens-servico/${osChecklist.id}/checklist`, data)
    },
    onSuccess: () => {
      refetchChecklist()
      setChecklistFormData({ descricao: '' })
      setChecklistErro('')
    },
    onError: (error: any) => {
      setChecklistErro(extrairMensagemErro(error) || 'Erro ao adicionar item')
    }
  })

  const marcarChecklistMutation = useMutation({
    mutationFn: async ({ osId, checklistId }: { osId: string; checklistId: string }) => {
      return api.put(`/ordens-servico/${osId}/checklist/${checklistId}`)
    },
    onSuccess: () => {
      refetchChecklist()
      toast.success('Checklist atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar checklist. Tente novamente.')
    }
  })

  const adicionarFotoMutation = useMutation({
    mutationFn: async (data: any) => {
      if (!osFotos) throw new Error('OS não selecionada')
      const params = new URLSearchParams()
      params.append('url_arquivo', data.url_arquivo)
      if (data.url_miniatura) params.append('url_miniatura', data.url_miniatura)
      
      return api.post(`/ordens-servico/${osFotos.id}/fotos?${params.toString()}`, {
        legenda: data.legenda,
        tipo_foto: data.tipo_foto,
        tirada_em: data.tirada_em ? new Date(data.tirada_em).toISOString() : null
      })
    },
    onSuccess: () => {
      refetchFotos()
      setFotoFormData({
        legenda: '',
        tipo_foto: 'outro',
        tirada_em: '',
        url_arquivo: '',
        url_miniatura: ''
      })
      setFotoErro('')
    },
    onError: (error: any) => {
      setFotoErro(extrairMensagemErro(error) || 'Erro ao adicionar foto')
    }
  })

  const adicionarItemMutation = useMutation({
    mutationFn: async (itemData: any) => {
      if (!osItens) throw new Error('OS não selecionada')
      return api.post(`/ordens-servico/${osItens.id}/itens`, itemData)
    },
    onSuccess: () => {
      refetchItens()
      setItemFormData({
        item_estoque_id: '',
        descricao: '',
        quantidade: 1,
        unidade: 'un',
        custo_unitario: 0,
        compra_externa: false
      })
      setItemErro('')
    },
    onError: (error: any) => {
      setItemErro(extrairMensagemErro(error) || 'Erro ao adicionar item')
    }
  })

  const deletarOSMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/ordens-servico/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] })
      toast.success('Ordem de serviço removida com sucesso!')
      setOsParaDeletar(null)
    },
    onError: (error: any) => {
      console.error('Erro ao deletar OS:', error)
      toast.error(error.response?.data?.detail || 'Erro ao deletar ordem de serviço')
    }
  })

  const criarOSMutation = useMutation({
    mutationFn: async (osData: any) => {
      return api.post('/ordens-servico', osData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] })
      setModalAberto(false)
      resetForm()
      setErro('')
      toast.success('Ordem de serviço criada com sucesso!')
    },
    onError: (error: any) => {
      setErro(extrairMensagemErro(error) || 'Erro ao criar ordem de serviço')
    }
  })

  const atualizarOSMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      return api.put(`/ordens-servico/${id}`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] })
      setModalAberto(false)
      resetForm()
      setErro('')
      toast.success('Ordem de serviço atualizada com sucesso!')
    },
    onError: (error: any) => {
      setErro(extrairMensagemErro(error) || 'Erro ao atualizar ordem de serviço')
    }
  })

  const handleCriarOS = () => {
    setOsEditando(null)
    setErro('')
    resetForm()
    setErro('')
    setModalAberto(true)
  }

  const handleSubmitOS = (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')

    if (!formData.cliente_id || !formData.tipo_servico_id || !formData.titulo || !formData.descricao) {
      setErro('Preencha todos os campos obrigatórios')
      return
    }

    if (osEditando) {
      // Atualizar OS existente
      const updateData: any = {
        cliente_id: formData.cliente_id,
        tecnico_id: formData.tecnico_id || null,
        tipo_servico_id: formData.tipo_servico_id,
        titulo: formData.titulo,
        descricao: formData.descricao,
        prioridade: formData.prioridade,
        valor_estimado: formData.valor_estimado,
        data_agendada: formData.data_agendada ? new Date(formData.data_agendada).toISOString() : null,
        status: formData.status,
        observacoes_internas: formData.observacoes_internas || null,
        endereco_id: formData.endereco_id || null,
        forma_pagamento: formData.forma_pagamento || null,
        emitir_nota: formData.emitir_nota
      }
      atualizarOSMutation.mutate({ id: osEditando.id, data: updateData })
    } else {
      // Criar nova OS
      const createData = {
        cliente_id: formData.cliente_id,
        tecnico_id: formData.tecnico_id || null,
        tipo_servico_id: formData.tipo_servico_id,
        titulo: formData.titulo,
        descricao: formData.descricao,
        prioridade: formData.prioridade,
        valor_estimado: formData.valor_estimado,
        data_agendada: formData.data_agendada ? new Date(formData.data_agendada).toISOString() : null,
        observacoes_internas: formData.observacoes_internas || null
      }
      criarOSMutation.mutate(createData)
    }
  }

  const handleEditarOS = (os: OrdemServico) => {
    setOsEditando(os)
    setErro('')
    setFormData({
      cliente_id: os.cliente_id,
      tecnico_id: os.tecnico_id || '',
      tipo_servico_id: os.tipo_servico_id,
      titulo: os.titulo,
      descricao: os.descricao,
      prioridade: os.prioridade,
      valor_estimado: os.valor_estimado,
      data_agendada: os.data_agendada ? os.data_agendada.slice(0, 16) : '',
      status: os.status,
      observacoes_internas: '',
      endereco_id: '',
      forma_pagamento: '',
      emitir_nota: false
    })
    setErro('')
    setModalAberto(true)
  }

  const handleDeletarOS = (os: OrdemServico) => {
    setOsParaDeletar(os)
  }

  const confirmarDeletarOS = () => {
    if (osParaDeletar) {
      deletarOSMutation.mutate(osParaDeletar.id)
    }
  }

  const handleGerenciarItens = (os: OrdemServico) => {
    setOsItens(os)
    setItemFormData({
      item_estoque_id: '',
      descricao: '',
      quantidade: 1,
      unidade: 'un',
      custo_unitario: 0,
      compra_externa: false
    })
    setItemErro('')
    setModalItensAberto(true)
  }

  const handleSubmitItem = (e: React.FormEvent) => {
    e.preventDefault()
    setItemErro('')

    if (!itemFormData.descricao || !itemFormData.quantidade || !itemFormData.custo_unitario) {
      setItemErro('Preencha todos os campos obrigatórios')
      return
    }

    adicionarItemMutation.mutate(itemFormData)
  }

  const handleGerenciarFotos = (os: OrdemServico) => {
    setOsFotos(os)
    setFotoFormData({
      legenda: '',
      tipo_foto: 'outro',
      tirada_em: '',
      url_arquivo: '',
      url_miniatura: ''
    })
    setFotoErro('')
    setModalFotosAberto(true)
  }

  const handleSubmitFoto = (e: React.FormEvent) => {
    e.preventDefault()
    setFotoErro('')

    if (!fotoFormData.url_arquivo) {
      setFotoErro('Informe a URL da foto')
      return
    }

    adicionarFotoMutation.mutate(fotoFormData)
  }

  const handleGerenciarChecklist = (os: OrdemServico) => {
    setOsChecklist(os)
    setChecklistFormData({ descricao: '' })
    setChecklistErro('')
    setModalChecklistAberto(true)
  }

  const handleSubmitChecklist = (e: React.FormEvent) => {
    e.preventDefault()
    setChecklistErro('')

    if (!checklistFormData.descricao) {
      setChecklistErro('Preencha a descrição')
      return
    }

    adicionarChecklistMutation.mutate(checklistFormData)
  }

  const handleMarcarChecklist = (checklistId: string) => {
    if (!osChecklist) return
    marcarChecklistMutation.mutate({ osId: osChecklist.id, checklistId })
  }

  const handleBaixarPDF = async (id: string, numero: string) => {
    try {
      const response = await api.get(`/ordens-servico/${id}/pdf`, { 
        responseType: 'blob' 
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `os_${numero}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF baixado com sucesso!');
    } catch (error) {
      toast.error('Erro ao gerar PDF');
    }
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'pendente': return 'bg-yellow-500/20 text-yellow-400';
      case 'em_andamento': return 'bg-blue-500/20 text-blue-400';
      case 'concluida': return 'bg-green-500/20 text-green-400';
      case 'cancelada': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  }

  const getPrioridadeColor = (prioridade: string): string => {
    const colors: Record<string, string> = {
      baixa: 'bg-gray-500/20 text-gray-400',
      normal: 'bg-blue-500/20 text-blue-400',
      alta: 'bg-orange-500/20 text-orange-400',
      urgente: 'bg-red-500/20 text-red-400',
    }
    return colors[prioridade] || 'bg-gray-500/20 text-gray-400'
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

  const extrairMensagemErro = (error: any): string => {
    if (typeof error === 'string') return error
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail)) return detail.map((d: any) => typeof d === 'string' ? d : d.msg).join(', ')
      if (typeof detail === 'object') return detail.msg || JSON.stringify(detail)
    }
    if (error?.message) return error.message
    return 'Erro desconhecido'
  }

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold" data-testid="titulo-ordens-servico">Ordens de Serviço</h1>
            <p className="text-muted-foreground">
              Gerencie as ordens de serviço do sistema
            </p>
          </div>
          <button
            onClick={handleCriarOS}
            data-testid="botao-nova-os"
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nova OS
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
              <option value="pendente">Pendente</option>
              <option value="em_andamento">Em Andamento</option>
              <option value="concluida">Concluída</option>
              <option value="cancelada">Cancelada</option>
            </CustomSelect>
            <CustomSelect
              value={filtroPrioridade || ''}
              onChange={(e) => setFiltroPrioridade(e.target.value || null)}
            >
              <option value="">Todas as Prioridades</option>
              <option value="baixa">Baixa</option>
              <option value="normal">Normal</option>
              <option value="alta">Alta</option>
              <option value="urgente">Urgente</option>
            </CustomSelect>
          </div>
        </GlassCard>

        {/* Tabela de Ordens de Serviço */}
        <GlassCard className="p-6">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : ordens && ordens.length > 0 ? (
            <DataTable
              data-testid="tabela-os"
              columns={[
                { key: 'numero_os', header: 'Número' },
                { key: 'titulo', header: 'Título' },
                { key: 'status', header: 'Status', render: (_value: any, row: OrdemServico) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(row.status ?? '')}`}>
                    {row.status ?? '—'}
                  </span>
                )},
                { key: 'prioridade', header: 'Prioridade', render: (_value: any, row: OrdemServico) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getPrioridadeColor(row.prioridade ?? '')}`}>
                    {row.prioridade ?? '—'}
                  </span>
                )},
                { key: 'valor_final', header: 'Valor', render: (_value: any, row: OrdemServico) => (
                  <span className="text-white">{formatarMoeda(row.valor_final > 0 ? row.valor_final : row.valor_estimado)}</span>
                )},
                { key: 'data_agendada', header: 'Data', render: (_value: any, row: OrdemServico) => (
                  <span className="text-white">{row.data_agendada ? formatarData(row.data_agendada) : '—'}</span>
                )},
                { key: 'criado_em', header: 'Criado em', render: (_value: any, row: OrdemServico) => (
                  <span className="text-white">{row.criado_em ? formatarData(row.criado_em) : '—'}</span>
                )},
                { key: 'acoes', header: 'Ações', render: (_value: any, row: OrdemServico) => (
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleEditarOS(row)} className="p-2 hover:bg-white/10 rounded-lg" title="Editar" data-testid="botao-editar-os"><Edit className="w-4 h-4" /></button>
                    <button onClick={() => handleBaixarPDF(row.id, row.numero_os)} className="p-2 hover:bg-violet-500/20 rounded-lg transition-colors text-violet-400" title="Baixar PDF"><Download className="w-4 h-4" /></button>
                    <button onClick={() => handleGerenciarItens(row)} className="p-2 hover:bg-white/10 rounded-lg" title="Itens"><Wrench className="w-4 h-4" /></button>
                    <button onClick={() => handleGerenciarFotos(row)} className="p-2 hover:bg-white/10 rounded-lg" title="Fotos"><Camera className="w-4 h-4" /></button>
                    <button onClick={() => handleGerenciarChecklist(row)} className="p-2 hover:bg-white/10 rounded-lg" title="Checklist"><CheckSquare className="w-4 h-4" /></button>
                    <button onClick={() => handleDeletarOS(row)} className="p-2 hover:bg-red-500/20 rounded-lg text-red-400" title="Deletar"><Trash2 className="w-4 h-4" /></button>
                  </div>
                )},
              ]}
              data={ordens.filter((os): os is OrdemServico => os !== null)}
            />
          ) : (
            <EstadoVazio
              icon={<Wrench className="w-12 h-12" />}
              titulo="Nenhuma ordem de serviço encontrada"
              descricao="Comece adicionando uma nova ordem de serviço ao sistema"
              acao={{
                label: "Adicionar OS",
                onClick: handleCriarOS
              }}
            />
          )}
        </GlassCard>

        {/* Modal de OS */}
        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="modal-nova-os">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  {osEditando ? 'Editar Ordem de Serviço' : 'Nova Ordem de Serviço'}
                </h2>
                <button
                  onClick={() => setModalAberto(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleSubmitOS} className="space-y-4">
                {erro && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
                    {erro}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Cliente *</label>
                    <select
                      value={formData.cliente_id}
                      onChange={(e) => setFormData({ ...formData, cliente_id: e.target.value })}
                      required
                      disabled={!!osEditando}
                      data-testid="campo-cliente"
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">Selecione um cliente</option>
                      {clientes?.map((cliente) => (
                        <option key={cliente.id} value={cliente.id}>
                          {cliente.nome}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Técnico</label>
                    <CustomSelect
                      value={formData.tecnico_id}
                      onChange={(e) => setFormData({ ...formData, tecnico_id: e.target.value })}
                    >
                      <option value="">Selecione um técnico</option>
                      {usuarios?.filter((u) => u.perfil === 'tecnico' || u.perfil === 'admin').map((usuario) => (
                        <option key={usuario.id} value={usuario.id}>
                          {usuario.nome_completo}
                        </option>
                      ))}
                    </CustomSelect>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tipo de Serviço *</label>
                  <select
                    value={formData.tipo_servico_id}
                    onChange={(e) => setFormData({ ...formData, tipo_servico_id: e.target.value })}
                    required
                    data-testid="campo-categoria"
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">Selecione um tipo de serviço</option>
                    {categoriasServico?.map((categoria) => (
                      <option key={categoria.id} value={categoria.id}>
                        {categoria.nome}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Título *</label>
                  <input
                    data-testid="campo-titulo"
                    type="text"
                    value={formData.titulo}
                    onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Título da ordem de serviço"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Descrição *</label>
                  <textarea
                    value={formData.descricao}
                    onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                    data-testid="campo-descricao"
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
                    placeholder="Descrição detalhada do serviço"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Prioridade</label>
                    <CustomSelect
                      value={formData.prioridade}
                      onChange={(e) => setFormData({ ...formData, prioridade: e.target.value })}
                      data-testid="campo-prioridade"
                    >
                      <option value="baixa">Baixa</option>
                      <option value="normal">Normal</option>
                      <option value="alta">Alta</option>
                      <option value="urgente">Urgente</option>
                    </CustomSelect>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Valor Estimado</label>
                    <input
                      type="number"
                      value={formData.valor_estimado}
                      onChange={(e) => {
                        const value = e.target.value
                        setFormData({ 
                          ...formData, 
                          valor_estimado: value === '' ? 0 : parseFloat(value) 
                        })
                      }}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0.00"
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>

                {osEditando && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Status</label>
                    <CustomSelect
                      data-testid="campo-status"
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    >
                      <option value="pendente">Pendente</option>
                      <option value="em_andamento">Em Andamento</option>
                      <option value="concluida">Concluída</option>
                      <option value="cancelada">Cancelada</option>
                    </CustomSelect>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-2">Data Agendada</label>
                  <input
                    type="datetime-local"
                    value={formData.data_agendada}
                    onChange={(e) => setFormData({ ...formData, data_agendada: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Observações Internas</label>
                  <textarea
                    value={formData.observacoes_internas}
                    onChange={(e) => setFormData({ ...formData, observacoes_internas: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[80px]"
                    placeholder="Observações internas (visíveis apenas para a equipe)"
                  />
                </div>

                <div className="flex justify-end gap-4 mt-6">
                  <button
                    type="button"
                    onClick={() => setModalAberto(false)}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={criarOSMutation.isPending || atualizarOSMutation.isPending}
                    data-testid="botao-salvar-os"
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {criarOSMutation.isPending || atualizarOSMutation.isPending ? 'Salvando...' : osEditando ? 'Atualizar' : 'Salvar'}
                  </button>
                </div>
              </form>
            </GlassCard>
          </div>
        )}

        {/* Modal de Itens */}
        {modalItensAberto && osItens && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  Itens da OS {osItens.numero_os}
                </h2>
                <button
                  onClick={() => setModalItensAberto(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Formulário para adicionar item */}
              <div className="mb-6 p-4 bg-white/5 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Adicionar Item</h3>
                {itemErro && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm mb-4">
                    {itemErro}
                  </div>
                )}
                <form onSubmit={handleSubmitItem} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Item do Estoque</label>
                      <CustomSelect
                        value={itemFormData.item_estoque_id}
                        onChange={(e) => setItemFormData({ ...itemFormData, item_estoque_id: e.target.value })}
                      >
                        <option value="">Selecione (opcional)</option>
                        {itensEstoque?.map((item: any) => (
                          <option key={item.id} value={item.id}>
                            {item.nome}
                          </option>
                        ))}
                      </CustomSelect>
                    </div>
                    <div className="flex items-center gap-2 pt-6">
                      <input
                        type="checkbox"
                        id="compra_externa"
                        checked={itemFormData.compra_externa}
                        onChange={(e) => setItemFormData({ ...itemFormData, compra_externa: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <label htmlFor="compra_externa" className="text-sm">Compra externa</label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Descrição *</label>
                    <input
                      type="text"
                      value={itemFormData.descricao}
                      onChange={(e) => setItemFormData({ ...itemFormData, descricao: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Descrição do item"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Quantidade *</label>
                      <input
                        type="number"
                        value={itemFormData.quantidade}
                        onChange={(e) => setItemFormData({ ...itemFormData, quantidade: parseFloat(e.target.value) || 0 })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        min="0"
                        step="0.01"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Unidade *</label>
                      <input
                        type="text"
                        value={itemFormData.unidade}
                        onChange={(e) => setItemFormData({ ...itemFormData, unidade: e.target.value })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="un, kg, m, etc"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Custo Unitário *</label>
                      <input
                        type="number"
                        value={itemFormData.custo_unitario}
                        onChange={(e) => setItemFormData({ ...itemFormData, custo_unitario: parseFloat(e.target.value) || 0 })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        min="0"
                        step="0.01"
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={adicionarItemMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {adicionarItemMutation.isPending ? 'Adicionando...' : 'Adicionar Item'}
                  </button>
                </form>
              </div>

              {/* Lista de itens */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Itens Adicionados</h3>
                {itensOS && itensOS.length > 0 ? (
                  <div className="space-y-2">
                    {itensOS.map((item: any) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium">{item.descricao}</p>
                          <p className="text-sm text-muted-foreground">
                            {item.quantidade} {item.unidade} × {formatarMoeda(item.custo_unitario)} = {formatarMoeda(item.custo_total)}
                          </p>
                          {item.compra_externa && (
                            <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded">Compra externa</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">Nenhum item adicionado</p>
                )}
              </div>
            </GlassCard>
          </div>
        )}

        {/* Modal de Fotos */}
        {modalFotosAberto && osFotos && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  Fotos da OS {osFotos.numero_os}
                </h2>
                <button
                  onClick={() => setModalFotosAberto(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Formulário para adicionar foto */}
              <div className="mb-6 p-4 bg-white/5 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Adicionar Foto</h3>
                {fotoErro && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm mb-4">
                    {fotoErro}
                  </div>
                )}
                <form onSubmit={handleSubmitFoto} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">URL da Foto *</label>
                    <input
                      type="url"
                      value={fotoFormData.url_arquivo}
                      onChange={(e) => setFotoFormData({ ...fotoFormData, url_arquivo: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="https://exemplo.com/foto.jpg"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">URL da Miniatura</label>
                    <input
                      type="url"
                      value={fotoFormData.url_miniatura}
                      onChange={(e) => setFotoFormData({ ...fotoFormData, url_miniatura: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="https://exemplo.com/miniatura.jpg (opcional)"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Legenda</label>
                    <input
                      type="text"
                      value={fotoFormData.legenda}
                      onChange={(e) => setFotoFormData({ ...fotoFormData, legenda: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Descrição da foto"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Tipo</label>
                      <CustomSelect
                        value={fotoFormData.tipo_foto}
                        onChange={(e) => setFotoFormData({ ...fotoFormData, tipo_foto: e.target.value as any })}
                      >
                        <option value="antes">Antes</option>
                        <option value="depois">Depois</option>
                        <option value="durante">Durante</option>
                        <option value="problema">Problema</option>
                        <option value="outro">Outro</option>
                      </CustomSelect>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Data/Hora</label>
                      <input
                        type="datetime-local"
                        value={fotoFormData.tirada_em}
                        onChange={(e) => setFotoFormData({ ...fotoFormData, tirada_em: e.target.value })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={adicionarFotoMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {adicionarFotoMutation.isPending ? 'Enviando...' : 'Enviar Foto'}
                  </button>
                </form>
              </div>

              {/* Lista de fotos */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Fotos Adicionadas</h3>
                {fotosOS && fotosOS.length > 0 ? (
                  <div className="grid grid-cols-3 gap-4">
                    {fotosOS.map((foto: any) => (
                      <div key={foto.id} className="relative group">
                        <img
                          src={foto.url_arquivo}
                          alt={foto.legenda || 'Foto'}
                          className="w-full h-48 object-cover rounded-lg"
                        />
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-end p-2">
                          <div className="text-white text-xs">
                            <p className="font-medium truncate">{foto.legenda || 'Sem legenda'}</p>
                            <p className="text-muted-foreground">{foto.tipo_foto}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">Nenhuma foto adicionada</p>
                )}
              </div>
            </GlassCard>
          </div>
        )}

        {/* Modal de Checklist */}
        {modalChecklistAberto && osChecklist && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">
                  Checklist da OS {osChecklist.numero_os}
                </h2>
                <button
                  onClick={() => setModalChecklistAberto(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Formulário para adicionar item */}
              <div className="mb-6 p-4 bg-white/5 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Adicionar Item</h3>
                {checklistErro && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm mb-4">
                    {checklistErro}
                  </div>
                )}
                <form onSubmit={handleSubmitChecklist} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Descrição *</label>
                    <input
                      type="text"
                      value={checklistFormData.descricao}
                      onChange={(e) => setChecklistFormData({ ...checklistFormData, descricao: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Descrição do item de checklist"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={adicionarChecklistMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {adicionarChecklistMutation.isPending ? 'Adicionando...' : 'Adicionar Item'}
                  </button>
                </form>
              </div>

              {/* Lista de checklist */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Itens do Checklist</h3>
                {checklistOS && checklistOS.length > 0 ? (
                  <div className="space-y-2">
                    {checklistOS.map((item: any) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex items-center gap-3 flex-1">
                          <button
                            onClick={() => handleMarcarChecklist(item.id)}
                            className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                              item.concluido
                                ? 'bg-green-500 border-green-500 text-white'
                                : 'border-white/30 hover:border-white/60'
                            }`}
                          >
                            {item.concluido && <CheckSquare className="w-4 h-4" />}
                          </button>
                          <span className={item.concluido ? 'line-through text-muted-foreground' : ''}>
                            {item.descricao}
                          </span>
                        </div>
                        {item.concluido && (
                          <span className="text-xs text-green-400">
                            {item.concluido_em ? formatarData(item.concluido_em) : ''}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">Nenhum item adicionado</p>
                )}
              </div>
            </GlassCard>
          </div>
        )}

        {/* Modal de Confirmação de Delete */}
        {osParaDeletar && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-md p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Confirmar Exclusão</h2>
                <button
                  onClick={() => setOsParaDeletar(null)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <p className="text-muted-foreground">
                  Tem certeza que deseja excluir a ordem de serviço <strong>{osParaDeletar.numero_os}</strong>?
                </p>
                <p className="text-sm text-muted-foreground">
                  {osParaDeletar.titulo}
                </p>
                <p className="text-sm text-red-400">
                  Esta ação não pode ser desfeita.
                </p>

                <div className="flex justify-end gap-4 mt-6">
                  <button
                    onClick={() => setOsParaDeletar(null)}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                    disabled={deletarOSMutation.isPending}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={confirmarDeletarOS}
                    disabled={deletarOSMutation.isPending}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deletarOSMutation.isPending ? 'Excluindo...' : 'Confirmar Exclusão'}
                  </button>
                </div>
              </div>
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
