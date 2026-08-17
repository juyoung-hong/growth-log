"""TaskGroupAttachment 도메인 모델의 검증 규칙을 확인한다."""

from __future__ import annotations

import pytest

from domain.common.exceptions import EmptyFieldError, InvalidFieldError
from domain.task_group_attachment import AttachmentType, TaskGroupAttachment


def test_제목이_비어있으면_예외() -> None:
    with pytest.raises(EmptyFieldError):
        TaskGroupAttachment(
            id=None,
            task_group_id=1,
            type=AttachmentType.URL,
            title="  ",
            external_url="https://example.com",
        )


def test_파일_타입인데_object_storage_path가_없으면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        TaskGroupAttachment(
            id=None, task_group_id=1, type=AttachmentType.FILE, title="자료"
        )


def test_URL_타입인데_external_url이_없으면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        TaskGroupAttachment(
            id=None, task_group_id=1, type=AttachmentType.URL, title="링크"
        )


def test_파일_타입이_external_url도_가지면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        TaskGroupAttachment(
            id=None,
            task_group_id=1,
            type=AttachmentType.FILE,
            title="자료",
            object_storage_path="task-group/1/abc",
            external_url="https://example.com",
        )


def test_URL_타입이_object_storage_path도_가지면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        TaskGroupAttachment(
            id=None,
            task_group_id=1,
            type=AttachmentType.URL,
            title="링크",
            external_url="https://example.com",
            object_storage_path="task-group/1/abc",
        )


def test_파일_크기가_음수면_예외() -> None:
    with pytest.raises(InvalidFieldError):
        TaskGroupAttachment(
            id=None,
            task_group_id=1,
            type=AttachmentType.FILE,
            title="자료",
            object_storage_path="task-group/1/abc",
            file_size_bytes=-1,
        )
