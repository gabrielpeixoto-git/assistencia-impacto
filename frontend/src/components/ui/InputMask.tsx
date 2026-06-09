import { useIMask } from 'react-imask'
import { useEffect } from 'react'

interface InputMaskProps {
  value: string
  onChange: (value: string) => void
  className?: string
  placeholder?: string
  onBlur?: () => void
  id?: string
  'data-testid'?: string
}

export function IMaskTelefone({ value, onChange, className = '', placeholder = '(00) 00000-0000', onBlur, id, 'data-testid': dataTestId }: InputMaskProps) {
  const { ref } = useIMask({
    mask: '(00) 00000-0000',
    definitions: {
      '#': /[1-9]/
    }
  }, {
    onAccept: (value: any) => onChange(value),
    defaultValue: value
  })

  useEffect(() => {
    if (ref.current) {
      (ref.current as any).value = value
    }
  }, [value, ref])

  return (
    <input
      ref={ref as any}
      id={id}
      type="text"
      className={`w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${className}`}
      placeholder={placeholder}
      onBlur={onBlur}
      data-testid={dataTestId}
    />
  )
}

interface IMaskCPFCNPJProps {
  tipo: 'cpf' | 'cnpj'
  value: string
  onChange: (value: string) => void
  className?: string
  onBlur?: () => void
  id?: string
  'data-testid'?: string
}

export function IMaskCPFCNPJ({ tipo, value, onChange, className = '', onBlur, id, 'data-testid': dataTestId }: IMaskCPFCNPJProps) {
  const mask = tipo === 'cpf' ? '000.000.000-00' : '00.000.000/0000-00'
  const placeholder = tipo === 'cpf' ? '000.000.000-00' : '00.000.000/0000-00'

  const { ref } = useIMask({
    mask
  }, {
    onAccept: (value: any) => onChange(value),
    defaultValue: value
  })

  useEffect(() => {
    if (ref.current) {
      (ref.current as any).value = value
    }
  }, [value, ref])

  return (
    <input
      ref={ref as any}
      id={id}
      type="text"
      className={`w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${className}`}
      placeholder={placeholder}
      onBlur={onBlur}
      data-testid={dataTestId}
    />
  )
}

export function IMaskCEP({ value, onChange, className = '', id }: InputMaskProps) {
  const { ref } = useIMask({
    mask: '00000-000'
  }, {
    onAccept: (value: any) => onChange(value),
    defaultValue: value
  })

  useEffect(() => {
    if (ref.current) {
      (ref.current as any).value = value
    }
  }, [value, ref])

  return (
    <input
      ref={ref as any}
      id={id}
      type="text"
      className={`w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary pr-10 ${className}`}
      placeholder="00000-000"
    />
  )
}
