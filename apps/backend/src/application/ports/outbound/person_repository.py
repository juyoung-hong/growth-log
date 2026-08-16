"""인물 저장소 포트.

애플리케이션 서비스(PersonService)가 영속성 계층에 무엇을 요구하는지를
정의하는 추상 인터페이스다. 이 파일은 Oracle도 SQLModel도 모른다 —
실제 구현체는 adapters/outbound/oracle_adb_26ai/person_repository.py의
SqlPersonRepository다.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.common.enums import Scope
from domain.person import Person


class PersonRepository(ABC):
    """인물 저장소가 반드시 구현해야 하는 메서드 목록.

    ``ABC``를 쓴 이유: 구현 클래스가 메서드를 하나라도 빠뜨리면,
    실제로 그 메서드를 호출하는 순간이 아니라 그 클래스를
    인스턴스화하는 순간 바로 ``TypeError``로 알려주기 때문이다.
    """

    @abstractmethod
    def add(self, person: Person) -> Person:
        """새 인물을 저장하고, id가 채워진 도메인 객체를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def get(self, person_id: int) -> Person | None:
        """id로 인물을 조회한다. 없으면 None을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def list(self, category: Scope | None = None) -> list[Person]:
        """구분(category)으로 필터링한 인물 목록을 반환한다. None이면 전체."""
        raise NotImplementedError

    @abstractmethod
    def update(self, person: Person) -> Person:
        """기존 인물 정보를 갱신하고, 갱신된 도메인 객체를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, person_id: int) -> None:
        """인물을 삭제한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> Person | None:
        """이메일로 인물을 조회한다. 이메일 중복 확인에 쓰인다."""
        raise NotImplementedError

    @abstractmethod
    def is_referenced(self, person_id: int) -> bool:
        """이 인물이 담당자·회의 참석자 등으로 다른 데이터에서 참조 중인지 확인한다."""
        raise NotImplementedError
