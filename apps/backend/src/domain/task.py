"""Task(작업, 기존 '레벨3') 도메인 모델.

TaskGroup에 속한 세부 작업. 프레임워크 의존성 없는 순수 파이썬이다.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from domain.common.enums import TaskStatus
from domain.common.exceptions import InvalidFieldError
from domain.common.validators import validate_not_empty

# 마감일을 찾으며 훑어볼 최대 일수. 연휴가 가장 길어도 열흘을 넘지 않으니
# 1년이면 정상 입력에서는 절대 닿지 않는다 — 무한 탐색을 막는 안전장치다.
_MAX_SCAN_DAYS = 365


def validate_schedule(start_date: date | None, due_date: date | None) -> None:
    """마감일이 시작일보다 빠르면 안 된다. Task 생성·일정 변경 양쪽에서 재사용한다."""
    if start_date and due_date and due_date < start_date:
        raise InvalidFieldError("due_date", "시작일보다 빠를 수 없습니다.")


def calculate_due_date(
    start_date: date,
    estimated_days: int,
    is_workday: Callable[[date], bool],
) -> date:
    """시작일부터 세어 estimated_days 번째 영업일을 반환한다.

    시작일을 1일째로 센다(스토리보드 SCENE 02: 08-18 + 2일 = 08-19).
    시작일 자체가 영업일이 아니면 다음 영업일부터 세기 시작한다.
    is_workday로 판별 책임을 밖으로 빼서 도메인이 공휴일 출처를
    모르게 한다.

    is_workday가 계속 False를 돌려주면(달력 구현이 잘못된 경우) 영업일을
    영영 못 채우므로, 한 해 치를 넘기면 멈추고 예외를 던진다 — 그냥 두면
    date.max까지 290만 번을 돌다가 OverflowError로 끝나서 원인을 알기
    어렵다.
    """
    if estimated_days < 1:
        raise InvalidFieldError("estimated_days", "0보다 커야 합니다.")

    day = start_date
    counted = 0
    for _ in range(_MAX_SCAN_DAYS):
        if is_workday(day):
            counted += 1
            if counted == estimated_days:
                return day
        day += timedelta(days=1)
    raise InvalidFieldError(
        "estimated_days", f"{_MAX_SCAN_DAYS}일 안에 채울 수 없는 값입니다."
    )


def is_weekend(day: date) -> bool:
    """토(5)·일(6)."""
    return day.weekday() >= 5


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
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.name, field="name")
        if self.estimated_days is not None and self.estimated_days <= 0:
            raise InvalidFieldError("estimated_days", "0보다 커야 합니다.")
        validate_schedule(self.start_date, self.due_date)
