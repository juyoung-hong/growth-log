"""MeetingTaskService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from application.services.meeting_service import MeetingService
from application.services.meeting_task_service import MeetingTaskService
from application.services.task_service import TaskService
from domain.common.enums import Scope
from domain.exceptions import MeetingNotFoundError, TaskNotFoundError
from domain.task_group import TaskGroup


def test_태스크를_연결한다(
    meeting_task_service: MeetingTaskService,
    meeting_service: MeetingService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    linked = meeting_task_service.add(meeting.id, task.id)

    assert linked.id == task.id
    assert [t.id for t in meeting_task_service.list(meeting.id)] == [task.id]


def test_태스크_쪽에서_미팅을_역조회한다(
    meeting_task_service: MeetingTaskService,
    meeting_service: MeetingService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    meeting_task_service.add(meeting.id, task.id)

    assert meeting_task_service.list_meetings_by_task(task.id) == [meeting.id]


def test_없는_Task를_연결하면_예외(
    meeting_task_service: MeetingTaskService,
    meeting_service: MeetingService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(TaskNotFoundError):
        meeting_task_service.add(meeting.id, 999)


def test_없는_미팅에_연결하면_예외(
    meeting_task_service: MeetingTaskService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    with pytest.raises(MeetingNotFoundError):
        meeting_task_service.add(999, task.id)


def test_연결을_제거한다(
    meeting_task_service: MeetingTaskService,
    meeting_service: MeetingService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    meeting = meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    meeting_task_service.add(meeting.id, task.id)

    meeting_task_service.remove(meeting.id, task.id)

    assert meeting_task_service.list(meeting.id) == []
