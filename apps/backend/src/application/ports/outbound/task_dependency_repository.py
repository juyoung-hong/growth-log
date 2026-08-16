"""Task 선행 관계 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TaskDependencyRepository(ABC):
    @abstractmethod
    def add(self, task_id: int, depends_on_task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, task_id: int, depends_on_task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, task_id: int, depends_on_task_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_depends_on_ids(self, task_id: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_task(self, task_id: int) -> None:
        """Task 삭제 캐스케이드용. task_id·depends_on_task_id 양쪽 컬럼
        모두에서 이 Task를 참조하는 행을 지운다(양방향) — 이 Task가
        선행 태스크인 다른 Task의 의존 관계도 같이 끊어야 하기 때문이다."""
        raise NotImplementedError
