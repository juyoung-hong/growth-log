"""공휴일 조회 라우터. 달력 UI가 토·일·공휴일을 색으로 구분하는 데 쓴다."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_holiday_service
from application.services.holiday_service import HolidayService

router = APIRouter(tags=["holidays"])

_MIN_YEAR = 1900
_MAX_YEAR = 2200


@router.get("/holidays", response_model=list[date])
def list_holidays(year: int, service: HolidayService = Depends(get_holiday_service)):
    if not (_MIN_YEAR <= year <= _MAX_YEAR):
        raise HTTPException(status_code=400, detail="year 값이 올바르지 않습니다.")
    return service.list_holidays(year)
