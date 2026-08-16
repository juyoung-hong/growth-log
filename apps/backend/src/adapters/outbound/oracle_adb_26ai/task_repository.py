"""TaskRepository의 Oracle/SQLModel 구현체."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlmodel import Session, and_, or_, select

from adapters.outbound.oracle_adb_26ai.models import TaskTable
from application.ports.outbound.task_repository import TaskRepository
from domain.common.enums import TaskStatus
from domain.task import Task


class SqlTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> Task:
        row = TaskTable(
            task_group_id=task.task_group_id,
            name=task.name,
            status=task.status.value,
            estimated_days=task.estimated_days,
            start_date=task.start_date,
            due_date=task.due_date,
            completed_at=task.completed_at,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, task_id: int) -> Task | None:
        row = self.session.get(TaskTable, task_id)
        return self._to_domain(row) if row else None

    def list(
        self, task_group_id: int, view: Literal["default", "all"] = "default"
    ) -> list[Task]:
        stmt = select(TaskTable).where(TaskTable.task_group_id == task_group_id)
        if view == "default":
            recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            stmt = stmt.where(
                or_(
                    TaskTable.status == TaskStatus.IN_PROGRESS.value,
                    and_(
                        TaskTable.status == TaskStatus.PENDING.value,
                        TaskTable.created_at >= recent_cutoff,
                    ),
                )
            )
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def update(self, task: Task) -> Task:
        row = self.session.get(TaskTable, task.id)
        row.name = task.name
        row.status = task.status.value
        row.estimated_days = task.estimated_days
        row.start_date = task.start_date
        row.due_date = task.due_date
        row.completed_at = task.completed_at
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def delete(self, task_id: int) -> None:
        row = self.session.get(TaskTable, task_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    @staticmethod
    def _to_domain(row: TaskTable) -> Task:
        return Task(
            id=row.id,
            task_group_id=row.task_group_id,
            name=row.name,
            status=TaskStatus(row.status),
            estimated_days=row.estimated_days,
            start_date=row.start_date,
            due_date=row.due_date,
            completed_at=row.completed_at,
        )
