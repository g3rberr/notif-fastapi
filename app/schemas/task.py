from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from enum import Enum
from datetime import datetime

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
    attempt_count: int
    max_attempts: int
    next_attempt_at: Optional[datetime] = None
    locked_by: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class EmailTaskCreate(BaseModel):
    to: EmailStr
    subject: Optional[str] = None
    message: str
