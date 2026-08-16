"""인물(Person) 도메인 모델.

이 모듈은 어떤 프레임워크에도 의존하지 않는 순수 파이썬이다.
FastAPI, SQLModel, pydantic 등은 여기서 import하지 않는다 — 그래야
"인물이란 무엇이고 어떤 값이 유효한가"라는 규칙이 API를 FastAPI에서
다른 것으로 바꾸거나, DB를 Oracle에서 다른 것으로 바꿔도 그대로 살아남는다.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.common.enums import Scope
from domain.common.validators import validate_email, validate_not_empty, validate_phone


@dataclass
class Person:
    """인물 기준정보."""

    id: int | None
    category: Scope
    name: str
    email: str | None = None
    phone: str | None = None
    affiliation: str | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.name, field="name")
        if self.email is not None:
            validate_email(self.email)
        if self.phone is not None:
            validate_phone(self.phone)
