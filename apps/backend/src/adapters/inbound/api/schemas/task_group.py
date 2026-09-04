from datetime import datetime

from pydantic import BaseModel, field_serializer

from adapters.inbound.api.schemas._datetime import to_kst_iso
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


class TaskGroupProgress(BaseModel):
    total_tasks: int
    done_tasks: int
    percent: int


class TaskGroupRead(BaseModel):
    id: int
    category: Scope
    name: str
    description: str | None
    status: TaskStatus
    is_archived: bool
    created_at: datetime | None
    progress: TaskGroupProgress | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | None) -> str | None:
        return to_kst_iso(value) if value is not None else None
