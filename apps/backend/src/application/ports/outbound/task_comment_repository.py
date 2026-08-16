"""Task 댓글 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.task_comment import TaskComment


class TaskCommentRepository(ABC):
    @abstractmethod
    def add(self, comment: TaskComment) -> TaskComment:
        raise NotImplementedError

    @abstractmethod
    def get(self, comment_id: int) -> TaskComment | None:
        raise NotImplementedError

    @abstractmethod
    def list(self, task_id: int) -> list[TaskComment]:
        """작성일순으로 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def update(self, comment: TaskComment) -> TaskComment:
        raise NotImplementedError

    @abstractmethod
    def delete(self, comment_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_by_task(self, task_id: int) -> None:
        """Task 삭제 캐스케이드용 — 해당 Task의 댓글을 전부 지운다."""
        raise NotImplementedError
