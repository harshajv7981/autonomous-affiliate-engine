from fastapi import FastAPI, HTTPException
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.analytics import router as analytics_router
from app.api.routes.offers import router as offers_router
from app.config import settings
from db.session import engine

app = FastAPI(title="Autonomous Affiliate Engine API")
app.include_router(offers_router)
app.include_router(analytics_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    checks: dict[str, str] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError:
        checks["database"] = "unavailable"

    redis_client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except RedisError:
        checks["redis"] = "unavailable"
    finally:
        redis_client.close()

    if any(status != "ok" for status in checks.values()):
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks})

    return {"status": "ready", "database": checks["database"], "redis": checks["redis"]}
