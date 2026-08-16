"""TaskGroup 참고자료(Attachment) 도메인 모델.

파일(Object Storage에 저장) 또는 외부 URL 링크, 둘 중 하나만 가질 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.common.exceptions import InvalidFieldError
from domain.common.validators import validate_not_empty


class AttachmentType(str, Enum):
    """참고자료가 업로드 파일인지, 외부 URL 링크인지 구분한다."""

    FILE = "파일"
    URL = "URL"


@dataclass
class TaskGroupAttachment:
    """TaskGroup에 첨부된 참고자료."""

    id: int | None
    task_group_id: int
    type: AttachmentType
    title: str
    object_storage_path: str | None = None
    external_url: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None

    def __post_init__(self) -> None:
        validate_not_empty(self.title, field="title")
        if self.type == AttachmentType.FILE:
            if not self.object_storage_path:
                raise InvalidFieldError(
                    "object_storage_path",
                    "파일 타입은 object_storage_path가 필요합니다.",
                )
            if self.external_url:
                raise InvalidFieldError(
                    "external_url", "파일 타입은 external_url을 가질 수 없습니다."
                )
        else:
            if not self.external_url:
                raise InvalidFieldError(
                    "external_url", "URL 타입은 external_url이 필요합니다."
                )
            if self.object_storage_path:
                raise InvalidFieldError(
                    "object_storage_path",
                    "URL 타입은 object_storage_path를 가질 수 없습니다.",
                )
        if self.file_size_bytes is not None and self.file_size_bytes < 0:
            raise InvalidFieldError("file_size_bytes", "음수일 수 없습니다.")
