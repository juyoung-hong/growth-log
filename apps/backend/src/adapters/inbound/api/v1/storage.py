"""저장공간 관리 라우터 — 사용량 조회, export, 아카이브 삭제."""

from __future__ import annotations

import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from adapters.inbound.api.deps import (
    get_attachment_service,
    get_export_service,
    get_meeting_service,
    get_storage_service,
    get_task_group_service,
    get_task_group_size_estimator,
    get_task_service,
)
from adapters.inbound.api.schemas.storage import (
    ExportCreate,
    ExportJobRead,
    ExportJobTaskGroupRead,
    StorageQuota,
    StorageUsageRead,
)
from application.ports.outbound.task_group_size_estimator import TaskGroupSizeEstimator
from application.services.attachment_service import AttachmentService
from application.services.export_service import ExportService
from application.services.meeting_service import MeetingService
from application.services.storage_service import StorageService
from application.services.task_group_service import TaskGroupService
from application.services.task_service import TaskService
from config.settings import settings
from domain.exceptions import (
    ExportJobNotFoundError,
    ExportLinkNotFoundError,
    TaskGroupNotFoundError,
)
from domain.task_group_attachment import AttachmentType

router = APIRouter(prefix="/storage", tags=["storage"])


def _quota(used_bytes: int, limit_bytes: int) -> StorageQuota:
    percent = round(used_bytes / limit_bytes * 100, 1) if limit_bytes else 0.0
    return StorageQuota(used_bytes=used_bytes, limit_bytes=limit_bytes, percent=percent)


@router.get("/usage", response_model=StorageUsageRead)
def get_usage(service: StorageService = Depends(get_storage_service)):
    usage = service.get_usage()
    db_quota = _quota(usage.db_used_bytes, settings.db_capacity_bytes)
    os_quota = _quota(
        usage.object_storage_used_bytes, settings.object_storage_capacity_bytes
    )
    threshold_percent = settings.storage_warning_threshold * 100
    warnings = []
    if db_quota.percent >= threshold_percent:
        warnings.append("db")
    if os_quota.percent >= threshold_percent:
        warnings.append("object_storage")
    return StorageUsageRead(
        checked_at=datetime.now(timezone.utc),
        db=db_quota,
        object_storage=os_quota,
        warnings=warnings,
    )


def _build_export_read(export_job, links) -> ExportJobRead:
    return ExportJobRead(
        id=export_job.id,
        requested_at=export_job.requested_at,
        completed_at=export_job.completed_at,
        task_groups=[
            ExportJobTaskGroupRead(
                task_group_id=link.task_group_id,
                db_bytes_freed=link.db_bytes_freed,
                object_storage_bytes_freed=link.object_storage_bytes_freed,
                is_source_deleted=link.is_source_deleted,
                deleted_at=link.deleted_at,
            )
            for link in links
        ],
    )


@router.get("/exports", response_model=list[ExportJobRead])
def list_exports(service: ExportService = Depends(get_export_service)):
    return [
        _build_export_read(job, service.list_links(job.id))
        for job in service.list_exports()
    ]


@router.post("/exports", response_model=ExportJobRead, status_code=201)
def create_export(
    body: ExportCreate, service: ExportService = Depends(get_export_service)
):
    try:
        export_job = service.create_export(body.task_group_ids)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")
    return _build_export_read(export_job, service.list_links(export_job.id))


@router.get("/exports/{export_job_id}/download")
def download_export(
    export_job_id: int, service: ExportService = Depends(get_export_service)
):
    try:
        content = service.build_zip(export_job_id)
    except ExportJobNotFoundError:
        raise HTTPException(status_code=404, detail="export를 찾을 수 없습니다.")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=export_{export_job_id}.zip"
        },
    )


@router.delete("/exports/{export_job_id}/task-groups/{task_group_id}", status_code=204)
def archive_delete(
    export_job_id: int,
    task_group_id: int,
    export_service: ExportService = Depends(get_export_service),
    task_group_service: TaskGroupService = Depends(get_task_group_service),
    attachment_service: AttachmentService = Depends(get_attachment_service),
    task_service: TaskService = Depends(get_task_service),
    meeting_service: MeetingService = Depends(get_meeting_service),
    size_estimator: TaskGroupSizeEstimator = Depends(get_task_group_size_estimator),
):
    """export가 이미 완료돼 로컬에 저장됐다고 사용자가 확인한 뒤에만
    호출되는, 원본 삭제를 확정하는 별도 엔드포인트다(0번 섹션 ④)."""
    try:
        link = export_service.get_link(export_job_id, task_group_id)
    except ExportLinkNotFoundError:
        raise HTTPException(status_code=404, detail="export 대상을 찾을 수 없습니다.")
    if link.is_source_deleted:
        raise HTTPException(status_code=409, detail="이미 삭제된 대상입니다.")

    object_storage_bytes_freed = sum(
        a.file_size_bytes or 0
        for a in attachment_service.list(task_group_id)
        if a.type == AttachmentType.FILE
    )
    db_bytes_freed = size_estimator.estimate_content_bytes(task_group_id)

    for task in task_service.list(task_group_id, view="all"):
        task_service.delete(task.id)
    for attachment in attachment_service.list(task_group_id):
        attachment_service.delete(attachment.id)
    for meeting in meeting_service.list(task_group_id):
        meeting_service.delete(meeting.id)
    task_group_service.update(task_group_id, is_archived=True)

    export_service.mark_deleted(
        export_job_id, task_group_id, db_bytes_freed, object_storage_bytes_freed
    )
