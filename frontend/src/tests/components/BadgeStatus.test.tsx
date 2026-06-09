import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BadgeStatus } from '@/components/comum/BadgeStatus'

describe('BadgeStatus', () => {
  it('Renderiza com status "pendente"', () => {
    render(<BadgeStatus status="pendente" />)
    const badge = screen.getByText('pendente')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-amber-500/10', 'text-amber-500')
  })

  it('Renderiza com status "concluida"', () => {
    render(<BadgeStatus status="concluida" />)
    const badge = screen.getByText('concluida')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-success/10', 'text-success')
  })

  it('Aplica classe CSS correta por status', () => {
    const { rerender } = render(<BadgeStatus status="pendente" />)
    let badge = screen.getByText('pendente')
    expect(badge).toHaveClass('bg-amber-500/10')

    rerender(<BadgeStatus status="concluida" />)
    badge = screen.getByText('concluida')
    expect(badge).toHaveClass('bg-success/10')

    rerender(<BadgeStatus status="cancelada" />)
    badge = screen.getByText('cancelada')
    expect(badge).toHaveClass('bg-destructive/10')
  })
})
