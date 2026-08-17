"""Meeting-Task 연결 유스케이스."""

from __future__ import annotations

from application.ports.outbound.meeting_repository import MeetingRepository
from application.ports.outbound.meeting_task_repository import MeetingTaskRepository
from application.ports.outbound.task_repository import TaskRepository
from domain.exceptions import MeetingNotFoundError, TaskNotFoundError
from domain.task import Task


class MeetingTaskService:
    """미팅 ↔ Task 연결 추가·제거·조회 유스케이스."""

    def __init__(
        self,
        task_link_repository: MeetingTaskRepository,
        meeting_repository: MeetingRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.task_link_repository = task_link_repository
        self.meeting_repository = meeting_repository
        self.task_repository = task_repository

    def list(self, meeting_id: int) -> list[Task]:
        self._ensure_meeting_exists(meeting_id)
        task_ids = self.task_link_repository.list_task_ids(meeting_id)
        return [self.task_repository.get(tid) for tid in task_ids]

    def list_meetings_by_task(self, task_id: int) -> list[int]:
        """Task 쪽 역조회용 — meeting_id 목록만 돌려준다. 실제 Meeting
        객체 조립(참석자·연결 태스크까지 채운 응답)은 라우터가 한다."""
        self._ensure_task_exists(task_id)
        return self.task_link_repository.list_meeting_ids_by_task(task_id)

    def add(self, meeting_id: int, task_id: int) -> Task:
        """연결하고, 연결된 Task를 반환한다. 이미 연결돼 있으면 멱등 무시.
        레벨2(TaskGroup) 경계를 넘어도 되므로 소속 검증은 하지 않는다
        (API 설계 6절 — 회의 하나에서 여러 프로젝트 얘기가 나올 수 있어서)."""
        self._ensure_meeting_exists(meeting_id)
        task = self._get_task(task_id)
        if not self.task_link_repository.exists(meeting_id, task_id):
            self.task_link_repository.add(meeting_id, task_id)
        return task

    def remove(self, meeting_id: int, task_id: int) -> None:
        self._ensure_meeting_exists(meeting_id)
        self.task_link_repository.remove(meeting_id, task_id)

    def _ensure_meeting_exists(self, meeting_id: int) -> None:
        if not self.meeting_repository.get(meeting_id):
            raise MeetingNotFoundError(meeting_id)

    def _ensure_task_exists(self, task_id: int) -> None:
        if not self.task_repository.get(task_id):
            raise TaskNotFoundError(task_id)

    def _get_task(self, task_id: int) -> Task:
        task = self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task
