"""Person 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

import pytest

from domain.common.enums import Scope
from domain.common.exceptions import (
    EmptyFieldError,
    InvalidEmailError,
    InvalidPhoneError,
)
from domain.person import Person


def test_이름이_비어있으면_예외() -> None:
    with pytest.raises(EmptyFieldError):
        Person(id=None, category=Scope.PERSONAL, name="   ")


@pytest.mark.parametrize(
    "invalid_email",
    ["not-an-email", "no-at-sign.com", "@no-local-part.com", "no-domain@"],
)
def test_이메일_형식이_잘못되면_예외(invalid_email: str) -> None:
    with pytest.raises(InvalidEmailError):
        Person(
            id=None,
            category=Scope.PERSONAL,
            name="홍길동",
            email=invalid_email,
        )


def test_이메일_형식이_올바르면_통과() -> None:
    person = Person(
        id=None,
        category=Scope.PERSONAL,
        name="홍길동",
        email="test@example.com",
    )
    assert person.email == "test@example.com"


@pytest.mark.parametrize(
    "invalid_phone",
    ["01012345678", "010 1234 5678", "abc-1234-5678", "010-12-5678"],
)
def test_전화번호_형식이_잘못되면_예외(invalid_phone: str) -> None:
    with pytest.raises(InvalidPhoneError):
        Person(
            id=None,
            category=Scope.PERSONAL,
            name="홍길동",
            phone=invalid_phone,
        )


def test_전화번호_형식이_올바르면_통과() -> None:
    person = Person(
        id=None, category=Scope.PERSONAL, name="홍길동", phone="010-1234-5678"
    )
    assert person.phone == "010-1234-5678"
