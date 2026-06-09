import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Usuario {
  id: string
  email: string
  nome_completo: string
  perfil: string
}

interface AuthState {
  usuario: Usuario | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  setAuth: (usuario: Usuario, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      usuario: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      setAuth: (usuario, token) =>
        set({ usuario, token, isAuthenticated: true, isLoading: false }),
      logout: () =>
        set({ usuario: null, token: null, isAuthenticated: false, isLoading: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)
