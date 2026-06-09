# PROMPT DEVIN AI — DIAGNÓSTICO E CORREÇÃO COMPLETA
## Sistema: Assistência Impacto | Prioridade: CRÍTICA

---

## CONTEXTO DO PROBLEMA

Você é um engenheiro sênior de software full-stack. O sistema **Assistência Impacto** está com
dois problemas que você deve resolver completamente, **sem interromper para perguntas**,
avançando fase por fase até tudo estar funcionando.

**Problema 1 (CRÍTICO):** O endpoint `POST /api/auth/login` está retornando erro **500 Internal
Server Error** quando chamado pelo frontend. O login está completamente quebrado.

**Problema 2:** A aba Agenda está com design fraco e precisar ser redesenhada visualmente.

Stack: FastAPI + SQLAlchemy 2.0 async + PostgreSQL + React 18 + TypeScript + Tailwind CSS + Vite.

---

## FASE 1 — DIAGNÓSTICO DO ERRO 500 NO LOGIN

### Passo 1.1 — Capturar o erro exato do backend

Execute o backend em modo verbose e capture o traceback completo do erro 500:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

Depois, em outro terminal, faça uma requisição de teste para forçar o erro e ver o traceback:

```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@assistenciaimpacto.com.br","senha":"Admin@123"}' \
  -v
```

Leia o traceback completo nos logs do uvicorn. **NÃO avance para o Passo 1.2 sem identificar
a causa raiz exata.**

### Passo 1.2 — Verificar os arquivos modificados recentemente

Liste todos os arquivos alterados nas últimas 24 horas para identificar o que foi mudado:

```bash
find . -newer .gitignore -name "*.py" -o -newer .gitignore -name "*.ts" \
  -o -newer .gitignore -name "*.tsx" | grep -v node_modules | grep -v __pycache__
```

Leia o conteúdo de cada arquivo Python modificado recentemente, especialmente:
- `backend/app/routers/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/core/seguranca.py`
- `backend/app/database.py`
- `backend/app/main.py`

### Passo 1.3 — Verificar configuração CORS

Leia `backend/app/main.py` e verifique se o middleware CORS está configurado com
`allow_origins` incluindo `http://localhost:5173`. Se estiver com `origins=["*"]` isso pode
causar problemas em alguns cenários. O correto é:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000",
                   "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Passo 1.4 — Verificar proxy do Vite

Leia `frontend/vite.config.ts` e confirme que o proxy está configurado assim:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    },
    '/ws': {
      target: 'ws://localhost:8000',
      ws: true,
    }
  }
}
```

### Passo 1.5 — Verificar arquivo .env do frontend

Leia o arquivo `frontend/.env`. Se existir `VITE_API_URL=http://localhost:8000`, isso pode
estar causando que o `api.ts` use URL absoluta (bypassando o proxy do Vite), gerando erro de
CORS ou dupla rota. Corrija o baseURL no `frontend/src/lib/api.ts` para:

```typescript
const api = axios.create({
  baseURL: '/api',  // RELATIVO — usa o proxy do Vite
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})
```

Se o `.env` tiver `VITE_API_URL`, confirme que o `api.ts` usa o proxy e não a variável
diretamente. Remova ou corrija conforme necessário.

### Passo 1.6 — Verificar schema do endpoint de login

Leia o router de autenticação e confirme o schema do body do login. O frontend deve enviar
exatamente os campos que o backend espera. Verifique:

- Backend (`backend/app/schemas/usuario.py` ou onde estiver o schema de login): confirme os
  nomes dos campos (ex: `email` e `senha`, ou `username` e `password`).
- Frontend (`frontend/src/pages/auth/LoginPage.tsx` ou onde faz o POST): confirme que está
  enviando os campos com os mesmos nomes.

Se houver divergência, corrija o frontend para enviar os nomes corretos.

### Passo 1.7 — Testar o banco de dados

Verifique se o PostgreSQL está rodando e acessível:

```bash
cd backend
python -c "
import asyncio
from app.database import engine
async def test():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('DB OK:', result.fetchone())
asyncio.run(test())
"
```

Se o banco não estiver acessível, verifique o arquivo `.env` do backend e inicie o PostgreSQL.

### Passo 1.8 — Reiniciar tudo e validar

Após identificar e corrigir a causa raiz:

1. Reinicie o backend
2. Reinicie o frontend
3. Execute o teste de login via curl e confirme status 200
4. Acesse http://localhost:5173 e faça login pela interface

**Critério de sucesso:** Login funcionando com `admin@assistenciaimpacto.com.br` e `Admin@123`.
Se as credenciais do seed forem diferentes, confirme no arquivo `backend/seed.py`.

---

## FASE 2 — REDESENHO COMPLETO DA ABA AGENDA

Após confirmar que o login está funcionando, redesenhe completamente o
`frontend/src/pages/agenda/AgendaPage.tsx` (ou o caminho equivalente onde está a AgendaPage).

### Requisitos visuais obrigatórios

**Tema:** Dark futurístico com glassmorphism, igual ao restante do sistema.
- Fundo: `#0A0B0F` / Superfície: `#111318` / Elevado: `#1A1D27`
- Cor primária: `#6C63FF` (violeta) / Secundária: `#00D4FF` (ciano)
- Cards: `backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl`

### Layout da nova Agenda

#### Header da página
```
[ ← Junho 2025 → ]   [ Hoje ]   [ Dia | Semana | Mês | Lista ]   [ + Novo Evento ]
```
- Título do mês com seta de navegação (prev/next)
- Botão "Hoje" para voltar à data atual
- Toggle de visualização: Dia / Semana / Mês / Lista
- Botão "+ Novo Evento" com gradiente violeta→ciano e efeito glow

#### Filtro de técnicos (logo abaixo do header)
- Avatares circulares clicáveis de cada técnico com cor personalizada
- "Todos" selecionado por padrão
- Técnico selecionado fica com borda brilhante violeta

#### Visualização Mês (padrão)
- Grade 7×5/6 com dias da semana no cabeçalho
- Dia atual: borda violeta + fundo violeta/10
- Dias fora do mês: opacidade 30%
- Eventos no dia: pills coloridos com nome truncado, máximo 3 visíveis + "+N mais"
- Cada evento com cor baseada no técnico ou tipo de serviço
- Hover no dia: fundo sutil + cursor pointer
- Clicar no dia: abre painel lateral de detalhes

#### Visualização Semana
- 7 colunas (dias) com cabeçalho mostrando dia da semana + número
- Eixo Y: horas (07h até 22h) com linhas guia
- Eventos posicionados na hora exata como blocos coloridos
- Eventos sobrepostos aparecem lado a lado
- Arrastar evento para reagendar (se possível, implementar drag básico)

#### Visualização Lista
- Agrupado por data (ex: "Hoje — Quinta, 5 Jun" como separador)
- Cada evento em card glassmorphism com:
  - Ícone grande (colorido conforme tipo) à esquerda
  - Título, nome do cliente e técnico responsável
  - Horário (ex: "09:00 – 11:00") com ícone de relógio
  - Endereço com ícone de localização
  - Badge de status colorido (agendado/confirmado/em andamento/concluído/cancelado)
  - Botões "Editar" e "Excluir" aparecem no hover à direita
- Estado vazio: ilustração SVG + "Nenhum evento para este período"

#### Painel lateral de detalhes (Sheet/Drawer)
Ao clicar em um evento ou dia:
- Slide-in pela direita com largura de 420px
- Título do evento com ícone colorido grande
- Informações: cliente, técnico, data/hora, endereço, status
- Se tiver OS vinculada: link para abrir a OS
- Botão "Editar Evento" e "Excluir"
- Botão "Fechar" no topo direito

#### Modal de novo/editar evento
Formulário em Dialog glassmorphism com:
- Título do evento (obrigatório)
- Tipo do evento: Serviço / Reunião / Manutenção / Indisponível / Outro (ícones)
- Cliente (autocomplete com busca)
- Técnico responsável (select com avatares)
- Data e hora início / Data e hora fim
- Endereço / Local (opcional)
- Observações (textarea)
- Cor do evento (palette de 8 cores)
- Botão "Salvar" com loading state
- Validação com React Hook Form + Zod em tempo real

#### Animações obrigatórias
- Entrada da página: `opacity: 0, x: -20` → `opacity: 1, x: 0` (Framer Motion)
- Painel lateral: slide da direita com spring animation
- Modal: scale + fade
- Troca de visualização (mês/semana/lista): crossfade
- Skeleton loaders enquanto carrega dados da API

### Código obrigatório no componente

```tsx
// Estrutura mínima obrigatória
const AgendaPage = () => {
  const [viewMode, setViewMode] = useState<'mes' | 'semana' | 'dia' | 'lista'>('mes')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [tecnicoFiltro, setTecnicoFiltro] = useState<string | null>(null)
  const [eventoSelecionado, setEventoSelecionado] = useState<Evento | null>(null)
  const [panelAberto, setPanelAberto] = useState(false)
  const [modalAberto, setModalAberto] = useState(false)
  const [eventoEditando, setEventoEditando] = useState<Evento | null>(null)

  // Query de eventos
  const { data: eventos, isLoading } = useQuery({
    queryKey: ['agenda', format(currentDate, 'yyyy-MM'), tecnicoFiltro],
    queryFn: () => agendaService.listar({
      de: startOfMonth(currentDate).toISOString(),
      ate: endOfMonth(currentDate).toISOString(),
      tecnico_id: tecnicoFiltro ?? undefined,
    }),
  })

  // Mapa de eventos por data (otimização de performance)
  const eventosPorDia = useMemo(() => {
    const mapa = new Map<string, Evento[]>()
    eventos?.forEach(evento => {
      const chave = format(parseISO(evento.data_hora_inicio), 'yyyy-MM-dd')
      if (!mapa.has(chave)) mapa.set(chave, [])
      mapa.get(chave)!.push(evento)
    })
    return mapa
  }, [eventos])

  // ... renderização dos componentes
}
```

### Cores por tipo de evento

```typescript
const CORES_EVENTO = {
  servico:      { bg: '#6C63FF20', border: '#6C63FF', text: '#6C63FF' },
  reuniao:      { bg: '#00D4FF20', border: '#00D4FF', text: '#00D4FF' },
  manutencao:   { bg: '#F59E0B20', border: '#F59E0B', text: '#F59E0B' },
  indisponivel: { bg: '#EF444420', border: '#EF4444', text: '#EF4444' },
  outro:        { bg: '#94A3B820', border: '#94A3B8', text: '#94A3B8' },
}
```

### Ícones por tipo (Lucide React)

```typescript
const ICONES_EVENTO = {
  servico:      Wrench,
  reuniao:      Users,
  manutencao:   Settings,
  indisponivel: XCircle,
  outro:        Calendar,
}
```

---

## FASE 3 — TESTES E VALIDAÇÃO FINAL

### 3.1 — Build sem erros

```bash
cd frontend
npm run build
```
**Critério:** Build deve completar com 0 erros TypeScript e 0 erros de compilação.

### 3.2 — Teste de login

Confirme que as seguintes ações funcionam:
1. Acessar http://localhost:5173 redireciona para `/login`
2. Login com credenciais corretas redireciona para o dashboard
3. Login com credenciais incorretas mostra mensagem de erro

### 3.3 — Teste da Agenda

Confirme que:
1. A aba Agenda carrega sem erros no console
2. Visualizações Mês / Semana / Lista alternam corretamente
3. Modal de novo evento abre, valida e salva
4. Painel lateral abre ao clicar em evento
5. Skeleton loaders aparecem durante carregamento

---

## FASE 4 — REGRAS ABSOLUTAS (NÃO VIOLE)

1. **NÃO modifique** nenhum arquivo de backend sem ter certeza absoluta que é necessário.
2. **NÃO delete** funções ou variáveis que estejam sendo usadas em outros lugares.
3. **Antes de remover** qualquer código existente, faça uma busca global para garantir
   que não está sendo importado ou usado em outro arquivo.
4. **Se encontrar múltiplos problemas**, resolva-os um por um, testando após cada correção.
5. **NÃO reinicie** o servidor enquanto tiver uma operação de escrita de banco de dados
   em andamento.
6. **Após cada mudança** em arquivo TypeScript, verifique se há erros com:
   `cd frontend && npx tsc --noEmit`
7. **Mantenha** todo o design system existente (cores, glassmorphism, fontes, Tailwind config).

---

## CHECKLIST FINAL — SÓ TERMINE QUANDO TUDO ESTIVER VERDE

- [ ] Login funcionando (status 200 da API + redirect correto no frontend)
- [ ] Sem erros 500 ou 4xx inesperados no backend
- [ ] `npm run build` passa com 0 erros
- [ ] Aba Agenda com novo design funcionando completamente
- [ ] Todas as 4 visualizações (Mês/Semana/Lista/Dia) renderizando
- [ ] Modal de novo evento funcionando (criar e editar)
- [ ] Filtro de técnicos funcionando
- [ ] Sem console.error() no browser (F12 deve estar limpo)
- [ ] Nenhuma outra página do sistema foi quebrada
