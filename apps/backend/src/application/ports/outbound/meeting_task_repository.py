"""Meeting-Task 연결 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MeetingTaskRepository(ABC):
    @abstractmethod
    def add(self, meeting_id: int, task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, meeting_id: int, task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, meeting_id: int, task_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_task_ids(self, meeting_id: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def list_meeting_ids_by_task(self, task_id: int) -> list[int]:
        """Task 쪽 역조회(GET /tasks/{id}/meetings)용."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_meeting(self, meeting_id: int) -> None:
        """미팅 삭제 캐스케이드용."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_task(self, task_id: int) -> None:
        """Task 삭제 캐스케이드용."""
        raise NotImplementedError
