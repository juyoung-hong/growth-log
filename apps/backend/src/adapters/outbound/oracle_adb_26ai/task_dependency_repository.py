from sqlmodel import Session, or_, select

from adapters.outbound.oracle_adb_26ai.models import TaskDependencyTable
from application.ports.outbound.task_dependency_repository import (
    TaskDependencyRepository,
)


class SqlTaskDependencyRepository(TaskDependencyRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, task_id: int, depends_on_task_id: int) -> None:
        row = TaskDependencyTable(
            task_id=task_id, depends_on_task_id=depends_on_task_id
        )
        self.session.add(row)
        self.session.commit()

    def remove(self, task_id: int, depends_on_task_id: int) -> None:
        row = self.session.get(TaskDependencyTable, (task_id, depends_on_task_id))
        if row:
            self.session.delete(row)
            self.session.commit()

    def exists(self, task_id: int, depends_on_task_id: int) -> bool:
        return (
            self.session.get(TaskDependencyTable, (task_id, depends_on_task_id))
            is not None
        )

    def list_depends_on_ids(self, task_id: int) -> list[int]:
        stmt = select(TaskDependencyTable.depends_on_task_id).where(
            TaskDependencyTable.task_id == task_id
        )
        return list(self.session.exec(stmt).all())

    def delete_by_task(self, task_id: int) -> None:
        stmt = select(TaskDependencyTable).where(
            or_(
                TaskDependencyTable.task_id == task_id,
                TaskDependencyTable.depends_on_task_id == task_id,
            )
        )
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()
