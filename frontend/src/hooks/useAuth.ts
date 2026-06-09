import { useAuthStore } from '@/store/auth.store'

export function useAuth() {
  const { usuario, token, isAuthenticated, setAuth, logout } = useAuthStore()

  return {
    usuario,
    token,
    isAuthenticated,
    setAuth,
    logout,
  }
}
