"""TaskDependencyService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

import pytest

from application.services.task_dependency_service import TaskDependencyService
from application.services.task_service import TaskService
from domain.common.enums import Scope
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import DependencyTaskGroupMismatchError, TaskNotFoundError
from domain.task_group import TaskGroup


def test_선행_관계를_추가한다(
    task_dependency_service: TaskDependencyService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    a = task_service.create(task_group_id=task_group.id, name="A")
    b = task_service.create(task_group_id=task_group.id, name="B")

    added = task_dependency_service.add(a.id, b.id)

    assert added.id == b.id
    assert [t.id for t in task_dependency_service.list(a.id)] == [b.id]


def test_자기_자신을_선행으로_지정하면_예외(
    task_dependency_service: TaskDependencyService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    a = task_service.create(task_group_id=task_group.id, name="A")

    with pytest.raises(InvalidFieldError):
        task_dependency_service.add(a.id, a.id)


def test_다른_TaskGroup의_Task를_선행으로_지정하면_예외(
    task_dependency_service: TaskDependencyService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    group1 = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹1")
    )
    group2 = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹2")
    )
    a = task_service.create(task_group_id=group1.id, name="A")
    b = task_service.create(task_group_id=group2.id, name="B")

    with pytest.raises(DependencyTaskGroupMismatchError):
        task_dependency_service.add(a.id, b.id)


def test_없는_Task를_선행으로_지정하면_예외(
    task_dependency_service: TaskDependencyService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    a = task_service.create(task_group_id=task_group.id, name="A")

    with pytest.raises(TaskNotFoundError):
        task_dependency_service.add(a.id, 999)


def test_선행_관계를_제거한다(
    task_dependency_service: TaskDependencyService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    a = task_service.create(task_group_id=task_group.id, name="A")
    b = task_service.create(task_group_id=task_group.id, name="B")
    task_dependency_service.add(a.id, b.id)

    task_dependency_service.remove(a.id, b.id)

    assert task_dependency_service.list(a.id) == []
