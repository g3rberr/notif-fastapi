import asyncio, json, logging
from uuid import UUID
from app.core.config import settings
from app.services.pubsub import get_redis_client, PubSub
from app.db.session import SessionLocal
from app.repositories.task_repo import TaskRepository
from app.models.task import TaskStatus

log = logging.getLogger("worker")

async def handle_existing(task_id: UUID):
    async with SessionLocal() as session:
        repo = TaskRepository(session)
        await repo.set_status(task_id, TaskStatus.PROCESSING)
        await asyncio.sleep(0.002)
        await repo.set_status(task_id, TaskStatus.DONE)

async def handle_new(title: str, payload: str | None):
    async with SessionLocal() as session:
        repo = TaskRepository(session)
        obj = await repo.add(title=title, payload=payload)
        await asyncio.sleep(0.002)
        await repo.set_status(obj.id, TaskStatus.DONE)

async def run():
    redis = get_redis_client()
    bus = PubSub(redis, settings.redis_channel)
    ps = await bus.subscribe()
    log.info("subscribed to channel '%s'", settings.redis_channel)
    try:
        async for msg in ps.listen():
            if not msg or msg.get("type") != "message":
                continue
            raw = msg.get("data")
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if "event_id" in data and "title" in data:
                await handle_new(data["title"], data.get("payload"))
            elif "task_id" in data:
                try:
                    tid = UUID(data["task_id"])
                except Exception:
                    continue
                await handle_existing(tid)
    finally:
        await ps.aclose()

if __name__ == "__main__":
    asyncio.run(run())
