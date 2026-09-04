"""한국 공휴일 어댑터. HolidayCalendarPort의 실제 구현체.

holidays 패키지는 음력 명절(설날·추석)의 양력 환산, 대체공휴일,
선거일까지 반영한다. 2026년 개정으로 공휴일이 된 제헌절·노동절도
연도 조건으로 처리하고 있어 별도 보정이 필요 없다.
"""

from __future__ import annotations

from datetime import date

import holidays

from application.ports.outbound.holiday_calendar_port import HolidayCalendarPort


class KrHolidayAdapter(HolidayCalendarPort):
    def __init__(self) -> None:
        # years를 지정하지 않으면 조회되는 연도를 필요할 때 채운다.
        self._holidays = holidays.SouthKorea()

    def is_holiday(self, day: date) -> bool:
        return day in self._holidays

    def list_holidays(self, year: int) -> list[date]:
        return sorted(holidays.SouthKorea(years=year).keys())


holiday_calendar_adapter = KrHolidayAdapter()
