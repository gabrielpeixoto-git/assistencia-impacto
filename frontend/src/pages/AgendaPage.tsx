import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, addMonths, subMonths, isToday } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/ui/GlassCard'
import { Button } from '@/components/ui/Button'
import { Plus, ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, MapPin, Wrench, Users, Settings, XCircle, Calendar, X, Edit, Trash2 } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

// Ícones por tipo
const ICONES_EVENTO = {
  servico: Wrench,
  reuniao: Users,
  manutencao: Settings,
  indisponivel: XCircle,
  outro: Calendar,
}

type ViewMode = 'mes' | 'semana' | 'lista'
type Evento = {
  id: string
  titulo: string
  tecnico_id: string
  cliente_id?: string
  data_hora_inicio: string
  data_hora_fim: string
  tipo_evento: 'servico' | 'reuniao' | 'manutencao' | 'indisponivel' | 'outro'
  cor: string
  cor_tecnico?: string
  endereco?: string
  observacoes?: string
  status: string
  tecnico_nome?: string
  cliente_nome?: string
}

// Helper para obter a cor do evento (prioriza cor do técnico)
const getCorEvento = (evento: Evento) => evento.cor_tecnico || evento.cor

// Helper para converter UTC para BRT na exibição
const formatarHorarioBRT = (dataISO: string, formato: string) => {
  const data = new Date(dataISO)
  
  // Para formatos de hora (HH:mm):
  if (formato === 'HH:mm') {
    return data.toLocaleTimeString('pt-BR', {
      timeZone: 'America/Sao_Paulo',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }
  
  // Para formatos de data (dd/MM/yyyy):
  if (formato === 'dd/MM/yyyy' || formato === "dd/MM/yyyy 'às' HH:mm") {
    return data.toLocaleString('pt-BR', {
      timeZone: 'America/Sao_Paulo',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: formato.includes('HH:mm') ? '2-digit' : undefined,
      minute: formato.includes('HH:mm') ? '2-digit' : undefined,
    }).replace(',', ' às')
  }
  
  // Para formatos de data extensa (EEEE, d 'de' MMMM):
  if (formato.includes('MMMM') || formato.includes('EEEE')) {
    // Usar date-fns com offset manual para BRT
    const offsetBRT = -3 * 60 // UTC-3 em minutos
    const dataLocal = new Date(data.getTime() + (data.getTimezoneOffset() + offsetBRT * -1) * 60000)
    return format(dataLocal, formato, { locale: ptBR })
  }
  
  // Para formatos de chave yyyy-MM-dd:
  const dataBRT = new Date(data.toLocaleString('en-US', { timeZone: 'America/Sao_Paulo' }))
  return format(dataBRT, formato, { locale: ptBR })
}

export function AgendaPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('mes')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [tecnicoFiltro, setTecnicoFiltro] = useState<string | null>(null)
  const [eventoSelecionado, setEventoSelecionado] = useState<Evento | null>(null)
  const [panelAberto, setPanelAberto] = useState(false)
  const [modalAberto, setModalAberto] = useState(false)
  const [modalDia, setModalDia] = useState<Date | null>(null)
  const [modalEventos, setModalEventos] = useState<Evento[]>([])
  const [modalEventosAberto, setModalEventosAberto] = useState(false)
  const [eventoEditando, setEventoEditando] = useState<Evento | null>(null)
  const [formData, setFormData] = useState({
    titulo: '',
    tecnico_id: '',
    cliente_id: '',
    data_hora_inicio: '',
    data_hora_fim: '',
    tipo_evento: 'servico' as 'servico' | 'reuniao' | 'manutencao' | 'indisponivel' | 'outro',
    cor: '#6C63FF',
    endereco: '',
    observacoes: '',
  })
  const [erro, setErro] = useState('')
  const { toast } = useToast()

  // Buscar técnicos
  const { data: tecnicos } = useQuery({
    queryKey: ['tecnicos'],
    queryFn: async () => {
      const response = await api.get('/usuarios/')
      return response.data.filter((u: any) => u.perfil === 'tecnico')
    },
  })

  // Buscar clientes
  const { data: clientes } = useQuery({
    queryKey: ['clientes'],
    queryFn: async () => {
      const response = await api.get('/clientes')
      return response.data.dados
    },
  })

  // Buscar eventos da agenda
  const { data: eventos, isLoading, refetch: refetchEventos } = useQuery({
    queryKey: ['agenda', format(currentDate, 'yyyy-MM'), tecnicoFiltro],
    queryFn: async () => {
      const params: any = {
        de: startOfMonth(currentDate).toISOString(),
        ate: endOfMonth(currentDate).toISOString(),
      }
      if (tecnicoFiltro) {
        params.tecnico_id = tecnicoFiltro
      }
      const response = await api.get('/agenda', { params })
      return response.data
    },
  })

  // Mapa de eventos por data
  const eventosPorDia = useMemo(() => {
    const mapa = new Map<string, Evento[]>()
    eventos?.forEach((evento: Evento) => {
      const chave = formatarHorarioBRT(evento.data_hora_inicio, 'yyyy-MM-dd')
      if (!mapa.has(chave)) mapa.set(chave, [])
      mapa.get(chave)!.push(evento)
    })
    return mapa
  }, [eventos])

  // Criar evento
  const criarEventoMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post('/agenda', data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Evento criado com sucesso' })
      setModalAberto(false)
      limparFormulario()
      refetchEventos()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao criar evento')
    },
  })

  // Atualizar evento
  const atualizarEventoMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await api.put(`/agenda/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Evento atualizado com sucesso' })
      setModalAberto(false)
      limparFormulario()
      refetchEventos()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao atualizar evento')
    },
  })

  // Excluir evento
  const excluirEventoMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/agenda/${id}`)
    },
    onSuccess: () => {
      toast({ title: 'Evento excluído com sucesso' })
      setPanelAberto(false)
      setEventoSelecionado(null)
      refetchEventos()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao excluir evento')
    },
  })

  const limparFormulario = () => {
    setFormData({
      titulo: '',
      tecnico_id: '',
      cliente_id: '',
      data_hora_inicio: '',
      data_hora_fim: '',
      tipo_evento: 'servico',
      cor: '#6C63FF',
      endereco: '',
      observacoes: '',
    })
    setEventoEditando(null)
    setErro('')
  }

  const handleSalvarEvento = () => {
    if (!formData.titulo || !formData.data_hora_inicio || !formData.data_hora_fim || !formData.tecnico_id) {
      setErro('Preencha os campos obrigatórios')
      return
    }
    if (eventoEditando) {
      atualizarEventoMutation.mutate({ id: eventoEditando.id, data: formData })
    } else {
      criarEventoMutation.mutate(formData)
    }
  }

  const handleEditarEvento = (evento: Evento) => {
    setEventoEditando(evento)
    setFormData({
      titulo: evento.titulo,
      tecnico_id: evento.tecnico_id,
      cliente_id: evento.cliente_id || '',
      data_hora_inicio: evento.data_hora_inicio,
      data_hora_fim: evento.data_hora_fim,
      tipo_evento: evento.tipo_evento,
      cor: evento.cor,
      endereco: evento.endereco || '',
      observacoes: evento.observacoes || '',
    })
    setModalAberto(true)
    setPanelAberto(false)
  }

  const handleExcluirEvento = (evento: Evento) => {
    if (confirm('Tem certeza que deseja excluir este evento?')) {
      excluirEventoMutation.mutate(evento.id)
    }
  }

  const handleNovoEvento = () => {
    limparFormulario()
    setModalAberto(true)
  }

  // Navegação de mês
  const mesAnterior = () => setCurrentDate(subMonths(currentDate, 1))
  const proximoMes = () => setCurrentDate(addMonths(currentDate, 1))
  const irParaHoje = () => setCurrentDate(new Date())

  // Dias do mês para visualização
  const diasDoMes = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentDate), { weekStartsOn: 0 })
    const end = endOfWeek(endOfMonth(currentDate), { weekStartsOn: 0 })
    return eachDayOfInterval({ start, end })
  }, [currentDate])

  // Dias da semana para visualização semana
  const diasDaSemana = useMemo(() => {
    const start = startOfWeek(currentDate, { weekStartsOn: 0 })
    return eachDayOfInterval({ start, end: new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000) })
  }, [currentDate])

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="space-y-6"
        data-testid="agenda-container"
      >
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={mesAnterior}
              className="hover:bg-white/10"
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            <h2 className="text-2xl font-bold min-w-[200px]">
              {format(currentDate, 'MMMM yyyy', { locale: ptBR })}
            </h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={proximoMes}
              className="hover:bg-white/10"
            >
              <ChevronRight className="w-5 h-5" />
            </Button>
            <Button
              variant="outline"
              onClick={irParaHoje}
              className="ml-2"
            >
              Hoje
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex bg-white/5 rounded-lg p-1">
              {(['mes', 'semana', 'lista'] as ViewMode[]).map((mode) => (
                <Button
                  key={mode}
                  variant={viewMode === mode ? 'default' : 'ghost'}
                  onClick={() => setViewMode(mode)}
                  className="capitalize text-sm px-3 py-1"
                >
                  {mode}
                </Button>
              ))}
            </div>
            <Button
              onClick={handleNovoEvento}
              className="bg-gradient-to-r from-[#6C63FF] to-[#00D4FF] hover:opacity-90"
              data-testid="btn-novo-evento"
            >
              <Plus className="w-4 h-4 mr-2" />
              Novo Evento
            </Button>
          </div>
        </div>

        {/* Filtro de técnicos */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setTecnicoFiltro(null)}
            className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
              tecnicoFiltro === null
                ? 'bg-[#6C63FF] text-white ring-2 ring-[#6C63FF] ring-offset-2 ring-offset-[#0A0B0F]'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            Todos
          </button>
          {tecnicos?.map((tecnico: any) => {
            // Determinar cor do técnico
            const nomeLower = tecnico.nome_completo.toLowerCase();
            let cor = '#6C63FF';
            if (nomeLower.includes('jo')) cor = '#6C63FF';
            else if (nomeLower.includes('maria')) cor = '#00D4FF';
            else if (nomeLower.includes('carlos')) cor = '#10B981';

            return (
              <button
                key={tecnico.id}
                onClick={() => setTecnicoFiltro(tecnico.id === tecnicoFiltro ? null : tecnico.id)}
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all border-2 ${
                  tecnicoFiltro === tecnico.id
                    ? 'text-white'
                    : 'text-white/70 hover:bg-white/20'
                }`}
                style={{
                  borderColor: cor,
                  backgroundColor: tecnicoFiltro === tecnico.id ? cor : cor + '20',
                  color: tecnicoFiltro === tecnico.id ? '#FFFFFF' : cor,
                  boxShadow: tecnicoFiltro === tecnico.id ? `0 0 12px ${cor}60` : 'none',
                }}
                title={tecnico.nome_completo}
              >
                {tecnico.nome_completo.charAt(0)}
              </button>
            );
          })}
        </div>

        {/* Conteúdo principal */}
        {isLoading ? (
          <GlassCard className="p-12">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-white/10 rounded w-1/4" />
              <div className="h-32 bg-white/10 rounded" />
              <div className="h-32 bg-white/10 rounded" />
            </div>
          </GlassCard>
        ) : viewMode === 'mes' ? (
          <VisualizacaoMes
            dias={diasDoMes}
            currentDate={currentDate}
            eventosPorDia={eventosPorDia}
            onEventoClick={(evento) => {
              setEventoSelecionado(evento)
              setPanelAberto(true)
            }}
            onDiaClick={(dia) => {
              const eventosDoDia = eventosPorDia.get(format(dia, 'yyyy-MM-dd'))
              if (eventosDoDia && eventosDoDia.length > 0) {
                setEventoSelecionado(eventosDoDia[0])
                setPanelAberto(true)
              }
            }}
            onMaisClick={(dia: Date, eventos: Evento[]) => {
              setModalDia(dia)
              setModalEventos(eventos)
              setModalEventosAberto(true)
            }}
          />
        ) : viewMode === 'semana' ? (
          <VisualizacaoSemana
            dias={diasDaSemana}
            eventosPorDia={eventosPorDia}
            onEventoClick={(evento) => {
              setEventoSelecionado(evento)
              setPanelAberto(true)
            }}
          />
        ) : (
          <VisualizacaoLista
            eventos={eventos || []}
            onEventoClick={(evento) => {
              setEventoSelecionado(evento)
              setPanelAberto(true)
            }}
          />
        )}

        {/* Painel lateral de detalhes */}
        <AnimatePresence>
          {panelAberto && eventoSelecionado && (
            <PainelDetalhes
              evento={eventoSelecionado}
              onClose={() => {
                setPanelAberto(false)
                setEventoSelecionado(null)
              }}
              onEditar={handleEditarEvento}
              onExcluir={handleExcluirEvento}
            />
          )}
        </AnimatePresence>

        {/* Modal de novo/editar evento */}
        <AnimatePresence>
          {modalAberto && (
            <ModalEvento
              eventoEditando={eventoEditando}
              formData={formData}
              setFormData={setFormData}
              tecnicos={tecnicos}
              clientes={clientes}
              erro={erro}
              onClose={() => {
                setModalAberto(false)
                limparFormulario()
              }}
              onSave={handleSalvarEvento}
              isPending={criarEventoMutation.isPending || atualizarEventoMutation.isPending}
            />
          )}
        </AnimatePresence>

        {/* Modal: Todos os eventos do dia */}
        <AnimatePresence>
          {modalEventosAberto && modalDia && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
              onClick={() => setModalEventosAberto(false)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-[#1A1D27] border border-white/10 rounded-2xl p-6 w-full max-w-md
                           shadow-2xl max-h-[80vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-white font-semibold text-lg">
                      {format(modalDia, "EEEE, d 'de' MMMM", { locale: ptBR })}
                    </h3>
                    <p className="text-slate-400 text-sm">{modalEventos.length} eventos</p>
                  </div>
                  <button
                    onClick={() => setModalEventosAberto(false)}
                    className="text-slate-400 hover:text-white transition-colors p-1 rounded-lg
                               hover:bg-white/10"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Event list */}
                <div className="space-y-2">
                  {modalEventos.map((evento) => {
                    const inicio = evento.data_hora_inicio
                      ? new Date(evento.data_hora_inicio).toLocaleTimeString('pt-BR', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : ''
                    return (
                      <button
                        key={evento.id}
                        onClick={() => {
                          setEventoSelecionado(evento)
                          setPanelAberto(true)
                          setModalEventosAberto(false)
                        }}
                        className="w-full text-left p-3 rounded-xl border border-white/10
                                   hover:bg-white/5 transition-all group"
                        style={{ borderLeftColor: getCorEvento(evento), borderLeftWidth: 3 }}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400 font-mono text-xs">{inicio}</span>
                          <span className="text-white text-sm font-medium group-hover:text-violet-300
                                           transition-colors truncate">
                            {evento.titulo}
                          </span>
                        </div>
                        {evento.tecnico_nome && (
                          <p className="text-slate-500 text-xs mt-0.5 ml-9">{evento.tecnico_nome}</p>
                        )}
                      </button>
                    )
                  })}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </PageWrapper>
  )
}

// Componente: Visualização Mês
function VisualizacaoMes({
  dias,
  currentDate,
  eventosPorDia,
  onEventoClick,
  onDiaClick,
  onMaisClick,
}: {
  dias: Date[]
  currentDate: Date
  eventosPorDia: Map<string, Evento[]>
  onEventoClick: (evento: Evento) => void
  onDiaClick: (dia: Date) => void
  onMaisClick: (dia: Date, eventos: Evento[]) => void
}) {
  const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

  return (
    <GlassCard className="p-6">
      <div className="grid grid-cols-7 gap-2 mb-2">
        {diasSemana.map((dia) => (
          <div key={dia} className="text-center text-sm font-medium text-white/60">
            {dia}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-2">
        {dias.map((dia) => {
          const chave = format(dia, 'yyyy-MM-dd')
          const eventosDoDia = eventosPorDia.get(chave) || []
          const ehHoje = isToday(dia)
          const ehMesAtual = isSameMonth(dia, currentDate)

          return (
            <motion.button
              key={chave}
              onClick={() => onDiaClick(dia)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`
                aspect-square rounded-lg p-2 text-left transition-all
                ${ehHoje ? 'bg-[#6C63FF]/20 border-2 border-[#6C63FF]' : ''}
                ${!ehMesAtual ? 'opacity-30' : ''}
                ${ehMesAtual && !ehHoje ? 'bg-white/5 hover:bg-white/10' : ''}
              `}
            >
              <div className="text-sm font-medium mb-1">{format(dia, 'd')}</div>
              <div className="space-y-1">
                {eventosDoDia.slice(0, 3).map((evento) => {
                  const inicio = formatarHorarioBRT(evento.data_hora_inicio, 'HH:mm');
                  const cor = getCorEvento(evento);
                  // Determinar o label do título baseado no tipo de evento
                  let displayTitle = evento.titulo;
                  if (evento.tipo_evento === 'servico' && evento.cliente_nome) {
                    displayTitle = evento.cliente_nome;
                  }
                  return (
                    <motion.button
                      key={evento.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onEventoClick(evento);
                      }}
                      whileHover={{ scale: 1.02 }}
                      className="text-xs px-1.5 py-0.5 rounded truncate text-left w-full"
                      style={{
                        backgroundColor: cor + '22',
                        borderLeft: `2px solid ${cor}`,
                        color: '#F1F5F9',
                      }}
                    >
                      <span className="font-mono text-[10px] opacity-80">{inicio}</span> {displayTitle}
                    </motion.button>
                  );
                })}
                {eventosDoDia.length > 3 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onMaisClick(dia, eventosDoDia)
                    }}
                    className="text-xs text-violet-400 hover:text-violet-300 font-medium px-1 py-0.5
                               hover:bg-white/5 rounded transition-colors cursor-pointer w-full text-left"
                  >
                    +{eventosDoDia.length - 3} mais
                  </button>
                )}
              </div>
            </motion.button>
          )
        })}
      </div>
    </GlassCard>
  )
}

// Componente: Visualização Semana
function VisualizacaoSemana({
  dias,
  eventosPorDia,
  onEventoClick,
}: {
  dias: Date[]
  eventosPorDia: Map<string, Evento[]>
  onEventoClick: (evento: Evento) => void
}) {
  const horas = Array.from({ length: 16 }, (_, i) => i + 7) // 7h às 22h

  return (
    <GlassCard className="p-6">
      <div className="grid grid-cols-8 gap-2">
        <div /> {/* Spacer para eixo Y */}
        {dias.map((dia) => (
          <div key={format(dia, 'yyyy-MM-dd')} className="text-center">
            <div className="text-sm font-medium">{format(dia, 'EEE', { locale: ptBR })}</div>
            <div className="text-lg font-bold">{format(dia, 'd')}</div>
          </div>
        ))}
      </div>
      <div className="mt-4 space-y-2">
        {horas.map((hora) => (
          <div key={hora} className="grid grid-cols-8 gap-2">
            <div className="text-xs text-white/60 text-right pr-2">
              {hora.toString().padStart(2, '0')}:00
            </div>
            {dias.map((dia) => {
              const chave = format(dia, 'yyyy-MM-dd')
              const eventosDoDia = eventosPorDia.get(chave) || []
              const eventosNaHora = eventosDoDia.filter((evento) => {
                const horaInicio = new Date(evento.data_hora_inicio).getHours()
                return horaInicio === hora
              })

              return (
                <div key={chave} className="bg-white/5 rounded min-h-[40px] relative">
                  {eventosNaHora.map((evento) => {
                    const inicio = formatarHorarioBRT(evento.data_hora_inicio, 'HH:mm');
                    const nomeCliente = evento.cliente_nome || evento.titulo.split(' — ')[0] || 'Sem cliente';
                    const cor = getCorEvento(evento);
                    return (
                      <motion.button
                        key={evento.id}
                        onClick={() => onEventoClick(evento)}
                        whileHover={{ scale: 1.02 }}
                        className="absolute inset-0 left-0 right-0 p-1 text-xs rounded truncate"
                        style={{
                          backgroundColor: cor + '22',
                          borderLeft: `2px solid ${cor}`,
                          color: '#F1F5F9',
                        }}
                        title={`${nomeCliente} - ${evento.tecnico_nome || 'Técnico'}\n${evento.endereco || ''}`}
                      >
                        {inicio} - {nomeCliente}
                      </motion.button>
                    );
                  })}
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </GlassCard>
  )
}

// Componente: Visualização Lista
function VisualizacaoLista({
  eventos,
  onEventoClick,
}: {
  eventos: Evento[]
  onEventoClick: (evento: Evento) => void
}) {
  const eventosAgrupados = useMemo(() => {
    const grupos = new Map<string, Evento[]>()
    eventos.forEach((evento) => {
      const chave = formatarHorarioBRT(evento.data_hora_inicio, 'yyyy-MM-dd')
      if (!grupos.has(chave)) grupos.set(chave, [])
      grupos.get(chave)!.push(evento)
    })
    return Array.from(grupos.entries()).sort((a, b) => a[0].localeCompare(b[0]))
  }, [eventos])

  if (eventos.length === 0) {
    return (
      <GlassCard className="p-12 text-center">
        <CalendarIcon className="w-16 h-16 mx-auto mb-4 text-white/30" />
        <p className="text-white/60">Nenhum evento agendado</p>
      </GlassCard>
    )
  }

  return (
    <div className="space-y-6">
      {eventosAgrupados.map(([data, eventosDoDia]) => (
        <div key={data}>
          <h3 className="text-lg font-semibold mb-3 text-white/80">
            {formatarHorarioBRT(data, "EEEE, d 'de' MMMM")}
          </h3>
          <div className="space-y-3">
            {eventosDoDia
              .sort((a, b) => new Date(a.data_hora_inicio).getTime() - new Date(b.data_hora_inicio).getTime())
              .map((evento) => (
                <motion.button
                  key={evento.id}
                  onClick={() => onEventoClick(evento)}
                  whileHover={{ scale: 1.01 }}
                  className="w-full text-left p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all"
                >
                  <div className="flex items-start gap-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center"
                      style={{
                        backgroundColor: getCorEvento(evento) + '22',
                        borderLeft: `3px solid ${getCorEvento(evento)}`,
                      }}
                    >
                      {(() => {
                        const Icon = ICONES_EVENTO[evento.tipo_evento] || Calendar
                        return <Icon className="w-6 h-6" style={{ color: getCorEvento(evento) }} />
                      })()}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg mb-1">{evento.titulo}</h4>
                      <div className="space-y-1 text-sm text-white/60">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>
                            {formatarHorarioBRT(evento.data_hora_inicio, 'HH:mm')} – {formatarHorarioBRT(evento.data_hora_fim, 'HH:mm')}
                          </span>
                        </div>
                        {evento.endereco && (
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span>{evento.endereco}</span>
                          </div>
                        )}
                        {evento.tecnico_nome && (
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            <span>{evento.tecnico_nome}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div
                      className="px-3 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: getCorEvento(evento) + '22',
                        color: getCorEvento(evento),
                      }}
                    >
                      {evento.status}
                    </div>
                  </div>
                </motion.button>
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// Componente: Painel de Detalhes
function PainelDetalhes({
  evento,
  onClose,
  onEditar,
  onExcluir,
}: {
  evento: Evento
  onClose: () => void
  onEditar: (evento: Evento) => void
  onExcluir: (evento: Evento) => void
}) {
  const Icon = ICONES_EVENTO[evento.tipo_evento] || Calendar

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed inset-y-0 right-0 w-[420px] bg-[#111318] border-l border-white/10 z-50 overflow-y-auto"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center"
            style={{
              backgroundColor: getCorEvento(evento) + '22',
              borderLeft: `4px solid ${getCorEvento(evento)}`,
            }}
          >
            <Icon className="w-8 h-8" style={{ color: getCorEvento(evento) }} />
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <h2 className="text-2xl font-bold mb-4">{evento.titulo}</h2>

        <div className="space-y-4">
          <div className="flex items-center gap-3 text-white/80">
            <Clock className="w-5 h-5" />
            <span>
              {formatarHorarioBRT(evento.data_hora_inicio, "dd/MM/yyyy 'às' HH:mm")} – {formatarHorarioBRT(evento.data_hora_fim, 'HH:mm')}
            </span>
          </div>

          {evento.endereco && (
            <div className="flex items-center gap-3 text-white/80">
              <MapPin className="w-5 h-5" />
              <span>{evento.endereco}</span>
            </div>
          )}

          {evento.tecnico_nome && (
            <div className="flex items-center gap-3 text-white/80">
              <Users className="w-5 h-5" />
              <span>{evento.tecnico_nome}</span>
            </div>
          )}

          {evento.cliente_nome && (
            <div className="flex items-center gap-3 text-white/80">
              <Users className="w-5 h-5" />
              <span>Cliente: {evento.cliente_nome}</span>
            </div>
          )}

          <div
            className="inline-block px-3 py-1 rounded-full text-sm font-medium"
            style={{
              backgroundColor: getCorEvento(evento) + '22',
              color: getCorEvento(evento),
            }}
          >
            {evento.status}
          </div>

          {evento.observacoes && (
            <div className="p-4 bg-white/5 rounded-lg">
              <p className="text-sm text-white/60">{evento.observacoes}</p>
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-8">
          <Button
            onClick={() => onEditar(evento)}
            className="flex-1"
            variant="outline"
          >
            <Edit className="w-4 h-4 mr-2" />
            Editar
          </Button>
          <Button
            onClick={() => onExcluir(evento)}
            className="flex-1"
            variant="destructive"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Excluir
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

// Componente: Modal de Evento
function ModalEvento({
  eventoEditando,
  formData,
  setFormData,
  tecnicos,
  clientes,
  erro,
  onClose,
  onSave,
  isPending,
}: {
  eventoEditando: Evento | null
  formData: any
  setFormData: (data: any) => void
  tecnicos: any[]
  clientes: any[]
  erro: string
  onClose: () => void
  onSave: () => void
  isPending: boolean
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-[#111318] border border-white/10 rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">
            {eventoEditando ? 'Editar Evento' : 'Novo Evento'}
          </h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Título *</label>
            <input
              type="text"
              value={formData.titulo}
              onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              placeholder="Título do evento"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Técnico *</label>
              <select
                value={formData.tecnico_id}
                onChange={(e) => setFormData({ ...formData, tecnico_id: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              >
                <option value="">Selecione um técnico</option>
                {tecnicos?.map((tecnico: any) => (
                  <option key={tecnico.id} value={tecnico.id}>
                    {tecnico.nome_completo}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Cliente</label>
              <select
                value={formData.cliente_id}
                onChange={(e) => setFormData({ ...formData, cliente_id: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              >
                <option value="">Selecione um cliente (opcional)</option>
                {clientes?.map((cliente: any) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.nome}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Data/Hora Início *</label>
              <input
                type="datetime-local"
                value={formData.data_hora_inicio}
                onChange={(e) => setFormData({ ...formData, data_hora_inicio: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Data/Hora Fim *</label>
              <input
                type="datetime-local"
                value={formData.data_hora_fim}
                onChange={(e) => setFormData({ ...formData, data_hora_fim: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Evento</label>
              <select
                value={formData.tipo_evento}
                onChange={(e) => setFormData({ ...formData, tipo_evento: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              >
                <option value="servico">Serviço</option>
                <option value="reuniao">Reunião</option>
                <option value="manutencao">Manutenção</option>
                <option value="indisponivel">Indisponível</option>
                <option value="outro">Outro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Cor</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={formData.cor}
                  onChange={(e) => setFormData({ ...formData, cor: e.target.value })}
                  className="w-12 h-10 rounded cursor-pointer"
                />
                <span className="text-sm text-white/60">{formData.cor}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Endereço</label>
            <input
              type="text"
              value={formData.endereco}
              onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
              placeholder="Endereço do evento"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Observações</label>
            <textarea
              value={formData.observacoes}
              onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] min-h-[100px]"
              placeholder="Observações adicionais"
              rows={3}
            />
          </div>
        </div>

        {erro && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mt-4">
            {erro}
          </div>
        )}

        <div className="flex justify-end gap-4 mt-6">
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={onSave}
            disabled={isPending}
            className="bg-gradient-to-r from-[#6C63FF] to-[#00D4FF]"
          >
            {isPending ? 'Salvando...' : 'Salvar'}
          </Button>
        </div>
      </motion.div>
    </motion.div>
  )
}
