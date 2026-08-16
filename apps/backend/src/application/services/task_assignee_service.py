"""Task 담당자 유스케이스."""

from __future__ import annotations

from application.ports.outbound.person_repository import PersonRepository
from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_assignee_repository import TaskAssigneeRepository
from application.ports.outbound.task_repository import TaskRepository
from domain.exceptions import PersonNotFoundError, TaskNotFoundError
from domain.person import Person
from domain.task_activity_log import ActivityEventType, TaskActivityLog


class TaskAssigneeService:
    """Task 담당자 추가·제거·조회 유스케이스."""

    def __init__(
        self,
        assignee_repository: TaskAssigneeRepository,
        task_repository: TaskRepository,
        person_repository: PersonRepository,
        activity_log_repository: TaskActivityLogRepository,
    ) -> None:
        self.assignee_repository = assignee_repository
        self.task_repository = task_repository
        self.person_repository = person_repository
        self.activity_log_repository = activity_log_repository

    def list(self, task_id: int) -> list[Person]:
        self._ensure_task_exists(task_id)
        person_ids = self.assignee_repository.list_person_ids(task_id)
        return [self.person_repository.get(pid) for pid in person_ids]

    def add(self, task_id: int, person_id: int) -> Person:
        """담당자를 추가하고, 추가된 인물을 반환한다(라우터가 201 응답에
        그대로 씀). 이미 담당자면 조용히 무시한다(멱등) — 같은 사람을
        두 번 추가하는 건 오류라기보다 결과가 같은 요청이다."""
        self._ensure_task_exists(task_id)
        person = self._get_person(person_id)
        if not self.assignee_repository.exists(task_id, person_id):
            self.assignee_repository.add(task_id, person_id)
            self.activity_log_repository.add(
                TaskActivityLog(
                    id=None,
                    task_id=task_id,
                    event_type=ActivityEventType.ASSIGNEE,
                    new_value=f"{person.name} 추가",
                )
            )
        return person

    def remove(self, task_id: int, person_id: int) -> None:
        self._ensure_task_exists(task_id)
        person = self._get_person(person_id)
        self.assignee_repository.remove(task_id, person_id)
        self.activity_log_repository.add(
            TaskActivityLog(
                id=None,
                task_id=task_id,
                event_type=ActivityEventType.ASSIGNEE,
                new_value=f"{person.name} 제거",
            )
        )

    def _ensure_task_exists(self, task_id: int) -> None:
        if not self.task_repository.get(task_id):
            raise TaskNotFoundError(task_id)

    def _get_person(self, person_id: int) -> Person:
        person = self.person_repository.get(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        return person
