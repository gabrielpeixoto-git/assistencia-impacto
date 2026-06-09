# PROMPT DEVIN — PORTAL PÚBLICO + CMD+K + UI POLISH
## Assistência Impacto — Features Finais de Completude
> Leia COMPLETO antes de executar. Estas são as últimas features do MVP.

---

## CONTEXTO

Stack: FastAPI + PostgreSQL + Redis + React 18 + TypeScript + Docker Compose  
Localização: `c:\Projeto Impacto Soluções`  
Senha admin: `admin123`  
App: `http://localhost` ou `http://localhost:5173` 

### Estado atual
✅ 316 testes, 88% cobertura  
✅ PDF verificado funcional (conteúdo extraível via PyPDF2)  
✅ WebSocket notificações ativo  
✅ Todos os módulos principais funcionando  
Pendente: Portal Público, Cmd+K, UI polish

---

## ═══ FASE 0 — PRÉ-CHECKS ═══

```powershell
docker compose ps
cd "c:\Projeto Impacto Soluções\backend"
python -m pytest tests/ -q 2>&1 | Select-String "passed|failed" | Select-Object -Last 2
```

---

## ═══ FASE 1 — PORTAL PÚBLICO DO CLIENTE ═══

> Permite clientes verem e aprovarem orçamentos sem precisar de login.
> Acesso por token único: `/portal/orcamento/{token}` 

### 1.1 — Verificar o que já existe

```powershell
cat "c:\Projeto Impacto Soluções\backend\app\routers\portal.py" | head -80
cat "c:\Projeto Impacto Soluções\frontend\src\pages\portal\PortalClientePage.tsx" 2>nul | head -50
```

Verifique se existe:
- Endpoint `GET /api/portal/orcamento/{token}` → dados públicos do orçamento
- Endpoint `POST /api/portal/orcamento/{token}/aprovar` 
- Endpoint `POST /api/portal/orcamento/{token}/recusar` 
- Campo `token_acesso_publico` no model `Orcamento` 

### 1.2 — Backend: garantir endpoints do portal

Se os endpoints não existem ou estão incompletos, implemente:

```python
# backend/app/routers/portal.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.orcamento import Orcamento, ItemOrcamento
from app.models.cliente import Cliente
from app.models.configuracao import Configuracao
from sqlalchemy import select
import uuid

router = APIRouter(prefix="/api/portal", tags=["portal"])

@router.get("/orcamento/{token}")
async def obter_orcamento_publico(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint público — não requer autenticação."""
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    cliente = (await db.execute(select(Cliente).where(Cliente.id == orcamento.cliente_id))).scalar_one_or_none()
    itens = (await db.execute(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento.id).order_by(ItemOrcamento.ordem))).scalars().all()
    
    return {
        "sucesso": True,
        "dados": {
            "id": str(orcamento.id),
            "numero_orcamento": orcamento.numero_orcamento,
            "titulo": orcamento.titulo,
            "descricao": orcamento.descricao,
            "status": orcamento.status.value if hasattr(orcamento.status, 'value') else orcamento.status,
            "valido_ate": orcamento.valido_ate.isoformat() if orcamento.valido_ate else None,
            "subtotal": orcamento.subtotal,
            "valor_desconto": orcamento.valor_desconto,
            "total": orcamento.total,
            "condicoes_pagamento": orcamento.condicoes_pagamento,
            "garantia": orcamento.garantia,
            "cliente": {
                "nome": cliente.nome if cliente else "N/A",
                "email": cliente.email if cliente else "",
            },
            "itens": [
                {
                    "descricao": item.descricao,
                    "quantidade": int(item.quantidade) if item.quantidade else 1,
                    "unidade": item.unidade or "un",
                    "preco_unitario": item.preco_unitario or 0,
                    "preco_total": item.preco_total or 0,
                }
                for item in itens
            ],
        }
    }

@router.post("/orcamento/{token}/aprovar")
async def aprovar_orcamento_publico(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Aprovação pública do orçamento pelo cliente."""
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    if orcamento.status not in ['rascunho', 'enviado', 'visualizado', 'RASCUNHO', 'ENVIADO', 'VISUALIZADO']:
        raise HTTPException(status_code=400, detail="Orçamento não pode ser aprovado no estado atual")
    
    from app.models.orcamento import StatusOrcamento
    from datetime import datetime, timezone
    orcamento.status = StatusOrcamento.APROVADO
    orcamento.aprovado_em = datetime.now(timezone.utc)
    await db.commit()
    
    return {"sucesso": True, "mensagem": "Orçamento aprovado com sucesso!"}

@router.post("/orcamento/{token}/recusar")
async def recusar_orcamento_publico(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Recusa pública do orçamento pelo cliente."""
    result = await db.execute(
        select(Orcamento).where(Orcamento.token_acesso_publico == token)
    )
    orcamento = result.scalar_one_or_none()
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    from app.models.orcamento import StatusOrcamento
    orcamento.status = StatusOrcamento.RECUSADO
    await db.commit()
    
    return {"sucesso": True, "mensagem": "Orçamento recusado."}
```

### 1.3 — Verificar se Orcamento tem token_acesso_publico

```powershell
cat "c:\Projeto Impacto Soluções\backend\app\models\orcamento.py" | Select-String "token"
```

Se não tiver, o field é necessário. Verifique também no seed se o campo está sendo populado:
```powershell
docker compose exec banco psql -U postgres -d assistencia_impacto -c `
  "SELECT numero_orcamento, token_acesso_publico FROM orcamentos LIMIT 3;"
```

### 1.4 — Frontend: PortalClientePage

A página deve ser acessível sem login em `/portal/orcamento/:token`.
Leia o arquivo atual:
```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\pages\portal\PortalClientePage.tsx"
```

Se estiver incompleto ou vazio, implemente:

```tsx
// src/pages/portal/PortalClientePage.tsx
import { useState } from 'react'
import { useParams } from '@tanstack/react-router'  // ou react-router
import { useQuery, useMutation } from '@tanstack/react-query'
import { CheckCircle, XCircle, FileText, Clock, AlertCircle } from 'lucide-react'
import axios from 'axios'

const apiPublico = axios.create({ baseURL: '/api' })

export function PortalClientePage() {
  const { token } = useParams({ strict: false }) as { token: string }
  const [decisao, setDecisao] = useState<'aprovado' | 'recusado' | null>(null)
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['portal-orcamento', token],
    queryFn: () => apiPublico.get(`/portal/orcamento/${token}`).then(r => r.data.dados),
    enabled: !!token
  })
  
  const aprovarMutation = useMutation({
    mutationFn: () => apiPublico.post(`/portal/orcamento/${token}/aprovar`),
    onSuccess: () => setDecisao('aprovado')
  })
  
  const recusarMutation = useMutation({
    mutationFn: () => apiPublico.post(`/portal/orcamento/${token}/recusar`),
    onSuccess: () => setDecisao('recusado')
  })
  
  if (isLoading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-4 border-violet-600 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-600">Carregando orçamento...</p>
      </div>
    </div>
  )
  
  if (error || !data) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Orçamento não encontrado</h2>
        <p className="text-gray-600">Este link pode ter expirado ou ser inválido.</p>
      </div>
    </div>
  )
  
  if (decisao === 'aprovado') return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center bg-white rounded-2xl p-12 shadow-lg max-w-md">
        <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
        <h2 className="text-2xl font-bold text-gray-900 mb-3">Orçamento Aprovado!</h2>
        <p className="text-gray-600 mb-2">Obrigado por aprovar o orçamento.</p>
        <p className="text-gray-500 text-sm">Nossa equipe entrará em contato em breve para agendar o serviço.</p>
      </div>
    </div>
  )
  
  if (decisao === 'recusado') return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center bg-white rounded-2xl p-12 shadow-lg max-w-md">
        <XCircle className="w-20 h-20 text-gray-400 mx-auto mb-6" />
        <h2 className="text-2xl font-bold text-gray-900 mb-3">Orçamento Recusado</h2>
        <p className="text-gray-600">Tudo bem. Entre em contato se mudar de ideia.</p>
      </div>
    </div>
  )
  
  const statusLabel: Record<string, string> = {
    rascunho: 'Rascunho', RASCUNHO: 'Rascunho',
    enviado: 'Enviado', ENVIADO: 'Enviado',
    visualizado: 'Visualizado', VISUALIZADO: 'Visualizado',
    aprovado: 'Aprovado', APROVADO: 'Aprovado ✓',
    recusado: 'Recusado', RECUSADO: 'Recusado',
  }
  
  const podeDecidir = ['enviado', 'visualizado', 'ENVIADO', 'VISUALIZADO'].includes(data.status)
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 py-4">
        <div className="max-w-3xl mx-auto px-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">Assistência Impacto</h1>
            <p className="text-xs text-gray-500">Portal do Cliente</p>
          </div>
        </div>
      </div>
      
      <div className="max-w-3xl mx-auto px-6 py-8">
        {/* Cabeçalho do orçamento */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Orçamento</p>
              <h2 className="text-2xl font-bold text-gray-900">{data.numero_orcamento}</h2>
              <p className="text-gray-600 mt-1">{data.titulo}</p>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              ['aprovado', 'APROVADO'].includes(data.status) 
                ? 'bg-green-100 text-green-800'
                : ['recusado', 'RECUSADO'].includes(data.status)
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {statusLabel[data.status] || data.status}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Cliente:</span>
              <span className="ml-2 text-gray-900 font-medium">{data.cliente?.nome}</span>
            </div>
            {data.valido_ate && (
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-500">Válido até:</span>
                <span className="ml-1 text-gray-900">{new Date(data.valido_ate).toLocaleDateString('pt-BR')}</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Itens */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 mb-6 overflow-hidden">
          <div className="px-8 py-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Itens do Orçamento</h3>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-8 py-3 text-xs font-medium text-gray-500 uppercase">Descrição</th>
                <th className="text-center px-4 py-3 text-xs font-medium text-gray-500 uppercase">Qtd</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Unit.</th>
                <th className="text-right px-8 py-3 text-xs font-medium text-gray-500 uppercase">Total</th>
              </tr>
            </thead>
            <tbody>
              {data.itens.map((item: any, i: number) => (
                <tr key={i} className="border-t border-gray-100">
                  <td className="px-8 py-3 text-gray-900">{item.descricao}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{item.quantidade} {item.unidade}</td>
                  <td className="px-4 py-3 text-right text-gray-600">R$ {Number(item.preco_unitario).toFixed(2)}</td>
                  <td className="px-8 py-3 text-right font-medium text-gray-900">R$ {Number(item.preco_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50">
              {data.valor_desconto > 0 && (
                <tr>
                  <td colSpan={3} className="px-8 py-2 text-right text-gray-500">Desconto:</td>
                  <td className="px-8 py-2 text-right text-red-600">- R$ {Number(data.valor_desconto).toFixed(2)}</td>
                </tr>
              )}
              <tr>
                <td colSpan={3} className="px-8 py-3 text-right font-bold text-gray-900">TOTAL:</td>
                <td className="px-8 py-3 text-right font-bold text-violet-600 text-lg">
                  R$ {Number(data.total).toFixed(2)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
        
        {/* Condições e garantia */}
        {(data.condicoes_pagamento || data.garantia) && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-6">
            {data.condicoes_pagamento && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-900 mb-2">Condições de Pagamento</h4>
                <p className="text-gray-600 text-sm">{data.condicoes_pagamento}</p>
              </div>
            )}
            {data.garantia && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Garantia</h4>
                <p className="text-gray-600 text-sm">{data.garantia}</p>
              </div>
            )}
          </div>
        )}
        
        {/* Botões de ação */}
        {podeDecidir && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
            <h3 className="font-semibold text-gray-900 mb-2">Sua Decisão</h3>
            <p className="text-gray-600 text-sm mb-6">Revise os itens acima e decida se deseja aprovar ou recusar este orçamento.</p>
            <div className="flex gap-4">
              <button
                onClick={() => aprovarMutation.mutate()}
                disabled={aprovarMutation.isPending}
                className="flex-1 py-3 px-6 rounded-xl bg-violet-600 text-white font-medium hover:bg-violet-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" />
                {aprovarMutation.isPending ? 'Aprovando...' : 'Aprovar Orçamento'}
              </button>
              <button
                onClick={() => recusarMutation.mutate()}
                disabled={recusarMutation.isPending}
                className="flex-1 py-3 px-6 rounded-xl border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <XCircle className="w-5 h-5" />
                {recusarMutation.isPending ? 'Recusando...' : 'Recusar'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PortalClientePage
```

### 1.5 — Registrar rota no router do frontend

```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\router.tsx" | Select-String "portal|Portal" | Select-Object -First 5
```

Se a rota `/portal/orcamento/$token` não existir, adicione ao router.tsx:
```typescript
// Adicionar às rotas públicas (sem autenticação):
{
  path: '/portal/orcamento/$token',
  component: PortalClientePage,
}
```

---

## ═══ FASE 2 — COMMAND PALETTE (CMD+K) ═══

### 2.1 — Verificar se já existe

```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\components\comum\BarraBusca.tsx" 2>nul | head -30
```

### 2.2 — Implementar CommandPalette component

```tsx
// src/components/comum/CommandPalette.tsx
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Search, X, Users, ClipboardList, Calendar, Package,
         DollarSign, FileText, Settings, LayoutDashboard } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '../../lib/api'

interface SearchResult {
  id: string
  tipo: 'cliente' | 'os' | 'orcamento'
  titulo: string
  subtitulo?: string
  url: string
}

const ATALHOS_RAPIDOS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, url: '/' },
  { id: 'clientes', label: 'Clientes', icon: Users, url: '/clientes' },
  { id: 'os', label: 'Ordens de Serviço', icon: ClipboardList, url: '/ordens-servico' },
  { id: 'orcamentos', label: 'Orçamentos', icon: FileText, url: '/orcamentos' },
  { id: 'agenda', label: 'Agenda', icon: Calendar, url: '/agenda' },
  { id: 'estoque', label: 'Estoque', icon: Package, url: '/estoque' },
  { id: 'financeiro', label: 'Financeiro', icon: DollarSign, url: '/financeiro' },
  { id: 'configuracoes', label: 'Configurações', icon: Settings, url: '/configuracoes' },
]

export function CommandPalette() {
  const [aberto, setAberto] = useState(false)
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  
  // Atalho Cmd+K / Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setAberto(prev => !prev)
        setQuery('')
      }
      if (e.key === 'Escape') setAberto(false)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])
  
  useEffect(() => {
    if (aberto) {
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [aberto])
  
  // Busca global (debounced)
  const { data: resultados } = useQuery({
    queryKey: ['busca-global', query],
    queryFn: async () => {
      if (query.length < 2) return []
      const [clientes, os, orc] = await Promise.allSettled([
        api.get(`/clientes?q=${query}&por_pagina=3`).then(r => r.data.dados?.map((c: any) => ({
          id: c.id, tipo: 'cliente' as const, titulo: c.nome,
          subtitulo: c.email || c.telefone, url: `/clientes/${c.id}` 
        }))),
        api.get(`/ordens-servico?q=${query}&por_pagina=3`).then(r => r.data.dados?.map((o: any) => ({
          id: o.id, tipo: 'os' as const, titulo: `${o.numero_os} - ${o.titulo || o.descricao?.slice(0,40)}`,
          subtitulo: o.status, url: `/ordens-servico/${o.id}` 
        }))),
        api.get(`/orcamentos?q=${query}&por_pagina=3`).then(r => r.data.dados?.map((o: any) => ({
          id: o.id, tipo: 'orcamento' as const, titulo: `${o.numero_orcamento} - ${o.titulo}`,
          subtitulo: `R$ ${Number(o.total || 0).toFixed(2)}`, url: `/orcamentos/${o.id}` 
        }))),
      ])
      return [
        ...(clientes.status === 'fulfilled' ? clientes.value || [] : []),
        ...(os.status === 'fulfilled' ? os.value || [] : []),
        ...(orc.status === 'fulfilled' ? orc.value || [] : []),
      ] as SearchResult[]
    },
    enabled: query.length >= 2,
  })
  
  const atalhosFiltrados = query.length < 2
    ? ATALHOS_RAPIDOS
    : ATALHOS_RAPIDOS.filter(a => a.label.toLowerCase().includes(query.toLowerCase()))
  
  const irPara = (url: string) => {
    navigate({ to: url })
    setAberto(false)
    setQuery('')
  }
  
  if (!aberto) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
         onClick={() => setAberto(false)}>
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      
      {/* Painel */}
      <div className="relative w-full max-w-xl mx-4 bg-[#1A1D27] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
           onClick={e => e.stopPropagation()}>
        
        {/* Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Buscar clientes, OS, orçamentos..."
            className="flex-1 bg-transparent text-white placeholder-slate-500 outline-none text-base"
          />
          {query && (
            <button onClick={() => setQuery('')}>
              <X className="w-4 h-4 text-slate-400" />
            </button>
          )}
          <kbd className="hidden sm:flex items-center gap-1 px-2 py-1 text-xs text-slate-500 border border-white/10 rounded">
            ESC
          </kbd>
        </div>
        
        {/* Resultados */}
        <div className="max-h-80 overflow-y-auto p-2">
          {/* Resultados da busca */}
          {resultados && resultados.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-slate-500 px-3 py-1 uppercase tracking-wide">Resultados</p>
              {resultados.map(item => (
                <button
                  key={item.id}
                  onClick={() => irPara(item.url)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center shrink-0">
                    {item.tipo === 'cliente' && <Users className="w-4 h-4 text-violet-400" />}
                    {item.tipo === 'os' && <ClipboardList className="w-4 h-4 text-blue-400" />}
                    {item.tipo === 'orcamento' && <FileText className="w-4 h-4 text-green-400" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-white truncate">{item.titulo}</p>
                    {item.subtitulo && <p className="text-xs text-slate-400 truncate">{item.subtitulo}</p>}
                  </div>
                </button>
              ))}
            </div>
          )}
          
          {/* Atalhos rápidos */}
          {atalhosFiltrados.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 px-3 py-1 uppercase tracking-wide">
                {query.length < 2 ? 'Atalhos Rápidos' : 'Páginas'}
              </p>
              {atalhosFiltrados.map(atalho => (
                <button
                  key={atalho.id}
                  onClick={() => irPara(atalho.url)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                    <atalho.icon className="w-4 h-4 text-slate-400" />
                  </div>
                  <p className="text-sm text-white">{atalho.label}</p>
                </button>
              ))}
            </div>
          )}
          
          {/* Estado vazio */}
          {query.length >= 2 && (!resultados || resultados.length === 0) && atalhosFiltrados.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Nenhum resultado para "{query}"</p>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="px-4 py-2 border-t border-white/10 flex gap-4 text-xs text-slate-500">
          <span><kbd className="font-mono">↵</kbd> selecionar</span>
          <span><kbd className="font-mono">↑↓</kbd> navegar</span>
          <span><kbd className="font-mono">Esc</kbd> fechar</span>
        </div>
      </div>
    </div>
  )
}
```

### 2.3 — Adicionar CommandPalette ao AppLayout

```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\components\layout\AppLayout.tsx" | head -30
```

Adicionar ao retorno do AppLayout:
```tsx
import { CommandPalette } from '../comum/CommandPalette'

// No JSX:
return (
  <>
    <CommandPalette />
    {/* resto do layout */}
  </>
)
```

### 2.4 — Adicionar indicador visual no TopBar

No TopBar, mostrar o atalho Cmd+K para os usuários descobrirem:
```tsx
// Em TopBar.tsx, substituir o campo de busca por um botão que abre a paleta:
<button
  onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))}
  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-slate-400 text-sm hover:bg-white/8 transition-colors"
>
  <Search className="w-4 h-4" />
  <span className="hidden md:block">Buscar...</span>
  <kbd className="hidden md:flex items-center gap-0.5 text-xs">
    <span>⌘</span><span>K</span>
  </kbd>
</button>
```

---

## ═══ FASE 3 — ESTADOS VAZIOS E SKELETON LOADERS ═══

> Cada lista e card devem ter estado visual quando estão carregando ou vazios.

### 3.1 — Verificar componentes existentes

```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\components\comum\SkeletonLoader.tsx" 2>nul | head -20
cat "c:\Projeto Impacto Soluções\frontend\src\components\comum\EstadoVazio.tsx" 2>nul | head -20
```

### 3.2 — Implementar/melhorar SkeletonLoader

```tsx
// src/components/comum/SkeletonLoader.tsx
export function SkeletonLine({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-white/10 rounded ${className}`} />
}

export function SkeletonCard() {
  return (
    <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
      <SkeletonLine className="h-4 w-1/3" />
      <SkeletonLine className="h-8 w-1/2" />
      <SkeletonLine className="h-3 w-2/3" />
    </div>
  )
}

export function SkeletonTabela({ linhas = 5 }: { linhas?: number }) {
  return (
    <div className="space-y-2">
      <div className="flex gap-4 px-4 py-3 border-b border-white/10">
        {[40, 20, 20, 20].map((w, i) => (
          <SkeletonLine key={i} className={`h-3 w-${w}%`} />
        ))}
      </div>
      {Array.from({ length: linhas }).map((_, i) => (
        <div key={i} className="flex gap-4 px-4 py-3">
          {[40, 20, 20, 20].map((w, j) => (
            <SkeletonLine key={j} className={`h-3`} style={{ width: `${w}%` }} />
          ))}
        </div>
      ))}
    </div>
  )
}
```

### 3.3 — Implementar/melhorar EstadoVazio

```tsx
// src/components/comum/EstadoVazio.tsx
import { LucideIcon } from 'lucide-react'
import { FileX, Users, ClipboardList, Package } from 'lucide-react'

interface EstadoVazioProps {
  icone?: LucideIcon
  titulo?: string
  descricao?: string
  acao?: React.ReactNode
}

export function EstadoVazio({
  icone: Icone = FileX,
  titulo = "Nenhum item encontrado",
  descricao = "Não há dados para exibir.",
  acao
}: EstadoVazioProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
        <Icone className="w-8 h-8 text-slate-500" />
      </div>
      <h3 className="text-base font-semibold text-white mb-1">{titulo}</h3>
      <p className="text-sm text-slate-400 max-w-xs mb-6">{descricao}</p>
      {acao}
    </div>
  )
}
```

### 3.4 — Aplicar skeleton loaders nas principais páginas

Nas páginas de lista (ClientesListaPage, OrdensServicoPage, EstoquePage, etc.),
onde há `isLoading`, use o SkeletonTabela:

```tsx
// Padrão a aplicar:
if (isLoading) return (
  <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
    <SkeletonTabela linhas={8} />
  </div>
)

// Se array vazio:
if (!dados || dados.length === 0) return (
  <EstadoVazio
    icone={Users}
    titulo="Nenhum cliente cadastrado"
    descricao="Adicione seu primeiro cliente para começar"
    acao={
      <button onClick={handleNovo} className="px-4 py-2 bg-violet-600 rounded-xl text-white text-sm">
        Novo Cliente
      </button>
    }
  />
)
```

Adicione skeleton/estado vazio nas páginas:
- ClientesListaPage — "Nenhum cliente cadastrado"
- OrdensServicoPage — "Nenhuma OS encontrada" 
- EstoquePage — "Estoque vazio"
- OrcamentosPage — "Nenhum orçamento criado"

---

## ═══ FASE 4 — VERIFICAÇÃO FINAL ═══

### 4.1 — Testes obrigatórios

```powershell
cd "c:\Projeto Impacto Soluções\backend"
python -m pytest tests/ -q 2>&1 | Select-String "passed|failed" | Select-Object -Last 2
```

**Meta: 316+ passed, 0 failed.**

### 4.2 — Build do frontend

```powershell
cd "c:\Projeto Impacto Soluções\frontend"
npm run build 2>&1 | Select-String "error TS" | Select-Object -First 10
```

### 4.3 — Testar Portal Público

```powershell
# Pegar token de um orçamento
docker compose exec banco psql -U postgres -d assistencia_impacto -c `
  "SELECT numero_orcamento, token_acesso_publico FROM orcamentos WHERE status='ENVIADO' LIMIT 1;"
```

Acesse `http://localhost:5173/portal/orcamento/{TOKEN}` no browser.
Deve mostrar a página do portal sem precisar de login.

### 4.4 — Testar Cmd+K

Abra `http://localhost:5173` e pressione Ctrl+K (ou Cmd+K no Mac).
Deve abrir a paleta de comandos.
Digite "cliente" — deve mostrar atalho para a página de Clientes.
Digite um nome de cliente real — deve encontrar o cliente via busca.

### 4.5 — Checklist final

- [ ] Portal `/portal/orcamento/:token` renderiza sem login
- [ ] Botão "Aprovar Orçamento" funciona e mostra confirmação
- [ ] Cmd+K / Ctrl+K abre a paleta de comandos
- [ ] Paleta busca clientes, OS e orçamentos
- [ ] Skeleton loaders aparecem durante carregamento
- [ ] Estados vazios exibidos quando não há dados
- [ ] 316+ testes, 0 falhas
- [ ] Build TypeScript sem erros

---

## ═══ REGRAS ═══

1. **Leia antes de criar** — se arquivo existe, edite.
2. **Rota pública do portal** — não pode exigir autenticação.
3. **Senha admin: `admin123`** não "Admin@123".
4. **PowerShell**: `;` em vez de `&&`.
5. **Não quebre testes** — rode após mudanças no backend.

## ORDEM DE PRIORIDADE

```
Fase 0  →  5 min
Fase 1  (Portal)  →  45 min  ← mais impacto de negócio
Fase 2  (Cmd+K)  →  30 min  ← melhor UX
Fase 3  (Polish) →  30 min  ← qualidade visual
Fase 4  (Verify) →  10 min  ← obrigatório
Total: ~2 horas
```
