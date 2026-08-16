"""TaskAssigneeService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

import pytest

from application.services.task_assignee_service import TaskAssigneeService
from application.services.task_service import TaskService
from domain.common.enums import Scope
from domain.exceptions import PersonNotFoundError, TaskNotFoundError
from domain.person import Person
from domain.task_activity_log import ActivityEventType
from domain.task_group import TaskGroup


def test_담당자를_추가하면_활동이력이_남는다(
    task_assignee_service: TaskAssigneeService,
    task_service: TaskService,
    task_group_repository,
    person_repository,
    activity_log_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )

    added = task_assignee_service.add(task.id, person.id)

    assert added.id == person.id
    logs = activity_log_repository.list(task.id)
    assert logs[-1].event_type == ActivityEventType.ASSIGNEE


def test_같은_담당자를_두번_추가해도_멱등하다(
    task_assignee_service: TaskAssigneeService,
    task_service: TaskService,
    task_group_repository,
    person_repository,
    activity_log_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )

    task_assignee_service.add(task.id, person.id)
    task_assignee_service.add(task.id, person.id)

    assignee_logs = [
        log
        for log in activity_log_repository.list(task.id)
        if log.event_type == ActivityEventType.ASSIGNEE
    ]
    assert len(assignee_logs) == 1


def test_없는_Task에_담당자를_추가하면_예외(
    task_assignee_service: TaskAssigneeService, person_repository
) -> None:
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    with pytest.raises(TaskNotFoundError):
        task_assignee_service.add(999, person.id)


def test_없는_인물을_담당자로_추가하면_예외(
    task_assignee_service: TaskAssigneeService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    with pytest.raises(PersonNotFoundError):
        task_assignee_service.add(task.id, 999)


def test_담당자_목록을_조회한다(
    task_assignee_service: TaskAssigneeService,
    task_service: TaskService,
    task_group_repository,
    person_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    task_assignee_service.add(task.id, person.id)

    assignees = task_assignee_service.list(task.id)
    assert [p.name for p in assignees] == ["홍주영"]


def test_담당자를_제거하면_활동이력이_남는다(
    task_assignee_service: TaskAssigneeService,
    task_service: TaskService,
    task_group_repository,
    person_repository,
    activity_log_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    person = person_repository.add(
        Person(id=None, category=Scope.COMPANY, name="홍주영")
    )
    task_assignee_service.add(task.id, person.id)

    task_assignee_service.remove(task.id, person.id)

    assert task_assignee_service.list(task.id) == []
    logs = activity_log_repository.list(task.id)
    assert logs[-1].event_type == ActivityEventType.ASSIGNEE
