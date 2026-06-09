# PROMPT DEVIN — CORRIGIR PDF + PRÓXIMAS FEATURES
## Assistência Impacto — PDF funcional + WebSocket + Seed Fix
> Leia COMPLETO antes de executar. Prioridade: PDF → Seed → WebSocket.

---

## CONTEXTO

Stack: FastAPI + PostgreSQL + Redis + React 18 + TypeScript + Docker Compose
Localização: `c:\Projeto Impacto Soluções` 
Senha admin: `admin123` (importante: não é Admin@123)
App: `http://localhost` ou `http://localhost:5173` 

### Estado atual (após última sessão)
✅ 316 testes passando, cobertura 88%  
✅ Timezone BRT corrigido  
✅ ConfiguracoesPage com aba Usuários funcional  
✅ RelatoriosPage com 4 abas  
❌ PDF gera arquivo de ~1.7KB (suspeito — precisa verificação)  
❌ Dados do seed com quantidades float estranhas (3.5786..., 2.8413...)

---

## ═══ FASE 0 — PRÉ-CHECKS ═══

```powershell
docker compose ps
cd "c:\Projeto Impacto Soluções\backend"
python -m pytest tests/ -q 2>&1 | Select-String "passed|failed" | Select-Object -Last 2
```

---

## ═══ FASE 1 — DIAGNÓSTICO E CORREÇÃO DO PDF ═══

### 1.1 — Verificar se o PDF abre (teste de validade real)

Abrir um PDF de 1.7KB pode ser válido se o conteúdo for simples.
Vamos fazer um teste que verifica o conteúdo visual:

```powershell
docker compose exec backend python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.orcamento import Orcamento
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        orc = (await db.execute(select(Orcamento).limit(1))).scalar_one_or_none()
        from app.services.pdf_service import gerar_pdf_orcamento
        pdf = await gerar_pdf_orcamento(orc.id, db)
        
        # Verificar estrutura do PDF
        print(f'Tamanho: {len(pdf)} bytes')
        print(f'Cabeçalho válido: {pdf[:5] == b\"%PDF-\"}')
        print(f'Termina com EOF: {b\"%%EOF\" in pdf[-100:]}')
        
        # Contar páginas (marcador /Page no PDF)
        paginas = pdf.count(b'/Type /Page')
        print(f'Páginas encontradas: {paginas}')
        
        # Contar texto (marcador BT/ET de text block)
        blocos_texto = pdf.count(b'BT')
        print(f'Blocos de texto: {blocos_texto}')

asyncio.run(check())
"
```

**Interpretação:**
- Se `Páginas encontradas: 0` e `Blocos de texto: 0` → PDF está corrompido
- Se `Páginas: 1+` e `Blocos: 5+` → PDF é válido, apenas pequeno

### 1.2A — Se o PDF está corrompido: substituir por fpdf2

fpdf2 é mais simples que ReportLab e não tem o problema de BytesIO:

```powershell
docker compose exec backend pip install fpdf2 --break-system-packages
```

Verificar se instalou:
```powershell
docker compose exec backend python -c "import fpdf; print('fpdf2 OK')"
```

Reescrever a função no pdf_service.py:

```python
# Substitua a função gerar_pdf_orcamento por esta versão usando fpdf2:
from fpdf import FPDF

async def gerar_pdf_orcamento(orcamento_id: str, db: AsyncSession) -> bytes:
    """Gera PDF do orçamento usando fpdf2. Retorna bytes."""
    from app.models.orcamento import Orcamento, ItemOrcamento
    from app.models.cliente import Cliente
    from sqlalchemy import select
    
    # Buscar dados
    orc = (await db.execute(select(Orcamento).where(Orcamento.id == orcamento_id))).scalar_one_or_none()
    if not orc:
        raise ValueError(f"Orçamento {orcamento_id} não encontrado")
    
    cliente = (await db.execute(select(Cliente).where(Cliente.id == orc.cliente_id))).scalar_one_or_none()
    itens = (await db.execute(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id))).scalars().all()
    
    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cabeçalho
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(108, 99, 255)  # Violeta
    pdf.cell(0, 10, "Assistencia Impacto", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "contato@assistenciaimpacto.com.br | (51) 99999-9999", ln=True)
    pdf.ln(3)
    pdf.set_draw_color(108, 99, 255)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Título
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, f"ORCAMENTO No. {orc.numero_orcamento}", ln=True)
    
    from datetime import date
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Data de emissao: {date.today().strftime('%d/%m/%Y')}", ln=True)
    if orc.valido_ate:
        pdf.cell(0, 6, f"Valido ate: {orc.valido_ate.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Dados do cliente
    if cliente:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(108, 99, 255)
        pdf.cell(0, 7, "DADOS DO CLIENTE", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 6, f"Nome: {cliente.nome}", ln=True)
        if cliente.email:
            pdf.cell(0, 6, f"Email: {cliente.email}", ln=True)
        if cliente.telefone:
            pdf.cell(0, 6, f"Telefone: {cliente.telefone}", ln=True)
        pdf.ln(5)
    
    # Tabela de itens
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(0, 7, "ITENS DO ORCAMENTO", ln=True)
    pdf.ln(2)
    
    # Cabeçalho da tabela
    pdf.set_fill_color(108, 99, 255)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(85, 8, "Descricao", fill=True, border=1)
    pdf.cell(20, 8, "Qtd", fill=True, border=1, align="C")
    pdf.cell(20, 8, "Unid", fill=True, border=1, align="C")
    pdf.cell(35, 8, "Preco Unit.", fill=True, border=1, align="R")
    pdf.cell(30, 8, "Total", fill=True, border=1, align="R", ln=True)
    
    # Linhas de itens
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 9)
    fill = False
    for item in itens:
        fill_color = (248, 249, 250) if fill else (255, 255, 255)
        pdf.set_fill_color(*fill_color)
        
        desc = (item.descricao or "")[:40]  # Truncar se muito longo
        qtd = int(item.quantidade) if item.quantidade else 1
        unid = item.unidade or "un"
        preco_unit = item.preco_unitario or 0
        preco_total = item.preco_total or (preco_unit * qtd)
        
        pdf.cell(85, 7, desc, fill=True, border=1)
        pdf.cell(20, 7, str(qtd), fill=True, border=1, align="C")
        pdf.cell(20, 7, unid, fill=True, border=1, align="C")
        pdf.cell(35, 7, f"R$ {preco_unit:.2f}", fill=True, border=1, align="R")
        pdf.cell(30, 7, f"R$ {preco_total:.2f}", fill=True, border=1, align="R", ln=True)
        fill = not fill
    
    pdf.ln(5)
    
    # Totais
    subtotal = orc.subtotal or 0
    desconto = orc.valor_desconto or 0
    total = orc.total or subtotal
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(150, 7, "Subtotal:", align="R")
    pdf.cell(40, 7, f"R$ {subtotal:.2f}", align="R", ln=True)
    if desconto > 0:
        pdf.cell(150, 7, "Desconto:", align="R")
        pdf.cell(40, 7, f"- R$ {desconto:.2f}", align="R", ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(150, 8, "TOTAL:", align="R")
    pdf.cell(40, 8, f"R$ {total:.2f}", align="R", ln=True)
    pdf.ln(5)
    
    # Condições de pagamento
    if orc.condicoes_pagamento:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(108, 99, 255)
        pdf.cell(0, 7, "CONDICOES DE PAGAMENTO", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, orc.condicoes_pagamento)
        pdf.ln(3)
    
    # Assinatura
    pdf.ln(10)
    pdf.set_draw_color(150, 150, 150)
    pdf.line(10, pdf.get_y(), 95, pdf.get_y())
    pdf.line(105, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(95, 5, "Assistencia Impacto", align="C")
    pdf.cell(95, 5, cliente.nome if cliente else "Cliente", align="C", ln=True)
    
    # Rodapé
    pdf.ln(10)
    pdf.set_draw_color(108, 99, 255)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Assistencia Impacto | contato@assistenciaimpacto.com.br | (51) 99999-9999", align="C", ln=True)
    
    return bytes(pdf.output())
```

### 1.2B — Se o PDF é válido mas pequeno: aceitar e seguir em frente

Se o teste da seção 1.1 mostrou que o PDF tem páginas e blocos de texto válidos,
o tamanho pequeno é esperado para PDFs com conteúdo simples e sem imagens.
Marque esta tarefa como concluída e pule para a Fase 2.

### 1.3 — Fazer o mesmo para gerar_pdf_ordem_servico

Após corrigir o orçamento, aplique o mesmo padrão para a OS:

```python
async def gerar_pdf_ordem_servico(os_id: str, db: AsyncSession) -> bytes:
    """Gera PDF da OS usando fpdf2. Retorna bytes."""
    from app.models.ordem_servico import OrdemServico, ItemOrdemServico, ChecklistOrdemServico
    from app.models.cliente import Cliente
    from app.models.usuario import Usuario
    
    os_obj = (await db.execute(select(OrdemServico).where(OrdemServico.id == os_id))).scalar_one_or_none()
    if not os_obj:
        raise ValueError(f"OS {os_id} não encontrada")
    
    cliente = (await db.execute(select(Cliente).where(Cliente.id == os_obj.cliente_id))).scalar_one_or_none()
    tecnico = None
    if os_obj.tecnico_id:
        tecnico = (await db.execute(select(Usuario).where(Usuario.id == os_obj.tecnico_id))).scalar_one_or_none()
    itens = (await db.execute(select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os_id))).scalars().all()
    checklist = (await db.execute(select(ChecklistOrdemServico).where(ChecklistOrdemServico.ordem_servico_id == os_id))).scalars().all()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cabeçalho igual ao orçamento
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(0, 10, "Assistencia Impacto", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "contato@assistenciaimpacto.com.br | (51) 99999-9999", ln=True)
    pdf.ln(3)
    pdf.set_draw_color(108, 99, 255)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Título OS
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, f"ORDEM DE SERVICO No. {os_obj.numero_os}", ln=True)
    
    # Grid de informações
    status_val = os_obj.status.value if hasattr(os_obj.status, 'value') else str(os_obj.status)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Status: {status_val}  |  Cliente: {cliente.nome if cliente else 'N/A'}  |  Tecnico: {tecnico.nome_completo if tecnico else 'N/A'}", ln=True)
    if os_obj.data_agendada:
        pdf.cell(0, 6, f"Data agendada: {os_obj.data_agendada.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Descrição
    if os_obj.descricao:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(108, 99, 255)
        pdf.cell(0, 7, "DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, os_obj.descricao)
        pdf.ln(5)
    
    # Checklist
    if checklist:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(108, 99, 255)
        pdf.cell(0, 7, "CHECKLIST", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        for item in checklist:
            marcador = "[X]" if item.concluido else "[ ]"
            pdf.cell(0, 6, f"  {marcador}  {item.descricao}", ln=True)
        pdf.ln(5)
    
    # Materiais
    if itens:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(108, 99, 255)
        pdf.cell(0, 7, "MATERIAIS UTILIZADOS", ln=True)
        pdf.ln(2)
        pdf.set_fill_color(108, 99, 255)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 8, "Descricao", fill=True, border=1)
        pdf.cell(20, 8, "Qtd", fill=True, border=1, align="C")
        pdf.cell(30, 8, "Custo Unit.", fill=True, border=1, align="R")
        pdf.cell(50, 8, "Total", fill=True, border=1, align="R", ln=True)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 9)
        for item in itens:
            pdf.cell(90, 7, (item.descricao or "")[:45], border=1)
            pdf.cell(20, 7, str(int(item.quantidade or 1)), border=1, align="C")
            pdf.cell(30, 7, f"R$ {item.custo_unitario or 0:.2f}", border=1, align="R")
            pdf.cell(50, 7, f"R$ {item.custo_total or 0:.2f}", border=1, align="R", ln=True)
        pdf.ln(5)
    
    # Assinatura
    pdf.ln(8)
    pdf.set_draw_color(150, 150, 150)
    pdf.line(10, pdf.get_y(), 95, pdf.get_y())
    pdf.line(105, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(95, 5, tecnico.nome_completo if tecnico else "Tecnico", align="C")
    pdf.cell(95, 5, cliente.nome if cliente else "Cliente", align="C", ln=True)
    
    return bytes(pdf.output())
```

### 1.4 — Testar PDF após correção

```powershell
docker compose restart backend
Start-Sleep -Seconds 8
$resp = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"email":"admin@assistenciaimpacto.com.br","senha":"admin123"}'
$token = $resp.access_token
$id = "f89d789a-a004-4abb-b954-36bbb7ef2ce4"  # ID do primeiro orçamento
New-Item -ItemType Directory -Path "c:\temp" -Force | Out-Null
Invoke-RestMethod -Uri "http://localhost:8000/api/orcamentos/$id/pdf" `
  -Headers @{Authorization="Bearer $token"} `
  -OutFile "c:\temp\orcamento_fpdf.pdf"
$size = (Get-Item "c:\temp\orcamento_fpdf.pdf").Length
Write-Host "Tamanho: $size bytes"
Write-Host "OK? $(if($size -gt 5000){'SIM (>5KB)'}elseif($size -gt 2000){'PARCIAL (entre 2-5KB)'}else{'NAO (<2KB)'})"
```

---

## ═══ FASE 2 — CORRIGIR DADOS DO SEED ═══

> Quantidades como 3.5786094851493... vêm de `random.uniform()` — devem ser inteiros.

### 2.1 — Identificar o problema no seed.py

```powershell
cat "c:\Projeto Impacto Soluções\backend\seed.py" | Select-String "random|quantidade|uniform"
```

### 2.2 — Corrigir quantidades de itens

Substitua `random.uniform()` por `random.randint()` onde aplicável:

```python
# ERRADO (gera floats como 3.578...):
quantidade=random.uniform(1, 5)

# CORRETO (gera inteiros como 1, 2, 3, 4, 5):
quantidade=random.randint(1, 5)
```

Leia o seed.py e identifique TODAS as ocorrências de `random.uniform` usadas
para quantidades de itens. Substitua por `random.randint`.

### 2.3 — Resetar dados de orçamentos/itens e resseedear

```powershell
# Limpar apenas os dados de itens de orçamento (não os orçamentos em si)
docker compose exec banco psql -U postgres -d assistencia_impacto -c `
  "TRUNCATE TABLE itens_orcamento CASCADE;"

# Não precisa truncar orçamentos — o seed vai pular se já existirem
# Resseedear apenas os itens
docker compose exec backend python seed.py
```

---

## ═══ FASE 3 — ADICIONAR NOTIFICAÇÕES WEBSOCKET ═══

> WebSocket para notificações em tempo real é uma feature pendente de alto valor.

### 3.1 — Verificar estado atual do WebSocket

```powershell
cat "c:\Projeto Impacto Soluções\backend\app\websocket\gerenciador.py"
cat "c:\Projeto Impacto Soluções\backend\app\main.py" | Select-String "websocket|ws"
```

### 3.2 — Verificar o frontend para WebSocket

```powershell
cat "c:\Projeto Impacto Soluções\frontend\src\lib\websocket.ts" 2>nul
cat "c:\Projeto Impacto Soluções\frontend\src\hooks\useWebSocket.ts" 2>nul
```

### 3.3 — Se o WebSocket já existe no backend, conectar o frontend

O sino de notificações no TopBar deve conectar ao WebSocket e receber eventos em tempo real.

**No frontend, o hook useWebSocket deve:**
```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '../store/auth.store'
import { useNotificacaoStore } from '../store/notificacao.store'

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const { token } = useAuthStore()
  const { adicionarNotificacao, incrementarNaoLidas } = useNotificacaoStore()
  
  const conectar = useCallback(() => {
    if (!token) return
    
    const wsUrl = `ws://localhost:8000/ws/notificacoes?token=${token}` 
    ws.current = new WebSocket(wsUrl)
    
    ws.current.onmessage = (event) => {
      try {
        const notificacao = JSON.parse(event.data)
        adicionarNotificacao(notificacao)
        incrementarNaoLidas()
      } catch (e) {
        console.error('Erro ao processar notificação WebSocket', e)
      }
    }
    
    ws.current.onerror = () => {
      // Silenciar erros de conexão (servidor pode estar offline)
    }
    
    ws.current.onclose = () => {
      // Reconectar após 5 segundos se o token ainda existe
      if (token) {
        setTimeout(conectar, 5000)
      }
    }
  }, [token])
  
  useEffect(() => {
    conectar()
    return () => {
      ws.current?.close()
    }
  }, [conectar])
  
  const enviarMensagem = useCallback((dados: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(dados))
    }
  }, [])
  
  return { enviarMensagem }
}
```

**No TopBar, usar o hook:**
```typescript
// Adicionar ao TopBar.tsx ou AppLayout.tsx
import { useWebSocket } from '../hooks/useWebSocket'

// No componente:
useWebSocket() // Conecta automaticamente quando montado
```

### 3.4 — Se o WebSocket não existe no backend, implementar

Leia o `gerenciador.py` e `main.py` para ver se há rota `/ws/notificacoes`.
Se não houver, adicione ao backend:

```python
# backend/app/routers/notificacoes.py (adicionar ao final):
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.gerenciador import gerenciador_ws

@router.websocket("/ws")
async def websocket_notificacoes(
    websocket: WebSocket,
    token: str = Query(default=None)
):
    """WebSocket para notificações em tempo real."""
    try:
        # Validar token
        if not token:
            await websocket.close(code=4001)
            return
        
        payload = verificar_token(token)
        usuario_id = payload.get("sub")
        
        await gerenciador_ws.conectar(websocket, usuario_id)
        try:
            while True:
                await websocket.receive_text()  # Manter conexão viva
        except WebSocketDisconnect:
            gerenciador_ws.desconectar(websocket, usuario_id)
    except Exception:
        await websocket.close(code=4000)
```

```python
# backend/app/websocket/gerenciador.py:
from fastapi import WebSocket
from typing import Dict, List
import json

class GerenciadorWebSocket:
    def __init__(self):
        self.conexoes_ativas: Dict[str, List[WebSocket]] = {}
    
    async def conectar(self, websocket: WebSocket, usuario_id: str):
        await websocket.accept()
        if usuario_id not in self.conexoes_ativas:
            self.conexoes_ativas[usuario_id] = []
        self.conexoes_ativas[usuario_id].append(websocket)
    
    def desconectar(self, websocket: WebSocket, usuario_id: str):
        if usuario_id in self.conexoes_ativas:
            self.conexoes_ativas[usuario_id].remove(websocket)
    
    async def enviar_para_usuario(self, usuario_id: str, dados: dict):
        """Envia notificação para todas as conexões de um usuário."""
        if usuario_id in self.conexoes_ativas:
            mensagem = json.dumps(dados)
            conexoes_mortas = []
            for ws in self.conexoes_ativas[usuario_id]:
                try:
                    await ws.send_text(mensagem)
                except Exception:
                    conexoes_mortas.append(ws)
            for ws in conexoes_mortas:
                self.conexoes_ativas[usuario_id].remove(ws)
    
    async def broadcast(self, dados: dict):
        """Envia para todos os usuários conectados."""
        for usuario_id in list(self.conexoes_ativas.keys()):
            await self.enviar_para_usuario(usuario_id, dados)

gerenciador_ws = GerenciadorWebSocket()
```

---

## ═══ FASE 4 — VERIFICAÇÃO FINAL ═══

### 4.1 — Testes

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

### 4.3 — Checklist final

- [ ] PDF de orçamento maior que 2KB e abre corretamente
- [ ] Quantidades dos itens de orçamento são inteiros no banco (não floats como 3.578)
- [ ] WebSocket conecta sem erro no frontend (verificar console do browser)
- [ ] 316+ testes passando, 0 failed
- [ ] Build frontend sem erros TypeScript
- [ ] Todos os 7 containers Up

---

## ═══ REGRAS ═══

1. **Senha admin é `admin123`** — não "Admin@123". Documente isso.
2. **Leia antes de editar** — cat arquivo antes de modificar.
3. **Windows PowerShell** — `;` em vez de `&&`, `Select-String` em vez de `grep`.
4. **Não quebre testes** — rode após cada mudança no backend.
5. **Se fpdf2 não funcionar** — tente `pip install reportlab --upgrade` no container.
6. **IDs hardcoded** — não use IDs hardcoded nos testes, busque do banco.

---

## ORDEM DE PRIORIDADE

```
Fase 0  (pré-checks)          →  5 min
Fase 1  (PDF — diagnóstico)   →  10 min
Fase 1  (PDF — correção)      →  30 min (se necessário)
Fase 2  (seed fix)            →  15 min
Fase 3  (WebSocket)           →  45 min
Fase 4  (verificação)         →  10 min
Total estimado: ~1.5 a 2 horas
```

Se o PDF do passo 1.1 mostrar `Páginas: 1+` e `Blocos de texto: 5+`, pule para Fase 2.
O problema pode ser apenas que PDFs simples são pequenos, o que é normal.
