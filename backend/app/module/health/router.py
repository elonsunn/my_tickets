import asyncio
from collections.abc import Awaitable

import structlog
from fastapi import APIRouter, Response
from sqlalchemy import text

from app.core.database import DBsession
from app.module.health.schema import ReadinessProbeResponse

router = APIRouter(prefix="/health", tags=["health"])
logger = structlog.get_logger(__name__)
PROBE_TIMEOUT = 2


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response, db: DBsession) -> ReadinessProbeResponse:
    healthy = await _health_probe(db.execute(text("SELECT 1")))
    response.status_code = 200 if healthy else 503
    return ReadinessProbeResponse(status="ok" if healthy else "unavailable")


async def _health_probe(check: Awaitable[object]) -> bool:
    try:
        async with asyncio.timeout(PROBE_TIMEOUT):
            await check
    except Exception:
        logger.warning("database readiness probe failed", exc_info=True)
        return False
    return True
