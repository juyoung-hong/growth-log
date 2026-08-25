"""KrHolidayAdapter가 실제 holidays 패키지로 한국 공휴일을 제대로
읽어오는지 확인한다.

다른 테스트는 전부 FakeHolidayCalendarPort로 달력을 고정해서 계산
로직만 검증한다. 여기서만 진짜 라이브러리를 태워서, 음력 명절과
대체공휴일이 기대대로 나오는지를 실측으로 붙잡아 둔다.
"""

from __future__ import annotations

from datetime import date

import pytest

from adapters.outbound.holiday.kr_holiday_adapter import KrHolidayAdapter


@pytest.fixture
def adapter() -> KrHolidayAdapter:
    return KrHolidayAdapter()


@pytest.mark.parametrize(
    ("day", "label"),
    [
        (date(2026, 2, 17), "설날 — 음력이라 매년 양력 날짜가 바뀐다"),
        (date(2026, 9, 25), "추석"),
        (date(2026, 3, 2), "삼일절(일요일) 대체 휴일"),
        (date(2026, 8, 17), "광복절(토요일) 대체 휴일"),
    ],
)
def test_공휴일을_인식한다(adapter: KrHolidayAdapter, day: date, label: str) -> None:
    assert adapter.is_holiday(day), label


def test_평범한_평일은_공휴일이_아니다(adapter: KrHolidayAdapter) -> None:
    assert not adapter.is_holiday(date(2026, 8, 20))


def test_주말은_공휴일로_치지_않는다(adapter: KrHolidayAdapter) -> None:
    """주말 여부는 도메인의 is_weekend가 따로 판단한다 —
    포트는 공휴일만 답한다."""
    assert not adapter.is_holiday(date(2026, 8, 22))
