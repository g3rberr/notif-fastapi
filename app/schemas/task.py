from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

class TaskRead(BaseModel):
    id: UUID
    title: str
    payload: Optional[str]
    status: TaskStatus

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    payload: str | dict | None = None