"""저장공간 사용량 유스케이스."""

from __future__ import annotations

from application.ports.outbound.database_usage_port import DatabaseUsagePort
from application.ports.outbound.object_storage_port import ObjectStoragePort
from application.ports.outbound.storage_usage_snapshot_repository import (
    StorageUsageSnapshotRepository,
)
from domain.storage import StorageUsage


class StorageService:
    """DB·Object Storage 사용량을 조회하고, 하루 1건 스냅샷을 남긴다."""

    def __init__(
        self,
        database_usage: DatabaseUsagePort,
        object_storage: ObjectStoragePort,
        snapshot_repository: StorageUsageSnapshotRepository,
    ) -> None:
        self.database_usage = database_usage
        self.object_storage = object_storage
        self.snapshot_repository = snapshot_repository

    def get_usage(self) -> StorageUsage:
        db_used_bytes = self.database_usage.get_used_bytes()
        object_storage_used_bytes = self.object_storage.get_used_bytes()
        if not self.snapshot_repository.has_snapshot_for_today():
            self.snapshot_repository.add(db_used_bytes, object_storage_used_bytes)
        return StorageUsage(
            db_used_bytes=db_used_bytes,
            object_storage_used_bytes=object_storage_used_bytes,
        )
