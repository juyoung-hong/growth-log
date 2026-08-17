from datetime import datetime

from pydantic import BaseModel


class StorageQuota(BaseModel):
    used_bytes: int
    limit_bytes: int
    percent: float


class StorageUsageRead(BaseModel):
    checked_at: datetime
    db: StorageQuota
    object_storage: StorageQuota
    warnings: list[str]


class ExportCreate(BaseModel):
    task_group_ids: list[int]


class ExportJobTaskGroupRead(BaseModel):
    task_group_id: int
    db_bytes_freed: int | None
    object_storage_bytes_freed: int | None
    is_source_deleted: bool
    deleted_at: datetime | None


class ExportJobRead(BaseModel):
    id: int
    requested_at: datetime
    completed_at: datetime | None
    task_groups: list[ExportJobTaskGroupRead]
