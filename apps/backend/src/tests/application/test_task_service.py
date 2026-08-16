"""TaskService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import date

import pytest

from application.services.task_service import TaskService
from domain.common.enums import Scope, TaskStatus
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import TaskGroupNotFoundError, TaskNotFoundError
from domain.task_activity_log import ActivityEventType
from domain.task_group import TaskGroup


def test_등록하면_활동이력에_등록_이벤트가_남는다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="설계 문서 작성")

    logs = task_service.list_activity_log(task.id)
    assert len(logs) == 1
    assert logs[0].event_type == ActivityEventType.REGISTERED


def test_없는_TaskGroup에_등록하면_예외(task_service: TaskService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        task_service.create(task_group_id=999, name="작업")


def test_완료로_바꾸면_completed_at이_채워진다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    updated = task_service.change_status(task.id, TaskStatus.DONE)

    assert updated.completed_at is not None
    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.COMPLETED


def test_완료에서_다른_상태로_바꾸면_completed_at이_비워진다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    task_service.change_status(task.id, TaskStatus.DONE)

    updated = task_service.change_status(task.id, TaskStatus.IN_PROGRESS)

    assert updated.completed_at is None
    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.STATUS


def test_마감일이_시작일보다_빠르면_일정_변경이_거부된다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    with pytest.raises(InvalidFieldError):
        task_service.change_schedule(
            task.id, start_date=date(2026, 8, 20), due_date=date(2026, 8, 10)
        )


def test_일정을_변경하면_활동이력에_사유가_남는다(
    task_service: TaskService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    task_service.change_schedule(
        task.id,
        start_date=date(2026, 8, 18),
        due_date=date(2026, 8, 21),
        reason="담당자 휴가로 순연",
    )

    logs = task_service.list_activity_log(task.id)
    assert logs[-1].event_type == ActivityEventType.SCHEDULE
    assert logs[-1].reason == "담당자 휴가로 순연"


def test_삭제하면_활동이력과_댓글도_함께_지워진다(
    task_service: TaskService,
    task_group_repository,
    activity_log_repository,
    task_comment_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    from domain.task_comment import TaskComment

    task_comment_repository.add(TaskComment(id=None, task_id=task.id, content="댓글"))

    task_service.delete(task.id)

    with pytest.raises(TaskNotFoundError):
        task_service.get(task.id)
    assert activity_log_repository.list(task.id) == []
    assert task_comment_repository.list(task.id) == []


def test_상태별_개수를_센다(task_service: TaskService, task_group_repository) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    t1 = task_service.create(task_group_id=task_group.id, name="A")
    task_service.create(task_group_id=task_group.id, name="B")
    task_service.change_status(t1.id, TaskStatus.DONE)

    counts = task_service.count_by_status(task_group.id)

    assert counts[TaskStatus.DONE] == 1
    assert counts[TaskStatus.PENDING] == 1
