import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface EstadoVazioProps {
  icon?: ReactNode
  titulo?: string
  description?: string
  descricao?: string
  acao?: ReactNode | { label: string; onClick: () => void }
  className?: string
}

export function EstadoVazio({
  icon,
  titulo,
  description,
  descricao,
  acao,
  className
}: EstadoVazioProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
      {icon && (
        <div className="p-4 rounded-full bg-muted/10 mb-4">
          {icon}
        </div>
      )}
      {titulo && (
        <h3 className="text-lg font-semibold mb-2">{titulo}</h3>
      )}
      {(description || descricao) && (
        <p className="text-muted-foreground mb-4 max-w-md">{description || descricao}</p>
      )}
      {acao && typeof acao === 'object' && 'onClick' in acao ? (
        <button
          onClick={acao.onClick}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          {acao.label}
        </button>
      ) : (
        acao
      )}
    </div>
  )
}
