"""Task 선행 관계 유스케이스."""

from __future__ import annotations

from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_dependency_repository import (
    TaskDependencyRepository,
)
from application.ports.outbound.task_repository import TaskRepository
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import DependencyTaskGroupMismatchError, TaskNotFoundError
from domain.task import Task
from domain.task_activity_log import ActivityEventType, TaskActivityLog


class TaskDependencyService:
    """Task 선행 관계 추가·제거·조회 유스케이스."""

    def __init__(
        self,
        dependency_repository: TaskDependencyRepository,
        task_repository: TaskRepository,
        activity_log_repository: TaskActivityLogRepository,
    ) -> None:
        self.dependency_repository = dependency_repository
        self.task_repository = task_repository
        self.activity_log_repository = activity_log_repository

    def list(self, task_id: int) -> list[Task]:
        self._get_task(task_id)
        depends_on_ids = self.dependency_repository.list_depends_on_ids(task_id)
        return [self.task_repository.get(tid) for tid in depends_on_ids]

    def add(self, task_id: int, depends_on_task_id: int) -> Task:
        """선행 관계를 추가하고, 선행 태스크를 반환한다(라우터가 201
        응답에 그대로 씀).

        자기 자신을 선행으로 지정하면 InvalidFieldError(→400).
        선행 태스크가 다른 TaskGroup 소속이면
        DependencyTaskGroupMismatchError(→422). 이미 있는 관계면
        조용히 무시한다(멱등).
        """
        if task_id == depends_on_task_id:
            raise InvalidFieldError(
                "depends_on_task_id", "자기 자신을 선행 태스크로 지정할 수 없습니다."
            )
        task = self._get_task(task_id)
        depends_on_task = self._get_task(depends_on_task_id)
        if task.task_group_id != depends_on_task.task_group_id:
            raise DependencyTaskGroupMismatchError(task_id, depends_on_task_id)

        if not self.dependency_repository.exists(task_id, depends_on_task_id):
            self.dependency_repository.add(task_id, depends_on_task_id)
            self.activity_log_repository.add(
                TaskActivityLog(
                    id=None,
                    task_id=task_id,
                    event_type=ActivityEventType.DEPENDENCY,
                    new_value=f"{depends_on_task.name} 추가",
                )
            )
        return depends_on_task

    def remove(self, task_id: int, depends_on_task_id: int) -> None:
        self._get_task(task_id)
        depends_on_task = self._get_task(depends_on_task_id)
        self.dependency_repository.remove(task_id, depends_on_task_id)
        self.activity_log_repository.add(
            TaskActivityLog(
                id=None,
                task_id=task_id,
                event_type=ActivityEventType.DEPENDENCY,
                new_value=f"{depends_on_task.name} 제거",
            )
        )

    def _get_task(self, task_id: int) -> Task:
        task = self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task
