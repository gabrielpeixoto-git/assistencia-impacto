import { ReactNode, useEffect } from 'react'
import { useUIStore } from '@/store/ui.store'
import { useAuthStore } from '@/store/auth.store'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { CommandPalette } from '@/components/CommandPalette'

interface AppLayoutProps {
  children: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { sidebarAberta, commandPaletteAberta, toggleCommandPalette, fecharCommandPalette } = useUIStore()
  const { isAuthenticated } = useAuthStore()
  
  // Ativar conexão WebSocket quando autenticado
  useWebSocket()

  // Atalho Cmd+K / Ctrl+K para abrir Command Palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        toggleCommandPalette()
      }
      if (e.key === 'Escape') {
        fecharCommandPalette()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleCommandPalette, fecharCommandPalette])

  if (!isAuthenticated) {
    return <>{children}</>
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarAberta ? 'ml-64' : 'ml-20'
        }`}
      >
        <TopBar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
      <CommandPalette isOpen={commandPaletteAberta} onClose={fecharCommandPalette} />
    </div>
  )
}
