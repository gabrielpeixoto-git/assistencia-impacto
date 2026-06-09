import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Calendar, Users, FileText, DollarSign, Settings, LogOut, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface Command {
  id: string
  icon: React.ReactNode
  label: string
  action: () => void
  category: string
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()

  const commands: Command[] = [
    {
      id: 'novo-cliente',
      icon: <Users className="w-4 h-4" />,
      label: 'Novo Cliente',
      action: () => navigate('/clientes/novo'),
      category: 'Clientes'
    },
    {
      id: 'listar-clientes',
      icon: <Users className="w-4 h-4" />,
      label: 'Listar Clientes',
      action: () => navigate('/clientes'),
      category: 'Clientes'
    },
    {
      id: 'novo-orcamento',
      icon: <FileText className="w-4 h-4" />,
      label: 'Novo Orçamento',
      action: () => navigate('/orcamentos/novo'),
      category: 'Orçamentos'
    },
    {
      id: 'listar-orcamentos',
      icon: <FileText className="w-4 h-4" />,
      label: 'Listar Orçamentos',
      action: () => navigate('/orcamentos'),
      category: 'Orçamentos'
    },
    {
      id: 'nova-os',
      icon: <Plus className="w-4 h-4" />,
      label: 'Nova Ordem de Serviço',
      action: () => navigate('/ordens-servico/nova'),
      category: 'Ordens de Serviço'
    },
    {
      id: 'listar-os',
      icon: <FileText className="w-4 h-4" />,
      label: 'Listar Ordens de Serviço',
      action: () => navigate('/ordens-servico'),
      category: 'Ordens de Serviço'
    },
    {
      id: 'agenda',
      icon: <Calendar className="w-4 h-4" />,
      label: 'Agenda',
      action: () => navigate('/agenda'),
      category: 'Agenda'
    },
    {
      id: 'financeiro',
      icon: <DollarSign className="w-4 h-4" />,
      label: 'Financeiro',
      action: () => navigate('/financeiro'),
      category: 'Financeiro'
    },
    {
      id: 'estoque',
      icon: <FileText className="w-4 h-4" />,
      label: 'Estoque',
      action: () => navigate('/estoque'),
      category: 'Estoque'
    },
    {
      id: 'configuracoes',
      icon: <Settings className="w-4 h-4" />,
      label: 'Configurações',
      action: () => navigate('/configuracoes'),
      category: 'Sistema'
    },
    {
      id: 'dashboard',
      icon: <FileText className="w-4 h-4" />,
      label: 'Dashboard',
      action: () => navigate('/dashboard'),
      category: 'Sistema'
    },
    {
      id: 'sair',
      icon: <LogOut className="w-4 h-4" />,
      label: 'Sair',
      action: () => {
        localStorage.removeItem('token')
        navigate('/login')
      },
      category: 'Sistema'
    }
  ]

  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cmd.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = []
    }
    acc[cmd.category].push(cmd)
    return acc
  }, {} as Record<string, Command[]>)

  const flatCommands = Object.values(groupedCommands).flat()

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isOpen) return

    if (e.key === 'Escape') {
      onClose()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(prev => (prev + 1) % flatCommands.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(prev => (prev - 1 + flatCommands.length) % flatCommands.length)
    } else if (e.key === 'Enter' && flatCommands.length > 0) {
      e.preventDefault()
      flatCommands[selectedIndex].action()
      onClose()
    }
  }, [isOpen, flatCommands, selectedIndex, onClose])

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleKeyDown])

  useEffect(() => {
    setSelectedIndex(0)
  }, [searchQuery])

  const handleCommandClick = (command: Command) => {
    command.action()
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed top-[20%] left-1/2 transform -translate-x-1/2 w-full max-w-2xl z-50"
          >
            <div className="glass-card p-6">
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar comandos..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-[#6C63FF]"
                  autoFocus
                />
              </div>

              <div className="max-h-96 overflow-y-auto">
                {Object.entries(groupedCommands).map(([category, cmds]) => (
                  <div key={category} className="mb-4">
                    <h3 className="text-xs font-semibold text-white/60 uppercase tracking-wider mb-2 px-2">
                      {category}
                    </h3>
                    <div className="space-y-1">
                      {cmds.map((cmd) => {
                        const globalIndex = flatCommands.indexOf(cmd)
                        return (
                          <motion.button
                            key={cmd.id}
                            onClick={() => handleCommandClick(cmd)}
                            whileHover={{ scale: 1.02 }}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all ${
                              globalIndex === selectedIndex
                                ? 'bg-[#6C63FF]/30 border border-[#6C63FF]'
                                : 'hover:bg-white/10 border border-transparent'
                            }`}
                          >
                            <span className="text-white/80">{cmd.icon}</span>
                            <span className="text-white">{cmd.label}</span>
                          </motion.button>
                        )
                      })}
                    </div>
                  </div>
                ))}

                {filteredCommands.length === 0 && (
                  <div className="text-center py-8 text-white/60">
                    Nenhum comando encontrado
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-white/50">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <kbd className="px-2 py-1 bg-white/10 rounded">↑↓</kbd>
                    <span>Navegar</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-2 py-1 bg-white/10 rounded">Enter</kbd>
                    <span>Selecionar</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-2 py-1 bg-white/10 rounded">Esc</kbd>
                    <span>Fechar</span>
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
