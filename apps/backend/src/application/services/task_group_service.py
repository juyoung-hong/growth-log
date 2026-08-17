"""TaskGroup 유스케이스."""

from datetime import date

from application.ports.outbound.task_group_repository import TaskGroupRepository
from domain.common.enums import Scope, TaskStatus
from domain.exceptions import TaskGroupNotFoundError
from domain.task_group import TaskGroup


class TaskGroupService:
    """TaskGroup 등록·조회·수정·삭제 유스케이스."""

    def __init__(self, repository: TaskGroupRepository) -> None:
        self.repository = repository

    def create(
        self,
        category: Scope,
        name: str,
        description: str | None = None,
        status: TaskStatus = TaskStatus.IN_PROGRESS,
    ) -> TaskGroup:
        """TaskGroup을 새로 등록한다.

        name이 비어있으면 (TaskGroup 생성 시점에) EmptyFieldError가 발생한다.
        """
        task_group = TaskGroup(
            id=None,
            category=category,
            name=name,
            description=description,
            status=status,
        )
        return self.repository.add(task_group)

    def get(self, task_group_id: int) -> TaskGroup:
        """id로 TaskGroup을 조회한다. 없으면 TaskGroupNotFoundError."""
        task_group = self.repository.get(task_group_id)
        if not task_group:
            raise TaskGroupNotFoundError(task_group_id)
        return task_group

    def list(
        self,
        category: Scope | None = None,
        status: TaskStatus | None = None,
        include_archived: bool = False,
        created_after: date | None = None,
        created_before: date | None = None,
    ) -> list[TaskGroup]:
        """TaskGroup 목록을 조회한다. 기본은 보관되지 않은 것만.
        created_after/created_before는 export 후보를 기간으로 좁힐 때 쓴다."""
        return self.repository.list(
            category, status, include_archived, created_after, created_before
        )

    def update(self, task_group_id: int, **fields: object) -> TaskGroup:
        """TaskGroup 정보를 부분 수정한다."""
        task_group = self.get(task_group_id)
        for key, value in fields.items():
            setattr(task_group, key, value)
        return self.repository.update(task_group)

    def delete(self, task_group_id: int) -> None:
        """TaskGroup을 삭제한다."""
        self.get(task_group_id)
        self.repository.delete(task_group_id)
