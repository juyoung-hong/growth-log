"""TaskGroup 저장소 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.common.enums import Scope, TaskStatus
from domain.task_group import TaskGroup


class TaskGroupRepository(ABC):
    """TaskGroup 저장소가 반드시 구현해야 하는 메서드 목록."""

    @abstractmethod
    def add(self, task_group: TaskGroup) -> TaskGroup:
        """새 TaskGroup을 저장하고, id가 채워진 도메인 객체를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def get(self, task_group_id: int) -> TaskGroup | None:
        """id로 TaskGroup을 조회한다. 없으면 None을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        category: Scope | None = None,
        status: TaskStatus | None = None,
        include_archived: bool = False,
    ) -> list[TaskGroup]:
        """조건에 맞는 TaskGroup 목록을 반환한다.

        include_archived가 False(기본값)면 is_archived=True인 TaskGroup은
        제외한다 — API 설계상 목록 조회의 기본 동작이다.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, task_group: TaskGroup) -> TaskGroup:
        """기존 TaskGroup 정보를 갱신하고, 갱신된 도메인 객체를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_group_id: int) -> None:
        """TaskGroup을 삭제한다."""
        raise NotImplementedError
