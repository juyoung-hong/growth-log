"""Export 유스케이스."""

from __future__ import annotations

import csv
import io
import mimetypes
import zipfile
from datetime import datetime, timezone

from application.ports.outbound.export_job_repository import ExportJobRepository
from application.ports.outbound.object_storage_port import ObjectStoragePort
from application.ports.outbound.task_group_repository import TaskGroupRepository
from application.services.attachment_service import AttachmentService
from application.services.meeting_service import MeetingService
from application.services.task_comment_service import TaskCommentService
from application.services.task_group_service import TaskGroupService
from application.services.task_service import TaskService
from domain.exceptions import (
    ExportJobNotFoundError,
    ExportLinkNotFoundError,
    TaskGroupNotFoundError,
)
from domain.export_job import ExportJob, ExportJobTaskGroup
from domain.task_group_attachment import AttachmentType


def _attachment_filename(attachment) -> str:
    """mime_type으로 확장자를 붙인다. title에 이미 그 확장자가 있으면 중복으로 안 붙인다."""
    ext = (
        mimetypes.guess_extension(attachment.mime_type)
        if attachment.mime_type
        else None
    )
    if ext and not attachment.title.lower().endswith(ext.lower()):
        return f"{attachment.title}{ext}"
    return attachment.title


class ExportService:
    """export 생성, zip 구성, 아카이브 삭제 상태 기록 유스케이스."""

    def __init__(
        self,
        export_job_repository: ExportJobRepository,
        task_group_repository: TaskGroupRepository,
        task_group_service: TaskGroupService,
        task_service: TaskService,
        task_comment_service: TaskCommentService,
        meeting_service: MeetingService,
        attachment_service: AttachmentService,
        object_storage: ObjectStoragePort,
    ) -> None:
        self.export_job_repository = export_job_repository
        self.task_group_repository = task_group_repository
        self.task_group_service = task_group_service
        self.task_service = task_service
        self.task_comment_service = task_comment_service
        self.meeting_service = meeting_service
        self.attachment_service = attachment_service
        self.object_storage = object_storage

    def create_export(self, task_group_ids: list[int]) -> ExportJob:
        """export_job을 동기적으로 생성한다. 원본 데이터는 전혀 건드리지
        않는다 — 삭제는 항상 별도 호출(mark_deleted, 라우터에서 조립)."""
        for task_group_id in task_group_ids:
            if not self.task_group_repository.get(task_group_id):
                raise TaskGroupNotFoundError(task_group_id)
        return self.export_job_repository.add(task_group_ids)

    def list_exports(self) -> list[ExportJob]:
        return self.export_job_repository.list()

    def list_links(self, export_job_id: int) -> list[ExportJobTaskGroup]:
        return self.export_job_repository.list_links(export_job_id)

    def get_link(self, export_job_id: int, task_group_id: int) -> ExportJobTaskGroup:
        link = self.export_job_repository.get_link(export_job_id, task_group_id)
        if not link:
            raise ExportLinkNotFoundError(export_job_id, task_group_id)
        return link

    def mark_deleted(
        self,
        export_job_id: int,
        task_group_id: int,
        db_bytes_freed: int,
        object_storage_bytes_freed: int,
    ) -> None:
        """아카이브 삭제가 끝난 뒤 그 사실을 기록한다. 실제 데이터 삭제는
        라우터가 이 메서드를 부르기 전에 이미 끝낸 상태다."""
        link = self.get_link(export_job_id, task_group_id)
        link.is_source_deleted = True
        link.deleted_at = datetime.now(timezone.utc)
        link.db_bytes_freed = db_bytes_freed
        link.object_storage_bytes_freed = object_storage_bytes_freed
        self.export_job_repository.update_link(link)

    def build_zip(self, export_job_id: int) -> bytes:
        """export_job에 연결된 TaskGroup들의 데이터를 zip으로 묶는다.
        구조화된 데이터는 엔티티별 CSV로, 참고자료 파일은 TaskGroup별
        폴더에 그대로 담는다(0번 섹션 ③)."""
        export_job = self.export_job_repository.get(export_job_id)
        if not export_job:
            raise ExportJobNotFoundError(export_job_id)

        links = self.export_job_repository.list_links(export_job_id)
        task_group_rows: list[dict] = []
        task_rows: list[dict] = []
        comment_rows: list[dict] = []
        activity_log_rows: list[dict] = []
        meeting_rows: list[dict] = []

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for link in links:
                self._collect_task_group(
                    zf,
                    link.task_group_id,
                    task_group_rows,
                    task_rows,
                    comment_rows,
                    activity_log_rows,
                    meeting_rows,
                )

            zf.writestr("task_groups.csv", _to_csv(task_group_rows))
            zf.writestr("tasks.csv", _to_csv(task_rows))
            zf.writestr("task_comments.csv", _to_csv(comment_rows))
            zf.writestr("task_activity_logs.csv", _to_csv(activity_log_rows))
            zf.writestr("meetings.csv", _to_csv(meeting_rows))

        return buffer.getvalue()

    def _collect_task_group(
        self,
        zf: zipfile.ZipFile,
        task_group_id: int,
        task_group_rows: list[dict],
        task_rows: list[dict],
        comment_rows: list[dict],
        activity_log_rows: list[dict],
        meeting_rows: list[dict],
    ) -> None:
        task_group = self.task_group_service.get(task_group_id)
        task_group_rows.append(
            {
                "id": task_group.id,
                "name": task_group.name,
                "category": task_group.category.value,
                "status": task_group.status.value,
                "description": task_group.description or "",
            }
        )

        for task in self.task_service.list(task_group_id, view="all"):
            task_rows.append(
                {
                    "id": task.id,
                    "task_group_id": task_group_id,
                    "name": task.name,
                    "status": task.status.value,
                    "start_date": task.start_date or "",
                    "due_date": task.due_date or "",
                    "completed_at": task.completed_at or "",
                }
            )
            for comment in self.task_comment_service.list(task.id):
                comment_rows.append(
                    {
                        "task_id": task.id,
                        "content": comment.content,
                        "created_at": comment.created_at,
                    }
                )
            for log in self.task_service.list_activity_log(task.id):
                activity_log_rows.append(
                    {
                        "task_id": task.id,
                        "event_type": log.event_type.value,
                        "old_value": log.old_value or "",
                        "new_value": log.new_value or "",
                        "reason": log.reason or "",
                        "event_at": log.event_at,
                    }
                )

        for meeting in self.meeting_service.list(task_group_id):
            meeting_rows.append(
                {
                    "id": meeting.id,
                    "task_group_id": task_group_id,
                    "status": meeting.status.value,
                    "scheduled_at": meeting.scheduled_at,
                    "agenda": meeting.agenda or "",
                    "content": meeting.content or "",
                }
            )

        folder = f"attachments/{task_group.id}_{task_group.name}"
        link_rows = []
        for attachment in self.attachment_service.list(task_group_id):
            if (
                attachment.type == AttachmentType.FILE
                and attachment.object_storage_path
            ):
                content = self.object_storage.download(attachment.object_storage_path)
                zf.writestr(f"{folder}/{_attachment_filename(attachment)}", content)
            else:
                link_rows.append(
                    {"title": attachment.title, "external_url": attachment.external_url}
                )
        if link_rows:
            zf.writestr(f"{folder}/_links.csv", _to_csv(link_rows))


def _to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
