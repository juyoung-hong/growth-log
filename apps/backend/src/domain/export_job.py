"""Export(내보내기) 도메인 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExportJob:
    id: int | None
    requested_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class ExportJobTaskGroup:
    """ExportJob과 TaskGroup의 연결. 아카이브 삭제 상태를 함께 담는다."""

    export_job_id: int
    task_group_id: int
    db_bytes_freed: int | None = None
    object_storage_bytes_freed: int | None = None
    is_source_deleted: bool = False
    deleted_at: datetime | None = None
