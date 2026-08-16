"""Task 활동이력 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.task_activity_log import TaskActivityLog


class TaskActivityLogRepository(ABC):
    @abstractmethod
    def add(self, log: TaskActivityLog) -> TaskActivityLog:
        raise NotImplementedError

    @abstractmethod
    def list(self, task_id: int) -> list[TaskActivityLog]:
        """시간순(event_at 오름차순)으로 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_task(self, task_id: int) -> None:
        """Task 삭제 캐스케이드용 — 해당 Task의 활동이력을 전부 지운다."""
        raise NotImplementedError
