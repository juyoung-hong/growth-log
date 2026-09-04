"""HolidayService 유스케이스를 Fake로 DB 없이 검증한다."""

from __future__ import annotations

from datetime import date

from application.services.holiday_service import HolidayService


def test_연도의_공휴일_목록을_돌려준다(holiday_calendar_port) -> None:
    holiday_calendar_port.holidays.add(date(2026, 1, 1))
    holiday_calendar_port.holidays.add(date(2026, 8, 17))
    holiday_calendar_port.holidays.add(date(2027, 1, 1))
    service = HolidayService(holiday_calendar=holiday_calendar_port)

    result = service.list_holidays(2026)

    assert result == [date(2026, 1, 1), date(2026, 8, 17)]
