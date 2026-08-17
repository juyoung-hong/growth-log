from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from adapters.outbound.oracle_adb_26ai.models import (
    ExportJobTable,
    ExportJobTaskGroupTable,
)
from application.ports.outbound.export_job_repository import ExportJobRepository
from domain.export_job import ExportJob, ExportJobTaskGroup


class SqlExportJobRepository(ExportJobRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, task_group_ids: list[int]) -> ExportJob:
        now = datetime.now(timezone.utc)
        # 동기 처리라 생성과 동시에 완료 처리한다.
        row = ExportJobTable(requested_at=now, completed_at=now)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)

        for task_group_id in task_group_ids:
            self.session.add(
                ExportJobTaskGroupTable(
                    export_job_id=row.id, task_group_id=task_group_id
                )
            )
        self.session.commit()

        return self._to_domain(row)

    def get(self, export_job_id: int) -> ExportJob | None:
        row = self.session.get(ExportJobTable, export_job_id)
        return self._to_domain(row) if row else None

    def list(self) -> list[ExportJob]:
        rows = self.session.exec(select(ExportJobTable)).all()
        return [self._to_domain(r) for r in rows]

    def get_link(
        self, export_job_id: int, task_group_id: int
    ) -> ExportJobTaskGroup | None:
        row = self.session.get(ExportJobTaskGroupTable, (export_job_id, task_group_id))
        return self._to_link_domain(row) if row else None

    def list_links(self, export_job_id: int) -> list[ExportJobTaskGroup]:
        stmt = select(ExportJobTaskGroupTable).where(
            ExportJobTaskGroupTable.export_job_id == export_job_id
        )
        rows = self.session.exec(stmt).all()
        return [self._to_link_domain(r) for r in rows]

    def update_link(self, link: ExportJobTaskGroup) -> ExportJobTaskGroup:
        row = self.session.get(
            ExportJobTaskGroupTable, (link.export_job_id, link.task_group_id)
        )
        row.db_bytes_freed = link.db_bytes_freed
        row.object_storage_bytes_freed = link.object_storage_bytes_freed
        row.is_source_deleted = "Y" if link.is_source_deleted else "N"
        row.deleted_at = link.deleted_at
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_link_domain(row)

    @staticmethod
    def _to_domain(row: ExportJobTable) -> ExportJob:
        return ExportJob(
            id=row.id, requested_at=row.requested_at, completed_at=row.completed_at
        )

    @staticmethod
    def _to_link_domain(row: ExportJobTaskGroupTable) -> ExportJobTaskGroup:
        return ExportJobTaskGroup(
            export_job_id=row.export_job_id,
            task_group_id=row.task_group_id,
            db_bytes_freed=row.db_bytes_freed,
            object_storage_bytes_freed=row.object_storage_bytes_freed,
            is_source_deleted=row.is_source_deleted == "Y",
            deleted_at=row.deleted_at,
        )
