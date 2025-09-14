from fastapi import APIRouter, Depends, status, Query
import orjson
from typing import List
from app.schemas.task import TaskRead, TaskCreate
from app.api.deps import get_task_service
from app.services.task_service import TaskService
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    body: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    title = body.title
    payload = body.payload
    if payload is not None and not isinstance(payload, str):
        payload = orjson.dumps(payload).decode()
    event_id = await service.publish(title=title, payload=payload)
    return {"accepted": True, "event_id": event_id}

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    repo = TaskRepository(session)
    tasks = await repo.list(limit=limit, offset=offset)
    return [TaskRead.model_validate(t) for t in tasks]
