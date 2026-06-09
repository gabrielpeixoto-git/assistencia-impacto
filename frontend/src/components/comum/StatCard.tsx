import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  icon: ReactNode
  value: string | number
  title?: string
  label?: string
  trend?: {
    value: number
    positive?: boolean
    isPositive?: boolean
  }
  className?: string
  testId?: string
}

export function StatCard({ icon, value, title, label, trend, className, testId }: StatCardProps) {
  const isPositive = trend?.positive !== undefined ? trend.positive : trend?.isPositive
  return (
    <div className={cn('glass-card-hover p-6', className)} data-testid={testId || 'stat-card'}>
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-lg bg-primary/10">
          {icon}
        </div>
        {trend && (
          <div
            className={cn(
              'flex items-center gap-1 text-sm font-medium',
              isPositive ? 'text-success' : 'text-destructive'
            )}
            data-testid={testId ? `${testId}-trend` : 'stat-card-trend'}
          >
            <span>{isPositive ? '↑' : '↓'}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <div className="text-3xl font-bold mb-1" data-testid={testId ? `${testId}-valor` : 'stat-card-valor'}>{value}</div>
      <div className="text-sm text-muted-foreground">{title || label}</div>
    </div>
  )
}
