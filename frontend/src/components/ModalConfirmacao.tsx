import { AlertTriangle } from 'lucide-react'
import { GlassCard } from './comum/GlassCard'

interface ModalConfirmacaoProps {
  aberto: boolean
  titulo: string
  mensagem: string
  textoBotaoConfirmar?: string
  corBotao?: string
  carregando: boolean
  onConfirmar: () => void
  onCancelar: () => void
}

export function ModalConfirmacao({
  aberto,
  titulo,
  mensagem,
  textoBotaoConfirmar = 'Deletar',
  corBotao = 'bg-red-500 hover:bg-red-600',
  carregando,
  onConfirmar,
  onCancelar
}: ModalConfirmacaoProps) {
  if (!aberto) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" data-testid="modal-confirmacao">
      <GlassCard className="w-full max-w-md p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-red-500/20 rounded-full">
            <AlertTriangle className="w-6 h-6 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold">{titulo}</h2>
        </div>

        <p className="text-muted-foreground mb-6">
          {mensagem}
        </p>

        <div className="flex justify-end gap-4">
          <button
            onClick={onCancelar}
            disabled={carregando}
            className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirmar}
            disabled={carregando}
            className={`px-4 py-2 text-white rounded-lg transition-colors disabled:opacity-50 ${corBotao}`}
            data-testid="botao-confirmar-modal"
          >
            {carregando ? 'Processando...' : textoBotaoConfirmar}
          </button>
        </div>
      </GlassCard>
    </div>
  )
}
