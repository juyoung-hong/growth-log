"""공휴일 조회 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date


class HolidayCalendarPort(ABC):
    @abstractmethod
    def is_holiday(self, day: date) -> bool:
        """해당 날짜가 공휴일이면 True. 주말 여부는 판단하지 않는다."""
        raise NotImplementedError
