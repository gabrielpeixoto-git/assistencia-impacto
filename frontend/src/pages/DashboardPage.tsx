import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { StatCard } from '@/components/comum/StatCard'
import { DataTable } from '@/components/comum/DataTable'
import { BadgeStatus } from '@/components/comum/BadgeStatus'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  FileText, 
  AlertTriangle,
  Calendar,
  Package
} from 'lucide-react'
import { toast } from 'sonner'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface DashboardResumo {
  os_hoje: number
  os_semana: number
  receita_mes: number
  despesas_mes: number
  lucro_mes: number
  orcamentos_pendentes: number
  pagamentos_atrasados: number
  itens_estoque_critico: number
  os_por_status: { status: string; quantidade: number }[]
  grafico_receita: { data: string; receita: number; despesas: number }[]
  top_clientes: { id: string; nome: string; total: number }[]
  top_tecnicos: { tecnico_id: string; quantidade: number }[]
  os_recentes: {
    id: string
    numero_os: string
    titulo: string
    status: string
    prioridade: string
    cliente_id: string
    tecnico_id: string
    criado_em: string
  }[]
  agenda_proximos_dias: {
    id: string
    titulo: string
    data_hora_inicio: string
    data_hora_fim: string
    tipo_evento: string
    status: string
    tecnico_id: string
    cliente_id: string
  }[]
}

export function DashboardPage() {
  const { data: dashboard, isLoading, isError, error } = useQuery<DashboardResumo>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get('/dashboard/resumo')
      const dados = response.data?.dados ?? response.data
      if (!dados) {
        throw new Error('Dashboard retornou dados vazios')
      }
      return dados
    },
    staleTime: 30_000,
    throwOnError: false
  })

  useEffect(() => {
    if (isError) {
      toast.error('Erro ao carregar dashboard', {
        description: error?.message
      })
    }
  }, [isError, error])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass-card p-6 h-32 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (isError || !dashboard) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-red-400 text-lg">Erro ao carregar o dashboard</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-700 rounded-lg text-white text-sm transition"
        >
          Tentar novamente
        </button>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pendente: 'bg-yellow-500/20 text-yellow-400',
      em_andamento: 'bg-blue-500/20 text-blue-400',
      concluida: 'bg-green-500/20 text-green-400',
      cancelada: 'bg-red-500/20 text-red-400',
      confirmada: 'bg-green-500/20 text-green-400',
      agendado: 'bg-blue-500/20 text-blue-400',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400'
  }

  const getPrioridadeColor = (prioridade: string) => {
    const colors: Record<string, string> = {
      baixa: 'bg-gray-500/20 text-gray-400',
      normal: 'bg-blue-500/20 text-blue-400',
      alta: 'bg-orange-500/20 text-orange-400',
      urgente: 'bg-red-500/20 text-red-400',
    }
    return colors[prioridade] || 'bg-gray-500/20 text-gray-400'
  }

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR')
  }

  const formatarDataHora = (data: string) => {
    return new Date(data).toLocaleString('pt-BR')
  }

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Visão geral do sistema
          </p>
        </div>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="OS Hoje"
          value={dashboard.os_hoje ?? 0}
          icon={<FileText className="w-5 h-5" />}
          trend={{ value: 12, positive: true }}
          testId="stat-card-os"
        />
        <StatCard
          title="OS Semana"
          value={dashboard.os_semana ?? 0}
          icon={<FileText className="w-5 h-5" />}
          trend={{ value: 8, positive: true }}
          testId="stat-card-semana"
        />
        <StatCard
          title="Receita Mensal"
          value={formatarMoeda(dashboard.receita_mes ?? 0)}
          icon={<DollarSign className="w-5 h-5 text-green-400" />}
          trend={{ value: 15, positive: true }}
          testId="stat-card-receita"
        />
        <StatCard
          title="Lucro Mensal"
          value={formatarMoeda(dashboard.lucro_mes ?? 0)}
          icon={(dashboard.lucro_mes ?? 0) >= 0 ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
          trend={{ value: (dashboard.lucro_mes ?? 0) >= 0 ? 10 : -5, positive: (dashboard.lucro_mes ?? 0) >= 0 }}
          testId="stat-card-lucro"
        />
      </div>

      {/* Cards de Alertas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Clientes Ativos"
          value={dashboard.top_clientes?.length || 0}
          icon={<Package className="w-5 h-5 text-blue-400" />}
          testId="stat-card-clientes"
        />
        <StatCard
          title="Orçamentos Pendentes"
          value={dashboard.orcamentos_pendentes ?? 0}
          icon={<FileText className="w-5 h-5 text-yellow-400" />}
          testId="stat-card-orcamentos"
        />
        <StatCard
          title="Pagamentos Atrasados"
          value={dashboard.pagamentos_atrasados ?? 0}
          icon={<AlertTriangle className="w-5 h-5 text-red-400" />}
          testId="stat-card-pagamentos"
        />
        <StatCard
          title="Estoque Crítico"
          value={dashboard.itens_estoque_critico ?? 0}
          icon={<Package className="w-5 h-5 text-orange-400" />}
          testId="stat-card-estoque"
        />
      </div>

      {/* Gráfico de Receita */}
      <div className="glass-card p-6" data-testid="grafico-receita">
        <h2 className="text-xl font-bold mb-4">Receita Últimos 7 Dias</h2>
        {(dashboard.grafico_receita ?? []).length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Sem dados disponíveis
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={256}>
            <LineChart data={dashboard.grafico_receita ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis 
                dataKey="data" 
                stroke="#888"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#888"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a1a', 
                  border: '1px solid #333',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="receita" 
                name="Receita"
                stroke="#10B981" 
                strokeWidth={2}
                dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="despesas" 
                name="Despesas"
                stroke="#EF4444" 
                strokeWidth={2}
                dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Gráfico de Status de OS */}
      <div className="glass-card p-6" data-testid="grafico-status-os">
        <h2 className="text-xl font-bold mb-4">Ordens de Serviço por Status</h2>
        {(dashboard.os_por_status ?? []).length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Sem dados disponíveis
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            {(dashboard.os_por_status ?? []).map((item) => {
              const cores: Record<string, string> = {
                pendente: '#F59E0B',
                confirmada: '#60a5fa',
                em_andamento: '#8B5CF6',
                concluida: '#10B981',
                cancelada: '#EF4444',
                aguardando: '#94A3B8',
              }
              const cor = cores[item.status] || '#94A3B8'
              const total = (dashboard.os_por_status ?? []).reduce((acc, i) => acc + i.quantidade, 0)
              const pct = total > 0 ? Math.round((item.quantidade / total) * 100) : 0
              return (
                <div key={item.status} className="flex items-center gap-3">
                  <div className="min-w-[100px] text-slate-400 text-sm capitalize">
                    {item.status.replace('_', ' ')}
                  </div>
                  <div className="flex-1 bg-white/8 rounded-full h-2 overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-800 ease-in-out" 
                      style={{ width: `${pct}%`, backgroundColor: cor }}
                    />
                  </div>
                  <div className="min-w-[30px] text-sm font-semibold text-right" style={{ color: cor }}>
                    {item.quantidade}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Ordens Recentes */}
      <div className="glass-card p-6" data-testid="tabela-os-recentes">
        <h2 className="text-xl font-bold mb-4">Ordens de Serviço Recentes</h2>
        <DataTable
          columns={[
            { key: 'numero_os', header: 'Número' },
            { key: 'titulo', header: 'Título' },
            { key: 'status', header: 'Status', render: (value) => (
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(value ?? '')}`}>
                {value ?? '—'}
              </span>
            )},
            { key: 'prioridade', header: 'Prioridade', render: (value) => (
              <span className={`px-2 py-1 rounded-full text-xs ${getPrioridadeColor(value ?? '')}`}>
                {value ?? '—'}
              </span>
            )},
            { key: 'criado_em', header: 'Data', render: (value) => value ? formatarData(value) : '—' },
          ]}
          data={dashboard.os_recentes ?? []}
        />
      </div>

      {/* Agenda Próximos Dias */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-4">Agenda - Próximos Dias</h2>
        {(dashboard.agenda_proximos_dias ?? []).length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Nenhum evento agendado para os próximos dias
          </p>
        ) : (
          <div className="space-y-3">
            {(dashboard.agenda_proximos_dias ?? []).map((evento) => (
              <div key={evento.id} className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
                <div className="p-3 rounded-lg bg-primary/10">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{evento.titulo}</h3>
                  <p className="text-sm text-muted-foreground">
                    {formatarDataHora(evento.data_hora_inicio)}
                  </p>
                </div>
                <BadgeStatus status={evento.status} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Top Clientes */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-4">Top Clientes</h2>
        {(dashboard.top_clientes ?? []).length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Nenhum cliente encontrado
          </p>
        ) : (
          <div className="space-y-3">
            {(dashboard.top_clientes ?? []).map((cliente, index) => (
              <div key={cliente.id} className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{cliente.nome}</h3>
                </div>
                <span className="font-bold text-green-400">
                  {formatarMoeda(cliente.total)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
      </div>
    </PageWrapper>
  )
}
