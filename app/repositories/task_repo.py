from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_, insert
from sqlalchemy.orm import load_only
from app.models.task import Task, TaskStatus
from app.core.config import settings

from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.task import Task, TaskStatus

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, *, title: str, payload: str | None, max_attempts: int | None = None) -> Task:
        stmt = (
            insert(Task)
            .values(
                title=title,
                payload=payload,
                status=TaskStatus.PENDING,
                max_attempts=max_attempts or settings.max_attempts,
            )
            .returning(Task)
        )
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.scalar_one()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[Task]:
        stmt = (
            select(Task)
            .options(load_only(
                Task.id, Task.title, Task.payload, Task.status, Task.created_at,
                Task.attempt_count, Task.max_attempts, Task.next_attempt_at,
                Task.locked_by, Task.last_error, Task.updated_at
            ))
            .order_by(Task.created_at.desc(), Task.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, task_id: UUID) -> Task | None:
        res = await self.session.execute(select(Task).where(Task.id == task_id))
        return res.scalars().first()

    async def mark_processing(self, task_id: UUID, worker_id: str | None = None) -> None:
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                status=TaskStatus.PROCESSING,
                locked_by=worker_id,
                locked_at=func.now(),
            )
        )
        await self.session.commit()

    async def set_done(self, task_id: UUID) -> None:
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskStatus.DONE, locked_by=None, last_error=None, next_attempt_at=None)
        )
        await self.session.commit()

    async def schedule_retry(self, task_id: UUID, *, attempt_inc: int, last_error: str, next_attempt_at):
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                status=TaskStatus.PENDING,
                attempt_count=Task.attempt_count + attempt_inc,
                last_error=last_error[:2000],
                next_attempt_at=next_attempt_at,
                locked_by=None,
            )
        )
        await self.session.commit()

    async def set_failed(self, task_id: UUID, *, last_error: str | None = None):
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=TaskStatus.FAILED, last_error=(last_error[:2000] if last_error else None), locked_by=None)
        )
        await self.session.commit()

    async def list_due_pending(self, *, limit: int = 100) -> Sequence[Task]:
        now = func.now()
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.status == TaskStatus.PENDING,
                    or_(Task.next_attempt_at.is_(None), Task.next_attempt_at <= now),
                    Task.attempt_count < Task.max_attempts,
                )
            )
            .order_by(Task.created_at.asc(), Task.id.asc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def ensure_processing(self, task_id: UUID, *, title: str, payload: str, worker_id: str | None):
        stmt = (
            pg_insert(Task)
            .values(id=task_id, title=title, payload=payload,
                    status=TaskStatus.PROCESSING, locked_by=worker_id)
            .on_conflict_do_update(
                index_elements=[Task.id],
                set_={"status": TaskStatus.PROCESSING, "locked_by": worker_id}
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
