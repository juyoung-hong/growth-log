"""Task(작업, 기존 '레벨3') 도메인 모델.

TaskGroup에 속한 세부 작업. 프레임워크 의존성 없는 순수 파이썬이다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from domain.common.enums import TaskStatus
from domain.common.exceptions import InvalidFieldError
from domain.common.validators import validate_not_empty


def validate_schedule(start_date: date | None, due_date: date | None) -> None:
    """마감일이 시작일보다 빠르면 안 된다. Task 생성·일정 변경 양쪽에서 재사용한다."""
    if start_date and due_date and due_date < start_date:
        raise InvalidFieldError("due_date", "시작일보다 빠를 수 없습니다.")


@dataclass
class Task:
    """TaskGroup에 속한 세부 작업."""

    id: int | None
    task_group_id: int
    name: str
    status: TaskStatus = TaskStatus.PENDING
    estimated_days: int | None = None
    start_date: date | None = None
    due_date: date | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.name, field="name")
        if self.estimated_days is not None and self.estimated_days <= 0:
            raise InvalidFieldError("estimated_days", "0보다 커야 합니다.")
        validate_schedule(self.start_date, self.due_date)
