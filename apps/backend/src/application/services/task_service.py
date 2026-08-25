"""Task 유스케이스.

상태 변경·일정 변경은 둘 다 활동이력을 부수효과로 남긴다는 공통점이 있어서
전용 메서드(change_status/change_schedule)로 분리했다 — PATCH /tasks/{id}로
아무 필드나 바꾸는 범용 update()와 섞으면 "왜 이 필드를 바꿀 땐 활동이력이
남고 저 필드는 안 남지?"가 코드만 봐서는 알기 어려워진다.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from application.ports.outbound.holiday_calendar_port import HolidayCalendarPort
from application.ports.outbound.meeting_task_repository import MeetingTaskRepository
from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from application.ports.outbound.task_assignee_repository import TaskAssigneeRepository
from application.ports.outbound.task_comment_repository import TaskCommentRepository
from application.ports.outbound.task_dependency_repository import (
    TaskDependencyRepository,
)
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.ports.outbound.task_repository import TaskRepository
from domain.common.enums import TaskStatus
from domain.exceptions import TaskGroupNotFoundError, TaskNotFoundError
from domain.task import Task, calculate_due_date, is_weekend, validate_schedule
from domain.task_activity_log import ActivityEventType, TaskActivityLog


class TaskService:
    """Task 등록·조회·수정·삭제 + 상태/일정 전이 유스케이스."""

    def __init__(
        self,
        task_repository: TaskRepository,
        activity_log_repository: TaskActivityLogRepository,
        comment_repository: TaskCommentRepository,
        assignee_repository: TaskAssigneeRepository,
        dependency_repository: TaskDependencyRepository,
        meeting_task_repository: MeetingTaskRepository,
        task_group_repository: TaskGroupRepository,
        holiday_calendar: HolidayCalendarPort,
    ) -> None:
        self.task_repository = task_repository
        self.activity_log_repository = activity_log_repository
        self.comment_repository = comment_repository
        self.assignee_repository = assignee_repository
        self.dependency_repository = dependency_repository
        self.meeting_task_repository = meeting_task_repository
        self.task_group_repository = task_group_repository
        self.holiday_calendar = holiday_calendar

    def _resolve_due_date(
        self,
        start_date: date | None,
        due_date: date | None,
        estimated_days: int | None,
    ) -> date | None:
        """마감일이 비어 있고 시작일+예상일수가 있으면 자동 계산한다."""
        if due_date is not None:
            return due_date
        if start_date is None or estimated_days is None:
            return None
        return calculate_due_date(start_date, estimated_days, self._is_workday)

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
            due_date=self._resolve_due_date(start_date, due_date, estimated_days),
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
        않기 때문이다(0번 섹션 참고).

        마감일을 비워서 보내면 이미 저장된 예상 소요일수를 근거로 자동
        계산한다 — 그래서 Task를 먼저 읽고 나서 마감일을 확정한다."""
        task = self.get(task_id)
        resolved_due_date = self._resolve_due_date(
            start_date, due_date, task.estimated_days
        )
        validate_schedule(start_date, resolved_due_date)

        old_value = self._format_schedule(task.start_date, task.due_date)
        new_value = self._format_schedule(start_date, resolved_due_date)

        task.start_date = start_date
        task.due_date = resolved_due_date
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

    def count_by_status_bulk(
        self, task_group_ids: list[int]
    ) -> dict[int, dict[TaskStatus, int]]:
        """목록 화면 진행률용 묶음 집계. count_by_status와 달리
        TaskGroup이 몇 개든 쿼리 한 번으로 끝난다."""
        return self.task_repository.count_by_status_bulk(task_group_ids)

    def delete(self, task_id: int) -> None:
        """Task를 삭제한다. API 설계 5.2절 순서: 댓글 → 활동이력 →
        담당자 → 선행 관계(양방향) → 미팅 연결 → Task 행."""
        self.get(task_id)
        self.comment_repository.delete_by_task(task_id)
        self.activity_log_repository.delete_by_task(task_id)
        self.assignee_repository.delete_by_task(task_id)
        self.dependency_repository.delete_by_task(task_id)
        self.meeting_task_repository.delete_by_task(task_id)
        self.task_repository.delete(task_id)

    def _ensure_task_group_exists(self, task_group_id: int) -> None:
        if not self.task_group_repository.get(task_group_id):
            raise TaskGroupNotFoundError(task_group_id)

    def _is_workday(self, day: date) -> bool:
        return not is_weekend(day) and not self.holiday_calendar.is_holiday(day)

    @staticmethod
    def _format_schedule(start_date: date | None, due_date: date | None) -> str:
        return f"{start_date or '-'} ~ {due_date or '-'}"
