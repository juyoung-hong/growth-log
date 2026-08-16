from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import TaskGroupAttachmentTable
from application.ports.outbound.task_group_attachment_repository import (
    TaskGroupAttachmentRepository,
)
from domain.task_group_attachment import AttachmentType, TaskGroupAttachment


class SqlTaskGroupAttachmentRepository(TaskGroupAttachmentRepository):
    """TaskGroupAttachmentRepository의 Oracle/SQLModel 구현체."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, attachment: TaskGroupAttachment) -> TaskGroupAttachment:
        row = TaskGroupAttachmentTable(
            task_group_id=attachment.task_group_id,
            type=attachment.type.value,
            title=attachment.title,
            object_storage_path=attachment.object_storage_path,
            external_url=attachment.external_url,
            file_size_bytes=attachment.file_size_bytes,
            mime_type=attachment.mime_type,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get(self, attachment_id: int) -> TaskGroupAttachment | None:
        row = self.session.get(TaskGroupAttachmentTable, attachment_id)
        return self._to_domain(row) if row else None

    def list(self, task_group_id: int) -> list[TaskGroupAttachment]:
        stmt = select(TaskGroupAttachmentTable).where(
            TaskGroupAttachmentTable.task_group_id == task_group_id
        )
        rows = self.session.exec(stmt).all()
        return [self._to_domain(r) for r in rows]

    def delete(self, attachment_id: int) -> None:
        row = self.session.get(TaskGroupAttachmentTable, attachment_id)
        if row:
            self.session.delete(row)
            self.session.commit()

    @staticmethod
    def _to_domain(row: TaskGroupAttachmentTable) -> TaskGroupAttachment:
        return TaskGroupAttachment(
            id=row.id,
            task_group_id=row.task_group_id,
            type=AttachmentType(row.type),
            title=row.title,
            object_storage_path=row.object_storage_path,
            external_url=row.external_url,
            file_size_bytes=row.file_size_bytes,
            mime_type=row.mime_type,
        )
