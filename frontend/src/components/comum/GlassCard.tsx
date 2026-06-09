import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  [key: string]: any
}

export function GlassCard({ children, className, hover = false, ...rest }: GlassCardProps) {
  return (
    <div
      className={cn(
        'backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl',
        hover && 'hover:bg-white/8 hover:border-white/20 transition-all duration-200',
        className
      )}
      {...rest}
    >
      {children}
    </div>
  )
}
