from datetime import datetime, timezone

from sqlmodel import Session, func, select

from adapters.outbound.oracle_adb_26ai.models import StorageUsageSnapshotTable
from application.ports.outbound.storage_usage_snapshot_repository import (
    StorageUsageSnapshotRepository,
)


class SqlStorageUsageSnapshotRepository(StorageUsageSnapshotRepository):
    def __init__(self, session: Session):
        self.session = session

    def has_snapshot_for_today(self) -> bool:
        today = datetime.now(timezone.utc).date()
        stmt = select(StorageUsageSnapshotTable).where(
            func.trunc(StorageUsageSnapshotTable.checked_at) == today
        )
        return self.session.exec(stmt).first() is not None

    def add(self, db_used_bytes: int, object_storage_used_bytes: int) -> None:
        row = StorageUsageSnapshotTable(
            db_used_bytes=db_used_bytes,
            object_storage_used_bytes=object_storage_used_bytes,
        )
        self.session.add(row)
        self.session.commit()
