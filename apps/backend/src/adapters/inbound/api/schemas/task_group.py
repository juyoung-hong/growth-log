from pydantic import BaseModel

from domain.common.enums import Scope, TaskStatus


class TaskGroupCreate(BaseModel):
    category: Scope
    name: str
    description: str | None = None
    status: TaskStatus = TaskStatus.IN_PROGRESS


class TaskGroupUpdate(BaseModel):
    category: Scope | None = None
    name: str | None = None
    description: str | None = None
    status: TaskStatus | None = None


class TaskGroupRead(BaseModel):
    id: int
    category: Scope
    name: str
    description: str | None
    status: TaskStatus
    is_archived: bool
