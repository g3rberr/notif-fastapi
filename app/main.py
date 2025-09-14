from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routers import health, tasks

setup_logging()
app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
