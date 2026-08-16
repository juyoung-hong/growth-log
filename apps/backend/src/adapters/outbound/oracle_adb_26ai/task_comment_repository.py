from datetime import datetime, timezone

from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import TaskCommentTable
from application.ports.outbound.task_comment_repository import TaskCommentRepository
from domain.task_comment import TaskComment


class SqlTaskCommentRepository(TaskCommentRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, comment: TaskComment) -> TaskComment:
        row = TaskCommentTable(task_id=comment.task_id, content=comment.content)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, comment_id: int) -> TaskComment | None:
        row = self.session.get(TaskCommentTable, comment_id)
        return self._to_domain(row) if row else None

    def list(self, task_id: int) -> list[TaskComment]:
        stmt = (
            select(TaskCommentTable)
            .where(TaskCommentTable.task_id == task_id)
            .order_by(TaskCommentTable.created_at)
        )
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def update(self, comment: TaskComment) -> TaskComment:
        row = self.session.get(TaskCommentTable, comment.id)
        row.content = comment.content
        row.updated_at = datetime.now(timezone.utc)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def delete(self, comment_id: int) -> None:
        row = self.session.get(TaskCommentTable, comment_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    def delete_by_task(self, task_id: int) -> None:
        stmt = select(TaskCommentTable).where(TaskCommentTable.task_id == task_id)
        for row in self.session.exec(stmt).all():
            self.session.delete(row)
        self.session.commit()

    @staticmethod
    def _to_domain(row: TaskCommentTable) -> TaskComment:
        return TaskComment(
            id=row.id,
            task_id=row.task_id,
            content=row.content,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
