from fastapi import APIRouter, Depends, status, Query
import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.task import TaskRead, EmailTaskCreate
from app.db.session import get_session
from app.repositories.task_repo import TaskRepository
from app.services.tasks_email import send_email_task
from uuid import uuid4


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/email", status_code=status.HTTP_202_ACCEPTED)
async def create_email_task(body: EmailTaskCreate):
    task_id = str(uuid4())
    payload = f'{{"to":"{body.to}","subject":{json.dumps(body.subject)},"message":{json.dumps(body.message)} }}'
    send_email_task.delay(task_id, payload)
    return {"accepted": True, "task_id": task_id}

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    repo = TaskRepository(session)
    tasks = await repo.list(limit=limit, offset=offset)
    return [TaskRead.model_validate(t) for t in tasks]
