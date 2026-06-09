import { cn } from '@/lib/utils'

interface BadgeStatusProps {
  status: string
  className?: string
}

const statusColors: Record<string, string> = {
  pendente: 'bg-amber-500/10 text-amber-500',
  confirmada: 'bg-blue-500/10 text-blue-500',
  em_andamento: 'bg-violet-500/10 text-violet-500',
  concluida: 'bg-success/10 text-success',
  cancelada: 'bg-destructive/10 text-destructive',
  aguardando: 'bg-muted/10 text-muted-foreground',
  rascunho: 'bg-gray-500/10 text-gray-500',
  enviado: 'bg-blue-500/10 text-blue-500',
  visualizado: 'bg-violet-500/10 text-violet-500',
  aprovado: 'bg-success/10 text-success',
  recusado: 'bg-destructive/10 text-destructive',
  expirado: 'bg-warning/10 text-warning',
  convertido: 'bg-success/10 text-success',
  pago: 'bg-success/10 text-success',
  atrasado: 'bg-destructive/10 text-destructive',
  parcial: 'bg-warning/10 text-warning',
}

export function BadgeStatus({ status, className }: BadgeStatusProps) {
  const colorClass = statusColors[status.toLowerCase()] || 'bg-muted/10 text-muted-foreground'
  
  return (
    <span
      className={cn(
        'px-2.5 py-1 rounded-full text-xs font-medium',
        colorClass,
        className
      )}
    >
      {status}
    </span>
  )
}
