"""Task 유스케이스.

상태 변경·일정 변경은 둘 다 활동이력을 부수효과로 남긴다는 공통점이 있어서
전용 메서드(change_status/change_schedule)로 분리했다 — PATCH /tasks/{id}로
아무 필드나 바꾸는 범용 update()와 섞으면 "왜 이 필드를 바꿀 땐 활동이력이
남고 저 필드는 안 남지?"가 코드만 봐서는 알기 어려워진다.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_comment_repository import TaskCommentRepository
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.ports.outbound.task_repository import TaskRepository
from domain.common.enums import TaskStatus
from domain.exceptions import TaskGroupNotFoundError, TaskNotFoundError
from domain.task import Task, validate_schedule
from domain.task_activity_log import ActivityEventType, TaskActivityLog


class TaskService:
    """Task 등록·조회·수정·삭제 + 상태/일정 전이 유스케이스."""

    def __init__(
        self,
        task_repository: TaskRepository,
        activity_log_repository: TaskActivityLogRepository,
        comment_repository: TaskCommentRepository,
        task_group_repository: TaskGroupRepository,
    ) -> None:
        self.task_repository = task_repository
        self.activity_log_repository = activity_log_repository
        self.comment_repository = comment_repository
        self.task_group_repository = task_group_repository

    def create(
        self,
        task_group_id: int,
        name: str,
        estimated_days: int | None = None,
        start_date: date | None = None,
        due_date: date | None = None,
    ) -> Task:
        """Task를 새로 등록한다. 등록 즉시 활동이력에 '등록' 이벤트를 남긴다."""
        self._ensure_task_group_exists(task_group_id)
        task = Task(
            id=None,
            task_group_id=task_group_id,
            name=name,
            estimated_days=estimated_days,
            start_date=start_date,
            due_date=due_date,
        )
        task = self.task_repository.add(task)
        self.activity_log_repository.add(
            TaskActivityLog(
                id=None, task_id=task.id, event_type=ActivityEventType.REGISTERED
            )
        )
        return task

    def get(self, task_id: int) -> Task:
        task = self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def list(
        self, task_group_id: int, view: Literal["default", "all"] = "default"
    ) -> list[Task]:
        self._ensure_task_group_exists(task_group_id)
        return self.task_repository.list(task_group_id, view)

    def update(self, task_id: int, **fields: object) -> Task:
        """name·estimated_days 등 일반 필드를 수정한다(상태·일정은 전용 메서드로)."""
        task = self.get(task_id)
        for key, value in fields.items():
            setattr(task, key, value)
        return self.task_repository.update(task)

    def change_status(self, task_id: int, status: TaskStatus) -> Task:
        """상태를 바꾼다. '완료'로 바뀌면 completed_at을 채우고, 완료에서
        다른 상태로 바뀌면 다시 비운다. 항상 활동이력을 남긴다."""
        task = self.get(task_id)
        old_status = task.status
        if old_status == status:
            return task

        task.status = status
        if status == TaskStatus.DONE:
            task.completed_at = datetime.now(timezone.utc)
            event_type = ActivityEventType.COMPLETED
        else:
            task.completed_at = None
            event_type = ActivityEventType.STATUS

        task = self.task_repository.update(task)
        self.activity_log_repository.add(
            TaskActivityLog(
                id=None,
                task_id=task_id,
                event_type=event_type,
                old_value=old_status.value,
                new_value=status.value,
            )
        )
        return task

    def change_schedule(
        self,
        task_id: int,
        start_date: date | None,
        due_date: date | None,
        reason: str | None = None,
    ) -> Task:
        """일정을 바꾼다. mutate하기 전에 validate_schedule을 직접 호출한다 —
        __post_init__은 이미 만들어진 객체를 setattr로 고칠 땐 재실행되지
        않기 때문이다(0번 섹션 참고)."""
        validate_schedule(start_date, due_date)
        task = self.get(task_id)
        old_value = self._format_schedule(task.start_date, task.due_date)
        new_value = self._format_schedule(start_date, due_date)

        task.start_date = start_date
        task.due_date = due_date
        task = self.task_repository.update(task)

        self.activity_log_repository.add(
            TaskActivityLog(
                id=None,
                task_id=task_id,
                event_type=ActivityEventType.SCHEDULE,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
            )
        )
        return task

    def list_activity_log(self, task_id: int) -> list[TaskActivityLog]:
        self.get(task_id)
        return self.activity_log_repository.list(task_id)

    def count_by_status(self, task_group_id: int) -> dict[TaskStatus, int]:
        """TaskGroup 진행률 계산에 쓰인다. 부모 존재 확인은 안 한다 —
        호출하는 라우터가 이미 TaskGroupService.get()으로 확인했을 것이기
        때문에 같은 조회를 중복하지 않는다."""
        tasks = self.task_repository.list(task_group_id, view="all")
        counts: dict[TaskStatus, int] = {}
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        return counts

    def delete(self, task_id: int) -> None:
        """Task를 삭제한다. 댓글·활동이력을 먼저 지운 뒤 Task 행을 지운다.
        담당자·선행 관계·미팅 연결은 아직 테이블이 없어서 이 두 개만
        지우면 된다 — 5·6단계에서 해당 테이블이 생기면 여기에 순서를
        추가한다(API 설계 5.2절 삭제 캐스케이드)."""
        self.get(task_id)
        self.comment_repository.delete_by_task(task_id)
        self.activity_log_repository.delete_by_task(task_id)
        self.task_repository.delete(task_id)

    def _ensure_task_group_exists(self, task_group_id: int) -> None:
        if not self.task_group_repository.get(task_group_id):
            raise TaskGroupNotFoundError(task_group_id)

    @staticmethod
    def _format_schedule(start_date: date | None, due_date: date | None) -> str:
        return f"{start_date or '-'} ~ {due_date or '-'}"
