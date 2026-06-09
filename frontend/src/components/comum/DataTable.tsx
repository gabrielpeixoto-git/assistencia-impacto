import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface Column<T> {
  key: keyof T | string
  header: string
  render?: (value: any, row: T) => ReactNode
  className?: string
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  loading?: boolean
  emptyMessage?: string
  className?: string
  testId?: string
  onRowClick?: (row: T) => void
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  emptyMessage = 'Nenhum registro encontrado',
  className,
  testId,
  onRowClick
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className={cn('space-y-3', className)} data-testid={testId ? `${testId}-loading` : 'skeleton-loader'}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 bg-muted/20 rounded animate-pulse" />
        ))}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className={cn('text-center py-12 text-muted-foreground', className)} data-testid={testId ? `${testId}-empty` : 'empty-state'}>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className={cn('overflow-x-auto', className)} data-testid={testId || 'datatable'}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-border">
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className={cn(
                  'text-left py-3 px-4 text-sm font-semibold text-muted-foreground',
                  column.className
                )}
                data-testid={testId ? `${testId}-header-${String(column.key)}` : undefined}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => {
            if (!row) return null
            return (
              <tr
                key={row.id || index}
                className={cn('border-b border-border hover:bg-white/5', onRowClick && 'cursor-pointer')}
                data-testid={testId ? `${testId}-row-${index}` : undefined}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={cn('py-3 px-4 text-sm', column.className)}
                    data-testid={testId ? `${testId}-cell-${String(column.key)}` : undefined}
                  >
                    {column.render && typeof column.render === 'function'
                      ? column.render(row[column.key], row)
                      : row[column.key] !== null && row[column.key] !== undefined
                      ? String(row[column.key])
                      : '—'}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
