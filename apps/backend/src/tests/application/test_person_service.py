"""PersonService 유스케이스를 FakePersonRepository로 DB 없이 검증한다."""

from __future__ import annotations

import pytest

from application.services.person_service import PersonService
from domain.common.enums import Scope
from domain.exceptions import EmailAlreadyExistsError, PersonNotFoundError


def test_인물을_생성한다(person_service: PersonService) -> None:
    person = person_service.create(
        category=Scope.COMPANY, name="홍주영", email="hjy@company.com"
    )
    assert person.id is not None
    assert person.name == "홍주영"


def test_이메일이_중복이면_생성이_거부된다(person_service: PersonService) -> None:
    person_service.create(
        category=Scope.COMPANY, name="홍주영", email="dup@company.com"
    )
    with pytest.raises(EmailAlreadyExistsError):
        person_service.create(
            category=Scope.COMPANY, name="김도현", email="dup@company.com"
        )


def test_id로_조회한다(person_service: PersonService) -> None:
    created = person_service.create(category=Scope.PERSONAL, name="이수현")
    found = person_service.get(created.id)
    assert found.name == "이수현"


def test_없는_id를_조회하면_예외(person_service: PersonService) -> None:
    with pytest.raises(PersonNotFoundError):
        person_service.get(999)


def test_부분_수정한다(person_service: PersonService) -> None:
    created = person_service.create(
        category=Scope.PERSONAL, name="이수현", phone="010-1111-2222"
    )
    updated = person_service.update(created.id, phone="010-9999-8888")
    assert updated.phone == "010-9999-8888"
    assert updated.name == "이수현"  # 안 건드린 필드는 그대로 유지


def test_전체_목록을_조회한다(person_service: PersonService) -> None:
    person_service.create(category=Scope.COMPANY, name="A")
    person_service.create(category=Scope.PERSONAL, name="B")
    assert len(person_service.list()) == 2


def test_구분으로_필터링해서_조회한다(person_service: PersonService) -> None:
    person_service.create(category=Scope.COMPANY, name="A")
    person_service.create(category=Scope.PERSONAL, name="B")
    company_only = person_service.list(Scope.COMPANY)
    assert len(company_only) == 1
    assert company_only[0].name == "A"


def test_삭제한다(person_service: PersonService) -> None:
    created = person_service.create(category=Scope.PERSONAL, name="지울사람")
    person_service.delete(created.id)
    with pytest.raises(PersonNotFoundError):
        person_service.get(created.id)
