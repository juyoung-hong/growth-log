"""MeetingService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from application.services.meeting_service import MeetingService
from domain.common.enums import Scope
from domain.exceptions import MeetingNotFoundError, TaskGroupNotFoundError
from domain.meeting import MeetingStatus
from domain.task_group import TaskGroup


def test_미팅을_등록한다(
    meeting_service: MeetingService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
        agenda="주간 진행 상황 공유",
    )
    assert meeting.status == MeetingStatus.SCHEDULED


def test_없는_TaskGroup에_미팅을_등록하면_예외(meeting_service: MeetingService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        meeting_service.create(
            task_group_id=999,
            scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
        )


def test_미팅을_완료로_변경한다(
    meeting_service: MeetingService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )

    updated = meeting_service.update(
        meeting.id, status=MeetingStatus.DONE, content="논의 결과 정리"
    )

    assert updated.status == MeetingStatus.DONE
    assert updated.content == "논의 결과 정리"


def test_삭제하면_참석자와_태스크_연결도_함께_지워진다(
    meeting_service: MeetingService,
    task_service,
    task_group_repository,
    meeting_attendee_repository,
    meeting_task_repository,
    person_repository,
) -> None:
    from domain.person import Person

    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    meeting_attendee_repository.add(meeting.id, person.id)
    meeting_task_repository.add(meeting.id, task.id)

    meeting_service.delete(meeting.id)

    assert not meeting_attendee_repository.exists(meeting.id, person.id)
    assert not meeting_task_repository.exists(meeting.id, task.id)
    with pytest.raises(MeetingNotFoundError):
        meeting_service.get(meeting.id)
