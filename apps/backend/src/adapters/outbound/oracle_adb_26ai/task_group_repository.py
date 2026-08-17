from datetime import date, datetime, timezone

from sqlmodel import Session, func, select

from adapters.outbound.oracle_adb_26ai.models import TaskGroupTable
from application.ports.outbound.task_group_repository import TaskGroupRepository
from domain.common.enums import Scope, TaskStatus
from domain.task_group import TaskGroup


class SqlTaskGroupRepository(TaskGroupRepository):
    """TaskGroupRepository의 Oracle/SQLModel 구현체."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, task_group: TaskGroup) -> TaskGroup:
        row = TaskGroupTable(
            category=task_group.category.value,
            name=task_group.name,
            description=task_group.description,
            status=task_group.status.value,
            is_archived="Y" if task_group.is_archived else "N",
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, task_group_id: int) -> TaskGroup | None:
        row = self.session.get(TaskGroupTable, task_group_id)
        return self._to_domain(row) if row else None

    def list(
        self,
        category: Scope | None = None,
        status: TaskStatus | None = None,
        include_archived: bool = False,
        created_after: date | None = None,
        created_before: date | None = None,
    ) -> list[TaskGroup]:
        stmt = select(TaskGroupTable)
        if not include_archived:
            stmt = stmt.where(TaskGroupTable.is_archived == "N")
        if category:
            stmt = stmt.where(TaskGroupTable.category == category.value)
        if status:
            stmt = stmt.where(TaskGroupTable.status == status.value)
        if created_after:
            stmt = stmt.where(func.trunc(TaskGroupTable.created_at) >= created_after)
        if created_before:
            stmt = stmt.where(func.trunc(TaskGroupTable.created_at) <= created_before)
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def update(self, task_group: TaskGroup) -> TaskGroup:
        row = self.session.get(TaskGroupTable, task_group.id)
        row.category = task_group.category.value
        row.name = task_group.name
        row.description = task_group.description
        row.status = task_group.status.value
        row.is_archived = "Y" if task_group.is_archived else "N"
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def delete(self, task_group_id: int) -> None:
        row = self.session.get(TaskGroupTable, task_group_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    @staticmethod
    def _to_domain(row: TaskGroupTable) -> TaskGroup:
        return TaskGroup(
            id=row.id,
            category=Scope(row.category),
            name=row.name,
            description=row.description,
            status=TaskStatus(row.status),
            is_archived=row.is_archived == "Y",
        )
