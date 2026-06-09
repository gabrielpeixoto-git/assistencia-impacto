import { useState } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { GlassCard } from '@/components/ui/GlassCard'
import { Button } from '@/components/ui/Button'
import { Plus, Search, Edit, Trash2, Save } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export function EquipePage() {
  const [modalAberto, setModalAberto] = useState(false)
  const [modalConfirmacaoAberto, setModalConfirmacaoAberto] = useState(false)
  const [membroEditando, setMembroEditando] = useState<any>(null)
  const [membroParaDeletar, setMembroParaDeletar] = useState<any>(null)
  const [busca, setBusca] = useState('')
  const [formData, setFormData] = useState({
    email: '',
    nome_completo: '',
    perfil: 'tecnico',
    telefone: '',
    senha: '',
    confirmar_senha: '',
  })
  const [erro, setErro] = useState('')
  const { toast } = useToast()

  const { data: membros, refetch } = useQuery({
    queryKey: ['equipe', busca],
    queryFn: async () => {
      const response = await api.get('/usuarios/', {
        params: busca ? { busca } : undefined,
      })
      return response.data
    },
  })

  const criarMembroMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post('/equipe/usuarios', data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Membro criado com sucesso' })
      setModalAberto(false)
      refetch()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao criar membro')
    },
  })

  const atualizarMembroMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await api.put(`/equipe/usuarios/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Membro atualizado com sucesso' })
      setModalAberto(false)
      setMembroEditando(null)
      refetch()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao atualizar membro')
    },
  })

  const deletarMembroMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete(`/equipe/usuarios/${id}`)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Membro deletado com sucesso' })
      setModalConfirmacaoAberto(false)
      setMembroParaDeletar(null)
      refetch()
    },
    onError: (error: any) => {
      setErro(error.response?.data?.detail || 'Erro ao deletar membro')
    },
  })

  const handleSalvarMembro = () => {
    if (!formData.email || !formData.nome_completo) {
      setErro('Preencha os campos obrigatorios')
      return
    }

    if (!membroEditando && (!formData.senha || formData.senha !== formData.confirmar_senha)) {
      setErro('As senhas nao conferem')
      return
    }

    if (membroEditando) {
      atualizarMembroMutation.mutate({ id: membroEditando.id, data: formData })
    } else {
      criarMembroMutation.mutate(formData)
    }
  }

  const confirmarDeletarMembro = () => {
    if (membroParaDeletar) {
      deletarMembroMutation.mutate(membroParaDeletar.id)
    }
  }

  const abrirModalEdicao = (membro: any) => {
    setMembroEditando(membro)
    setFormData({
      email: membro.email,
      nome_completo: membro.nome_completo,
      perfil: membro.perfil,
      telefone: membro.telefone || '',
      senha: '',
      confirmar_senha: '',
    })
    setModalAberto(true)
  }

  return (
    <PageWrapper>
      <div className="space-y-6" data-testid="equipe-container">
        <div className="flex items-center justify-between">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              data-testid="input-busca-equipe"
              type="text"
              placeholder="Buscar membro..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="pl-10 pr-4 py-2 bg-[var(--input)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 w-64"
            />
          </div>

          <Button
            data-testid="btn-novo-usuario"
            onClick={() => {
              setMembroEditando(null)
              setFormData({
                email: '',
                nome_completo: '',
                perfil: 'tecnico',
                telefone: '',
                senha: '',
                confirmar_senha: '',
              })
              setModalAberto(true)
            }}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Novo Membro
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {membros?.map((membro: any) => (
            <GlassCard
              key={membro.id}
              data-testid={`card-tecnico-${membro.id}`}
              className="p-4"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="font-semibold text-primary">
                      {membro.nome_completo
                        .split(' ')
                        .map((n: string) => n[0])
                        .join('')
                        .toUpperCase()
                        .slice(0, 2)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold">{membro.nome_completo}</h3>
                    <p className="text-sm text-muted-foreground">{membro.email}</p>
                  </div>
                </div>
                <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                  {membro.perfil}
                </span>
              </div>

              <div className="flex items-center gap-2 mt-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => abrirModalEdicao(membro)}
                  data-testid={`btn-editar-${membro.id}`}
                >
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setMembroParaDeletar(membro)
                    setModalConfirmacaoAberto(true)
                  }}
                  data-testid={`btn-deletar-${membro.id}`}
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
              </div>
            </GlassCard>
          ))}
        </div>

        {modalConfirmacaoAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <GlassCard className="w-full max-w-md p-6">
              <h2 className="text-xl font-bold mb-4">Deletar Membro</h2>
              <p className="text-muted-foreground mb-6">
                Tem certeza que deseja deletar este membro da equipe? Esta acao nao pode ser desfeita.
              </p>
              <div className="flex justify-end gap-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setModalConfirmacaoAberto(false)
                    setMembroParaDeletar(null)
                  }}
                >
                  Cancelar
                </Button>
                <Button
                  variant="destructive"
                  onClick={confirmarDeletarMembro}
                  disabled={deletarMembroMutation.isPending}
                >
                  {deletarMembroMutation.isPending ? 'Deletando...' : 'Deletar'}
                </Button>
              </div>
            </GlassCard>
          </div>
        )}

        {modalAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="modal-usuario">
            <GlassCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold mb-6" data-testid="modal-titulo">
                {membroEditando ? 'Editar Membro' : 'Novo Membro'}
              </h2>

              <div className="space-y-4">
                <div>
                  <label htmlFor="email-equipe" className="block text-sm font-medium mb-2">
                    Email *
                  </label>
                  <input
                    data-testid="input-email-usuario"
                    id="email-equipe"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="email@exemplo.com"
                    disabled={!!membroEditando}
                  />
                  {membroEditando && (
                    <p className="text-xs text-muted-foreground mt-1">Email nao pode ser alterado</p>
                  )}
                </div>

                <div>
                  <label htmlFor="nome-completo-equipe" className="block text-sm font-medium mb-2">
                    Nome Completo *
                  </label>
                  <input
                    data-testid="input-nome-usuario"
                    id="nome-completo-equipe"
                    type="text"
                    value={formData.nome_completo}
                    onChange={(e) => setFormData({ ...formData, nome_completo: e.target.value })}
                    className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Nome do membro"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="perfil-equipe" className="block text-sm font-medium mb-2">
                      Perfil
                    </label>
                    <select
                      data-testid="select-perfil-usuario"
                      id="perfil-equipe"
                      value={formData.perfil}
                      onChange={(e) => setFormData({ ...formData, perfil: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="visualizador">Visualizador</option>
                      <option value="tecnico">Tecnico</option>
                      <option value="gerente">Gerente</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="telefone-equipe" className="block text-sm font-medium mb-2">
                      Telefone
                    </label>
                    <input
                      data-testid="input-telefone-usuario"
                      id="telefone-equipe"
                      type="tel"
                      value={formData.telefone}
                      onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                </div>

                {!membroEditando && (
                  <>
                    <div>
                      <label htmlFor="senha-equipe" className="block text-sm font-medium mb-2">
                        Senha *
                      </label>
                      <input
                        data-testid="input-senha-usuario"
                        id="senha-equipe"
                        type="password"
                        value={formData.senha}
                        onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Minimo 8 caracteres"
                      />
                    </div>

                    <div>
                      <label htmlFor="confirmar-senha-equipe" className="block text-sm font-medium mb-2">
                        Confirmar Senha *
                      </label>
                      <input
                        data-testid="input-confirmar-senha-usuario"
                        id="confirmar-senha-equipe"
                        type="password"
                        value={formData.confirmar_senha}
                        onChange={(e) => setFormData({ ...formData, confirmar_senha: e.target.value })}
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Confirme a senha"
                      />
                    </div>
                  </>
                )}
              </div>

              {erro && (
                <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
                  {erro}
                </div>
              )}

              <div className="flex justify-end gap-4 mt-6">
                <Button
                  variant="outline"
                  data-testid="btn-cancelar-modal"
                  onClick={() => setModalAberto(false)}
                >
                  Cancelar
                </Button>
                <Button
                  data-testid="btn-salvar-usuario"
                  onClick={handleSalvarMembro}
                  disabled={criarMembroMutation.isPending || atualizarMembroMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {criarMembroMutation.isPending || atualizarMembroMutation.isPending ? 'Salvando...' : 'Salvar'}
                </Button>
              </div>
            </GlassCard>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
