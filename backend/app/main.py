from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import init_db
from loguru import logger
import sys


# Configurar logger
logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida do app."""
    logger.info("Iniciando aplicação Assistência Impacto...")
    # Inicializar banco de dados
    await init_db()
    logger.info("Banco de dados inicializado com sucesso")
    yield
    logger.info("Encerrando aplicação...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Assistência Impacto API",
    description="API do sistema de gestão para manutenção residencial e comercial",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar state do limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar diretório de uploads como arquivos estáticos
# app.mount("/uploads", StaticFiles(directory=settings.diretorio_uploads), name="uploads")

# Rota de health check
@app.get("/health")
async def health_check():
    """Verificação de saúde da API."""
    from app.database import get_db
    from sqlalchemy import text

    try:
        # Testar conexão com banco de dados
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            break

        return {
            "status": "ok",
            "servico": "assistencia-impacto-api",
            "versao": "1.0.0",
            "banco_dados": "conectado",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check falhou: {str(e)}")
        return {
            "status": "error",
            "servico": "assistencia-impacto-api",
            "banco_dados": "desconectado",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Importar routers
from app.routers import auth, usuarios, clientes, ordens_servico, orcamentos, agenda, financeiro, estoque, dashboard, categorias_servico, configuracoes, notificacoes, health, portal, whatsapp
from app.websocket import handler as websocket_handler

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuários"])
app.include_router(clientes.router)
app.include_router(ordens_servico.router)
app.include_router(orcamentos.router)
app.include_router(agenda.router)
app.include_router(financeiro.router)
app.include_router(estoque.router)
app.include_router(dashboard.router)
app.include_router(categorias_servico.router)
app.include_router(configuracoes.router)
app.include_router(notificacoes.router, prefix="/api")
app.include_router(health.router)
app.include_router(portal.router)
app.include_router(whatsapp.router)

# Incluir rotas WebSocket
app.include_router(websocket_handler.router, prefix="/api", tags=["WebSocket"])

# Middleware para SPA: retorna index.html para rotas não-API
# @app.middleware("http")
# async def spa_middleware(request: Request, call_next):
#     """Middleware para SPA: retorna index.html para rotas não-API."""
#     path = request.url.path
#     
#     # Rotas da API não devem ser interceptadas
#     api_routes = ["/api", "/health", "/ws", "/docs", "/redoc", "/openapi.json"]
#     if any(path.startswith(route) for route in api_routes):
#         return await call_next(request)
#     
#     # Arquivos estáticos (assets) não devem ser interceptados
#     if path.startswith("/assets/") or path.startswith("/logo.svg"):
#         return await call_next(request)
#     
#     # Para outras rotas, tenta servir o arquivo estático primeiro
#     response = await call_next(request)
#     
#     # Se for 404 e não for rota da API, retorna index.html
#     if response.status_code == 404:
#         return FileResponse("/app/frontend/dist/index.html")
#     
#     return response

# Montar frontend estático (depois dos routers para não interceptar rotas da API)
# try:
#     app.mount("/", StaticFiles(directory="/app/frontend/dist", html=True), name="frontend")
# except Exception as e:
#     logger.warning(f"Não foi possível montar frontend estático: {e}")
