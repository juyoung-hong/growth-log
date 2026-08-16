"""Task 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

from datetime import date

import pytest

from domain.common.exceptions import EmptyFieldError, InvalidFieldError
from domain.task import Task


def test_이름이_비어있으면_예외() -> None:
    with pytest.raises(EmptyFieldError):
        Task(id=None, task_group_id=1, name="  ")


def test_예상소요일이_0이하이면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        Task(id=None, task_group_id=1, name="작업", estimated_days=0)


def test_마감일이_시작일보다_빠르면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        Task(
            id=None,
            task_group_id=1,
            name="작업",
            start_date=date(2026, 8, 20),
            due_date=date(2026, 8, 10),
        )
