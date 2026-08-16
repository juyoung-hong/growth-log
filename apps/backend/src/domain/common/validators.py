"""여러 도메인 엔티티가 재사용하는 값 형식 검증 함수 모음.

프레임워크에 의존하지 않는 순수 함수들이다. 형식이 잘못되면
InvalidFieldError를 던지고, 올바르면 아무것도 반환하지 않는다.
새 도메인(레벨2, 레벨3 등)에서 이름·이메일·전화번호 검증이 필요하면
여기 함수를 그대로 가져다 쓰면 된다.
"""

from __future__ import annotations

import re

from domain.common.exceptions import (
    EmptyFieldError,
    InvalidEmailError,
    InvalidPhoneError,
)

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# 하이픈을 반드시 포함해야 한다: 010-1234-5678, 02-1234-5678 등.
# 지역번호/이동통신 앞자리(0으로 시작, 1~2자리) - 3~4자리 - 4자리.
_PHONE_PATTERN = re.compile(r"^0\d{1,2}-\d{3,4}-\d{4}$")


def validate_not_empty(value: str, *, field: str) -> None:
    if not value.strip():
        raise EmptyFieldError(field)


def validate_email(value: str, *, field: str = "email") -> None:
    if not _EMAIL_PATTERN.match(value):
        raise InvalidEmailError(value, field)


def validate_phone(value: str, *, field: str = "phone") -> None:
    if not _PHONE_PATTERN.match(value):
        raise InvalidPhoneError(value, field)
