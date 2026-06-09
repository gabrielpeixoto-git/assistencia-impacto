import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/auth.store'
import { Zap, Mail, Lock, AlertCircle } from 'lucide-react'
import api from '@/lib/api'

export function LoginPage() {
  const [email, setEmail] = useState('admin@assistenciaimpacto.com.br')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')

    // Validação de campos vazios
    if (!email || !email.trim()) {
      setErro('Email é obrigatório')
      return
    }
    if (!senha || !senha.trim()) {
      setErro('Senha é obrigatória')
      return
    }

    // Debug logging temporário
    console.log('[Login] Tentando login com:', { email })
    console.log('[Login] API baseURL:', api.defaults.baseURL)
    console.log('[Login] URL completa:', api.defaults.baseURL + '/auth/login')

    setCarregando(true)

    try {
      const response = await api.post('/auth/login', { email, senha })
      console.log('[Login] Sucesso:', response)
      const { access_token, refresh_token, usuario } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      setAuth(usuario, access_token)
      navigate('/')
    } catch (error: any) {
      console.error('[Login] Erro completo:', error)
      console.error('[Login] Response data:', error?.response?.data)
      console.error('[Login] Status:', error?.response?.status)
      setErro(error.response?.data?.detail || 'Erro ao fazer login')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="glass-card p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="p-3 rounded-xl bg-primary/10">
              <Zap className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">
                Assistência Impacto
              </h1>
              <p className="text-sm text-muted-foreground">
                Sistema de Gestão
              </p>
            </div>
          </div>

          {/* Formulário */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {erro && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-2 text-destructive text-sm"
                data-testid="erro-login"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{erro}</span>
              </motion.div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="seu@email.com"
                    data-testid="input-email"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="password"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="••••••••"
                    data-testid="input-senha"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={carregando}
              data-testid="btn-login"
              className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {carregando ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>Esqueceu sua senha? Entre em contato com o administrador.</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
