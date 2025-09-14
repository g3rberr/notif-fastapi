from app.db.session import engine
from app.db.base import Base
from app.models import task

async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
