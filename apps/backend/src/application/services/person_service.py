"""인물 유스케이스.

PersonRepository 포트에만 의존한다 — DB가 Oracle인지, 테스트용 가짜
저장소인지 이 파일은 알지 못하고 알 필요도 없다.
"""

from application.ports.outbound.person_repository import PersonRepository
from domain.common.enums import Scope
from domain.exceptions import (
    EmailAlreadyExistsError,
    PersonNotFoundError,
    PersonReferencedError,
)
from domain.person import Person


class PersonService:
    """인물 등록·조회·수정·삭제 유스케이스."""

    def __init__(self, repository: PersonRepository) -> None:
        self.repository = repository

    def create(
        self,
        category: Scope,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        affiliation: str | None = None,
    ) -> Person:
        """인물을 새로 등록한다.

        이메일이 주어졌는데 이미 등록된 이메일이면 EmailAlreadyExistsError.
        name/email/phone 형식이 잘못되면 (Person 생성 시점에)
        InvalidPersonDataError가 발생한다.
        """
        if email and self.repository.find_by_email(email):
            raise EmailAlreadyExistsError(email)
        person = Person(
            id=None,
            category=category,
            name=name,
            email=email,
            phone=phone,
            affiliation=affiliation,
        )
        return self.repository.add(person)

    def get(self, person_id: int) -> Person:
        """id로 인물을 조회한다. 없으면 PersonNotFoundError."""
        person = self.repository.get(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        return person

    def list(self, category: Scope | None = None) -> list[Person]:
        """인물 목록을 조회한다."""
        return self.repository.list(category)

    def update(self, person_id: int, **fields: object) -> Person:
        """인물 정보를 부분 수정한다. 이메일을 바꾸는 경우 중복도 다시 확인한다."""
        person = self.get(person_id)
        new_email = fields.get("email", person.email)
        if new_email and new_email != person.email:
            existing = self.repository.find_by_email(new_email)
            if existing and existing.id != person_id:
                raise EmailAlreadyExistsError(new_email)
        for key, value in fields.items():
            setattr(person, key, value)
        return self.repository.update(person)

    def delete(self, person_id: int) -> None:
        """인물을 삭제한다. 다른 데이터에서 참조 중이면 PersonReferencedError."""
        self.get(person_id)
        if self.repository.is_referenced(person_id):
            raise PersonReferencedError(person_id)
        self.repository.delete(person_id)
