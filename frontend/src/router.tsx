import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ClientesPage } from '@/pages/ClientesPage'
import { OrdensServicoPage } from '@/pages/OrdensServicoPage'
import { OrcamentosPage } from '@/pages/OrcamentosPage'
import { AgendaPage } from '@/pages/AgendaPage'
import { VisaoFinanceira } from '@/pages/VisaoFinanceira'
import { TransacoesPage } from '@/pages/TransacoesPage'
import { EstoquePage } from '@/pages/EstoquePage'
import { EquipePage } from '@/pages/EquipePage'
import { RelatoriosPage } from '@/pages/RelatoriosPage'
import { ConfiguracoesPage } from '@/pages/ConfiguracoesPage'
import { PortalOrcamentoPage } from '@/pages/PortalOrcamentoPage'
import { PortalOSPage } from '@/pages/PortalOSPage'
import { AppLayout } from '@/components/layout/AppLayout'
import { useAuthStore } from './store/auth.store'

// Wrapper de proteção de rota
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isLoading = useAuthStore((state) => state.isLoading)

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div>Carregando...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  // Rotas públicas do portal (sem autenticação)
  {
    path: '/portal/orcamento/:token',
    element: <PortalOrcamentoPage />,
  },
  {
    path: '/portal/os/:token',
    element: <PortalOSPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout>
          <Outlet />
        </AppLayout>
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      // Adicionar outras rotas aqui conforme necessário
      {
        path: 'ordens-servico',
        element: <OrdensServicoPage />,
      },
      {
        path: 'orcamentos',
        element: <OrcamentosPage />,
      },
      {
        path: 'agenda',
        element: <AgendaPage />,
      },
      {
        path: 'clientes',
        element: <ClientesPage />,
      },
      {
        path: 'financeiro',
        element: <VisaoFinanceira />,
      },
      {
        path: 'transacoes',
        element: <TransacoesPage />,
      },
      {
        path: 'estoque',
        element: <EstoquePage />,
      },
      {
        path: 'equipe',
        element: <EquipePage />,
      },
      {
        path: 'relatorios',
        element: <RelatoriosPage />,
      },
      {
        path: 'configuracoes',
        element: <ConfiguracoesPage />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])
