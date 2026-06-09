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
import { schemaEstoqueItem, EstoqueItemFormData } from '@/lib/validacoes'
import { 
  Plus, 
  Search, 
  Edit,
  Trash2,
  Package,
  AlertTriangle,
  ArrowUpDown,
  Save,
  X
} from 'lucide-react'

interface ItemEstoque {
  id: string
  sku: string
  nome: string
  descricao: string | null
  categoria_id: string
  unidade: string
  estoque_atual: number
  estoque_minimo: number
  estoque_maximo: number
  custo_unitario: number
  preco_venda: number
  percentual_markup: number
  fornecedor: string | null
  codigo_fornecedor: string | null
  url_imagem: string | null
  codigo_barras: string | null
  localizacao_estoque: string | null
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

interface CategoriaEstoque {
  id: string
  nome: string
  cor: string
  icone: string
  ativo: boolean
}

export function EstoquePage() {
  const [busca, setBusca] = useState('')
  const [filtroCategoria, setFiltroCategoria] = useState<string | null>(null)
  const [filtroEstoqueBaixo, setFiltroEstoqueBaixo] = useState(false)
  const [modalAberto, setModalAberto] = useState(false)
  const [itemEditando, setItemEditando] = useState<ItemEstoque | null>(null)
  const [erro, setErro] = useState('')
  const [modalConfirmacaoAberto, setModalConfirmacaoAberto] = useState(false)
  const [itemParaDeletar, setItemParaDeletar] = useState<string | null>(null)
  const [modalMovimentacaoAberto, setModalMovimentacaoAberto] = useState(false)
  const [itemMovimentacao, setItemMovimentacao] = useState<ItemEstoque | null>(null)
  const { register, handleSubmit, formState: { errors }, reset, setValue } = useForm<EstoqueItemFormData>({
    resolver: zodResolver(schemaEstoqueItem),
    defaultValues: {
      sku: '',
      nome: '',
      descricao: '',
      categoria_id: '',
      custo_unitario: 0,
      preco_venda: 0,
      estoque_atual: 0,
      estoque_minimo: 0
    }
  })
  const [formDataMovimentacao, setFormDataMovimentacao] = useState({
    tipo_movimentacao: 'entrada',
    quantidade: '',
    custo_unitario: '',
    observacoes: ''
  })

  const queryClient = useQueryClient()

  const { data: itens, isLoading, isError, refetch } = useQuery<ItemEstoque[]>({
    queryKey: ['estoque'],
    queryFn: async () => {
      const response = await api.get('/estoque/itens')
      return response.data
    }
  })

  const itensFiltrados = itens?.filter(item => {
    if (item.ativo === false) return false
    
    const buscaTrim = busca.trim()
    if (!buscaTrim) return true
    
    const matchBusca = 
      item.nome.toLowerCase().includes(buscaTrim.toLowerCase()) ||
      (item.sku ?? '').toLowerCase().includes(buscaTrim.toLowerCase())
    const matchCategoria = !filtroCategoria || item.categoria_id === filtroCategoria
    const matchEstoqueBaixo = !filtroEstoqueBaixo || item.estoque_atual <= item.estoque_minimo
    return matchBusca && matchCategoria && matchEstoqueBaixo
  }) || []

  const { data: categorias } = useQuery<CategoriaEstoque[]>({
    queryKey: ['categorias-estoque'],
    queryFn: async () => {
      const response = await api.get('/estoque/categorias')
      return response.data
    }
  })



  const deletarItemMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/estoque/itens/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estoque'] })
      toast.success('Item deletado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao deletar item. Tente novamente.')
    }
  })

  const criarItemMutation = useMutation({
    mutationFn: async (itemData: any) => {
      return api.post('/estoque/itens', itemData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estoque'] })
      setModalAberto(false)
      setItemEditando(null)
      resetForm()
      setErro('')
      toast.success('Item criado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao criar item. Tente novamente.')
    }
  })

  const atualizarItemMutation = useMutation({
    mutationFn: async ({ id, itemData }: { id: string; itemData: any }) => {
      return api.put(`/estoque/itens/${id}`, itemData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estoque'] })
      setModalAberto(false)
      setItemEditando(null)
      resetForm()
      setErro('')
      toast.success('Item atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar item. Tente novamente.')
    }
  })

  const criarMovimentacaoMutation = useMutation({
    mutationFn: async (movimentacaoData: any) => {
      return api.post('/estoque/movimentacoes', movimentacaoData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estoque'] })
      setModalMovimentacaoAberto(false)
      setItemMovimentacao(null)
      resetFormMovimentacao()
      toast.success('Movimentação registrada com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao registrar movimentação. Tente novamente.')
    }
  })

  const resetForm = () => {
    reset()
  }

  const resetFormMovimentacao = () => {
    setFormDataMovimentacao({
      tipo_movimentacao: 'entrada',
      quantidade: '',
      custo_unitario: '',
      observacoes: ''
    })
  }


  const handleCriarItem = () => {
    setItemEditando(null)
    setErro('')
    resetForm()
    setModalAberto(true)
  }

  const handleEditarItem = (item: ItemEstoque) => {
    setItemEditando(item)
    setErro('')
    setValue('sku', item.sku ?? '')
    setValue('nome', item.nome ?? '')
    setValue('descricao', item.descricao ?? '')
    setValue('categoria_id', item.categoria_id ?? '')
    setValue('custo_unitario', item.custo_unitario ?? 0)
    setValue('preco_venda', item.preco_venda ?? 0)
    setValue('estoque_atual', item.estoque_atual ?? 0)
    setValue('estoque_minimo', item.estoque_minimo ?? 0)
    setModalAberto(true)
  }

  const handleDeletarItem = (id: string) => {
    setItemParaDeletar(id)
    setModalConfirmacaoAberto(true)
  }

  const confirmarDeletarItem = async () => {
    if (itemParaDeletar) {
      try {
        await deletarItemMutation.mutateAsync(itemParaDeletar)
        setModalConfirmacaoAberto(false)
        setItemParaDeletar(null)
        toast.success('Item deletado com sucesso!')
      } catch (error) {
        toast.error('Erro ao deletar item. Tente novamente.')
      }
    }
  }

  const handleGerenciarMovimentacao = (item: ItemEstoque) => {
    setItemMovimentacao(item)
    resetFormMovimentacao()
    setModalMovimentacaoAberto(true)
  }

  const onSubmit = async (data: EstoqueItemFormData) => {
    const itemData = {
      sku: data.sku,
      nome: data.nome,
      descricao: data.descricao || null,
      categoria_id: data.categoria_id,
      unidade: 'un',
      estoque_minimo: data.estoque_minimo || 0,
      estoque_maximo: 0,
      custo_unitario: data.custo_unitario,
      preco_venda: data.preco_venda,
      percentual_markup: 0,
      fornecedor: null,
      codigo_fornecedor: null,
      codigo_barras: null,
      localizacao_estoque: null
    }

    try {
      if (itemEditando) {
        await atualizarItemMutation.mutateAsync({ id: itemEditando.id, itemData })
      } else {
        await criarItemMutation.mutateAsync(itemData)
      }
    } catch (error) {
      toast.error('Erro ao salvar item. Tente novamente.')
    }
  }

  const handleSalvarMovimentacao = async () => {
    const quantidadeNumerica = parseFloat(formDataMovimentacao.quantidade)
    const custoUnitarioNumerico = parseFloat(formDataMovimentacao.custo_unitario)
    
    if (!quantidadeNumerica || !custoUnitarioNumerico || quantidadeNumerica <= 0 || custoUnitarioNumerico <= 0) {
      toast.error('Erro de validação', {
        description: 'Preencha os campos obrigatórios: quantidade e custo unitário (valores maiores que zero)'
      })
      return
    }

    const movimentacaoData = {
      item_estoque_id: itemMovimentacao?.id,
      tipo_movimentacao: formDataMovimentacao.tipo_movimentacao,
      quantidade: quantidadeNumerica,
      custo_unitario: custoUnitarioNumerico,
      observacoes: formDataMovimentacao.observacoes || null
    }

    try {
      await criarMovimentacaoMutation.mutateAsync(movimentacaoData)
      toast.success('Movimentação registrada com sucesso!')
    } catch (error) {
      toast.error('Erro ao registrar movimentação. Tente novamente.')
    }
  }

  const getUnidadeColor = (unidade: string) => {
    const colors: Record<string, string> = {
      un: 'bg-blue-500/20 text-blue-400',
      kg: 'bg-green-500/20 text-green-400',
      l: 'bg-purple-500/20 text-purple-400',
      m: 'bg-orange-500/20 text-orange-400',
    }
    return colors[unidade] || 'bg-gray-500/20 text-gray-400'
  }

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }


  const isEstoqueBaixo = (item: ItemEstoque) => {
    return item.estoque_atual <= item.estoque_minimo
  }

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Estoque</h1>
            <p className="text-muted-foreground">
              Gerencie os itens de estoque e suas movimentações
            </p>
          </div>
          <button
            onClick={handleCriarItem}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Novo Item
          </button>
        </div>

        {/* Filtros */}
        <GlassCard className="p-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar por nome, código..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <CustomSelect
              value={filtroCategoria || ''}
              onChange={(e) => setFiltroCategoria(e.target.value || null)}
            >
              <option value="">Todas as Categorias</option>
              {/* Opções de categorias seriam carregadas da API */}
            </CustomSelect>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filtroEstoqueBaixo}
                onChange={(e) => setFiltroEstoqueBaixo(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm">Estoque Baixo</span>
            </label>
          </div>
        </GlassCard>

        {/* Tabela de Itens */}
        <GlassCard className="p-6" data-testid="tabela-estoque">
          {isError ? (
            <ErroRede onTentarNovamente={() => refetch()} />
          ) : isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : itens && itens.length > 0 ? (
            <DataTable
              columns={[
                { key: 'sku', header: 'SKU' },
                { key: 'nome', header: 'Nome' },
                { key: 'unidade', header: 'Un', render: (_value: any, row: ItemEstoque) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${getUnidadeColor(row.unidade)}`}>
                    {row.unidade}
                  </span>
                )},
                { key: 'estoque_atual', header: 'Quantidade', render: (_value: any, row: ItemEstoque) => (
                  <div className="flex items-center gap-2">
                    <Package className="w-4 h-4 text-muted-foreground" />
                    <span className={isEstoqueBaixo(row) ? 'text-red-400 font-bold' : ''}>
                      {row.estoque_atual}
                    </span>
                    {isEstoqueBaixo(row) && <AlertTriangle className="w-4 h-4 text-red-400" />}
                  </div>
                )},
                { key: 'estoque_minimo', header: 'Mínima', render: (_value: any, row: ItemEstoque) => row.estoque_minimo ?? '—' },
                { key: 'custo_unitario', header: 'Custo', render: (_value: any, row: ItemEstoque) => row.custo_unitario !== undefined && row.custo_unitario !== null ? formatarMoeda(row.custo_unitario) : '—' },
                { key: 'preco_venda', header: 'Venda', render: (_value: any, row: ItemEstoque) => row.preco_venda !== undefined && row.preco_venda !== null ? formatarMoeda(row.preco_venda) : '—' },
                { key: 'ativo', header: 'Status', render: (_value: any, row: ItemEstoque) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    row.ativo ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {row.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                )},
                { key: 'acoes', header: 'Ações', render: (_value: any, row: ItemEstoque) => (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleEditarItem(row) }}
                      className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleGerenciarMovimentacao(row) }}
                      className="p-2 hover:bg-blue-500/20 rounded-lg transition-colors text-blue-400"
                      title="Movimentação"
                    >
                      <ArrowUpDown className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeletarItem(row.id) }}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                      title="Deletar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )},
              ]}
              data={itensFiltrados}
            />
          ) : (
            <EstadoVazio
              icon={<Package className="w-12 h-12" />}
              titulo="Nenhum item encontrado"
              descricao="Comece adicionando um novo item ao estoque"
              acao={{
                label: "Adicionar Item",
                onClick: handleCriarItem
              }}
            />
          )}
        </GlassCard>

        {/* Modal de Confirmação */}
        <ModalConfirmacao
          aberto={modalConfirmacaoAberto}
          titulo="Deletar Item"
          mensagem="Tem certeza que deseja deletar este item? Esta ação não pode ser desfeita."
          textoBotaoConfirmar="Deletar"
          carregando={deletarItemMutation.isPending}
          onConfirmar={confirmarDeletarItem}
          onCancelar={() => {
            setModalConfirmacaoAberto(false)
            setItemParaDeletar(null)
          }}
        />

        {/* Modal de Item */}
        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6">
                {itemEditando ? 'Editar Item' : 'Novo Item'}
              </h2>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="sku-estoque" className="block text-sm font-medium mb-2">SKU *</label>
                    <input
                      id="sku-estoque"
                      type="text"
                      {...register('sku')}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Código do item"
                    />
                    {errors.sku && (
                      <p className="text-red-400 text-sm mt-1">{errors.sku.message}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="nome-estoque" className="block text-sm font-medium mb-2">Nome *</label>
                    <input
                      id="nome-estoque"
                      type="text"
                      {...register('nome')}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Nome do item"
                    />
                    {errors.nome && (
                      <p className="text-red-400 text-sm mt-1">{errors.nome.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label htmlFor="descricao-estoque" className="block text-sm font-medium mb-2">Descrição</label>
                  <textarea
                    id="descricao-estoque"
                    {...register('descricao')}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[80px]"
                    placeholder="Descrição do item"
                    rows={2}
                  />
                  {errors.descricao && (
                    <p className="text-red-400 text-sm mt-1">{errors.descricao.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="categoria-estoque" className="block text-sm font-medium mb-2">Categoria *</label>
                    <CustomSelect
                      id="categoria-estoque"
                      {...register('categoria_id')}
                    >
                      <option value="">Selecione uma categoria</option>
                      {categorias?.filter(c => c.ativo).map((categoria) => (
                        <option key={categoria.id} value={categoria.id}>
                          {categoria.nome}
                        </option>
                      ))}
                    </CustomSelect>
                    {errors.categoria_id && (
                      <p className="text-red-400 text-sm mt-1">{errors.categoria_id.message}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="unidade-estoque" className="block text-sm font-medium mb-2">Unidade</label>
                    <CustomSelect
                      id="unidade-estoque"
                      defaultValue="unidade"
                    >
                      <option value="unidade">Unidade</option>
                      <option value="metro">Metro</option>
                      <option value="litro">Litro</option>
                      <option value="kg">Quilograma</option>
                      <option value="caixa">Caixa</option>
                      <option value="rolo">Rolo</option>
                      <option value="par">Par</option>
                    </CustomSelect>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="estoque-minimo-estoque" className="block text-sm font-medium mb-2">Estoque Mínimo</label>
                    <input
                      id="estoque-minimo-estoque"
                      type="number"
                      step="0.01"
                      min="0"
                      {...register('estoque_minimo', { valueAsNumber: true })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0"
                    />
                    {errors.estoque_minimo && (
                      <p className="text-red-400 text-sm mt-1">{errors.estoque_minimo.message}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="estoque-maximo-estoque" className="block text-sm font-medium mb-2">Estoque Máximo</label>
                    <input
                      id="estoque-maximo-estoque"
                      type="number"
                      step="0.01"
                      min="0"
                      defaultValue="0"
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0"
                    />
                  </div>

                  <div>
                    <label htmlFor="markup-estoque" className="block text-sm font-medium mb-2">Markup (%)</label>
                    <input
                      id="markup-estoque"
                      type="number"
                      step="0.01"
                      min="0"
                      defaultValue="0"
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="custo-unitario-estoque" className="block text-sm font-medium mb-2">Custo Unitário *</label>
                    <input
                      id="custo-unitario-estoque"
                      type="number"
                      step="0.01"
                      min="0"
                      {...register('custo_unitario', { valueAsNumber: true })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0,00"
                    />
                    {errors.custo_unitario && (
                      <p className="text-red-400 text-sm mt-1">{errors.custo_unitario.message}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="preco-venda-estoque" className="block text-sm font-medium mb-2">Preço de Venda *</label>
                    <input
                      id="preco-venda-estoque"
                      type="number"
                      step="0.01"
                      min="0"
                      {...register('preco_venda', { valueAsNumber: true })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0,00"
                    />
                    {errors.preco_venda && (
                      <p className="text-red-400 text-sm mt-1">{errors.preco_venda.message}</p>
                    )}
                  </div>
                </div>

              </div>

              {erro && (
                <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
                  {erro}
                </div>
              )}

              <div className="flex justify-end gap-4 mt-6">
                <button
                  onClick={() => setModalAberto(false)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Cancelar
                </button>
                <button
                  onClick={handleSubmit(onSubmit)}
                  disabled={criarItemMutation.isPending || atualizarItemMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {criarItemMutation.isPending || atualizarItemMutation.isPending ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </GlassCard>
          </div>
        )}

        {/* Modal de Movimentação */}
        {modalMovimentacaoAberto && itemMovimentacao && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6">
                Movimentação de Estoque - {itemMovimentacao.nome}
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo de Movimentação</label>
                  <CustomSelect
                    value={formDataMovimentacao.tipo_movimentacao}
                    onChange={(e) => setFormDataMovimentacao({ ...formDataMovimentacao, tipo_movimentacao: e.target.value })}
                  >
                    <option value="entrada">Entrada</option>
                    <option value="saida">Saída</option>
                    <option value="ajuste">Ajuste</option>
                  </CustomSelect>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Quantidade *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={formDataMovimentacao.quantidade}
                      onChange={(e) => setFormDataMovimentacao({ ...formDataMovimentacao, quantidade: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0,00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Custo Unitário *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={formDataMovimentacao.custo_unitario}
                      onChange={(e) => setFormDataMovimentacao({ ...formDataMovimentacao, custo_unitario: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="0,00"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Observações</label>
                  <textarea
                    value={formDataMovimentacao.observacoes}
                    onChange={(e) => setFormDataMovimentacao({ ...formDataMovimentacao, observacoes: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[80px]"
                    placeholder="Observações sobre a movimentação"
                    rows={2}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  onClick={() => setModalMovimentacaoAberto(false)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Cancelar
                </button>
                <button
                  onClick={handleSalvarMovimentacao}
                  disabled={criarMovimentacaoMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {criarMovimentacaoMutation.isPending ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
