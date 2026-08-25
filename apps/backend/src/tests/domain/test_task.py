"""Task 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

from datetime import date

import pytest

from domain.common.exceptions import EmptyFieldError, InvalidFieldError
from domain.task import Task, calculate_due_date, is_weekend


def _weekdays_only(day: date) -> bool:
    """주말만 쉬는 달력. 공휴일 없는 기본 케이스에 쓴다."""
    return not is_weekend(day)


def _weekdays_except(*holidays: date):
    """주말 + 지정한 날짜를 쉬는 달력을 만든다."""
    holiday_set = set(holidays)
    return lambda day: not is_weekend(day) and day not in holiday_set


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


def test_토요일과_일요일만_주말이다() -> None:
    # 2026-08-17(월) ~ 08-23(일)
    weekend_flags = [is_weekend(date(2026, 8, d)) for d in range(17, 24)]
    assert weekend_flags == [False, False, False, False, False, True, True]


def test_예상소요일_1일이면_시작일_당일이_마감일() -> None:
    assert calculate_due_date(date(2026, 8, 18), 1, _weekdays_only) == date(2026, 8, 18)


def test_스토리보드_예시대로_시작일을_1일째로_센다() -> None:
    """SCENE 02: 시작 08-18(화) + 예상 2일 -> 마감 08-19(수)."""
    assert calculate_due_date(date(2026, 8, 18), 2, _weekdays_only) == date(2026, 8, 19)


def test_주말은_영업일로_세지_않는다() -> None:
    # 08-21(금)이 1일째, 22~23은 주말이라 건너뛰고 24(월)이 2일째, 25(화)가 3일째
    assert calculate_due_date(date(2026, 8, 21), 3, _weekdays_only) == date(2026, 8, 25)


def test_시작일이_주말이면_다음_영업일부터_센다() -> None:
    # 08-22(토)에 시작해도 첫 영업일은 08-24(월)
    assert calculate_due_date(date(2026, 8, 22), 1, _weekdays_only) == date(2026, 8, 24)


def test_중간에_공휴일이_있으면_그만큼_밀린다() -> None:
    # 08-17(월)이 공휴일이라 18(화)이 1일째, 19(수)가 2일째
    calendar = _weekdays_except(date(2026, 8, 17))
    assert calculate_due_date(date(2026, 8, 17), 2, calendar) == date(2026, 8, 19)


def test_연휴_전체를_건너뛴다() -> None:
    """2026 설 연휴(02-16~18) 케이스. 02-13(금)이 1일째,
    주말과 연휴를 건너뛰고 02-19(목)이 2일째, 02-20(금)이 3일째."""
    calendar = _weekdays_except(date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18))
    assert calculate_due_date(date(2026, 2, 13), 3, calendar) == date(2026, 2, 20)


def test_예상소요일이_0이하이면_마감일을_계산하지_않는다() -> None:
    with pytest.raises(InvalidFieldError):
        calculate_due_date(date(2026, 8, 18), 0, _weekdays_only)


def test_영업일을_영영_못_채우면_무한히_돌지_않고_예외() -> None:
    """달력 구현이 잘못돼 모든 날이 휴일이어도 1년 안에 멈춰야 한다."""
    with pytest.raises(InvalidFieldError):
        calculate_due_date(date(2026, 8, 18), 1, lambda day: False)
