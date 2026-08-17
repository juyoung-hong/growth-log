"""Meeting 참석자(다대다) 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MeetingAttendeeRepository(ABC):
    @abstractmethod
    def add(self, meeting_id: int, person_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, meeting_id: int, person_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, meeting_id: int, person_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_person_ids(self, meeting_id: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_meeting(self, meeting_id: int) -> None:
        """미팅 삭제 캐스케이드용."""
        raise NotImplementedError

    @abstractmethod
    def is_person_referenced(self, person_id: int) -> bool:
        """이 인물이 참석자로 하나라도 지정돼 있는지. Person 삭제 검증용."""
        raise NotImplementedError
