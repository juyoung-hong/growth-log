"""공용 pytest fixture. tests/ 하위 모든 테스트에서 바로 쓸 수 있다."""

from __future__ import annotations

import pytest

from application.ports.outbound.person_repository import PersonRepository
from application.services.person_service import PersonService
from domain.common.enums import Scope
from domain.person import Person


class FakePersonRepository(PersonRepository):
    """테스트용 인메모리 PersonRepository. 실제 DB 없이 서비스 로직만 검증한다."""

    def __init__(self) -> None:
        self._store: dict[int, Person] = {}
        self._next_id = 1

    def add(self, person: Person) -> Person:
        person.id = self._next_id
        self._store[person.id] = person
        self._next_id += 1
        return person

    def get(self, person_id: int) -> Person | None:
        return self._store.get(person_id)

    def list(self, category: Scope | None = None) -> list[Person]:
        values = list(self._store.values())
        if category:
            values = [p for p in values if p.category == category]
        return values

    def update(self, person: Person) -> Person:
        self._store[person.id] = person
        return person

    def delete(self, person_id: int) -> None:
        self._store.pop(person_id, None)

    def find_by_email(self, email: str) -> Person | None:
        return next((p for p in self._store.values() if p.email == email), None)

    def is_referenced(self, person_id: int) -> bool:
        return False


@pytest.fixture
def person_service() -> PersonService:
    """DB 없이 동작하는 PersonService. 매 테스트마다 빈 저장소로 새로 시작한다."""
    return PersonService(FakePersonRepository())
