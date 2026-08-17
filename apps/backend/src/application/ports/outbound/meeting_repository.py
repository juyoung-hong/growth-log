"""Meeting 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.meeting import Meeting


class MeetingRepository(ABC):
    @abstractmethod
    def add(self, meeting: Meeting) -> Meeting:
        raise NotImplementedError

    @abstractmethod
    def get(self, meeting_id: int) -> Meeting | None:
        raise NotImplementedError

    @abstractmethod
    def list(self, task_group_id: int) -> list[Meeting]:
        raise NotImplementedError

    @abstractmethod
    def update(self, meeting: Meeting) -> Meeting:
        raise NotImplementedError

    @abstractmethod
    def delete(self, meeting_id: int) -> None:
        raise NotImplementedError
