import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { useNotificacaoStore } from '@/store/notificacao.store'
import { 
  Building2,
  MessageCircle,
  FileText,
  Bell,
  Users,
  Save,
  Loader2
} from 'lucide-react'

interface Configuracoes {
  nome_empresa: string
  cnpj_empresa: string
  telefone_empresa: string
  email_empresa: string
  endereco_empresa: string
  smtp_host: string
  smtp_porta: number
  smtp_usuario: string
  email_remetente: string
  nome_remetente: string
  evolution_api_url: string
  evolution_api_key: string
  whatsapp_telefone: string
  viacep_api_url: string
  url_frontend: string
  ambiente: string
  permitir_registro_publico: boolean
  tamanho_maximo_upload_mb: number
  tipos_imagem_permitidos: string
  pdf_rodape: string
  // Preferências de Notificação
  notif_nova_os: boolean
  notif_orcamento_aprovado: boolean
  notif_orcamento_rejeitado: boolean
  notif_agendamento_proximo: boolean
  notif_estoque_baixo: boolean
  notif_relatorio_semanal: boolean
  notif_canal_email: boolean
  notif_canal_sistema: boolean
  notif_frequencia: string
  // Preferências de Aparência
  tema_dark_mode: boolean
  tema_cor_primaria: string
  tema_densidade: string
  // Configurações Regionais
  regiao_moeda: string
  regiao_fuso_horario: string
  regiao_formato_data: string
  regiao_idioma: string
}

// Funções de máscara
const mascaraCNPJ = (value: string): string => {
  const numbers = value.replace(/\D/g, '')
  return numbers.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
    .replace(/^(\d{2})(\d{3})(\d{3})(\d{4})$/, '$1.$2.$3/$4')
    .replace(/^(\d{2})(\d{3})(\d{3})$/, '$1.$2.$3')
    .replace(/^(\d{2})(\d{3})$/, '$1.$2')
    .slice(0, 18)
}

const mascaraTelefone = (value: string): string => {
  const numbers = value.replace(/\D/g, '')
  return numbers.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3')
    .replace(/^(\d{2})(\d{5})$/, '($1) $2')
    .replace(/^(\d{2})$/, '($1')
    .slice(0, 15)
}

// Funções de validação
const validarCNPJ = (cnpj: string): boolean => {
  const cnpjLimpo = cnpj.replace(/\D/g, '')
  if (cnpjLimpo.length !== 14) return false
  // Validação básica - pode ser expandida
  return true
}

const validarEmail = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

const validarTelefone = (telefone: string): boolean => {
  const numeros = telefone.replace(/\D/g, '')
  return numeros.length === 10 || numeros.length === 11
}

export function ConfiguracoesPage() {
  const [abaAtiva, setAbaAtiva] = useState('empresa')
  const [dadosEditados, setDadosEditados] = useState<Partial<Configuracoes>>({})
  const [errosValidacao, setErrosValidacao] = useState<Record<string, string>>({})
  const { adicionarNotificacao } = useNotificacaoStore()

  const { data: configuracoes, isLoading, refetch } = useQuery<Configuracoes>({
    queryKey: ['configuracoes'],
    queryFn: async () => {
      const response = await api.get('/configuracoes')
      return response.data
    }
  })

  const { data: listaUsuarios, isLoading: loadingUsuarios } = useQuery({
    queryKey: ['usuarios-config'],
    queryFn: async () => {
      const response = await api.get('/usuarios')
      return response.data.dados || []
    },
    enabled: abaAtiva === 'usuarios'
  })

  const salvarMutation = useMutation({
    mutationFn: async (dados: Partial<Configuracoes>) => {
      const response = await api.put('/configuracoes', dados)
      return response.data
    },
    onSuccess: () => {
      adicionarNotificacao({
        id: Date.now().toString(),
        titulo: 'Sucesso',
        corpo: 'Configurações salvas com sucesso',
        tipo: 'sucesso'
      })
      refetch()
      setDadosEditados({})
      setErrosValidacao({})
    },
    onError: (error: any) => {
      adicionarNotificacao({
        id: Date.now().toString(),
        titulo: 'Erro',
        corpo: error.response?.data?.detail || 'Erro ao salvar configurações',
        tipo: 'erro'
      })
    }
  })

  const handleInputChange = (campo: string, valor: string | number | boolean) => {
    setDadosEditados(prev => ({ ...prev, [campo]: valor }))
    // Limpar erro do campo quando usuário começa a digitar
    if (errosValidacao[campo]) {
      setErrosValidacao(prev => {
        const novo = { ...prev }
        delete novo[campo]
        return novo
      })
    }
  }

  const handleSalvar = () => {
    // Validar campos da aba Empresa
    const erros: Record<string, string> = {}
    
    // Validar CNPJ se foi alterado
    const cnpjValor = dadosEditados.cnpj_empresa ?? configuracoes?.cnpj_empresa ?? ''
    if (cnpjValor && !validarCNPJ(cnpjValor)) {
      erros.cnpj_empresa = 'CNPJ inválido'
    }
    
    // Validar email se foi alterado
    const emailValor = dadosEditados.email_empresa ?? configuracoes?.email_empresa ?? ''
    if (emailValor && !validarEmail(emailValor)) {
      erros.email_empresa = 'Email inválido'
    }
    
    // Validar telefone se foi alterado
    const telefoneValor = dadosEditados.telefone_empresa ?? configuracoes?.telefone_empresa ?? ''
    if (telefoneValor && !validarTelefone(telefoneValor)) {
      erros.telefone_empresa = 'Telefone inválido'
    }
    
    // Validar nome e endereço (não vazios se foram alterados)
    if (dadosEditados.nome_empresa !== undefined && !dadosEditados.nome_empresa.trim()) {
      erros.nome_empresa = 'Nome da empresa é obrigatório'
    }
    if (dadosEditados.endereco_empresa !== undefined && !dadosEditados.endereco_empresa.trim()) {
      erros.endereco_empresa = 'Endereço é obrigatório'
    }
    
    if (Object.keys(erros).length > 0) {
      setErrosValidacao(erros)
      adicionarNotificacao({
        id: Date.now().toString(),
        titulo: 'Erro de validação',
        corpo: 'Corrija os erros antes de salvar',
        tipo: 'erro'
      })
      return
    }
    
    salvarMutation.mutate(dadosEditados)
  }

  const valorAtual = (campo: keyof Configuracoes): string | number | boolean => {
    if (dadosEditados[campo] !== undefined) {
      return dadosEditados[campo]!
    }
    return (configuracoes as any)?.[campo] ?? ''
  }

  const abas = [
    { id: 'empresa', label: 'Empresa', icon: Building2 },
    { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle },
    { id: 'pdf', label: 'PDF', icon: FileText },
    { id: 'notificacoes', label: 'Notificações', icon: Bell },
    { id: 'usuarios', label: 'Usuários', icon: Users },
  ]

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Configurações</h1>
            <p className="text-muted-foreground">
              Gerencie as configurações do sistema
            </p>
          </div>
          <button
            onClick={handleSalvar}
            disabled={salvarMutation.isPending || Object.keys(dadosEditados).length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {salvarMutation.isPending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Save className="w-5 h-5" />
            )}
            {salvarMutation.isPending ? 'Salvando...' : 'Salvar'}
          </button>
        </div>

        {/* Abas */}
        <div className="flex gap-2 border-b border-white/10">
          {abas.map(aba => {
            const Icon = aba.icon
            return (
              <button
                key={aba.id}
                onClick={() => setAbaAtiva(aba.id)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
                  abaAtiva === aba.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4" />
                {aba.label}
              </button>
            )
          })}
        </div>

        {/* Conteúdo das Abas */}
        <GlassCard className="p-6">
          {isLoading ? (
            <div className="text-center py-8">
              <p>Carregando configurações...</p>
            </div>
          ) : !configuracoes ? (
            <div className="text-center py-8">
              <p>Não foi possível carregar as configurações.</p>
            </div>
          ) : (
            <>
              {abaAtiva === 'empresa' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold">Informações da Empresa</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Nome da Empresa</label>
                      <input
                        type="text"
                        value={valorAtual('nome_empresa') as string}
                        onChange={(e) => handleInputChange('nome_empresa', e.target.value)}
                        className={`w-full px-4 py-2 bg-white/10 border rounded-lg focus:outline-none focus:ring-2 ${
                          errosValidacao.nome_empresa ? 'border-red-500 focus:ring-red-500' : 'border-white/20 focus:ring-primary'
                        }`}
                      />
                      {errosValidacao.nome_empresa && (
                        <p className="text-red-500 text-sm mt-1">{errosValidacao.nome_empresa}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">CNPJ</label>
                      <input
                        type="text"
                        value={mascaraCNPJ(valorAtual('cnpj_empresa') as string)}
                        onChange={(e) => {
                          const valor = e.target.value.replace(/\D/g, '').slice(0, 14)
                          handleInputChange('cnpj_empresa', valor)
                        }}
                        placeholder="00.000.000/0000-00"
                        className={`w-full px-4 py-2 bg-white/10 border rounded-lg focus:outline-none focus:ring-2 ${
                          errosValidacao.cnpj_empresa ? 'border-red-500 focus:ring-red-500' : 'border-white/20 focus:ring-primary'
                        }`}
                      />
                      {errosValidacao.cnpj_empresa && (
                        <p className="text-red-500 text-sm mt-1">{errosValidacao.cnpj_empresa}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Email de Contato</label>
                      <input
                        type="email"
                        value={valorAtual('email_empresa') as string}
                        onChange={(e) => handleInputChange('email_empresa', e.target.value)}
                        className={`w-full px-4 py-2 bg-white/10 border rounded-lg focus:outline-none focus:ring-2 ${
                          errosValidacao.email_empresa ? 'border-red-500 focus:ring-red-500' : 'border-white/20 focus:ring-primary'
                        }`}
                      />
                      {errosValidacao.email_empresa && (
                        <p className="text-red-500 text-sm mt-1">{errosValidacao.email_empresa}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Telefone de Contato</label>
                      <input
                        type="text"
                        value={mascaraTelefone(valorAtual('telefone_empresa') as string)}
                        onChange={(e) => {
                          const valor = e.target.value.replace(/\D/g, '').slice(0, 11)
                          handleInputChange('telefone_empresa', valor)
                        }}
                        placeholder="(00) 00000-0000"
                        className={`w-full px-4 py-2 bg-white/10 border rounded-lg focus:outline-none focus:ring-2 ${
                          errosValidacao.telefone_empresa ? 'border-red-500 focus:ring-red-500' : 'border-white/20 focus:ring-primary'
                        }`}
                      />
                      {errosValidacao.telefone_empresa && (
                        <p className="text-red-500 text-sm mt-1">{errosValidacao.telefone_empresa}</p>
                      )}
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium mb-2">Endereço</label>
                      <input
                        type="text"
                        value={valorAtual('endereco_empresa') as string}
                        onChange={(e) => handleInputChange('endereco_empresa', e.target.value)}
                        className={`w-full px-4 py-2 bg-white/10 border rounded-lg focus:outline-none focus:ring-2 ${
                          errosValidacao.endereco_empresa ? 'border-red-500 focus:ring-red-500' : 'border-white/20 focus:ring-primary'
                        }`}
                      />
                      {errosValidacao.endereco_empresa && (
                        <p className="text-red-500 text-sm mt-1">{errosValidacao.endereco_empresa}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {abaAtiva === 'whatsapp' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold">Configurações do WhatsApp</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">URL da API Evolution</label>
                      <input
                        type="text"
                        value={valorAtual('evolution_api_url') as string}
                        onChange={(e) => handleInputChange('evolution_api_url', e.target.value)}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="http://evolution-api:8080"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Chave de API</label>
                      <input
                        type="password"
                        value={valorAtual('evolution_api_key') as string || ''}
                        onChange={(e) => handleInputChange('evolution_api_key', e.target.value)}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Sua chave da API Evolution"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Número de Telefone</label>
                      <input
                        type="text"
                        value={mascaraTelefone(valorAtual('whatsapp_telefone') as string)}
                        onChange={(e) => {
                          const valor = e.target.value.replace(/\D/g, '').slice(0, 11)
                          handleInputChange('whatsapp_telefone', valor)
                        }}
                        placeholder="(51) 99999-9999"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <button
                      onClick={() => {
                        adicionarNotificacao({
                          id: Date.now().toString(),
                          titulo: 'Informação',
                          corpo: 'Teste de conexão em desenvolvimento',
                          tipo: 'info'
                        })
                      }}
                      className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                    >
                      <MessageCircle className="w-4 h-4" />
                      Testar Conexão
                    </button>
                  </div>
                </div>
              )}

              {abaAtiva === 'pdf' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold">Configurações de PDF</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Cor Primária</label>
                      <div className="flex gap-3">
                        <input
                          type="color"
                          value={valorAtual('tema_cor_primaria') as string || '#6C63FF'}
                          onChange={(e) => handleInputChange('tema_cor_primaria', e.target.value)}
                          className="w-16 h-10 rounded cursor-pointer"
                        />
                        <input
                          type="text"
                          value={valorAtual('tema_cor_primaria') as string || '#6C63FF'}
                          onChange={(e) => handleInputChange('tema_cor_primaria', e.target.value)}
                          className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="#6C63FF"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Cor Secundária</label>
                      <div className="flex gap-3">
                        <input
                          type="color"
                          value="#00D4FF"
                          disabled
                          className="w-16 h-10 rounded cursor-pointer opacity-50"
                        />
                        <input
                          type="text"
                          value="#00D4FF"
                          disabled
                          className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg opacity-50 cursor-not-allowed"
                        />
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">Cor secundária fixa: #00D4FF</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Texto do Rodapé</label>
                      <textarea
                        value={valorAtual('pdf_rodape') as string || ''}
                        onChange={(e) => handleInputChange('pdf_rodape', e.target.value)}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
                        placeholder="Texto que aparecerá no rodapé de todos os PDFs"
                      />
                    </div>
                  </div>
                </div>
              )}

              {abaAtiva === 'notificacoes' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-bold">Preferências de Notificação</h2>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Eventos</h3>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_nova_os') as boolean}
                          onChange={(e) => handleInputChange('notif_nova_os', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Nova Ordem de Serviço criada</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_orcamento_aprovado') as boolean}
                          onChange={(e) => handleInputChange('notif_orcamento_aprovado', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Orçamento aprovado</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_orcamento_rejeitado') as boolean}
                          onChange={(e) => handleInputChange('notif_orcamento_rejeitado', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Orçamento rejeitado</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_agendamento_proximo') as boolean}
                          onChange={(e) => handleInputChange('notif_agendamento_proximo', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Agendamento em menos de 24h</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_estoque_baixo') as boolean}
                          onChange={(e) => handleInputChange('notif_estoque_baixo', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Estoque abaixo do mínimo</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_relatorio_semanal') as boolean}
                          onChange={(e) => handleInputChange('notif_relatorio_semanal', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Relatório semanal disponível</span>
                      </label>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Canal de Notificação</h3>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_canal_email') as boolean}
                          onChange={(e) => handleInputChange('notif_canal_email', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>E-mail</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={valorAtual('notif_canal_sistema') as boolean}
                          onChange={(e) => handleInputChange('notif_canal_sistema', e.target.checked)}
                          className="w-5 h-5 rounded border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Sistema (push interno)</span>
                      </label>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Frequência</h3>
                    <div className="space-y-2">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="radio"
                          name="frequencia"
                          value="imediato"
                          checked={valorAtual('notif_frequencia') as string === 'imediato'}
                          onChange={(e) => handleInputChange('notif_frequencia', e.target.value)}
                          className="w-5 h-5 border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Imediato</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="radio"
                          name="frequencia"
                          value="diario"
                          checked={valorAtual('notif_frequencia') as string === 'diario'}
                          onChange={(e) => handleInputChange('notif_frequencia', e.target.value)}
                          className="w-5 h-5 border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Resumo diário</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="radio"
                          name="frequencia"
                          value="semanal"
                          checked={valorAtual('notif_frequencia') as string === 'semanal'}
                          onChange={(e) => handleInputChange('notif_frequencia', e.target.value)}
                          className="w-5 h-5 border-white/20 bg-white/10 text-primary focus:ring-2 focus:ring-primary"
                        />
                        <span>Resumo semanal</span>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {abaAtiva === 'usuarios' && (
                <GlassCard className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-white">Usuários do Sistema</h3>
                    <span className="text-sm text-slate-400">
                      {listaUsuarios?.length || 0} usuário(s)
                    </span>
                  </div>
                  
                  {loadingUsuarios ? (
                    <div className="text-center py-8 text-slate-400">
                      <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                      Carregando usuários...
                    </div>
                  ) : listaUsuarios && listaUsuarios.length > 0 ? (
                    <div className="space-y-3">
                      {listaUsuarios.map((user: any) => (
                        <div key={user.id} 
                             className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
                          <div className="flex items-center gap-3">
                            {/* Avatar com iniciais */}
                            <div className="w-10 h-10 rounded-full bg-violet-600/30 border border-violet-500/30 
                                            flex items-center justify-center text-violet-300 font-semibold text-sm">
                              {user.nome_completo?.split(' ').map((n: string) => n[0]).slice(0,2).join('').toUpperCase()}
                            </div>
                            <div>
                              <p className="text-white font-medium">{user.nome_completo}</p>
                              <p className="text-slate-400 text-sm">{user.email}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {/* Badge de perfil */}
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                              user.perfil === 'ADMIN' ? 'bg-violet-500/20 text-violet-300' :
                              user.perfil === 'GERENTE' ? 'bg-blue-500/20 text-blue-300' :
                              'bg-slate-500/20 text-slate-300'
                            }`}>
                              {user.perfil}
                            </span>
                            {/* Status ativo/inativo */}
                            <span className={`w-2 h-2 rounded-full ${user.ativo ? 'bg-green-400' : 'bg-red-400'}`} 
                                  title={user.ativo ? 'Ativo' : 'Inativo'} />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-slate-400">
                      <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
                      <p>Nenhum usuário encontrado</p>
                    </div>
                  )}
                </GlassCard>
              )}
            </>
          )}
        </GlassCard>
      </div>
    </PageWrapper>
  )
}
