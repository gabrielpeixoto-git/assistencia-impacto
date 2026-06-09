import { cn } from '@/lib/utils'

interface SkeletonLoaderProps {
  className?: string
}

export function SkeletonLoader({ className }: SkeletonLoaderProps) {
  return (
    <div
      className={cn('animate-pulse bg-muted/20 rounded', className)}
      role="status"
      aria-label="Carregando..."
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-6 space-y-4">
      <SkeletonLoader className="h-4 w-1/3" />
      <SkeletonLoader className="h-8 w-2/3" />
      <SkeletonLoader className="h-4 w-full" />
      <SkeletonLoader className="h-4 w-3/4" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <SkeletonLoader className="h-10 w-full" />
        </div>
      ))}
    </div>
  )
}
