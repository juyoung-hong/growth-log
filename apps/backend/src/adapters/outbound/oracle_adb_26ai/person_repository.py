from datetime import datetime, timezone

from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import PersonTable
from application.ports.outbound.person_repository import PersonRepository
from domain.common.enums import Scope
from domain.person import Person


class SqlPersonRepository(PersonRepository):
    """PersonRepository의 Oracle/SQLModel 구현체.

    PersonTable(SQLModel 행) ↔ Person(도메인 객체) 변환이 이 클래스의 역할이다.
    """

    def __init__(self, session: Session):
        self.session = session

    def add(self, person: Person) -> Person:
        row = PersonTable(
            category=person.category.value,
            name=person.name,
            email=person.email,
            phone=person.phone,
            affiliation=person.affiliation,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, person_id: int) -> Person | None:
        row = self.session.get(PersonTable, person_id)
        return self._to_domain(row) if row else None

    def list(self, category: Scope | None = None) -> list[Person]:
        stmt = select(PersonTable)
        if category:
            stmt = stmt.where(PersonTable.category == category.value)
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def update(self, person: Person) -> Person:
        row = self.session.get(PersonTable, person.id)
        row.category = person.category.value
        row.name = person.name
        row.email = person.email
        row.phone = person.phone
        row.affiliation = person.affiliation
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def delete(self, person_id: int) -> None:
        row = self.session.get(PersonTable, person_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    def find_by_email(self, email: str) -> Person | None:
        row = self.session.exec(
            select(PersonTable).where(PersonTable.email == email)
        ).first()
        return self._to_domain(row) if row else None

    def is_referenced(self, person_id: int) -> bool:
        # level3_assignee / meeting_attendee 테이블이 아직 없습니다(로드맵 5~6단계에서 생김).
        # 그 단계에서 실제 참조 확인 쿼리로 채우면 됩니다.
        return False

    @staticmethod
    def _to_domain(row: PersonTable) -> Person:
        return Person(
            id=row.id,
            category=Scope(row.category),
            name=row.name,
            email=row.email,
            phone=row.phone,
            affiliation=row.affiliation,
        )
