import { useState } from 'react'

interface Toast {
  title?: string
  description?: string
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = (props: Toast) => {
    console.log('Toast:', props)
    setToasts(prev => [...prev, props])
  }

  return { toast, toasts }
}
