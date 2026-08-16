"""Task 담당자(다대다) 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TaskAssigneeRepository(ABC):
    @abstractmethod
    def add(self, task_id: int, person_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, task_id: int, person_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, task_id: int, person_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_person_ids(self, task_id: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_task(self, task_id: int) -> None:
        """Task 삭제 캐스케이드용."""
        raise NotImplementedError

    @abstractmethod
    def is_person_referenced(self, person_id: int) -> bool:
        """이 인물이 담당자로 하나라도 지정돼 있는지. Person 삭제 검증용."""
        raise NotImplementedError
