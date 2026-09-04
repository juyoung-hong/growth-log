from datetime import date, datetime

from pydantic import BaseModel, field_serializer

from adapters.inbound.api.schemas._datetime import to_kst_iso
from domain.common.enums import TaskStatus


class TaskCreate(BaseModel):
    name: str
    estimated_days: int | None = None
    start_date: date | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    name: str | None = None
    estimated_days: int | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskScheduleUpdate(BaseModel):
    start_date: date | None = None
    due_date: date | None = None
    estimated_days: int | None = None
    reason: str | None = None


class TaskRead(BaseModel):
    id: int
    task_group_id: int
    name: str
    status: TaskStatus
    estimated_days: int | None
    start_date: date | None
    due_date: date | None
    completed_at: datetime | None
    created_at: datetime | None

    @field_serializer("completed_at", "created_at")
    def serialize_timestamps(self, value: datetime | None) -> str | None:
        return to_kst_iso(value) if value is not None else None


class TaskActivityLogRead(BaseModel):
    id: int
    event_type: str
    event_at: datetime
    old_value: str | None
    new_value: str | None
    reason: str | None

    @field_serializer("event_at")
    def serialize_event_at(self, value: datetime) -> str:
        return to_kst_iso(value)
