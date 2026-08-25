"""Task 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from domain.common.enums import TaskStatus
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

    @abstractmethod
    def count_by_status_bulk(
        self, task_group_ids: list[int]
    ) -> dict[int, dict[TaskStatus, int]]:
        """여러 TaskGroup의 상태별 Task 개수를 한 번에 집계한다.
        목록 화면 진행률용 — TaskGroup마다 따로 조회하면 N+1이 된다."""
        raise NotImplementedError
