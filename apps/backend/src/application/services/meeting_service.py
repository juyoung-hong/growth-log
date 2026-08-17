"""Meeting 유스케이스."""

from __future__ import annotations

from datetime import datetime

from application.ports.outbound.meeting_attendee_repository import (
    MeetingAttendeeRepository,
)
from application.ports.outbound.meeting_repository import MeetingRepository
from application.ports.outbound.meeting_task_repository import MeetingTaskRepository
from application.ports.outbound.task_group_repository import TaskGroupRepository
from domain.exceptions import MeetingNotFoundError, TaskGroupNotFoundError
from domain.meeting import Meeting


class MeetingService:
    """미팅 등록·조회·수정·삭제 유스케이스."""

    def __init__(
        self,
        meeting_repository: MeetingRepository,
        attendee_repository: MeetingAttendeeRepository,
        task_link_repository: MeetingTaskRepository,
        task_group_repository: TaskGroupRepository,
    ) -> None:
        self.meeting_repository = meeting_repository
        self.attendee_repository = attendee_repository
        self.task_link_repository = task_link_repository
        self.task_group_repository = task_group_repository

    def create(
        self, task_group_id: int, scheduled_at: datetime, agenda: str | None = None
    ) -> Meeting:
        """미팅을 등록한다. 참석자·연결 태스크는 이 메서드가 안 다룬다 —
        각각 전용 서비스가 있고, 생성 요청에 같이 왔으면 라우터가
        생성 직후 그 서비스들을 호출해서 이어붙인다(12절)."""
        self._ensure_task_group_exists(task_group_id)
        meeting = Meeting(
            id=None,
            task_group_id=task_group_id,
            scheduled_at=scheduled_at,
            agenda=agenda,
        )
        return self.meeting_repository.add(meeting)

    def get(self, meeting_id: int) -> Meeting:
        meeting = self.meeting_repository.get(meeting_id)
        if not meeting:
            raise MeetingNotFoundError(meeting_id)
        return meeting

    def list(self, task_group_id: int) -> list[Meeting]:
        self._ensure_task_group_exists(task_group_id)
        return self.meeting_repository.list(task_group_id)

    def update(self, meeting_id: int, **fields: object) -> Meeting:
        """scheduled_at/agenda/content/status 중 필요한 것만 부분 수정한다."""
        meeting = self.get(meeting_id)
        for key, value in fields.items():
            setattr(meeting, key, value)
        return self.meeting_repository.update(meeting)

    def delete(self, meeting_id: int) -> None:
        """미팅을 삭제한다. 참석자·연결 태스크 관계부터 정리한다(API 설계 6절)."""
        self.get(meeting_id)
        self.attendee_repository.delete_by_meeting(meeting_id)
        self.task_link_repository.delete_by_meeting(meeting_id)
        self.meeting_repository.delete(meeting_id)

    def _ensure_task_group_exists(self, task_group_id: int) -> None:
        if not self.task_group_repository.get(task_group_id):
            raise TaskGroupNotFoundError(task_group_id)
