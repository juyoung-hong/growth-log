"""공휴일 조회 유스케이스."""

from __future__ import annotations

from datetime import date

from application.ports.outbound.holiday_calendar_port import HolidayCalendarPort


class HolidayService:
    """프론트 달력 UI가 특정 연도의 공휴일을 표시하는 데 쓴다. Task 마감일
    자동 계산과 같은 HolidayCalendarPort를 그대로 재사용해, 달력에 빨갛게
    표시되는 날과 실제로 마감일 계산에서 제외되는 날이 갈리지 않게 한다."""

    def __init__(self, holiday_calendar: HolidayCalendarPort) -> None:
        self.holiday_calendar = holiday_calendar

    def list_holidays(self, year: int) -> list[date]:
        return self.holiday_calendar.list_holidays(year)
