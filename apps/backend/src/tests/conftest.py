"""공용 pytest fixture. tests/ 하위 모든 테스트에서 바로 쓸 수 있다."""

from __future__ import annotations

import pytest

from application.ports.outbound.person_repository import PersonRepository
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.services.person_service import PersonService
from application.services.task_group_service import TaskGroupService
from domain.common.enums import Scope, TaskStatus
from domain.person import Person
from domain.task_group import TaskGroup


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


class FakeTaskGroupRepository(TaskGroupRepository):
    """테스트용 인메모리 TaskGroupRepository."""

    def __init__(self) -> None:
        self._store: dict[int, TaskGroup] = {}
        self._next_id = 1

    def add(self, task_group: TaskGroup) -> TaskGroup:
        task_group.id = self._next_id
        self._store[task_group.id] = task_group
        self._next_id += 1
        return task_group

    def get(self, task_group_id: int) -> TaskGroup | None:
        return self._store.get(task_group_id)

    def list(
        self,
        category: Scope | None = None,
        status: TaskStatus | None = None,
        include_archived: bool = False,
    ) -> list[TaskGroup]:
        values = list(self._store.values())
        if not include_archived:
            values = [v for v in values if not v.is_archived]
        if category:
            values = [v for v in values if v.category == category]
        if status:
            values = [v for v in values if v.status == status]
        return values

    def update(self, task_group: TaskGroup) -> TaskGroup:
        self._store[task_group.id] = task_group
        return task_group

    def delete(self, task_group_id: int) -> None:
        self._store.pop(task_group_id, None)


@pytest.fixture
def task_group_service() -> TaskGroupService:
    """DB 없이 동작하는 TaskGroupService. 매 테스트마다 빈 저장소로 새로 시작한다."""
    return TaskGroupService(FakeTaskGroupRepository())
