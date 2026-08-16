from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import TaskAssigneeTable
from application.ports.outbound.task_assignee_repository import TaskAssigneeRepository


class SqlTaskAssigneeRepository(TaskAssigneeRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, task_id: int, person_id: int) -> None:
        row = TaskAssigneeTable(task_id=task_id, person_id=person_id)
        self.session.add(row)
        self.session.commit()

    def remove(self, task_id: int, person_id: int) -> None:
        row = self.session.get(TaskAssigneeTable, (task_id, person_id))
        if row:
            self.session.delete(row)
            self.session.commit()

    def exists(self, task_id: int, person_id: int) -> bool:
        return self.session.get(TaskAssigneeTable, (task_id, person_id)) is not None

    def list_person_ids(self, task_id: int) -> list[int]:
        stmt = select(TaskAssigneeTable.person_id).where(
            TaskAssigneeTable.task_id == task_id
        )
        return list(self.session.exec(stmt).all())

    def delete_by_task(self, task_id: int) -> None:
        stmt = select(TaskAssigneeTable).where(TaskAssigneeTable.task_id == task_id)
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

    def is_person_referenced(self, person_id: int) -> bool:
        stmt = select(TaskAssigneeTable).where(TaskAssigneeTable.person_id == person_id)
        return self.session.exec(stmt).first() is not None
