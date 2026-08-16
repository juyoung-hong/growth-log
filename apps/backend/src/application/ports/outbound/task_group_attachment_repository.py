"""TaskGroup 참고자료 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.task_group_attachment import TaskGroupAttachment


class TaskGroupAttachmentRepository(ABC):
    """참고자료 저장소가 반드시 구현해야 하는 메서드 목록."""

    @abstractmethod
    def add(self, attachment: TaskGroupAttachment) -> TaskGroupAttachment:
        """새 참고자료를 저장하고, id가 채워진 도메인 객체를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def get(self, attachment_id: int) -> TaskGroupAttachment | None:
        """id로 참고자료를 조회한다. 없으면 None을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def list(self, task_group_id: int) -> list[TaskGroupAttachment]:
        """특정 TaskGroup에 속한 참고자료 목록을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, attachment_id: int) -> None:
        """참고자료를 삭제한다(DB 행만 — Object Storage 원본 삭제는 서비스 책임)."""
        raise NotImplementedError
