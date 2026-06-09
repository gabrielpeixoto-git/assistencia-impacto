import { WifiOff, RefreshCw } from 'lucide-react'
import { GlassCard } from './comum/GlassCard'

interface ErroRedeProps {
  onTentarNovamente: () => void
}

export function ErroRede({ onTentarNovamente }: ErroRedeProps) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <GlassCard className="w-full max-w-md p-8 text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-red-500/20 rounded-full">
            <WifiOff className="w-12 h-12 text-red-400" />
          </div>
        </div>

        <h2 className="text-2xl font-bold mb-3">
          Não foi possível conectar ao servidor
        </h2>

        <p className="text-muted-foreground mb-6">
          Verifique se o servidor está rodando e tente novamente.
        </p>

        <button
          onClick={onTentarNovamente}
          className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          Tentar novamente
        </button>
      </GlassCard>
    </div>
  )
}
