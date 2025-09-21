from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routers import health, tasks
from fastapi.responses import ORJSONResponse

setup_logging()
app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
