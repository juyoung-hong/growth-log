"""ExportService 유스케이스를 Fake로 DB/OCI 없이 검증한다."""

from __future__ import annotations

import io
import zipfile

import pytest

from application.services.export_service import ExportService
from domain.common.enums import Scope
from domain.exceptions import (
    ExportJobNotFoundError,
    ExportLinkNotFoundError,
    TaskGroupNotFoundError,
)
from domain.task_group import TaskGroup


def test_export를_생성한다(
    export_service: ExportService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    job = export_service.create_export([task_group.id])

    assert job.id is not None
    links = export_service.list_links(job.id)
    assert [link.task_group_id for link in links] == [task_group.id]


def test_없는_TaskGroup으로_export_생성하면_예외(export_service: ExportService) -> None:
    with pytest.raises(TaskGroupNotFoundError):
        export_service.create_export([999])


def test_zip에_csv와_첨부파일이_들어간다(
    export_service: ExportService,
    task_group_repository,
    task_service,
    attachment_service,
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task_service.create(task_group_id=task_group.id, name="작업")
    attachment_service.create_file_attachment(
        task_group_id=task_group.id,
        title="자료.txt",
        content=b"hello",
        mime_type="text/plain",
    )
    job = export_service.create_export([task_group.id])

    content = export_service.build_zip(job.id)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        names = zf.namelist()
        assert "task_groups.csv" in names
        assert "tasks.csv" in names
        assert any(
            n.startswith("attachments/") and n.endswith("자료.txt") for n in names
        )


def test_아카이브_삭제_상태를_기록한다(
    export_service: ExportService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    job = export_service.create_export([task_group.id])

    export_service.mark_deleted(
        job.id, task_group.id, db_bytes_freed=100, object_storage_bytes_freed=200
    )

    link = export_service.get_link(job.id, task_group.id)
    assert link.is_source_deleted is True
    assert link.db_bytes_freed == 100


def test_없는_링크를_조회하면_예외(export_service: ExportService) -> None:
    with pytest.raises(ExportLinkNotFoundError):
        export_service.get_link(999, 999)


def test_전체_export_이력을_조회한다(
    export_service: ExportService, task_group_repository
) -> None:
    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    export_service.create_export([task_group.id])
    export_service.create_export([task_group.id])

    assert len(export_service.list_exports()) == 2


def test_없는_export로_zip을_생성하면_예외(export_service: ExportService) -> None:
    with pytest.raises(ExportJobNotFoundError):
        export_service.build_zip(999)


def test_zip에_댓글_활동이력_미팅_URL참고자료가_반영된다(
    export_service: ExportService,
    task_group_repository,
    task_service,
    task_comment_service,
    meeting_service,
    attachment_service,
) -> None:
    from datetime import datetime, timezone

    task_group = task_group_repository.add(
        TaskGroup(id=None, category=Scope.COMPANY, name="그룹")
    )
    task = task_service.create(task_group_id=task_group.id, name="작업")
    task_comment_service.create(task.id, "댓글입니다")
    meeting_service.create(
        task_group_id=task_group.id,
        scheduled_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
    )
    attachment_service.create_url_attachment(
        task_group_id=task_group.id,
        title="레퍼런스",
        external_url="https://example.com",
    )
    job = export_service.create_export([task_group.id])

    content = export_service.build_zip(job.id)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        comments_csv = zf.read("task_comments.csv").decode("utf-8")
        meetings_csv = zf.read("meetings.csv").decode("utf-8")
        link_files = [n for n in zf.namelist() if n.endswith("_links.csv")]

    assert "댓글입니다" in comments_csv
    assert "2026-08-20" in meetings_csv
    assert len(link_files) == 1


def test_제목에_이미_확장자가_있으면_중복으로_안_붙는다() -> None:
    from application.services.export_service import _attachment_filename
    from domain.task_group_attachment import AttachmentType, TaskGroupAttachment

    attachment = TaskGroupAttachment(
        id=1,
        task_group_id=1,
        type=AttachmentType.FILE,
        title="사진.jpg",
        object_storage_path="task-group/1/abc",
        mime_type="image/jpeg",
    )

    assert _attachment_filename(attachment) == "사진.jpg"


def test_제목에_확장자가_없으면_mime_type_기준으로_붙는다() -> None:
    from application.services.export_service import _attachment_filename
    from domain.task_group_attachment import AttachmentType, TaskGroupAttachment

    attachment = TaskGroupAttachment(
        id=1,
        task_group_id=1,
        type=AttachmentType.FILE,
        title="스크린샷",
        object_storage_path="task-group/1/abc",
        mime_type="image/jpeg",
    )

    assert _attachment_filename(attachment) == "스크린샷.jpg"
