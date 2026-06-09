# PROMPT DEVIN — CORREÇÃO DEFINITIVA DO ERRO 500 NO LOGIN
## Prioridade: CRÍTICA | Não pare até resolver completamente

---

## O PROBLEMA EXATO

O browser mostra: `POST http://localhost:5173/api/auth/login → 500 (Internal Server Error)`

O Devin anterior testou o backend com Python e recebeu 200 — **isso não reproduz o erro**.
O problema acontece especificamente quando a requisição vem do **browser através do proxy do Vite**.
Você deve reproduzir e corrigir o erro exato, não contorná-lo.

---

## PASSO 1 — CAPTURAR O TRACEBACK REAL DO BACKEND

### 1.1 Inicie o backend com saída de erro completa

```powershell
cd "C:\Projeto Impacto Soluções\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug 2>&1
```

Deixe este terminal aberto e visível. Cada requisição irá mostrar logs aqui.

### 1.2 Simule EXATAMENTE como o browser faz a requisição

Em outro terminal, execute este comando que imita o browser com cabeçalhos Origin:

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "http://localhost:5173"
    "Referer" = "http://localhost:5173/login"
}
$body = '{"email":"admin@assistenciaimpacto.com.br","senha":"admin123"}' 
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method POST -Headers $headers -Body $body -UseBasicParsing
```

### 1.3 Leia o traceback completo

Volte ao terminal do backend (Passo 1.1) e copie o traceback completo do erro.
**O traceback vai mostrar exatamente qual linha de código está quebrando.**

Procure por linhas como:
```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "...", line X, in ...
    <código que falhou>
```

---

## PASSO 2 — VERIFICAR OS SUSPEITOS MAIS COMUNS

### 2.1 Verificar o arquivo de autenticação

Leia estes arquivos completamente e identifique o problema:

```
backend/app/routers/auth.py
backend/app/services/auth_service.py
backend/app/core/seguranca.py
backend/app/dependencies.py
```

Procure por:
- Código que tenta acessar o banco de dados e pode falhar em sessão async
- `response.set_cookie()` com parâmetros incorretos (como `samesite` inválido)
- Import de módulo que pode estar falhando silenciosamente
- `await` faltando em operação assíncrona

### 2.2 Verificar o endpoint de login especificamente

No arquivo `auth.py` (router), encontre o endpoint `POST /login` e verifique:

```python
# PROBLEMA COMUM 1: SameSite inválido no cookie
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    samesite="lax",   # deve ser "lax", "strict" ou "none" (lowercase)
    secure=False,     # False em desenvolvimento
    max_age=604800,
)

# PROBLEMA COMUM 2: import de módulo que quebra
# Verifique se todos os imports no topo do arquivo estão funcionando
```

### 2.3 Verificar se há erro de import em algum módulo

Execute este comando para ver se há erro de import:

```powershell
cd "C:\Projeto Impacto Soluções\backend"
python -c "from app.routers.auth import router; print('OK')"
python -c "from app.services.auth_service import AuthService; print('OK')"
python -c "from app.core.seguranca import criar_token_acesso; print('OK')"
```

Se qualquer um deles mostrar erro, esse é o problema.

### 2.4 Verificar conexão com banco de dados durante requisição real

```powershell
cd "C:\Projeto Impacto Soluções\backend"
python -c "
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT email FROM usuarios LIMIT 1'))
        row = result.fetchone()
        print('Usuário encontrado:', row)
asyncio.run(test())
"
```

---

## PASSO 3 — VERIFICAR O PROXY DO VITE

Leia `frontend/vite.config.ts` e confirme que está EXATAMENTE assim:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
      },
    }
  }
})
```

**IMPORTANTE:** Se o proxy estiver usando `rewrite: (path) => path.replace(/^\/api/, '')`,
isso remove o `/api` antes de enviar para o backend — o que faz o backend não encontrar a rota.
Nesse caso, ou remova o rewrite OU ajuste o target para `http://localhost:8000/api`.

### 3.1 Verificar o arquivo api.ts

Leia `frontend/src/lib/api.ts` e confirme o baseURL:

```typescript
// CORRETO — usa proxy relativo
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

// ERRADO — URL absoluta que bypassa o proxy
const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // isso causa CORS!
})
```

Se estiver com URL absoluta, corrija para `/api`.

### 3.2 Verificar arquivo .env do frontend

Se existir `frontend/.env`, verifique se tem `VITE_API_URL` e como é usado no `api.ts`.
Se o `api.ts` usa `import.meta.env.VITE_API_URL` como baseURL, isso causa CORS 500.
Corrija para usar `/api` fixo.

---

## PASSO 4 — TESTE DEFINITIVO

Após corrigir o problema identificado:

### 4.1 Reinicie o backend

```powershell
# Mate qualquer processo Python na porta 8000
netstat -ano | findstr :8000
# Anote o PID e execute:
taskkill /F /PID <PID>

# Inicie novamente
cd "C:\Projeto Impacto Soluções\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4.2 Teste com Origin do browser (deve retornar 200)

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Origin" = "http://localhost:5173"
}
$body = '{"email":"admin@assistenciaimpacto.com.br","senha":"admin123"}'
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method POST -Headers $headers -Body $body -UseBasicParsing
Write-Host "Status:" $response.StatusCode
Write-Host "Conteúdo:" $response.Content.Substring(0, 100)
```

**Critério de sucesso: StatusCode = 200**

### 4.3 Teste através do proxy Vite (deve retornar 200)

```powershell
$headers = @{"Content-Type" = "application/json"}
$body = '{"email":"admin@assistenciaimpacto.com.br","senha":"admin123"}'
$response = Invoke-WebRequest -Uri "http://localhost:5173/api/auth/login" -Method POST -Headers $headers -Body $body -UseBasicParsing
Write-Host "Status:" $response.StatusCode
```

**Critério de sucesso: StatusCode = 200**

---

## PASSO 5 — SE O BANCO DE DADOS ESTIVER COM PROBLEMA

Se os testes do Passo 2.4 falharem, o PostgreSQL pode estar inacessível. Verifique:

```powershell
# Verificar se PostgreSQL está rodando
netstat -ano | findstr :5432
```

Se a porta 5432 não aparecer, o PostgreSQL não está rodando.
Inicie o serviço do PostgreSQL:

```powershell
Start-Service postgresql*
```

Ou se usar PostgreSQL portátil:
```powershell
cd "C:\Projeto Impacto Soluções"
# Verificar se tem docker-compose.yml com postgres
type docker-compose.yml | findstr postgres
```

---

## PASSO 6 — VERIFICAR MIGRAÇÕES DO BANCO

Talvez as migrações não estejam aplicadas corretamente:

```powershell
cd "C:\Projeto Impacto Soluções\backend"
python -m alembic current
python -m alembic upgrade head
```

Se alembic falhar, verifique o `DATABASE_URL` no arquivo `.env` do backend.

---

## REGRAS ABSOLUTAS

1. **NÃO** declare o problema resolvido sem fazer o teste do Passo 4.3 (via proxy 5173)
2. **NÃO** teste apenas com `requests.post()` no Python sem o header `Origin`
3. **LEIA** o traceback completo do backend antes de tentar qualquer correção
4. **SE** encontrar o traceback, cole-o completo no chat antes de corrigir
5. **APÓS** cada correção, rode `npx tsc --noEmit` no frontend para garantir 0 erros TypeScript
6. **BUILD** final: `cd frontend && npm run build` deve passar com 0 erros

---

## CHECKLIST — SÓ FINALIZE QUANDO TUDO VERDE

- [ ] Traceback do erro 500 foi identificado e lido
- [ ] Causa raiz corrigida no arquivo correto
- [ ] Teste via Python COM header Origin retorna 200
- [ ] Teste via proxy Vite (porta 5173) retorna 200
- [ ] Login funciona no browser (http://localhost:5173/login)
- [ ] `npm run build` passa com 0 erros
- [ ] Console do browser (F12) sem erros vermelhos após login
