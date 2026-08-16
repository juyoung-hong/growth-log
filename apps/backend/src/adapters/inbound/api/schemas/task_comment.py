from datetime import datetime

from pydantic import BaseModel


class TaskCommentCreate(BaseModel):
    content: str


class TaskCommentUpdate(BaseModel):
    content: str


class TaskCommentRead(BaseModel):
    id: int
    task_id: int
    content: str
    created_at: datetime
    updated_at: datetime
