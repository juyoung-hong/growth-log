"""TaskGroupService 유스케이스를 FakeTaskGroupRepository로 DB 없이 검증한다."""

from __future__ import annotations

import pytest

from application.services.task_group_service import TaskGroupService
from domain.common.enums import Scope, TaskStatus
from domain.exceptions import TaskGroupNotFoundError


def test_작업그룹을_생성한다(task_group_service: TaskGroupService) -> None:
    task_group = task_group_service.create(
        category=Scope.COMPANY, name="메일서버 이중화"
    )
    assert task_group.id is not None
    assert task_group.status == TaskStatus.IN_PROGRESS  # 기본값


def test_id로_조회한다(task_group_service: TaskGroupService) -> None:
    created = task_group_service.create(category=Scope.PERSONAL, name="이직 준비")
    found = task_group_service.get(created.id)
    assert found.name == "이직 준비"


def test_없는_id를_조회하면_예외(task_group_service: TaskGroupService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        task_group_service.get(999)


def test_부분_수정한다(task_group_service: TaskGroupService) -> None:
    created = task_group_service.create(category=Scope.COMPANY, name="A")
    updated = task_group_service.update(created.id, status=TaskStatus.DONE)
    assert updated.status == TaskStatus.DONE
    assert updated.name == "A"  # 안 건드린 필드는 그대로 유지


def test_기본_목록_조회는_보관된_항목을_제외한다(
    task_group_service: TaskGroupService,
) -> None:
    active = task_group_service.create(category=Scope.COMPANY, name="진행중인 것")
    archived = task_group_service.create(category=Scope.COMPANY, name="보관된 것")
    task_group_service.update(archived.id, is_archived=True)

    default_list = task_group_service.list()
    assert [tg.id for tg in default_list] == [active.id]

    full_list = task_group_service.list(include_archived=True)
    assert len(full_list) == 2


def test_구분과_상태로_필터링해서_조회한다(
    task_group_service: TaskGroupService,
) -> None:
    task_group_service.create(category=Scope.COMPANY, name="A", status=TaskStatus.DONE)
    task_group_service.create(category=Scope.PERSONAL, name="B")

    company_only = task_group_service.list(category=Scope.COMPANY)
    assert len(company_only) == 1

    done_only = task_group_service.list(status=TaskStatus.DONE)
    assert len(done_only) == 1
    assert done_only[0].name == "A"


def test_삭제한다(task_group_service: TaskGroupService) -> None:
    created = task_group_service.create(category=Scope.PERSONAL, name="지울 것")
    task_group_service.delete(created.id)
    with pytest.raises(TaskGroupNotFoundError):
        task_group_service.get(created.id)
