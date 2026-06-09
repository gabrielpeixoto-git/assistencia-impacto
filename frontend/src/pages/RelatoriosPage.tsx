import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/comum/GlassCard'
import { StatCard } from '@/components/comum/StatCard'
import CustomSelect from '@/components/ui/CustomSelect'
import { 
  FileText,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Calendar,
  Download,
  Package
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend
} from 'recharts'

interface RelatorioFinanceiro {
  realizado: {
    receitas: number
    despesas: number
    saldo: number
  }
}

interface DashboardResumo {
  os_por_status: { status: string; quantidade: number }[]
  grafico_receita: { data: string; receita: number; despesas: number }[]
  top_tecnicos: { tecnico_id: string; nome: string; quantidade: number }[]
}

interface RelatorioOrcamentos {
  total: number
  aprovados: number
  pendentes: number
  rejeitados: number
  taxa_conversao: number
}

interface ItemEstoque {
  id: string
  nome: string
  sku: string
  estoque_atual: number
  estoque_minimo: number
  custo_unitario: number
  unidade: string
  categoria_id: string
  ativo: boolean
}

export function RelatoriosPage() {
  const [periodo, setPeriodo] = useState('trimestre')
  const [abaAtiva, setAbaAtiva] = useState('financeiro')

  const { data: financeiro } = useQuery<RelatorioFinanceiro>({
    queryKey: ['relatorio-financeiro', periodo],
    queryFn: async () => {
      const response = await api.get('/financeiro/dashboard', { params: { periodo } })
      return response.data
    }
  })

  const { data: dashboard } = useQuery<DashboardResumo>({
    queryKey: ['dashboard-resumo', periodo],
    queryFn: async () => {
      const response = await api.get('/dashboard/resumo', { params: { periodo } })
      return response.data
    }
  })

  const { data: tendenciaReceita } = useQuery<{ data: string; receita: number; despesas: number }[]>({
    queryKey: ['financeiro-tendencia', periodo],
    queryFn: async () => {
      const response = await api.get('/financeiro/grafico/tendencia', { params: { periodo } })
      return response.data
    }
  })

  const { data: orcamentos } = useQuery<RelatorioOrcamentos>({
    queryKey: ['relatorio-orcamentos', periodo],
    queryFn: async () => {
      const response = await api.get('/orcamentos/resumo', { params: { periodo } })
      return response.data
    }
  })

  const { data: estoqueCritico, isLoading: isLoadingEstoque } = useQuery<ItemEstoque[]>({
    queryKey: ['estoque-critico'],
    queryFn: async () => {
      const response = await api.get('/estoque/itens', { params: { estoque_baixo: true, limit: 50 } })
      return response.data
    },
    enabled: abaAtiva === 'estoque'
  })

  const formatarMoeda = (valor: number | undefined | null) => {
    const safeValue = valor ?? 0
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(safeValue)
  }

  // Processar dados de ordens de serviço por status
  const ordensPorStatus = dashboard?.os_por_status || []
  const osStats = {
    total: ordensPorStatus.reduce((acc, item) => acc + item.quantidade, 0),
    concluidas: ordensPorStatus.find(o => o.status === 'concluida')?.quantidade || 0,
    em_andamento: ordensPorStatus.find(o => o.status === 'em_andamento')?.quantidade || 0,
    pendentes: ordensPorStatus.find(o => o.status === 'pendente')?.quantidade || 0,
    canceladas: ordensPorStatus.find(o => o.status === 'cancelada')?.quantidade || 0
  }

  // Calcular margem de lucro
  const receita = financeiro?.realizado?.receitas ?? 0
  const despesa = financeiro?.realizado?.despesas ?? 0
  const lucro = financeiro?.realizado?.saldo ?? (receita - despesa)
  const margemLucro = receita > 0 ? ((lucro / receita) * 100) : 0

  const handleExportarRelatorio = async () => {
    try {
      // Buscar todos os dados para o período selecionado
      const [financeiroRes, dashboardRes, orcamentosRes] = await Promise.all([
        api.get('/financeiro/dashboard', { params: { periodo } }),
        api.get('/dashboard/resumo', { params: { periodo } }),
        api.get('/orcamentos/resumo', { params: { periodo } })
      ])

      const financeiroData = financeiroRes.data
      const dashboardData = dashboardRes.data
      const orcamentosData = orcamentosRes.data

      // Criar conteúdo CSV
      let csvContent = 'RELATÓRIO FINANCEIRO\n'
      csvContent += `Período;${periodo}\n`
      csvContent += `Receita Total;${formatarMoeda(financeiroData.realizado?.receitas ?? 0)}\n`
      csvContent += `Despesa Total;${formatarMoeda(financeiroData.realizado?.despesas ?? 0)}\n`
      csvContent += `Lucro;${formatarMoeda(financeiroData.realizado?.saldo ?? 0)}\n\n`

      csvContent += 'ORDENS DE SERVIÇO\n'
      csvContent += `Total;${dashboardData.os_por_status?.reduce((acc: number, item: any) => acc + item.quantidade, 0) ?? 0}\n`
      dashboardData.os_por_status?.forEach((item: any) => {
        csvContent += `${item.status};${item.quantidade}\n`
      })
      csvContent += '\n'

      csvContent += 'ORÇAMENTOS\n'
      csvContent += `Total;${orcamentosData.total ?? 0}\n`
      csvContent += `Aprovados;${orcamentosData.aprovados ?? 0}\n`
      csvContent += `Pendentes;${orcamentosData.pendentes ?? 0}\n`
      csvContent += `Rejeitados;${orcamentosData.rejeitados ?? 0}\n`
      csvContent += `Taxa de Conversão;${orcamentosData.taxa_conversao ?? 0}%\n\n`

      csvContent += 'GRÁFICO DE RECEITA\n'
      csvContent += 'Data;Valor\n'
      dashboardData.grafico_receita?.forEach((item: any) => {
        csvContent += `${item.data};${formatarMoeda(item.valor)}\n`
      })

      // Criar blob e fazer download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `relatorio_${periodo}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Erro ao exportar relatório:', error)
      alert('Erro ao exportar relatório. Tente novamente.')
    }
  }

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Relatórios</h1>
            <p className="text-muted-foreground">
              Visualize métricas e estatísticas do sistema
            </p>
          </div>
          <div className="flex gap-4">
            <CustomSelect
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value)}
            >
              <option value="hoje">Hoje</option>
              <option value="semana">Esta Semana</option>
              <option value="mes">Este Mês</option>
              <option value="trimestre">Este Trimestre</option>
              <option value="ano">Este Ano</option>
            </CustomSelect>
            <button
              onClick={handleExportarRelatorio}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Download className="w-5 h-5" />
              Exportar
            </button>
          </div>
        </div>

        {/* Abas */}
        <div className="flex gap-2 border-b border-white/10">
          <button
            onClick={() => setAbaAtiva('financeiro')}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              abaAtiva === 'financeiro'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            Financeiro
          </button>
          <button
            onClick={() => setAbaAtiva('ordens')}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              abaAtiva === 'ordens'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <FileText className="w-4 h-4" />
            Ordens de Serviço
          </button>
          <button
            onClick={() => setAbaAtiva('tecnicos')}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              abaAtiva === 'tecnicos'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Users className="w-4 h-4" />
            Técnicos
          </button>
          <button
            onClick={() => setAbaAtiva('estoque')}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              abaAtiva === 'estoque'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Package className="w-4 h-4" />
            Estoque
          </button>
        </div>

        {/* Conteúdo das Abas */}
        {abaAtiva === 'financeiro' && (
          <div className="space-y-6">
            {/* Cards de Resumo Financeiro */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Receita Total"
                value={formatarMoeda(receita)}
                icon={<DollarSign className="w-5 h-5 text-green-400" />}
              />
              <StatCard
                title="Despesa Total"
                value={formatarMoeda(despesa)}
                icon={<DollarSign className="w-5 h-5 text-red-400" />}
              />
              <StatCard
                title="Lucro"
                value={formatarMoeda(lucro)}
                icon={lucro >= 0 ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
              />
              <StatCard
                title="Margem de Lucro"
                value={`${margemLucro.toFixed(1)}%`}
                icon={<TrendingUp className="w-5 h-5 text-blue-400" />}
              />
            </div>

            {/* Gráfico de Receita */}
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Tendência de Receita
              </h2>
              {dashboard?.grafico_receita && dashboard.grafico_receita.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboard.grafico_receita}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-white/10" />
                    <XAxis
                      dataKey="data"
                      className="text-xs"
                      stroke="hsl(var(--muted-foreground))"
                    />
                    <YAxis
                      className="text-xs"
                      stroke="hsl(var(--muted-foreground))"
                      tickFormatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
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
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  Sem dados disponíveis
                </p>
              )}
            </GlassCard>
          </div>
        )}

        {abaAtiva === 'ordens' && (
          <div className="space-y-6">
            {/* Cards de Resumo de Ordens */}
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Ordens de Serviço por Status
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 bg-white/10 rounded-lg">
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{osStats.total}</p>
                </div>
                <div className="p-4 bg-green-500/10 rounded-lg">
                  <p className="text-sm text-green-400">Concluídas</p>
                  <p className="text-2xl font-bold text-green-400">{osStats.concluidas}</p>
                </div>
                <div className="p-4 bg-blue-500/10 rounded-lg">
                  <p className="text-sm text-blue-400">Em Andamento</p>
                  <p className="text-2xl font-bold text-blue-400">{osStats.em_andamento}</p>
                </div>
                <div className="p-4 bg-yellow-500/10 rounded-lg">
                  <p className="text-sm text-yellow-400">Pendentes</p>
                  <p className="text-2xl font-bold text-yellow-400">{osStats.pendentes}</p>
                </div>
                <div className="p-4 bg-red-500/10 rounded-lg">
                  <p className="text-sm text-red-400">Canceladas</p>
                  <p className="text-2xl font-bold text-red-400">{osStats.canceladas}</p>
                </div>
              </div>
            </GlassCard>

            {/* Cards de Resumo de Orçamentos */}
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Orçamentos
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 bg-white/10 rounded-lg">
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{orcamentos?.total ?? 0}</p>
                </div>
                <div className="p-4 bg-green-500/10 rounded-lg">
                  <p className="text-sm text-green-400">Aprovados</p>
                  <p className="text-2xl font-bold text-green-400">{orcamentos?.aprovados ?? 0}</p>
                </div>
                <div className="p-4 bg-yellow-500/10 rounded-lg">
                  <p className="text-sm text-yellow-400">Pendentes</p>
                  <p className="text-2xl font-bold text-yellow-400">{orcamentos?.pendentes ?? 0}</p>
                </div>
                <div className="p-4 bg-red-500/10 rounded-lg">
                  <p className="text-sm text-red-400">Rejeitados</p>
                  <p className="text-2xl font-bold text-red-400">{orcamentos?.rejeitados ?? 0}</p>
                </div>
                <div className="p-4 bg-blue-500/10 rounded-lg">
                  <p className="text-sm text-blue-400">Taxa de Conversão</p>
                  <p className="text-2xl font-bold text-blue-400">{`${orcamentos?.taxa_conversao ?? 0}%`}</p>
                </div>
              </div>
            </GlassCard>
          </div>
        )}

        {abaAtiva === 'tecnicos' && (
          <div className="space-y-6">
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Users className="w-5 h-5" />
                Desempenho da Equipe (Top Técnicos)
              </h2>
              {dashboard?.top_tecnicos && dashboard.top_tecnicos.length > 0 ? (
                <div style={{ width: '100%', height: '350px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dashboard.top_tecnicos} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                      <XAxis
                        type="number"
                        tick={{ fill: '#9CA3AF', fontSize: 12 }}
                        stroke="#9CA3AF"
                        allowDecimals={false}
                        domain={[0, 'dataMax']}
                        tickFormatter={(value) => Math.round(value).toString()}
                      />
                      <YAxis
                        type="category"
                        dataKey="nome"
                        tick={{ fill: '#9CA3AF', fontSize: 12 }}
                        stroke="#9CA3AF"
                        width={120}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1F2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#F9FAFB'
                        }}
                        formatter={(value: number) => [value, 'OS Concluídas']}
                      />
                      <Bar
                        dataKey="quantidade"
                        fill="#10B981"
                        radius={[0, 4, 4, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  Sem dados disponíveis
                </p>
              )}
            </GlassCard>
          </div>
        )}

        {abaAtiva === 'estoque' && (
          <div className="space-y-6">
            {/* Cards de Resumo de Estoque */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard
                title="Itens com Estoque Baixo"
                value={estoqueCritico?.length ?? 0}
                icon={<Package className="w-5 h-5 text-yellow-400" />}
              />
              <StatCard
                title="Valor Total em Estoque"
                value={formatarMoeda(estoqueCritico?.reduce((acc, item) => acc + (item.estoque_atual * item.custo_unitario), 0) ?? 0)}
                icon={<DollarSign className="w-5 h-5 text-green-400" />}
              />
              <StatCard
                title="Itens Críticos"
                value={estoqueCritico?.filter(item => item.estoque_atual === 0)?.length ?? 0}
                icon={<TrendingDown className="w-5 h-5 text-red-400" />}
              />
            </div>

            {/* Tabela de Itens com Estoque Baixo */}
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Package className="w-5 h-5" />
                Itens com Estoque Crítico
              </h2>
              {isLoadingEstoque ? (
                <div className="text-center py-8">
                  <p>Carregando dados de estoque...</p>
                </div>
              ) : estoqueCritico && estoqueCritico.length > 0 ? (
                <div className="space-y-3">
                  {estoqueCritico.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                          <Package className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{item.nome}</p>
                          <p className="text-sm text-muted-foreground">SKU: {item.sku}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold ${item.estoque_atual === 0 ? 'text-red-400' : 'text-yellow-400'}`}>
                          {item.estoque_atual} {item.unidade}
                        </p>
                        <p className="text-sm text-muted-foreground">Mínimo: {item.estoque_minimo} {item.unidade}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Nenhum item com estoque crítico</p>
                </div>
              )}
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
