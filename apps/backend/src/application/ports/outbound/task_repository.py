"""Task 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from domain.task import Task


class TaskRepository(ABC):
    """Task 저장소가 반드시 구현해야 하는 메서드 목록."""

    @abstractmethod
    def add(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self, task_group_id: int, view: Literal["default", "all"] = "default"
    ) -> list[Task]:
        """view='default'는 진행중 전체 + 최근 30일 이내 등록된 보류만 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: int) -> None:
        raise NotImplementedError
