from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.sqlalchemy_url,
    echo=False,
    future=True,
    pool_size=16,
    max_overflow=16,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=3,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
