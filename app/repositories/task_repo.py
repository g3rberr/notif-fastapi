from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import load_only
from app.models.task import Task, TaskStatus

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, *, title: str, payload: str | None) -> Task:
        obj = Task(title=title, payload=payload, status=TaskStatus.PENDING)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[Task]:
        stmt = (
            select(Task)
            .options(load_only(Task.id, Task.title, Task.payload, Task.status, Task.created_at))
            .order_by(Task.created_at.desc(), Task.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def set_status(self, task_id: UUID, status: TaskStatus) -> Task | None:
        await self.session.execute(update(Task).where(Task.id == task_id).values(status=status))
        await self.session.commit()
        res = await self.session.execute(select(Task).where(Task.id == task_id))
        return res.scalars().first()
