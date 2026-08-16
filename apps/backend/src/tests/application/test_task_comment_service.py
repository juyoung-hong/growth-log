"""TaskCommentService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

import pytest

from application.services.task_comment_service import TaskCommentService
from application.services.task_service import TaskService
from domain.common.enums import Scope
from domain.common.exceptions import EmptyFieldError
from domain.exceptions import TaskCommentNotFoundError, TaskNotFoundError
from domain.task_group import TaskGroup


def test_댓글을_등록한다(
    task_comment_service: TaskCommentService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")

    comment = task_comment_service.create(task.id, "진행 상황 공유합니다")
    assert comment.id is not None


def test_없는_task에_댓글을_달면_예외(task_comment_service: TaskCommentService) -> None:
    with pytest.raises(TaskNotFoundError):
        task_comment_service.create(999, "내용")


def test_댓글을_수정하면_덮어써진다(
    task_comment_service: TaskCommentService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    comment = task_comment_service.create(task.id, "원래 내용")

    updated = task_comment_service.update(comment.id, "수정된 내용")
    assert updated.content == "수정된 내용"


def test_빈_내용으로_수정하면_예외(
    task_comment_service: TaskCommentService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    comment = task_comment_service.create(task.id, "원래 내용")

    with pytest.raises(EmptyFieldError):
        task_comment_service.update(comment.id, "   ")


def test_댓글을_삭제한다(
    task_comment_service: TaskCommentService,
    task_service: TaskService,
    task_group_repository,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    comment = task_comment_service.create(task.id, "지울 댓글")

    task_comment_service.delete(comment.id)

    with pytest.raises(TaskCommentNotFoundError):
        task_comment_service.update(comment.id, "다시 쓰기")
