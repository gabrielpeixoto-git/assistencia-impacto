from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
import redis.asyncio as redis
from app.config import settings

router = APIRouter(tags=["health"])

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check para Docker e monitoramento."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"erro: {e}"

    return {
        "status": "ok" if db_status == "ok" else "degradado",
        "banco": db_status,
        "versao": "1.0.0",
        "ambiente": settings.ambiente,
    }
