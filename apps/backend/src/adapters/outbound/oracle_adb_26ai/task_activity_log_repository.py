from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import TaskActivityLogTable
from application.ports.outbound.task_activity_log_repository import (
    TaskActivityLogRepository,
)
from domain.task_activity_log import ActivityEventType, TaskActivityLog


class SqlTaskActivityLogRepository(TaskActivityLogRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, log: TaskActivityLog) -> TaskActivityLog:
        row = TaskActivityLogTable(
            task_id=log.task_id,
            event_type=log.event_type.value,
            old_value=log.old_value,
            new_value=log.new_value,
            reason=log.reason,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def list(self, task_id: int) -> list[TaskActivityLog]:
        stmt = (
            select(TaskActivityLogTable)
            .where(TaskActivityLogTable.task_id == task_id)
            .order_by(TaskActivityLogTable.event_at)
        )
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def delete_by_task(self, task_id: int) -> None:
        stmt = select(TaskActivityLogTable).where(
            TaskActivityLogTable.task_id == task_id
        )
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

    @staticmethod
    def _to_domain(row: TaskActivityLogTable) -> TaskActivityLog:
        return TaskActivityLog(
            id=row.id,
            task_id=row.task_id,
            event_type=ActivityEventType(row.event_type),
            old_value=row.old_value,
            new_value=row.new_value,
            reason=row.reason,
            event_at=row.event_at,
        )
