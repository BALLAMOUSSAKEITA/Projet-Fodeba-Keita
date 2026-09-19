from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter()


async def check_redis() -> str:
    try:
        client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        await client.aclose()
        return "ok"
    except Exception:
        return "unavailable"


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    redis_status = await check_redis()

    return HealthResponse(
        status="ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status,
    )
