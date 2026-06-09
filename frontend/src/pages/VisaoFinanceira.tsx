import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { DataTable } from '@/components/comum/DataTable'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { EstadoVazio } from '@/components/comum/EstadoVazio'
import { StatCard } from '@/components/comum/StatCard'
import { 
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  ArrowUpRight
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface Transacao {
  id: string
  descricao: string
  tipo: string
  valor: number
  status: string
  data_vencimento: string
  data_pagamento: string
  categoria_id: string
  criado_em: string
}

interface DashboardFinanceiroBackend {
  periodo: {
    data_inicio: string
    data_fim: string
  }
  realizado: {
    receitas: number
    despesas: number
    saldo: number
  }
  pendente: {
    receitas: number
    despesas: number
  }
  atrasado: {
    receitas: number
    despesas: number
  }
}

interface DashboardFinanceiro {
  receita_total: number
  despesa_total: number
  lucro: number
  pagamentos_pendentes: number
  pagamentos_atrasados: number
}

interface ReceitaDespesaMes {
  mes: string
  receita: number
  despesa: number
}

interface DistribuicaoCategoria {
  categoria: string
  valor: number
  cor: string
}

export function VisaoFinanceira() {
  const { data: dashboardBackend } = useQuery<DashboardFinanceiroBackend>({
    queryKey: ['financeiro-dashboard'],
    queryFn: async () => {
      const response = await api.get('/financeiro/dashboard')
      return response.data
    }
  })

  const { data: transacoes, isLoading: isLoadingTransacoes } = useQuery<Transacao[]>({
    queryKey: ['transacoes'],
    queryFn: async () => {
      const response = await api.get('/financeiro/transacoes', { params: { limit: 5 } })
      return response.data
    }
  })

  const { data: dadosReceitasDespesas } = useQuery<ReceitaDespesaMes[]>({
    queryKey: ['grafico-receitas-despesas-mes'],
    queryFn: async () => {
      const response = await api.get('/financeiro/grafico/receitas-despesas-mes')
      return response.data
    }
  })

  const { data: dadosDistribuicao } = useQuery<DistribuicaoCategoria[]>({
    queryKey: ['grafico-distribuicao-categoria'],
    queryFn: async () => {
      const response = await api.get('/financeiro/grafico/distribuicao-categoria')
      return response.data
    }
  })

  // Mapear dados do backend para o formato esperado pelo frontend
  const dashboard: DashboardFinanceiro | undefined = dashboardBackend ? {
    receita_total: dashboardBackend.realizado.receitas || 0,
    despesa_total: dashboardBackend.realizado.despesas || 0,
    lucro: dashboardBackend.realizado.saldo || 0,
    pagamentos_pendentes: (dashboardBackend.pendente.receitas || 0) + (dashboardBackend.pendente.despesas || 0),
    pagamentos_atrasados: (dashboardBackend.atrasado.receitas || 0) + (dashboardBackend.atrasado.despesas || 0)
  } : undefined

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

  const formatarMes = (mes: string) => {
    const [ano, mesNum] = mes.split('-')
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return `${meses[parseInt(mesNum) - 1]}/${ano.slice(-2)}`
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B']

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Visão Financeira</h1>
            <p className="text-muted-foreground">
              Resumo geral das finanças do negócio
            </p>
          </div>
        </div>

        {/* Cards de Estatísticas */}
        {dashboard && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Receita Total"
              value={formatarMoeda(dashboard.receita_total)}
              icon={<DollarSign className="w-5 h-5 text-green-400" />}
            />
            <StatCard
              title="Despesa Total"
              value={formatarMoeda(dashboard.despesa_total)}
              icon={<DollarSign className="w-5 h-5 text-red-400" />}
            />
            <StatCard
              title="Lucro"
              value={formatarMoeda(dashboard.lucro)}
              icon={dashboard.lucro >= 0 ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
            />
            <StatCard
              title="Pagamentos Pendentes"
              value={formatarMoeda(dashboard.pagamentos_pendentes)}
              icon={<Calendar className="w-5 h-5 text-yellow-400" />}
            />
          </div>
        )}

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4">Receitas x Despesas por Mês</h3>
            <div className="h-64">
              {dadosReceitasDespesas && dadosReceitasDespesas.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dadosReceitasDespesas}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      dataKey="mes" 
                      tickFormatter={formatarMes}
                      stroke="#888888"
                      fontSize={12}
                    />
                    <YAxis 
                      tickFormatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
                      stroke="#888888"
                      fontSize={12}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(30, 30, 30, 0.9)', 
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '8px'
                      }}
                      labelFormatter={formatarMes}
                      formatter={(value: number) => formatarMoeda(value)}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="receita" 
                      name="Receitas" 
                      stroke="#10B981" 
                      strokeWidth={2}
                      dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="despesa" 
                      name="Despesas" 
                      stroke="#EF4444" 
                      strokeWidth={2}
                      dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Sem dados disponíveis</p>
                  </div>
                </div>
              )}
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4">Distribuição por Categoria</h3>
            <div className="h-64">
              {dadosDistribuicao && dadosDistribuicao.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dadosDistribuicao}
                      cx="35%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="valor"
                    >
                      {dadosDistribuicao.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.cor || COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(30, 30, 30, 0.9)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number, _name: any, props: any) => {
                        return [formatarMoeda(value), props.payload.categoria]
                      }}
                    />
                    <Legend
                      layout="vertical"
                      verticalAlign="middle"
                      align="right"
                      wrapperStyle={{ paddingLeft: '10px', fontSize: '12px' }}
                      formatter={(value, entry) => {
                        if (!entry?.payload) return value
                        const total = dadosDistribuicao.reduce((acc, d) => acc + d.valor, 0)
                        const percent = ((entry.payload.value / total) * 100).toFixed(0)
                        return (
                          <span style={{ color: '#ccc', fontSize: '12px' }}>
                            {entry.payload.categoria} ({percent}%)
                          </span>
                        )
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <ArrowUpRight className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Sem dados disponíveis</p>
                  </div>
                </div>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Tabela Resumida - Últimas Transações */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold mb-4">Últimas Transações</h3>
          {isLoadingTransacoes ? (
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
              ]}
              data={transacoes}
            />
          ) : (
            <EstadoVazio
              icon={<DollarSign className="w-12 h-12" />}
              titulo="Nenhuma transação encontrada"
              descricao="Não há transações registradas no sistema"
            />
          )}
        </GlassCard>
      </div>
    </PageWrapper>
  )
}
