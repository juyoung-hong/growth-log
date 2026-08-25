from datetime import date, datetime

from pydantic import BaseModel

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


class TaskActivityLogRead(BaseModel):
    id: int
    event_type: str
    event_at: datetime
    old_value: str | None
    new_value: str | None
    reason: str | None
