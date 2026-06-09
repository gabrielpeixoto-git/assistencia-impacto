import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { DataTable } from '@/components/comum/DataTable'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { EstadoVazio } from '@/components/comum/EstadoVazio'
import { ModalConfirmacao } from '@/components/ModalConfirmacao'
import { ErroRede } from '@/components/ErroRede'
import { IMaskTelefone, IMaskCPFCNPJ, IMaskCEP } from '@/components/ui/InputMask'
import CustomSelect from '@/components/ui/CustomSelect'
import { toast } from 'sonner'
import { validarCPF, validarCNPJ } from '@/utils/validacaoDocumento'
import { 
  Plus, 
  Search, 
  Phone, 
  Mail, 
  MapPin,
  Edit,
  Trash2,
  Building2
} from 'lucide-react'

interface Cliente {
  id: string
  nome: string
  email: string | null
  telefone: string | null
  whatsapp: string | null
  tipo_documento: string
  numero_documento: string | null
  tipo_cliente: string
  logradouro: string | null
  numero: string | null
  complemento: string | null
  bairro: string | null
  cidade: string | null
  estado: string | null
  cep: string | null
  observacoes: string | null
  ativo: boolean
  criado_em: string
}


export function ClientesPage() {
  const [busca, setBusca] = useState('')
  const [filtroAtivo, setFiltroAtivo] = useState<boolean | null>(null)
  const [modalAberto, setModalAberto] = useState(false)
  const [clienteEditando, setClienteEditando] = useState<Cliente | null>(null)
  const [modalEnderecoAberto, setModalEnderecoAberto] = useState(false)
  const [clienteEndereco, setClienteEndereco] = useState<Cliente | null>(null)
  const [erro, setErro] = useState('')
  const [modalConfirmacaoAberto, setModalConfirmacaoAberto] = useState(false)
  const [clienteParaDeletar, setClienteParaDeletar] = useState<string | null>(null)
  const [buscandoCEP, setBuscandoCEP] = useState(false)
  const [errosCampo, setErrosCampo] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    whatsapp: '',
    tipo_documento: 'cpf' as 'cpf' | 'cnpj',
    numero_documento: '',
    tipo_cliente: 'residencial',
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    estado: '',
    cep: '',
    observacoes: ''
  })

  const queryClient = useQueryClient()

  const { data: clientes, isLoading, isError, error, refetch } = useQuery<Cliente[]>({
    queryKey: ['clientes', busca, filtroAtivo],
    queryFn: async () => {
      const params: any = {}
      if (busca) params.busca = busca
      if (filtroAtivo !== null) params.ativo = filtroAtivo
      
      const response = await api.get('/clientes', { params })
      return response.data
    },
    throwOnError: false
  })

  useEffect(() => {
    if (isError) {
      toast.error('Erro ao carregar clientes', {
        description: error?.message
      })
    }
  }, [isError, error])



  const deletarClienteMutation = useMutation({
    mutationFn: async (id: string) => {
      return api.delete(`/clientes/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      toast.success('Cliente removido com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao deletar cliente. Tente novamente.')
    }
  })

  const criarClienteMutation = useMutation({
    mutationFn: async (clienteData: any) => {
      return api.post('/clientes', clienteData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      setModalAberto(false)
      setClienteEditando(null)
      setErro('')
      toast.success('Cliente criado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao criar cliente. Tente novamente.')
    }
  })

  const atualizarClienteMutation = useMutation({
    mutationFn: async ({ id, clienteData }: { id: string; clienteData: any }) => {
      return api.put(`/clientes/${id}`, clienteData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      setModalAberto(false)
      setClienteEditando(null)
      setErro('')
      toast.success('Cliente atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar cliente. Tente novamente.')
    }
  })

  const handleCriarCliente = () => {
    setClienteEditando(null)
    setErro('')
    setFormData({
      nome: '',
      email: '',
      telefone: '',
      whatsapp: '',
      tipo_documento: 'cpf',
      numero_documento: '',
      tipo_cliente: 'residencial',
      logradouro: '',
      numero: '',
      complemento: '',
      bairro: '',
      cidade: '',
      estado: '',
      cep: '',
      observacoes: ''
    })
    setModalAberto(true)
  }

  const handleEditarCliente = (cliente: Cliente) => {
    setClienteEditando(cliente)
    setErro('')
    setFormData({
      nome: cliente.nome,
      email: cliente.email || '',
      telefone: cliente.telefone || '',
      whatsapp: cliente.whatsapp || '',
      tipo_documento: (cliente.tipo_documento as 'cpf' | 'cnpj') || 'cpf',
      numero_documento: cliente.numero_documento || '',
      tipo_cliente: cliente.tipo_cliente,
      logradouro: cliente.logradouro || '',
      numero: cliente.numero || '',
      complemento: cliente.complemento || '',
      bairro: cliente.bairro || '',
      cidade: cliente.cidade || '',
      estado: cliente.estado || '',
      cep: cliente.cep || '',
      observacoes: cliente.observacoes || ''
    })
    setModalAberto(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (clienteEditando) {
      atualizarClienteMutation.mutate({
        id: clienteEditando.id,
        clienteData: formData
      })
    } else {
      criarClienteMutation.mutate(formData)
    }
  }

  const handleDeletarCliente = (id: string) => {
    setClienteParaDeletar(id)
    setModalConfirmacaoAberto(true)
  }

  const confirmarDeletarCliente = () => {
    if (clienteParaDeletar) {
      deletarClienteMutation.mutate(clienteParaDeletar)
      setModalConfirmacaoAberto(false)
      setClienteParaDeletar(null)
    }
  }

  const buscarCEP = async (cep: string) => {
    const cepLimpo = cep.replace(/\D/g, '')
    if (cepLimpo.length !== 8) return

    setBuscandoCEP(true)
    try {
      const response = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
      const data = await response.json()

      if (data.erro) {
        toast.error('CEP não encontrado')
        return
      }

      setFormData({
        ...formData,
        logradouro: data.logradouro || formData.logradouro,
        bairro: data.bairro || formData.bairro,
        cidade: data.localidade || formData.cidade,
        estado: data.uf || formData.estado
      })
    } catch (error) {
      toast.error('Erro ao buscar CEP. Tente novamente.')
    } finally {
      setBuscandoCEP(false)
    }
  }

  const handleGerenciarEnderecos = (cliente: Cliente) => {
    setClienteEndereco(cliente)
    setModalEnderecoAberto(true)
  }

  const formatarCPF_CNPJ = (valor: string | null) => {
    if (!valor) return '-'
    const numeros = valor.replace(/\D/g, '')
    if (numeros.length === 11) {
      return numeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
    } else if (numeros.length === 14) {
      return numeros.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
    }
    return valor
  }

  const formatarTelefone = (valor: string | null) => {
    if (!valor) return '-'
    const numeros = valor.replace(/\D/g, '')
    if (numeros.length === 11) {
      return numeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
    }
    return valor
  }

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Clientes</h1>
            <p className="text-muted-foreground">
              Gerencie seus clientes e seus endereços
            </p>
          </div>
          <button
            onClick={handleCriarCliente}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            data-testid="botao-novo-cliente"
          >
            <Plus className="w-5 h-5" />
            Novo Cliente
          </button>
        </div>

        {/* Filtros */}
        <GlassCard className="p-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar por nome, email, telefone..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <CustomSelect
              value={filtroAtivo === null ? '' : filtroAtivo ? 'true' : 'false'}
              onChange={(e) => setFiltroAtivo(e.target.value === '' ? null : e.target.value === 'true')}
            >
              <option value="">Todos</option>
              <option value="true">Ativos</option>
              <option value="false">Inativos</option>
            </CustomSelect>
          </div>
        </GlassCard>

        {/* Tabela de Clientes */}
        <GlassCard className="p-6" data-testid="tabela-clientes">
          {isError ? (
            <ErroRede onTentarNovamente={() => refetch()} />
          ) : isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : clientes && clientes.length > 0 ? (
            <DataTable
              columns={[
                { key: 'nome', header: 'Nome' },
                { key: 'email', header: 'Email', render: (_value: any, row: Cliente) => (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    {row.email}
                  </div>
                )},
                { key: 'telefone', header: 'Telefone', render: (_value: any, row: Cliente) => (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-muted-foreground" />
                    {formatarTelefone(row.telefone)}
                  </div>
                )},
                { key: 'numero_documento', header: 'CPF/CNPJ', render: (_value: any, row: Cliente) => formatarCPF_CNPJ(row.numero_documento) },
                { key: 'tipo_cliente', header: 'Tipo', render: (_value: any, row: Cliente) => (
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-muted-foreground" />
                    {row.tipo_cliente === 'residencial' ? 'Residencial' : 'Comercial'}
                  </div>
                )},
                { key: 'ativo', header: 'Status', render: (_value: any, row: Cliente) => (
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    row.ativo ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {row.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                )},
                { key: 'acoes', header: 'Ações', render: (_value: any, row: Cliente) => (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEditarCliente(row)}
                      className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                      title="Editar"
                      data-testid="botao-editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleGerenciarEnderecos(row)}
                      className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                      title="Endereços"
                    >
                      <MapPin className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeletarCliente(row.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
                      title="Deletar"
                      data-testid="botao-excluir"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )},
              ]}
              data={clientes}
            />
          ) : (
            <EstadoVazio
              icon={<Building2 className="w-12 h-12" />}
              titulo="Nenhum cliente encontrado"
              descricao="Comece adicionando um novo cliente ao sistema"
              acao={{
                label: "Adicionar Cliente",
                onClick: handleCriarCliente
              }}
            />
          )}
        </GlassCard>

        {/* Modal de Cliente */}
        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" data-testid="modal-novo-cliente">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6">
                {clienteEditando ? 'Editar Cliente' : 'Novo Cliente'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Dados Pessoais */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Dados Pessoais</h3>
                  <div>
                    <label htmlFor="nome-cliente" className="block text-sm font-medium mb-1">Nome *</label>
                    <input
                      id="nome-cliente"
                      type="text"
                      required
                      value={formData.nome}
                      data-testid="campo-nome"
                      onChange={(e) => {
                        setFormData({ ...formData, nome: e.target.value })
                        setErrosCampo({ ...errosCampo, nome: '' })
                      }}
                      onBlur={() => {
                        if (formData.nome && formData.nome.length < 2) {
                          setErrosCampo({ ...errosCampo, nome: 'Nome deve ter pelo menos 2 caracteres' })
                        }
                      }}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    {errosCampo.nome && (
                      <p className="text-red-400 text-sm mt-1">{errosCampo.nome}</p>
                    )}
                  </div>
                  <div>
                    <label htmlFor="email-cliente" className="block text-sm font-medium mb-1">Email</label>
                    <input
                      id="email-cliente"
                      type="email"
                      value={formData.email}
                      data-testid="campo-email"
                      onChange={(e) => {
                        setFormData({ ...formData, email: e.target.value })
                        setErrosCampo({ ...errosCampo, email: '' })
                      }}
                      onBlur={() => {
                        if (formData.email) {
                          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
                          if (!emailRegex) {
                            setErrosCampo({ ...errosCampo, email: 'Email inválido' })
                          }
                        }
                      }}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    {errosCampo.email && (
                      <p className="text-red-400 text-sm mt-1">{errosCampo.email}</p>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="telefone-cliente" className="block text-sm font-medium mb-1">Telefone</label>
                      <IMaskTelefone
                        id="telefone-cliente"
                        data-testid="campo-telefone"
                        value={formData.telefone}
                        onChange={(value) => setFormData({ ...formData, telefone: value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="whatsapp-cliente" className="block text-sm font-medium mb-1">WhatsApp</label>
                      <IMaskTelefone
                        id="whatsapp-cliente"
                        data-testid="campo-whatsapp"
                        value={formData.whatsapp}
                        onChange={(value) => setFormData({ ...formData, whatsapp: value })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="tipo-documento-cliente" className="block text-sm font-medium mb-1">Tipo de Documento</label>
                      <CustomSelect
                        id="tipo-documento-cliente"
                        value={formData.tipo_documento}
                        onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value as 'cpf' | 'cnpj' })}
                      >
                        <option value="cpf">CPF</option>
                        <option value="cnpj">CNPJ</option>
                      </CustomSelect>
                    </div>
                    <div>
                      <label htmlFor="numero-documento-cliente" className="block text-sm font-medium mb-1">Número do Documento</label>
                      <IMaskCPFCNPJ
                        id="numero-documento-cliente"
                        data-testid="campo-numero-documento"
                        tipo={formData.tipo_documento}
                        value={formData.numero_documento}
                        onChange={(value) => {
                          setFormData({ ...formData, numero_documento: value })
                          setErrosCampo({ ...errosCampo, numero_documento: '' })
                        }}
                        onBlur={() => {
                          if (formData.numero_documento) {
                            const valido = formData.tipo_documento === 'cpf' 
                              ? validarCPF(formData.numero_documento)
                              : validarCNPJ(formData.numero_documento)
                            if (!valido) {
                              setErrosCampo({ ...errosCampo, numero_documento: `${formData.tipo_documento.toUpperCase()} inválido` })
                            }
                          }
                        }}
                      />
                      {errosCampo.numero_documento && (
                        <p className="text-red-400 text-sm mt-1">{errosCampo.numero_documento}</p>
                      )}
                    </div>
                  </div>
                  <div>
                    <label htmlFor="tipo-cliente-cliente" className="block text-sm font-medium mb-1">Tipo de Cliente</label>
                    <CustomSelect
                      id="tipo-cliente-cliente"
                      value={formData.tipo_cliente}
                      onChange={(e) => setFormData({ ...formData, tipo_cliente: e.target.value })}
                    >
                      <option value="residencial">Residencial</option>
                      <option value="comercial">Comercial</option>
                    </CustomSelect>
                  </div>
                </div>

                {/* Endereço */}
                <div className="space-y-4 pt-4 border-t border-white/20">
                  <h3 className="text-lg font-semibold">Endereço</h3>
                  <div>
                    <label htmlFor="logradouro-cliente" className="block text-sm font-medium mb-1">Logradouro</label>
                    <input
                      id="logradouro-cliente"
                      type="text"
                      value={formData.logradouro}
                      data-testid="campo-endereco"
                      onChange={(e) => setFormData({ ...formData, logradouro: e.target.value })}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="numero-cliente" className="block text-sm font-medium mb-1">Número</label>
                      <input
                        id="numero-cliente"
                        type="text"
                        value={formData.numero}
                        onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <div>
                      <label htmlFor="complemento-cliente" className="block text-sm font-medium mb-1">Complemento</label>
                      <input
                        id="complemento-cliente"
                        type="text"
                        value={formData.complemento}
                        onChange={(e) => setFormData({ ...formData, complemento: e.target.value })}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="bairro-cliente" className="block text-sm font-medium mb-1">Bairro</label>
                    <input
                      id="bairro-cliente"
                      type="text"
                      value={formData.bairro}
                      onChange={(e) => setFormData({ ...formData, bairro: e.target.value })}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="cidade-cliente" className="block text-sm font-medium mb-1">Cidade</label>
                      <input
                        id="cidade-cliente"
                        type="text"
                        value={formData.cidade}
                        onChange={(e) => setFormData({ ...formData, cidade: e.target.value })}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <div>
                      <label htmlFor="estado-cliente" className="block text-sm font-medium mb-1">Estado</label>
                      <input
                        id="estado-cliente"
                        type="text"
                        value={formData.estado}
                        onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                        maxLength={2}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="cep-cliente" className="block text-sm font-medium mb-1">CEP</label>
                    <div className="relative">
                      <IMaskCEP
                        id="cep-cliente"
                        value={formData.cep}
                        onChange={(value) => {
                          setFormData({ ...formData, cep: value })
                          buscarCEP(value)
                        }}
                      />
                      {buscandoCEP && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Observações */}
                <div className="space-y-4 pt-4 border-t border-white/20">
                  <div>
                    <label htmlFor="observacoes-cliente" className="block text-sm font-medium mb-1">Observações</label>
                    <textarea
                      id="observacoes-cliente"
                      value={formData.observacoes}
                      onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                {erro && (
                  <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
                    {erro}
                  </div>
                )}

                <div className="flex justify-end gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setModalAberto(false)}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={criarClienteMutation.isPending || atualizarClienteMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                    data-testid="botao-salvar"
                  >
                    {criarClienteMutation.isPending || atualizarClienteMutation.isPending ? 'Salvando...' : 'Salvar'}
                  </button>
                </div>
              </form>
            </GlassCard>
          </div>
        )}

        {/* Modal de Confirmação */}
        <ModalConfirmacao
          aberto={modalConfirmacaoAberto}
          titulo="Deletar Cliente"
          mensagem="Tem certeza que deseja deletar este cliente? Esta ação não pode ser desfeita."
          textoBotaoConfirmar="Deletar"
          carregando={deletarClienteMutation.isPending}
          onConfirmar={confirmarDeletarCliente}
          onCancelar={() => {
            setModalConfirmacaoAberto(false)
            setClienteParaDeletar(null)
          }}
        />

        {/* Modal de Endereços */}
        {modalEnderecoAberto && clienteEndereco && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6">
                Endereços de {clienteEndereco.nome}
              </h2>
              {/* Lista de endereços - a ser implementado */}
              <p className="text-muted-foreground">
                Gerenciamento de endereços em desenvolvimento
              </p>
              <div className="flex justify-end gap-4 mt-6">
                <button
                  onClick={() => setModalEnderecoAberto(false)}
                  className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                >
                  Fechar
                </button>
              </div>
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
