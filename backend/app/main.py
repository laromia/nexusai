from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A unified AI orchestration platform "
        "integrating multiple AI providers."
    ),
    debug=settings.DEBUG
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to NexusAI",
        "version": settings.APP_VERSION,
        "status": "running"
    }


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)