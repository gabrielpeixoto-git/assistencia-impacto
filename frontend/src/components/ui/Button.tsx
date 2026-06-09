import { ReactNode, ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
  size?: 'default' | 'icon'
  children: ReactNode
  className?: string
}

export function Button({ 
  variant = 'default', 
  size = 'default', 
  children, 
  className = '',
  ...props 
}: ButtonProps) {
  const baseClasses = 'rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50'
  
  const variantClasses = {
    default: 'bg-primary text-white hover:bg-primary/90',
    outline: 'border border-border hover:bg-[var(--hover-bg)]',
    ghost: 'hover:bg-[var(--hover-bg)]',
    destructive: 'bg-destructive text-white hover:bg-destructive/90'
  }
  
  const sizeClasses = {
    default: 'px-4 py-2',
    icon: 'p-2'
  }
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
