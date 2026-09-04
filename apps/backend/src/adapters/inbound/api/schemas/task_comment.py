from datetime import datetime

from pydantic import BaseModel, field_serializer

from adapters.inbound.api.schemas._datetime import to_kst_iso


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

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return to_kst_iso(value)
