"""Meeting 요청/응답 DTO. scheduled_at 응답은 KST로 변환한다(API 설계 2절)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, field_serializer

from adapters.inbound.api.schemas.person import PersonRead
from adapters.inbound.api.schemas.task import TaskRead
from domain.meeting import MeetingStatus

KST = timezone(timedelta(hours=9))


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
        """Oracle TIMESTAMP는 시간대 정보 없이 저장되므로, 여기서 읽어온
        값은 항상 naive datetime이다. 그 값이 UTC라는 걸 우리가 알고
        있으니(쓸 때 항상 UTC로 저장했으므로) 명시적으로 라벨을 붙인 뒤
        KST로 변환한다 — 이 replace가 없으면 파이썬이 naive datetime을
        시스템 로컬 시간대로 잘못 해석해서 변환이 틀어진다."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(KST).isoformat()
