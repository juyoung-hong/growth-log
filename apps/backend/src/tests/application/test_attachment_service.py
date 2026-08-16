"""AttachmentService 유스케이스를 Fake로 DB/Object Storage 없이 검증한다."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from application.services.attachment_service import AttachmentService
from domain.common.enums import Scope
from domain.exceptions import (
    FileTooLargeError,
    TaskGroupAttachmentNotFoundError,
    TaskGroupNotFoundError,
)
from domain.task_group import TaskGroup


def test_URL_참고자료를_등록한다(
    attachment_service: AttachmentService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    attachment = attachment_service.create_url_attachment(
        task_group_id=task_group.id,
        title="레퍼런스 문서",
        external_url="https://example.com",
    )
    assert attachment.id is not None


def test_없는_TaskGroup에_등록하면_예외(attachment_service: AttachmentService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        attachment_service.create_url_attachment(
            task_group_id=999, title="레퍼런스", external_url="https://example.com"
        )


def test_파일_참고자료를_등록하면_object_storage에_업로드된다(
    attachment_service: AttachmentService, task_group_repository, fake_object_storage
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.PERSONAL, name="그룹")
    )
    attachment = attachment_service.create_file_attachment(
        task_group_id=task_group.id,
        title="회의자료",
        content=b"hello",
        mime_type="text/plain",
    )
    assert fake_object_storage.uploaded[attachment.object_storage_path] == b"hello"


def test_파일_크기가_상한을_넘으면_예외(
    attachment_service: AttachmentService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    huge_content = b"x" * (21 * 1024 * 1024)  # 21MB, 상한(20MB) 초과
    with pytest.raises(FileTooLargeError):
        attachment_service.create_file_attachment(
            task_group_id=task_group.id,
            title="큰 파일",
            content=huge_content,
            mime_type="application/pdf",
        )


def test_이미지는_리사이즈_후_JPEG로_변환된다(
    attachment_service: AttachmentService, task_group_repository, fake_object_storage
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    big_image = Image.new("RGB", (4000, 3000), color="red")
    buffer = io.BytesIO()
    big_image.save(buffer, format="PNG")

    attachment = attachment_service.create_file_attachment(
        task_group_id=task_group.id,
        title="스크린샷",
        content=buffer.getvalue(),
        mime_type="image/png",
    )

    assert attachment.mime_type == "image/jpeg"
    uploaded_bytes = fake_object_storage.uploaded[attachment.object_storage_path]
    resized = Image.open(io.BytesIO(uploaded_bytes))
    assert resized.format == "JPEG"
    assert max(resized.size) <= 2000


def test_삭제하면_object_storage에서도_제거된다(
    attachment_service: AttachmentService, task_group_repository, fake_object_storage
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    attachment = attachment_service.create_file_attachment(
        task_group_id=task_group.id,
        title="자료",
        content=b"data",
        mime_type="text/plain",
    )

    attachment_service.delete(attachment.id)

    assert attachment.object_storage_path not in fake_object_storage.uploaded
    with pytest.raises(TaskGroupAttachmentNotFoundError):
        attachment_service.delete(attachment.id)
