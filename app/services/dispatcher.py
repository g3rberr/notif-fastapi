import asyncio
from app.db.session import SessionLocal
from app.repositories.task_repo import TaskRepository
from app.services.tasks_email import send_email_task

CHECK_INTERVAL_SEC = 5
BATCH_LIMIT = 100

async def dispatch_due_tasks():
    async with SessionLocal() as session:
        repo = TaskRepository(session)
        due = await repo.list_due_pending(limit=BATCH_LIMIT)
        for t in due:
            send_email_task.delay(str(t.id), t.payload or "")

async def run_forever():
    while True:
        try:
            await dispatch_due_tasks()
        except Exception as e:
            print(f"[dispatcher] error: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(run_forever())
