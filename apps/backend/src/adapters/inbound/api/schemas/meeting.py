"""Meeting 요청/응답 DTO. scheduled_at 응답은 KST로 변환한다(API 설계 2절)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_serializer

from adapters.inbound.api.schemas._datetime import to_kst_iso
from adapters.inbound.api.schemas.person import PersonRead
from adapters.inbound.api.schemas.task import TaskRead
from domain.meeting import MeetingStatus


class MeetingCreate(BaseModel):
    scheduled_at: datetime
    agenda: str | None = None
    attendee_person_ids: list[int] = []
    task_ids: list[int] = []


class MeetingUpdate(BaseModel):
    scheduled_at: datetime | None = None
    agenda: str | None = None
    content: str | None = None
    status: MeetingStatus | None = None


class MeetingRead(BaseModel):
    id: int
    task_group_id: int
    status: MeetingStatus
    scheduled_at: datetime
    agenda: str | None
    content: str | None
    attendees: list[PersonRead] = []
    tasks: list[TaskRead] = []

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(self, value: datetime) -> str:
        return to_kst_iso(value)
