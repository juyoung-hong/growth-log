"""TaskGroup 참고자료 유스케이스.

리포지토리 2개(TaskGroupAttachmentRepository, TaskGroupRepository)와
ObjectStoragePort를 함께 조립한다 — 참고자료를 등록하려면 그 전에
TaskGroup이 실제로 존재하는지부터 확인해야 하기 때문이다.
"""

from __future__ import annotations

import io
from uuid import uuid4

from PIL import Image

from application.ports.outbound.object_storage_port import ObjectStoragePort
from application.ports.outbound.task_group_attachment_repository import (
    TaskGroupAttachmentRepository,
)
from application.ports.outbound.task_group_repository import TaskGroupRepository
from config.settings import settings
from domain.exceptions import (
    FileTooLargeError,
    TaskGroupAttachmentNotFoundError,
    TaskGroupNotFoundError,
)
from domain.task_group_attachment import AttachmentType, TaskGroupAttachment


class AttachmentService:
    """참고자료 등록·조회·삭제 유스케이스."""

    def __init__(
        self,
        attachment_repository: TaskGroupAttachmentRepository,
        task_group_repository: TaskGroupRepository,
        object_storage: ObjectStoragePort,
    ) -> None:
        self.attachment_repository = attachment_repository
        self.task_group_repository = task_group_repository
        self.object_storage = object_storage

    def list(self, task_group_id: int) -> list[TaskGroupAttachment]:
        """특정 TaskGroup의 참고자료 목록을 조회한다."""
        self._ensure_task_group_exists(task_group_id)
        return self.attachment_repository.list(task_group_id)

    def create_url_attachment(
        self, task_group_id: int, title: str, external_url: str
    ) -> TaskGroupAttachment:
        """URL 참고자료를 등록한다."""
        self._ensure_task_group_exists(task_group_id)
        attachment = TaskGroupAttachment(
            id=None,
            task_group_id=task_group_id,
            type=AttachmentType.URL,
            title=title,
            external_url=external_url,
        )
        return self.attachment_repository.add(attachment)

    def create_file_attachment(
        self, task_group_id: int, title: str, content: bytes, mime_type: str
    ) -> TaskGroupAttachment:
        """파일 참고자료를 등록한다.

        content가 settings.upload_max_bytes를 넘으면 FileTooLargeError.
        이미지면 리사이즈+JPEG 변환 후 저장하고, mime_type도 image/jpeg로
        바뀐다 — level2_attachment(=task_group_attachment)에는 처리된
        최종 결과만 남는다(API 설계 4.1절).
        """
        self._ensure_task_group_exists(task_group_id)

        if len(content) > settings.upload_max_bytes:
            raise FileTooLargeError(len(content))

        if _is_image(mime_type):
            content = _resize_and_convert_to_jpeg(
                content, settings.image_resize_max_px, settings.image_jpeg_quality
            )
            mime_type = "image/jpeg"

        object_storage_path = f"task-group/{task_group_id}/{uuid4()}"
        self.object_storage.upload(object_storage_path, content, mime_type)

        attachment = TaskGroupAttachment(
            id=None,
            task_group_id=task_group_id,
            type=AttachmentType.FILE,
            title=title,
            object_storage_path=object_storage_path,
            file_size_bytes=len(content),
            mime_type=mime_type,
        )
        return self.attachment_repository.add(attachment)

    def delete(self, attachment_id: int) -> None:
        """참고자료를 삭제한다. 파일 타입이면 Object Storage 원본도 함께 지운다."""
        attachment = self._get_attachment(attachment_id)
        if attachment.type == AttachmentType.FILE and attachment.object_storage_path:
            self.object_storage.delete(attachment.object_storage_path)
        self.attachment_repository.delete(attachment_id)

    def _ensure_task_group_exists(self, task_group_id: int) -> None:
        if not self.task_group_repository.get(task_group_id):
            raise TaskGroupNotFoundError(task_group_id)

    def _get_attachment(self, attachment_id: int) -> TaskGroupAttachment:
        attachment = self.attachment_repository.get(attachment_id)
        if not attachment:
            raise TaskGroupAttachmentNotFoundError(attachment_id)
        return attachment


def _is_image(mime_type: str) -> bool:
    return mime_type.startswith("image/")


def _resize_and_convert_to_jpeg(content: bytes, max_px: int, quality: int) -> bytes:
    image = Image.open(io.BytesIO(content))
    image = image.convert("RGB")  # JPEG는 알파 채널(투명도)을 지원하지 않는다
    image.thumbnail((max_px, max_px))  # 긴 변 기준 축소. 원본이 더 작으면 그대로 둔다
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()
